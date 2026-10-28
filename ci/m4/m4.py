#!/usr/bin/env python3
"""M4 checks against a running StarRocks + Arrow Flight SQL server (docs/M4-CI.md §4).

    m4.py --checks 1,2,3,4,5 --out DIR --tpch DIR --types DIR [--token T]

Expects StarRocks on 127.0.0.1:9030 (root, no password) whose BE reaches the Flight server at $M4_FLIGHT_URI.
Every check compares StarRocks with DuckDB on the same parquet files (or with tests/m4/reference/sf1).

On the maintainer's stand (docs/LOCAL-FINAL-CHECK.md), with an existing catalog and no parquet files:

    m4.py --checks 4,5 --out DIR --existing-catalog flight --reference bench/reference/sf10 \
          --ref-catalog jdbc --sr-cases-ref tests/m4/sr-cases/sr-cases.ref

StarRocks connection from $M4_SR_HOST / $M4_SR_PORT / $M4_SR_USER / $M4_SR_PASSWORD (defaults as above).
Writes DIR/results.md (summary + details) and DIR/results.json; exit code 0 even on failed checks (the
workflow decides), 2 on harness errors.
"""
import argparse, datetime, decimal, functools, json, os, re, struct, sys, time, traceback, uuid
from decimal import Decimal

decimal.getcontext().prec = 80

import duckdb
import pymysql

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M4 = os.path.join(REPO, "tests", "m4")
FLIGHT_URI = os.environ.get("M4_FLIGHT_URI", "grpc://flight1:32010")
# flight.compression of every catalog the checks create (m4 input `compression`; check 13 sets its own)
COMPRESSION = os.environ.get("M4_COMPRESSION", "none") or "none"


# ---------------------------------------------------------------- connections

def sr_connect():
    c = pymysql.connect(host=os.environ.get("M4_SR_HOST", "127.0.0.1"), port=int(os.environ.get("M4_SR_PORT", "9030")),
                        user=os.environ.get("M4_SR_USER", "root"), password=os.environ.get("M4_SR_PASSWORD", ""),
                        autocommit=True,
                        read_timeout=1800, write_timeout=600)
    with c.cursor() as cur:
        cur.execute("SET time_zone = 'UTC'")
        cur.execute("SET query_timeout = 1800")
    return c


def sr(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return list(cur.fetchall()) if cur.description else []


def sr_cols(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return [d[0] for d in cur.description], list(cur.fetchall())


def duck(tpch_dir, types_dir):
    d = duckdb.connect()
    d.execute("SET TimeZone = 'UTC'")
    d.execute("CREATE SCHEMA tpch")
    for t in sorted(os.listdir(tpch_dir)):
        d.execute(f"CREATE VIEW tpch.{t} AS SELECT * FROM read_parquet('{tpch_dir}/{t}/*.parquet')")
    d.execute("CREATE SCHEMA types")
    for t in sorted(os.listdir(types_dir)):
        d.execute(f"CREATE VIEW types.{t} AS SELECT * FROM read_parquet('{types_dir}/{t}/*.parquet')")
    return d


# ---------------------------------------------------------------- normalisation

def norm(v, kind=None):
    """Value -> comparable string. kind: 'float' (single precision), 'exact' (decimals unrounded) or None
    (decimals rounded to 4 places as in sr_cases.py)."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if kind == "float":     # compare as float32: StarRocks prints FLOAT with float32 precision (1e-45)
            return format(struct.unpack("f", struct.pack("f", v))[0], ".6g")
        if kind == "exact" or v != v or v in (float("inf"), float("-inf")):
            return format(v, ".9g")
        v = Decimal(format(v, ".12g"))      # DOUBLE vs DECIMAL (avg): both rounded like sr_cases.py
    if isinstance(v, Decimal):
        d = (v if kind == "exact" else round(v, 4)).normalize()
        return "0" if d == 0 else format(d, "f")
    if isinstance(v, datetime.datetime):
        if v.tzinfo is not None:
            v = v.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return v.isoformat(sep=" ")
    if isinstance(v, (datetime.date, datetime.time)):
        return v.isoformat()
    if isinstance(v, (bytes, bytearray, memoryview)):
        return bytes(v).hex()
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, (list, tuple, dict)):
        return re.sub(r"\s", "", json.dumps(v, default=str, sort_keys=True, ensure_ascii=False))
    return str(v)


def norm_text(cell, typ):
    """Reference TSV cell (DuckDB text) -> same form as norm() of the StarRocks value."""
    if cell == "NULL":
        return cell
    if typ.startswith("DECIMAL"):
        return norm(Decimal(cell))
    if typ in ("DOUBLE", "FLOAT"):
        return norm(float(cell))
    return cell


def norm_sr_as(v, typ):
    """StarRocks value normalised by the reference column type (StarRocks may type an expression differently)."""
    if v is None:
        return "NULL"
    if typ.startswith("DECIMAL"):
        return norm(Decimal(str(v)))
    if typ in ("DOUBLE", "FLOAT"):
        return norm(float(v))
    return norm(v)


# ---------------------------------------------------------------- results

class Result:
    def __init__(self, num, title):
        self.num, self.title, self.items, self.notes = num, title, [], []

    def add(self, name, ok, detail=""):
        self.items.append((name, bool(ok), detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail[:300]}", flush=True)

    @property
    def ok(self):
        return bool(self.items) and all(i[1] for i in self.items)


def guarded(res, name, fn):
    try:
        fn()
    except Exception as e:  # one failing item must not stop the check
        res.add(name, False, f"ERROR {type(e).__name__}: {e}".replace("\n", " "))


def remote_sql(conn, sql):
    plan = "\n".join(r[0] for r in sr(conn, "EXPLAIN " + sql))
    m = re.findall(r"REMOTE SQL:\s*(.*)", plan)
    return " | ".join(m), plan


# ---------------------------------------------------------------- check 1: catalog + metadata

def check1(conn, args, res):
    sr(conn, "DROP CATALOG IF EXISTS flight")
    props = [f'"type" = "flight"', f'"flight.uri" = "{FLIGHT_URI}"']
    if args.token:
        props.append(f'"flight.token" = "{args.token}"')
    if COMPRESSION != "none":
        props.append(f'"flight.compression" = "{COMPRESSION}"')
    sr(conn, "CREATE EXTERNAL CATALOG flight PROPERTIES (" + ", ".join(props) + ")")
    res.add("create catalog", True)

    def show_create():
        txt = " ".join(str(c) for r in sr(conn, "SHOW CREATE CATALOG flight") for c in r)
        leaked = bool(args.token) and args.token in txt
        res.add("SHOW CREATE CATALOG masks the token", not leaked, txt.replace("\n", " ")[:400])
        if COMPRESSION != "none":
            res.add(f"SHOW CREATE CATALOG has flight.compression = {COMPRESSION}",
                    re.search(r'"flight\.compression"\s*=\s*"' + COMPRESSION + '"', txt) is not None)
    guarded(res, "SHOW CREATE CATALOG", show_create)

    dbs = [r[0] for r in sr(conn, "SHOW DATABASES FROM flight")]
    res.add("SHOW DATABASES has tpch and types", {"tpch", "types"} <= set(dbs), f"got {dbs}")
    tpch = sorted(r[0] for r in sr(conn, "SHOW TABLES FROM flight.tpch"))
    want = sorted(os.listdir(args.tpch))
    res.add("SHOW TABLES FROM flight.tpch", tpch == want, f"got {tpch}")
    types = sorted(r[0] for r in sr(conn, "SHOW TABLES FROM flight.types"))
    res.add("SHOW TABLES FROM flight.types", types == sorted(os.listdir(args.types)), f"got {types}")

    # DESC of the TPC-H tables: the DuckDB types mapped as designed (PLAN §2.2).
    d = args.duck
    for t in want:
        def one(t=t):
            got = {r[0]: r[1].upper() for r in sr(conn, f"DESC flight.tpch.{t}")}
            exp = {r[0]: r[1] for r in d.execute(f"DESCRIBE tpch.{t}").fetchall()}
            bad = [f"{c}: {exp[c]} -> {got.get(c)}" for c in exp if not type_ok(exp[c], got.get(c))]
            res.add(f"DESC flight.tpch.{t}", not bad, "; ".join(bad))
        guarded(res, f"DESC flight.tpch.{t}", one)
    for t in types:
        got = [(r[0], r[1]) for r in sr(conn, f"DESC flight.types.{t}")]
        res.notes.append(f"DESC flight.types.{t}: " + ", ".join(f"{c} {ty}" for c, ty in got))
        exp = {r[0]: r[1] for r in d.execute(f"DESCRIBE types.{t}").fetchall()}
        gotd = {c: ty.upper() for c, ty in got}
        bad = [f"{c}: {exp[c]} -> {gotd.get(c)}" for c in exp if not type_ok(exp[c], gotd.get(c))]
        res.add(f"DESC flight.types.{t}", not bad, "; ".join(bad))
    for t in want:
        check_desc_exact(conn, res, "tpch", t)
    for t in types:
        check_desc_exact(conn, res, "types", t)


# PLAN §2.2 type mapping (as FlightTypeMapper, flight.nested_types=native, flight.converted_types=convert), applied
# to the Arrow schema the server reports in GetTables(include_schema): the expected DESC type, or None for a hidden
# column. Converted types (TIME, DURATION, INTERVAL, DECIMAL256, *View) only at the top level.
def plan_type(t, top=True):
    import pyarrow as pa
    T = pa.types
    if isinstance(t, pa.ExtensionType):
        return None
    if top:
        if T.is_time(t) or T.is_interval(t) or T.is_string_view(t):
            return "VARCHAR(1073741824)"
        if T.is_duration(t):
            return "BIGINT"
        if T.is_binary_view(t):
            return "VARBINARY"
        if T.is_decimal256(t):
            if not (1 <= t.precision and 0 <= t.scale <= t.precision):
                return None
            return f"DECIMAL({t.precision},{t.scale})" if t.precision <= 38 else "VARCHAR(1073741824)"
        if T.is_list_view(t) or T.is_large_list_view(t):
            it = plan_type(t.value_type, False)
            return it and f"ARRAY<{it}>"
    if T.is_dictionary(t):
        return plan_type(t.value_type, top)
    if T.is_dictionary(t):
        return plan_type(t.value_type)
    if T.is_boolean(t):
        return "BOOLEAN"
    if T.is_integer(t):
        signed = {8: "TINYINT", 16: "SMALLINT", 32: "INT", 64: "BIGINT"}
        unsigned = {8: "SMALLINT", 16: "INT", 32: "BIGINT", 64: "LARGEINT"}
        return (signed if T.is_signed_integer(t) else unsigned)[t.bit_width]
    if T.is_float16(t) or T.is_float32(t):
        return "FLOAT"
    if T.is_float64(t):
        return "DOUBLE"
    if T.is_decimal128(t):
        return f"DECIMAL({t.precision},{t.scale})" if 1 <= t.precision <= 38 and 0 <= t.scale <= t.precision else None
    if T.is_string(t) or T.is_large_string(t):
        return "VARCHAR(1073741824)"
    if T.is_binary(t) or T.is_large_binary(t) or T.is_fixed_size_binary(t):
        return "VARBINARY"
    if T.is_date(t):
        return "DATE"
    if T.is_timestamp(t):
        return "DATETIME"
    if T.is_list(t) or T.is_large_list(t) or T.is_fixed_size_list(t):
        it = plan_type(t.value_type, False)
        return it and f"ARRAY<{it}>"
    if T.is_map(t):
        k, v = plan_type(t.key_type, False), plan_type(t.item_type, False)
        return f"MAP<{k},{v}>" if k and v and not re.match(r"(ARRAY|MAP|STRUCT)<", k) else None
    if T.is_struct(t):
        fs = [(t.field(i).name, plan_type(t.field(i).type, False)) for i in range(t.num_fields)]
        if not fs or any(not n or not ty for n, ty in fs):
            return None
        return "STRUCT<" + ",".join(f"{n.upper()} {ty}" for n, ty in fs) + ">"
    return None     # null, union, run-end encoded, extension types; converted types inside nested ones: hidden


def norm_desc(ty):
    """StarRocks DESC type text in the form plan_type() produces."""
    s = ty.replace("`", "").upper()
    s = re.sub(r"\s*,\s*", ",", s)
    s = re.sub(r"\b(TINYINT|SMALLINT|INT|BIGINT|LARGEINT)\(\d+\)", r"\1", s)
    s = re.sub(r"\bDECIMAL(32|64|128)\(", "DECIMAL(", s)
    return re.sub(r"\s+", " ", s).strip()


@functools.lru_cache(maxsize=None)
def server_schema(schema, table):
    import adbc_driver_flightsql.dbapi as fs
    with fs.connect(FLIGHT_URI) as c:
        return c.adbc_get_table_schema(table, db_schema_filter=schema)


def check_desc_exact(conn, res, schema, table):
    def one():
        sch = server_schema(schema, table)
        exp = [(f.name, plan_type(f.type)) for f in sch]
        hidden = [f"{n} ({sch.field(n).type})" for n, ty in exp if ty is None]
        exp = [(n, ty) for n, ty in exp if ty is not None]
        got = [(r[0], norm_desc(r[1])) for r in sr(conn, f"DESC flight.{schema}.{table}")]
        bad = [f"{e} != {g}" for e, g in zip(exp, got) if e != g]
        if len(exp) != len(got):
            bad.append(f"{len(got)} columns, expected {len(exp)}")
        res.add(f"DESC flight.{schema}.{table} = PLAN §2.2 mapping of the server schema", not bad,
                "; ".join(bad[:6]) + (f" hidden: {', '.join(hidden)}" if hidden else ""))
    guarded(res, f"DESC flight.{schema}.{table} exact", one)


# DuckDB type -> accepted StarRocks DESC types (None = hidden). Nested types: hidden or native are both accepted
# here (catalog option flight.nested_types); the check reports what was seen.
def type_ok(duck_type, sr_type):
    dt = duck_type.upper()
    st = (sr_type or "").upper()
    simple = {
        "BOOLEAN": ["BOOLEAN"], "TINYINT": ["TINYINT"], "SMALLINT": ["SMALLINT"], "INTEGER": ["INT"],
        "BIGINT": ["BIGINT"], "UTINYINT": ["SMALLINT"], "USMALLINT": ["INT"], "UINTEGER": ["BIGINT"],
        "UBIGINT": ["LARGEINT", "DECIMAL(20,0)", "DECIMAL128(20,0)"], "FLOAT": ["FLOAT"], "DOUBLE": ["DOUBLE"], "DATE": ["DATE"],
        "TIMESTAMP": ["DATETIME"], "TIMESTAMP_NS": ["DATETIME"], "TIMESTAMP WITH TIME ZONE": ["DATETIME"],
        "BLOB": ["VARBINARY"], "UUID": ["VARBINARY", "VARCHAR", None, ""],
        "TIME": ["VARCHAR"], "INTERVAL": ["VARCHAR"],
    }
    if dt in simple:
        return any(st == a or (a and st.startswith(a + "(")) for a in simple[dt]) or (st == "" and None in simple[dt])
    if dt == "VARCHAR":
        return st.startswith("VARCHAR")
    m = re.match(r"DECIMAL\((\d+),(\d+)\)", dt)
    if m:
        return st.replace(" ", "") in (f"DECIMAL({m[1]},{m[2]})", f"DECIMAL32({m[1]},{m[2]})",
                                       f"DECIMAL64({m[1]},{m[2]})", f"DECIMAL128({m[1]},{m[2]})")
    if dt.endswith("[]"):
        return st == "" or st.startswith("ARRAY") or st.startswith("JSON")
    if dt.startswith("STRUCT"):
        return st == "" or st.startswith("STRUCT") or st.startswith("JSON")
    if dt.startswith("MAP"):
        return st == "" or st.startswith("MAP") or st.startswith("JSON")
    return False


# ---------------------------------------------------------------- check 2: every column of the types tables

def adbc_probe(sql, headers=None):
    """Ask the Flight server directly (ADBC Flight SQL), bypassing StarRocks: (schema, rows) as text."""
    import adbc_driver_flightsql.dbapi as fs
    kw = {f"adbc.flight.sql.rpc.call_header.{k}": v for k, v in (headers or {}).items()}
    with fs.connect(FLIGHT_URI, db_kwargs=kw) as c, c.cursor() as cur:
        cur.execute(sql)
        t = cur.fetch_arrow_table()
        return str(t.schema).replace("\n", "; "), t.to_pylist()


# Text forms of converted types, as the BE writes them (normalize_batch in flight_connector.cpp).
def fmt_time(v, unit):
    per, digits = {"s": (1, 0), "ms": (1000, 3), "us": (10**6, 6), "ns": (10**9, 9)}[unit]
    a = abs(v)
    secs = a // per
    out = ("-" if v < 0 else "") + f"{secs // 3600:02}:{secs // 60 % 60:02}:{secs % 60:02}"
    return out + (f".{a % per:0{digits}}" if digits else "")


def fmt_interval(months, days, nanos):
    out = "P"

    def comp(neg, value, unit):
        return f"{'-' if neg else ''}{value}{unit}" if value else ""
    am = abs(months)
    out += comp(months < 0, am // 12, "Y") + comp(months < 0, am % 12, "M") + comp(days < 0, abs(days), "D")
    if nanos:
        neg, an, sec = nanos < 0, abs(nanos), 10**9
        out += "T" + comp(neg, an // (3600 * sec), "H") + comp(neg, an // (60 * sec) % 60, "M")
        frac = an % sec
        if frac:
            out += f"{'-' if neg else ''}{an // sec % 60}.{format(frac, '09d').rstrip('0')}S"
        else:
            out += comp(neg, an // sec % 60, "S")
    return "PT0S" if out == "P" else out


def converted_expected(schema, table, col):
    """{id: normalized value} of a converted column, from the server's own Arrow values (ADBC); None when the
    column's Arrow type is mapped exactly."""
    import adbc_driver_flightsql.dbapi as fs
    import pyarrow as pa
    T = pa.types
    t = server_schema(schema, table).field(col).type
    if not (T.is_time(t) or T.is_interval(t) or T.is_duration(t) or T.is_decimal256(t)
            or T.is_string_view(t) or T.is_binary_view(t)):
        return None
    with fs.connect(FLIGHT_URI) as c, c.cursor() as cur:
        cur.execute(f'SELECT id, "{col}" FROM {schema}.{table}')
        tb = cur.fetch_arrow_table()
    ids, arr = tb.column(0).to_pylist(), tb.column(1).combine_chunks()
    if T.is_time(arr.type):
        vals = [None if v is None else fmt_time(v, arr.type.unit)
                for v in arr.cast(pa.int64() if T.is_time64(arr.type) else pa.int32()).to_pylist()]
    elif T.is_duration(arr.type):
        vals = arr.cast(pa.int64()).to_pylist()
    elif T.is_interval(arr.type) and arr.type == pa.month_day_nano_interval():
        vals = [None if v is None else fmt_interval(v.months, v.days, v.nanoseconds) for v in arr.to_pylist()]
    elif T.is_string_view(arr.type) or T.is_binary_view(arr.type):
        vals = arr.cast(pa.string() if T.is_string_view(arr.type) else pa.binary()).to_pylist()
    else:   # decimal256
        vals = arr.to_pylist()
    return {i: norm(v, "exact") for i, v in zip(ids, vals)}


def check2(conn, args, res):
    d = args.duck
    sql = "SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id"
    for hdr in ({}, {"x-flight-result-mode": "partial"}, {"x-flight-result-mode": "complete"}):
        try:
            sch, rows = adbc_probe(sql, hdr)
            res.notes.append(f"server direct (ADBC, headers {hdr}): {sql} -> schema {sch}; rows {rows}")
        except Exception as e:
            res.notes.append(f"server direct (ADBC, headers {hdr}) failed: {type(e).__name__}: {e}"[:500])
    try:   # same column through StarRocks with result mode complete
        catalog(conn, "flight_cmp", flight__result_mode="complete")
        rows = sr(conn, "SELECT id, c_ubigint FROM flight_cmp.types.alltypes_full WHERE id IN (2, 3) ORDER BY id")
        res.notes.append(f"StarRocks, result_mode=complete: c_ubigint id 2,3 = {rows}")
        sr(conn, "DROP CATALOG flight_cmp")
    except Exception as e:
        res.notes.append(f"StarRocks complete-mode probe failed: {type(e).__name__}: {e}"[:400])
        try:
            import adbc_driver_flightsql.dbapi as fs
            with fs.connect(FLIGHT_URI) as c:
                sch = c.adbc_get_table_schema("alltypes_full", db_schema_filter="types")
                res.notes.append("server GetTables schema of types.alltypes_full: " + str(sch).replace("\n", "; "))
        except Exception as e:
            res.notes.append(f"server GetTables schema failed: {type(e).__name__}: {e}"[:500])
    for t in sorted(os.listdir(args.types)):
        sr_cols_ = [r[0] for r in sr(conn, f"DESC flight.types.{t}")]
        dk = {r[0]: r[1] for r in d.execute(f"DESCRIBE types.{t}").fetchall()}
        hidden = [c for c in dk if c not in sr_cols_]
        res.notes.append(f"types.{t}: hidden columns {hidden}")
        _, rows = sr_cols(conn, f"SELECT * FROM flight.types.{t}")
        exp_n = d.execute(f"SELECT count(*) FROM types.{t}").fetchone()[0]
        res.add(f"types.{t} SELECT * row count", len(rows) == exp_n, f"got {len(rows)} expected {exp_n}")
        for c in sr_cols_:
            if c == "id":
                continue
            def one(c=c):
                kind = "float" if dk.get(c) == "FLOAT" else "exact"
                got = {r[0]: norm(r[1], kind) for r in sr(conn, f"SELECT id, `{c}` FROM flight.types.{t}")}
                conv = converted_expected("types", t, c)
                if conv is not None:
                    exp = conv
                elif dk.get(c) == "TIMESTAMP_NS":
                    # DuckDB's Python conversion truncates ns toward zero; the BE floors to microseconds
                    q = f'SELECT id, epoch_ns("{c}") FROM types.{t}'
                    epoch = datetime.datetime(1970, 1, 1)
                    exp = {r[0]: norm(None if r[1] is None else epoch + datetime.timedelta(microseconds=r[1] // 1000))
                           for r in d.execute(q).fetchall()}
                else:
                    exp = {r[0]: norm(r[1], kind) for r in d.execute(f'SELECT id, "{c}" FROM types.{t}').fetchall()}
                diff = [i for i in exp if got.get(i, "<missing>") != exp[i]]
                extra = len(set(got) - set(exp))
                det = f"{len(diff)}/{len(exp)} differ" + (f", {extra} extra ids" if extra else "")
                if diff:
                    det += "; e.g. " + "; ".join(f"id={i}: sr={got.get(i, '<missing>')!r} duck={exp[i]!r}"
                                                 for i in diff[:3])
                res.add(f"types.{t}.{c} ({dk.get(c)})", not diff and not extra, det)
            guarded(res, f"types.{t}.{c}", one)


# ---------------------------------------------------------------- check 3: M4-TESTS §1–2

LIKE_SR = r"'%a\\_b%'"
LIKE_DUCK = r"'%a\_b%' ESCAPE '\'"

# (id, sql with {c} = catalog, must-contain in REMOTE SQL, must-not-contain, compare mode, session sets)
CASES3 = [
    ("1.1", "SELECT l_orderkey, l_quantity FROM {c}.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'",
     ["WHERE", "DATE '1998-09-01'", "= 'R'"], [], "rows", []),
    ("1.2", "SELECT * FROM {c}.tpch.nation LIMIT 5", ["LIMIT 5"], [], "count", []),
    ("1.3", "SELECT * FROM {c}.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3", ["LIKE 'A%'", "LIMIT 3"], [], "rows", []),
    ("1.4", "SELECT count(*) FROM {c}.tpch.customer WHERE c_comment LIKE " + LIKE_SR, [], ["WHERE", "LIMIT"], "rows", []),
    ("1.5", "SELECT l_orderkey, l_quantity FROM {c}.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'",
     [], ["WHERE"], "rows", ["flight_filter_pushdown = false"]),
    ("2.1", "SELECT count(*) FROM {c}.tpch.lineitem", ['count(*) AS "__flight_agg_0"'], [], "rows", []),
    ("2.2", "SELECT count(*) FROM {c}.tpch.lineitem WHERE l_quantity > 45", ['"__flight_agg_0"', '"l_quantity" > 45'], [], "rows", []),
    ("2.3", "SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM {c}.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2",
     ['GROUP BY "l_returnflag", "l_linestatus"', "__flight_agg_0"], [], "rows", []),
    ("2.4", "SELECT DISTINCT n_regionkey FROM {c}.tpch.nation", ['GROUP BY "n_regionkey"'], [], "rows", []),
    ("2.5", "SELECT avg(l_quantity) FROM {c}.tpch.lineitem", [], ["__flight_agg", "avg("], "rows", []),
    ("2.6", "SELECT count(DISTINCT l_suppkey) FROM {c}.tpch.lineitem", [], ["__flight_agg"], "rows", []),
    ("2.7", "SELECT o_orderpriority, count(*) FROM {c}.tpch.orders WHERE o_comment LIKE " + LIKE_SR + " GROUP BY 1",
     [], ["__flight_agg"], "rows", []),
    ("2.8", "SELECT count(*) FROM {c}.tpch.nation WHERE n_nationkey < 0", [], [], "rows", []),
    ("2.9", "SELECT l_returnflag, count(*) c FROM {c}.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000", ["__flight_agg"], [], "rows", []),
    ("2.10", "SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM {c}.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2",
     [], ["__flight_agg"], "rows", ["flight_aggregate_pushdown = false"]),
]
BOTH_MODES = {"2.1", "2.2", "2.3", "2.4", "2.9"}


def make_catalogs(conn, args):
    base = [f'"type" = "flight"', f'"flight.uri" = "{FLIGHT_URI}"']
    if args.token:
        base.append(f'"flight.token" = "{args.token}"')
    if COMPRESSION != "none":
        base.append(f'"flight.compression" = "{COMPRESSION}"')
    for name, extra in (("flight", []), ("flight_c", ['"flight.result_mode" = "complete"']),
                        ("flight_noagg", ['"flight.pushdown.aggregate" = "false"'])):
        sr(conn, f"DROP CATALOG IF EXISTS {name}")
        sr(conn, f"CREATE EXTERNAL CATALOG {name} PROPERTIES (" + ", ".join(base + extra) + ")")


def duck_rows(d, sql):
    q = re.sub(r"\bflight\w*\.tpch\.", "tpch.", sql).replace(LIKE_SR, LIKE_DUCK)
    return [tuple(norm(v) for v in r) for r in d.execute(q).fetchall()]


def run_case(conn, d, res, cid, sql, must, mustnot, mode, sets):
    for s in sets:
        sr(conn, "SET " + s)
    try:
        rs, plan = remote_sql(conn, sql)
        miss = [m for m in must if m not in rs] + (["REMOTE SQL"] if not rs else [])
        bad = [m for m in mustnot if m in rs]
        t0 = time.time()
        got = [tuple(norm(v) for v in r) for r in sr(conn, sql)]
        secs = time.time() - t0
        exp = duck_rows(d, sql)
        if mode == "count":
            same = len(got) == len(exp)
        else:
            same = sorted(got) == sorted(exp) and ("ORDER BY" not in sql or got == exp)
        det = f"REMOTE SQL: {rs[:300]}"
        if miss:
            det += f" | missing {miss}"
        if bad:
            det += f" | unexpected {bad}"
        det += f" | rows {len(got)} ({secs:.2f}s)"
        if not same:
            det += f" | result differs: sr={got[:3]} duck={exp[:3]}"
        res.add(f"{cid} {sql}", not miss and not bad and same, det)
    finally:
        for s in sets:
            sr(conn, "SET " + s.split("=")[0].strip() + " = true")


def check3(conn, args, res):
    make_catalogs(conn, args)
    for cid, sql, must, mustnot, mode, sets in CASES3:
        guarded(res, cid, lambda: run_case(conn, args.duck, res, cid, sql.format(c="flight"), must, mustnot, mode, sets))
        if cid in BOTH_MODES:
            guarded(res, cid + " complete", lambda: run_case(conn, args.duck, res, cid + " (complete)",
                                                            sql.format(c="flight_c"), must, mustnot, mode, sets))
    sql = CASES3[7][1].format(c="flight_noagg")
    guarded(res, "2.11", lambda: run_case(conn, args.duck, res, "2.11 (flight.pushdown.aggregate=false)", sql,
                                          [], ["__flight_agg"], "rows", []))


# ---------------------------------------------------------------- check 4: TPC-H SF1

def load_ref(q, ref):
    cols = [l.rstrip("\n").split("\t") for l in open(f"{ref}/{q}.cols") if l.strip()]
    rows = [l.rstrip("\n").split("\t") for l in open(f"{ref}/{q}.tsv") if l.rstrip("\n") != ""]
    return cols, rows


def flight_scan_cardinalities(conn, sql):
    """[(table, cardinality)] of the FlightScanNodes in EXPLAIN COSTS."""
    out, cur = [], None
    for line in (r[0] for r in sr(conn, "EXPLAIN COSTS " + sql)):
        if re.search(r"\d+:FlightScanNode", line):
            cur = ["?", None]
        elif cur is not None:
            m = re.search(r"TABLE:\s*(\S+)", line)
            if m:
                cur[0] = m.group(1)
            m = re.search(r"cardinality[:=]\s*(-?\d+)", line)
            if m:
                out.append((cur[0], int(m.group(1))))
                cur = None
    return out


def check4_stats(conn, res):
    # local final check A-1: Flight scans reached the CBO without row counts (cardinality -1 / 1, lineitem as
    # hash build side). After a query (the end of a query used to clear the row-count cache) every Flight scan
    # of q05 must carry a real row count.
    sql = open(os.path.join(M4, "queries", "q05.sql")).read().strip().rstrip(";")
    sr(conn, "SELECT count(*) FROM region")
    cards = flight_scan_cardinalities(conn, sql)
    ok = len(cards) == 6 and all(c > 1 for _, c in cards)
    res.add("q05 EXPLAIN COSTS: row counts of all 6 Flight scans", ok, ", ".join(f"{t}={c}" for t, c in cards))


def check4_column_stats(conn, res):
    # P2: column min/max from the server (flight.column_stats). q05 keeps one year of o_orderdate (1992-01-01 ..
    # 1998-08-02 at SF1): about 15% of the 1.5M orders, ~228K. Without column statistics the optimizer's default
    # selectivities give 94K or 375K, both outside the band. The band scales with the orders row count (the
    # local check runs SF10: 2276507 is correct there).
    sql = open(os.path.join(M4, "queries", "q05.sql")).read().strip().rstrip(";")
    scale = int(sr(conn, "SELECT count(*) FROM orders")[0][0]) / 1_500_000
    cards = flight_scan_cardinalities(conn, sql)
    orders = [c for t, c in cards if t.split(".")[-1] == "orders"]
    lo, hi = int(150_000 * scale), int(320_000 * scale)
    ok = len(orders) == 1 and lo <= orders[0] <= hi
    res.add("q05 EXPLAIN COSTS: orders estimate from o_orderdate min/max", ok,
            f"orders={orders}, band {lo}..{hi} (scale {scale:g})")
    for q in ("q05", "q08", "q09"):
        sql = open(os.path.join(M4, "queries", f"{q}.sql")).read().strip().rstrip(";")
        joins = [l.strip() for l in (r[0] for r in sr(conn, "EXPLAIN " + sql))
                 if re.search(r"HASH JOIN|TABLE: |EXCHANGE|PLAN FRAGMENT", l)]
        res.notes.append(f"{q} scans: " + ", ".join(f"{t}={c}" for t, c in flight_scan_cardinalities(conn, sql)))
        res.notes.append(f"{q} plan outline: " + " / ".join(joins))


def check4(conn, args, res):
    sr(conn, f"SET CATALOG {args.catalog}")
    sr(conn, "USE tpch")
    guarded(res, "q05 EXPLAIN COSTS: row counts of all 6 Flight scans", lambda: check4_stats(conn, res))
    guarded(res, "q05 EXPLAIN COSTS: orders estimate from o_orderdate min/max",
            lambda: check4_column_stats(conn, res))
    timings = []
    ref_timings = []
    topn_default = sr(conn, "SHOW VARIABLES LIKE 'cbo_push_down_topn_limit'")[0][1]
    try:
        for topn in ("default", "0"):
            if topn == "0":
                sr(conn, "SET cbo_push_down_topn_limit = 0")
            for i in range(1, 23):
                q = f"q{i:02d}"
                def one(q=q, topn=topn):
                    sql = open(os.path.join(M4, "queries", f"{q}.sql")).read().strip().rstrip(";")
                    # StarRocks has no SQL-standard substring(x FROM a FOR b) (q22)
                    sql = re.sub(r"substring\(\s*([\w.]+)\s+FROM\s+(\d+)\s+FOR\s+(\d+)\s*\)",
                                 r"substring(\1, \2, \3)", sql, flags=re.I)
                    cols, ref = load_ref(q, args.reference)
                    t0 = time.time()
                    got = sr(conn, sql)
                    secs = time.time() - t0
                    timings.append((q, topn, secs))
                    if args.ref_catalog:
                        # same query on the other catalog (e.g. the JDBC bridge): equal rows, timing for comparison.
                        # Its errors belong to its own item, not to the item of the catalog under test.
                        other, ref_err = None, None
                        sr(conn, f"SET CATALOG {args.ref_catalog}")
                        try:
                            sr(conn, "USE tpch")
                            t1 = time.time()
                            other = sr(conn, sql)
                            ref_timings.append((q, topn, time.time() - t1))
                        except Exception as e:
                            ref_err = f"ERROR of {args.ref_catalog} {type(e).__name__}: {e}".replace("\n", " ")
                        finally:
                            sr(conn, f"SET CATALOG {args.catalog}")
                            sr(conn, "USE tpch")
                        if ref_err:
                            res.add(f"{q} topn={topn} = {args.ref_catalog}", False, ref_err)
                        else:
                            a = [tuple(norm(v) for v in r) for r in got]
                            b = [tuple(norm(v) for v in r) for r in other]
                            same = sorted(a) == sorted(b) and ("ORDER BY" not in sql.upper() or a == b)
                            res.add(f"{q} topn={topn} = {args.ref_catalog}", same,
                                    f"rows {len(a)}/{len(b)}" + ("" if same else f" | {args.catalog}={a[:2]} "
                                                                 f"{args.ref_catalog}={b[:2]}"))
                    types = [c[1] for c in cols]
                    g = [tuple(norm_sr_as(v, ty) for v, ty in zip(r, types)) for r in got]
                    e = [tuple(norm_text(v, ty) for v, ty in zip(r, types)) for r in ref]
                    keys = [k for k, c in enumerate(cols) if len(c) > 2 and c[2] == "key"]
                    ok = len(got) == len(ref) and sorted(g) == sorted(e) and \
                        [tuple(r[k] for k in keys) for r in g] == [tuple(r[k] for k in keys) for r in e]
                    det = f"rows {len(got)}/{len(ref)} {secs:.2f}s"
                    if not ok:
                        dg = [r for r in g if r not in set(e)][:2]
                        de = [r for r in e if r not in set(g)][:2]
                        det += f" | only in sr: {dg} | only in ref: {de}"
                    res.add(f"{q} topn={topn}", ok, det)
                guarded(res, f"{q} topn={topn}", one)
    finally:
        sr(conn, f"SET cbo_push_down_topn_limit = {topn_default}")
        sr(conn, "SET CATALOG default_catalog")
    res.notes.append(f"timings {args.catalog} (s): " + ", ".join(f"{q}/{t}={s:.2f}" for q, t, s in timings))
    if ref_timings:
        res.notes.append(f"timings {args.ref_catalog} (s): " +
                         ", ".join(f"{q}/{t}={s:.2f}" for q, t, s in ref_timings))
        res.notes.append(f"total (s): {args.catalog} {sum(t[2] for t in timings):.1f}, "
                         f"{args.ref_catalog} {sum(t[2] for t in ref_timings):.1f}")


# ---------------------------------------------------------------- check 5: sr-cases on SF1

def load_sr_cases_ref(path):
    """sr-cases.ref (JDBC bridge answers): '### <query>' followed by its rows, tab-separated text."""
    ref, cur = {}, None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith("### "):
            cur = ref.setdefault(line[4:], [])
        elif cur is not None and line != "":
            cur.append(tuple(norm_ref_cell(c) for c in line.split("\t")))
    return ref


def norm_ref_cell(cell):
    if re.fullmatch(r"-?\d+(\.\d+)?([eE][-+]?\d+)?", cell):
        return norm(Decimal(cell))
    return cell


def check5(conn, args, res):
    d = args.duck
    refs = load_sr_cases_ref(args.sr_cases_ref) if args.sr_cases_ref else None
    sr(conn, "SET CATALOG default_catalog")
    for q in [l.rstrip("\n") for l in open(os.path.join(M4, "sr-cases", "sr-cases.sql")) if l.strip()]:
        def one(q=q):
            # same rewriting as sr_cases.py: "x" identifiers become `x` unless the query has string literals
            sq = q if "'" in q else q.replace('"', '`')
            sq = re.sub(r"\btpch\.", f"{args.catalog}.tpch.", sq).replace("`tpch`.", f"{args.catalog}.tpch.")
            got = [tuple(norm(v) for v in r) for r in sr(conn, sq)]
            if refs is not None:
                if q not in refs:
                    raise KeyError(f"query not in {args.sr_cases_ref}")
                exp = refs[q]
            else:
                dq = q.replace("\\'", "''")   # DuckDB has no backslash escapes
                exp = [tuple(norm(v) for v in r) for r in d.execute(dq).fetchall()]
            ordered = "ORDER BY" in q.upper()
            ok = (got == exp) if ordered else (sorted(got) == sorted(exp))
            res.add(sq, ok, f"rows {len(got)}" + ("" if ok else f" | sr={got[:3]} duck={exp[:3]}"))
        guarded(res, q, one)


# ---------------------------------------------------------------- server control (checks 6–9)

import subprocess, threading

def stack(*a, env=None):
    e = dict(os.environ)
    e.update(env or {})
    p = subprocess.run([os.path.join(REPO, "ci", "m4", "stack.sh"), *a], env=e, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"stack.sh {' '.join(a)} failed: {(p.stdout + p.stderr)[-1500:]}")
    return p.stdout


def flight_restart(args, servers=("flight1",), env=None):
    """Replace all Flight servers by `servers` (one cluster), started with the extra FLIGHT_* env."""
    stack("stop", "flight1", "flight2")
    # cluster members wait for each other before "started": start all, then wait for each
    for n in servers:
        stack("flight", args.assets, n, ",".join(servers), env=dict(env or {}, M4_NO_WAIT="1"))
    for n in servers:
        stack("wait", n)


def catalog(conn, name, uri=None, **props):
    p = {"type": "flight", "flight.uri": uri or FLIGHT_URI}
    if COMPRESSION != "none":
        p["flight.compression"] = COMPRESSION
    p.update({k.replace("__", "."): v for k, v in props.items()})
    sr(conn, f"DROP CATALOG IF EXISTS {name}")
    sr(conn, f"CREATE EXTERNAL CATALOG {name} PROPERTIES (" +
       ", ".join(f'"{k}" = "{v}"' for k, v in p.items()) + ")")


def try_sql(conn, sql):
    t0 = time.time()
    try:
        return True, sr(conn, sql), time.time() - t0
    except Exception as e:
        return False, f"{type(e).__name__}: {e}".replace("\n", " ")[:400], time.time() - t0


def be_alive(conn):
    with conn.cursor() as cur:
        cur.execute("SHOW BACKENDS")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return bool(rows) and all(r[cols.index("Alive")] == "true" for r in rows)


SCAN_Q = "SELECT count(*), sum(l_quantity), sum(length(l_comment)) FROM {c}.tpch.lineitem"


def query_profile(conn, qid, out_dir=None, label="", wait=30):
    """Profile text of query `qid` (needs enable_profile=true when it ran); reported asynchronously."""
    txt, err = "", ""
    for _ in range(wait):
        try:
            r = sr(conn, f"SELECT get_query_profile('{qid}')")
            txt = str(r[0][0] or "") if r else ""
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        if txt:
            break
        time.sleep(1)
    if out_dir and txt:
        with open(os.path.join(out_dir, f"profile-{label or qid}.txt"), "w") as f:
            f.write(txt)
    return txt, err


def counter_sum(profile, name):
    return sum(int(x) for x in re.findall(rf"\b{name}: (\d+)\b", profile))


# ---------------------------------------------------------------- check 6: failover (two servers)

# check 6 "during": three full lineitem reads, so the kill lands well inside the read
SCAN6_Q = ("SELECT count(*), sum(l_quantity), sum(length(l_comment)) FROM (" +
           " UNION ALL ".join(["SELECT l_quantity, l_comment FROM {c}.tpch.lineitem"] * 3) + ") t")
KILL_AT = 0.35      # fraction of the measured read time


def check6(conn, args, res):
    exp = [tuple(norm(v) for v in r) for r in args.duck.execute(SCAN_Q.format(c="x").replace("x.tpch.", "tpch.")).fetchall()]
    exp6 = [tuple(norm(v) for v in r) for r in args.duck.execute(SCAN6_Q.format(c="x").replace("x.tpch.", "tpch.")).fetchall()]
    try:
        flight_restart(args, ("flight1", "flight2"))
        catalog(conn, "flight_fo", "grpc://flight1:32010,grpc://flight2:32010")
        sr(conn, "SET flight_aggregate_pushdown = false")   # the BE must read every endpoint
        q = SCAN_Q.format(c="flight_fo")
        ok, r, secs = try_sql(conn, q)
        got = [tuple(norm(v) for v in x) for x in r] if ok else r
        res.add("both servers up: full scan correct", ok and got == exp, f"{secs:.1f}s got={got} exp={exp}")
        q6 = SCAN6_Q.format(c="flight_fo")
        try_sql(conn, q6)                                  # warm-up (server caches, metadata)
        ok, r, t_read = try_sql(conn, q6)
        got = [tuple(norm(v) for v in x) for x in r] if ok else r
        res.add("both servers up: 3x lineitem read correct", ok and got == exp6, f"{t_read:.1f}s got={got}")
        n_ep = remote_sql(conn, q)[1].count("flight")  # informational
        res.notes.append(f"plan of the failover scan mentions 'flight' {n_ep}x")

        stack("stop", "flight2")
        t_q = time.time()
        ok, r, secs = try_sql(conn, q)
        got = [tuple(norm(v) for v in x) for x in r] if ok else r
        res.add("flight2 stopped before the query: succeeds via backup locations", ok and got == exp,
                f"{secs:.1f}s got={got}")
        # the run artifact is not reachable from every session: keep the relevant log lines in the results
        fe = subprocess.run(["docker", "exec", "sr", "sh", "-c",
                             "tail -n 2000 /data/deploy/starrocks/fe/log/fe.log | grep -E 'trying next location' | tail -n 8"],
                            capture_output=True, text=True)
        res.notes.append("query after the stop ran " + time.strftime("%H:%M:%S", time.gmtime(t_q)) +
                         f"–{time.strftime('%H:%M:%S', time.gmtime(t_q + secs))} UTC; fe.log failover lines: " +
                         " / ".join(fe.stdout.splitlines())[-2000:])
        if not ok:
            f1 = subprocess.run(["docker", "logs", "--since", "60s", "flight1"], capture_output=True, text=True)
            hits = [l for l in (f1.stdout + f1.stderr).splitlines() if re.search(r"WARN|ERROR|SEVERE|Exception|Member|GetFlightInfo|execution=", l)]
            res.notes.append(f"flight1 WARN/ERROR/member lines (last 60 s): {len(hits)}; "
                             + " / ".join(h[:300] for h in hits[-12:]))

        stack("flight", args.assets, "flight2", "flight1,flight2")
        time.sleep(10)
        out = {}
        def run():
            c2 = sr_connect()
            sr(c2, "SET flight_aggregate_pushdown = false")
            sr(c2, "SET enable_profile = true")
            out["t0"] = time.time()
            out["r"] = try_sql(c2, q6)
            out["t1"] = time.time()
            try:
                out["qid"] = sr(c2, "SELECT last_query_id()")[0][0]
            finally:
                c2.close()
        th = threading.Thread(target=run)
        th.start()
        time.sleep(max(1.0, KILL_AT * t_read))
        stack("kill", "flight2")
        t_kill = time.time()
        th.join(600)
        ok, r, secs = out.get("r", (False, "no result (hung)", 0))
        kill_at = t_kill - out.get("t0", t_kill)
        after = out.get("t1", t_kill) - t_kill
        res.notes.append(f"during: read time with both servers {t_read:.1f}s; flight2 killed {kill_at:.1f}s into "
                         f"the query; query ended {after:.1f}s after the kill")
        if ok:
            got = [tuple(norm(v) for v in x) for x in r]
            res.add("flight2 killed during the read: no wrong/duplicate rows", got == exp6,
                    f"query succeeded in {secs:.1f}s got={got} exp={exp6}")
        else:
            res.add("flight2 killed during the read: clean error", "hung" not in r, f"{secs:.1f}s {r}")
        failovers = None
        if out.get("qid"):
            p, _ = query_profile(conn, out["qid"], args.out, "check6-during")
            failovers = counter_sum(p, "FailoverCount") if p else None
        # proof that the kill hit a running read: the query failed, or an endpoint failed over to its backup
        res.add("the kill overlapped the read (query ended after it; error or FailoverCount > 0)",
                after > 0.2 and (not ok or bool(failovers)),
                f"ended {after:.1f}s after the kill, {'error' if not ok else 'success'}, FailoverCount={failovers}")
        res.add("BE alive after failover tests", be_alive(conn))
    finally:
        sr(conn, "SET flight_aggregate_pushdown = true")
        flight_restart(args)


# ---------------------------------------------------------------- check 7: KILL QUERY during a long scan

def check7(conn, args, res):
    branch = "SELECT l_comment FROM flight.tpch.lineitem"
    q = "SELECT count(*), sum(length(l_comment)) FROM (" + " UNION ALL ".join([branch] * 8) + ") t"
    c2 = sr_connect()
    cid = sr(c2, "SELECT CONNECTION_ID()")[0][0]
    out = {}
    def run():
        out["r"] = try_sql(c2, q)
        out["t"] = time.time()
    th = threading.Thread(target=run)
    th.start()
    time.sleep(4)
    if not th.is_alive():
        res.add("scan still running after 4 s (precondition)", False, str(out.get("r"))[:300])
        return
    t_kill = time.time()
    sr(conn, f"KILL QUERY {cid}")
    th.join(120)
    if th.is_alive():
        res.add("KILL QUERY stops the scan", False, "query still running 120 s after KILL")
        return
    ok, r, _ = out["r"]
    dt = out["t"] - t_kill
    res.add("KILL QUERY stops the scan within ~1 s", not ok and dt < 2.0, f"{dt:.2f}s after KILL: {r}")
    time.sleep(2)
    log = subprocess.run(["docker", "logs", "--since", "60s", "flight1"], capture_output=True, text=True)
    hits = [l for l in (log.stdout + log.stderr).splitlines() if re.search(r"cancel", l, re.I)]
    res.notes.append(f"flight1 log lines with 'cancel' after the KILL: {len(hits)}; " + " / ".join(hits[:3])[:400])
    ok2, r2, _ = try_sql(conn, "SELECT count(*) FROM flight.tpch.nation")
    res.add("next query works", ok2 and r2[0][0] == 25, str(r2)[:200])
    c2.close()


# ---------------------------------------------------------------- check 8: token and TLS

def check8(conn, args, res):
    tok = args.token or ("m4tok" + os.urandom(12).hex())
    q = "SELECT count(*) FROM {c}.tpch.nation"
    def expect(cat, good, label):
        ok, r, secs = try_sql(conn, q.format(c=cat))
        passed = (ok and r[0][0] == 25) if good else not ok
        res.add(label, passed, f"{'ok ' + str(r) if ok else r}")
        if not ok and tok in str(r):
            res.add(label + ": token not in the error", False, "token appears in the error text")
    try:
        flight_restart(args, env={"FLIGHT_AUTH_PROVIDER": "token", "FLIGHT_AUTH_TOKEN": tok})
        catalog(conn, "f_tok", flight__token=tok)
        expect("f_tok", True, "token server, right token")
        catalog(conn, "f_bad", flight__token="wrong" + tok[5:])
        expect("f_bad", False, "token server, wrong token fails")
        catalog(conn, "f_none")
        expect("f_none", False, "token server, no token fails")
        catalog(conn, "f_basic", flight__user="m4", flight__password=tok)
        expect("f_basic", True, "token server, basic auth user:<token>")
        txt = " ".join(str(c) for r in sr(conn, "SHOW CREATE CATALOG f_basic") for c in r)
        res.add("SHOW CREATE CATALOG masks the password", tok not in txt, txt[:300])
        for cat in ("f_tok", "f_basic"):
            def prof(cat=cat):
                sr(conn, "SET enable_profile = true")
                try:
                    sr(conn, f"SELECT n_name FROM {cat}.tpch.nation")
                    qid = sr(conn, "SELECT last_query_id()")[0][0]
                finally:
                    sr(conn, "SET enable_profile = false")
                p, err = query_profile(conn, qid, args.out, f"check8-{cat}")
                res.add(f"query profile of a {cat} scan has the Flight scan", "RowsRead" in p,
                        f"{len(p)} chars" if p else f"no profile for {qid}: {err}")
                res.add(f"query profile of a {cat} scan: token not in it", bool(p) and tok not in p,
                        "token found in the profile" if tok in p else "")
            guarded(res, f"profile {cat}", prof)

        certs = os.path.join(os.environ.get("M4_STATE", os.path.expanduser("~/.m4-state")), "certs")
        stack("certs", certs, "flight1")
        flight_restart(args, env={"FLIGHT_TLS_CERT": "/certs/server.crt", "FLIGHT_TLS_KEY": "/certs/server.key",
                                  "FLIGHT_BEARER_TOKEN": tok, "M4_CERTS": certs})
        subprocess.run(["docker", "cp", os.path.join(certs, "server.crt"), "sr:/tmp/m4-ca.pem"], check=True)
        tls = "grpc+tls://flight1:32010"
        catalog(conn, "f_tls", tls, flight__token=tok, flight__tls__ca_file="/tmp/m4-ca.pem")
        expect("f_tls", True, "TLS, trusted CA file")
        catalog(conn, "f_tls_host", "grpc+tls://flight1-alias:32010", flight__token=tok,
                flight__tls__ca_file="/tmp/m4-ca.pem")
        expect("f_tls_host", False, "TLS, wrong host name fails")
        catalog(conn, "f_tls_noca", tls, flight__token=tok)
        expect("f_tls_noca", False, "TLS, untrusted certificate fails")
        catalog(conn, "f_tls_noverify", tls, flight__token=tok, flight__tls__verify="false")
        expect("f_tls_noverify", True, "TLS, flight.tls.verify=false")
        catalog(conn, "f_plain_vs_tls", flight__token=tok)
        expect("f_plain_vs_tls", False, "plain client against the TLS server fails")
    finally:
        for c in ("f_tok", "f_bad", "f_none", "f_basic", "f_tls", "f_tls_host", "f_tls_noca", "f_tls_noverify",
                  "f_plain_vs_tls"):
            sr(conn, f"DROP CATALOG IF EXISTS {c}")
        flight_restart(args)
    # the token grep over fe.log / be.INFO / be.WARNING runs in the workflow after all checks (M4_TOKEN)


# ---------------------------------------------------------------- check 9: memory limit

def check9(conn, args, res):
    q = ("SELECT count(*) FROM (SELECT l_comment, l_orderkey, l_partkey FROM flight.tpch.lineitem "
         "GROUP BY l_comment, l_orderkey, l_partkey) t")
    sr(conn, "SET flight_aggregate_pushdown = false")
    sr(conn, "SET query_mem_limit = 104857600")
    try:
        ok, r, secs = try_sql(conn, q)
        res.add("big aggregation under query_mem_limit=100MB fails cleanly", not ok and re.search(r"mem|limit", str(r), re.I),
                f"{secs:.1f}s {'succeeded: ' + str(r) if ok else r}")
    finally:
        sr(conn, "SET query_mem_limit = 0")
        sr(conn, "SET flight_aggregate_pushdown = true")
    time.sleep(3)
    res.add("BE alive afterwards", be_alive(conn))
    ok, r, _ = try_sql(conn, "SELECT count(*) FROM flight.tpch.nation")
    res.add("next query works", ok and r[0][0] == 25, str(r)[:200])
    guarded(res, "q18 local exchange behind the Flight scans", lambda: check9_exchange(conn, args, res))


def byte_values(profile, name):
    """Values of a BYTES counter `name` in a profile text (e.g. `name: 12.345 MB`), in bytes."""
    mult = {"": 1, "B": 1, "KB": 1 << 10, "MB": 1 << 20, "GB": 1 << 30, "TB": 1 << 40}
    return [float(v) * mult[u or ""] for v, u in re.findall(rf"(?<![\w]){name}: ([\d.]+)\s*([KMGT]?B)?", profile)]


def check9_exchange(conn, args, res):
    """A-4 (q18 SF10 at BE 4G): a fast Flight scan used to fill the local passthrough exchange behind it up to
    dop * 128 MB while the join build sides were not ready; flight.exchange_buffer_mb (default 16) caps it."""
    sql = open(os.path.join(M4, "queries", "q18.sql")).read().strip().rstrip(";")
    out = {}
    try:
        catalog(conn, "f_exch0", flight__exchange_buffer_mb="0")
        for cat in ("flight", "f_exch0"):
            sr(conn, f"SET CATALOG {cat}")
            sr(conn, "USE tpch")
            sr(conn, "SET enable_profile = true")
            try:
                rows = sr(conn, sql)
                qid = sr(conn, "SELECT last_query_id()")[0][0]
            finally:
                sr(conn, "SET enable_profile = false")
            p, err = query_profile(conn, qid, args.out, f"check9-q18-{cat}")
            peaks = byte_values(p, "LocalExchangePeakMemoryUsage")
            node = byte_values(p, "QueryPeakMemoryUsagePerNode")
            out[cat] = (rows, max(peaks) if peaks else None, max(node) if node else None, err)
    finally:
        sr(conn, "SET CATALOG default_catalog")
        sr(conn, "DROP CATALOG IF EXISTS f_exch0")
    mb = lambda v: "n/a" if v is None else f"{v / 1048576:.1f} MB"
    (r16, ex16, node16, e16), (r0, ex0, node0, e0) = out["flight"], out["f_exch0"]
    det = (f"flight (16 MB/driver): exchange peak {mb(ex16)}, query peak/node {mb(node16)}; "
           f"exchange_buffer_mb=0: exchange peak {mb(ex0)}, query peak/node {mb(node0)}; "
           f"cpus {os.cpu_count()}" + (f" | {e16 or e0}" if ex16 is None or ex0 is None else ""))
    res.add("q18 same rows with flight.exchange_buffer_mb=16 and 0",
            sorted(map(tuple, r16)) == sorted(map(tuple, r0)) and len(r16) > 0, f"rows {len(r16)}/{len(r0)}")
    # the comparison only means something when the uncapped exchange gets past one driver's cap; below that (SF1 on
    # the 2-vCPU runner: 2.5-3.5 MB either way) the two peaks differ by noise (m4 39949914514)
    res.add("q18 local exchange peak with the cap <= without (when the uncapped peak exceeds 16 MB)",
            ex16 is not None and ex0 is not None and (ex16 <= ex0 or ex0 <= 16 * 1048576), det)
    bound = 16 * 1048576 * (os.cpu_count() or 1) + 16 * 1048576
    res.add("q18 local exchange peak <= 16 MB x cpus (+16 MB)", ex16 is not None and ex16 <= bound, det)
    # A-4 headroom: the pre-aggregation above the pushed GROUP BY l_orderkey streams (no second hash table);
    # whether the optimizer splits that aggregation at all depends on the scale, so this is a note
    sr(conn, "SET CATALOG flight")
    sr(conn, "USE tpch")
    try:
        plan = "\n".join(r[0] for r in sr(conn, "EXPLAIN VERBOSE " + sql))
    finally:
        sr(conn, "SET CATALOG default_catalog")
    res.notes.append("q18 pre-aggregation modes: "
                     + (", ".join(sorted(set(re.findall(r"streaming preaggregation mode: (\w+)", plan)))) or "auto only")
                     + ("; aggregation pushed" if "__flight_agg_" in plan else "; aggregation NOT pushed"))


# ---------------------------------------------------------------- check 10: lakeFS commits (P3)

def store_env():
    """Settings `stack.sh lakefs` wrote ($M4_STATE/store.env); empty for the default S3 store."""
    f = os.path.join(os.environ.get("M4_STATE", os.path.expanduser("~/.m4-state")), "store.env")
    env = {}
    if os.path.exists(f):
        for line in open(f):
            k, _, v = line.strip().partition("=")
            if k:
                env[k] = v.strip("'")
    return env


def check10(conn, args, res):
    """lakeFS (m4 input store=lakefs): the server reads lakefs://m4lake/main/parquet; a commit between two queries is
    seen by the second one, never half of it, and staged (uncommitted) files are reported as a note."""
    env = store_env()
    if env.get("M4_STORE") != "lakefs":
        res.add("store is lakeFS", False, "run the m4 workflow with store=lakefs")
        return
    sys.path.insert(0, os.path.join(REPO, "ci", "m4"))
    import lakefs
    os.environ.setdefault("LAKEFS_KEY", env["FLIGHT_LAKEFS_ACCESS_KEY"])
    os.environ.setdefault("LAKEFS_SECRET", env["FLIGHT_LAKEFS_SECRET_KEY"])
    q = "SELECT count(*), sum(id) FROM flight.lfs.t"
    val = lambda: tuple(int(x or 0) for x in sr(conn, q)[0])
    first = val()
    res.add("lfs.t at the setup commit", first == (1, 1), f"got {first}, head {lakefs.head()[:12]}")

    # staged, not committed: a branch read in lakeFS includes it; the server pins the branch to its head commit
    lakefs.put("lfs/t/part-1.parquet", lakefs.parquet_rows([2, 3]))
    time.sleep(3)
    staged = val()
    res.notes.append(f"with part-1 staged (uncommitted) a query returns {staged} "
                     f"({'not visible' if staged == first else 'VISIBLE: the branch is read with staging'})")

    lakefs.put("lfs/t/part-2.parquet", lakefs.parquet_rows([4, 5, 6, 7]))
    c2 = lakefs.commit("m4 check 10: part-1 + part-2")
    t0, seen, last = time.time(), set(), None
    while time.time() - t0 < 60:
        last = val()
        seen.add(last)
        if last == (7, 28):
            break
        time.sleep(1)
    res.add("a commit with 2 files is seen after the commit", last == (7, 28),
            f"got {last} after {time.time() - t0:.1f} s, commit {c2[:12]}")
    res.add("no query saw half of the commit", seen <= {first, staged, (7, 28)}, f"seen {sorted(seen)}")

    lakefs.delete("lfs/t/part-0.parquet")
    c3 = lakefs.commit("m4 check 10: drop part-0")
    t0 = time.time()
    while time.time() - t0 < 60:
        last = val()
        if last == (6, 27):
            break
        time.sleep(1)
    res.add("a commit deleting a file is seen", last == (6, 27), f"got {last} after {time.time() - t0:.1f} s, "
                                                                f"commit {c3[:12]}")
    ok, r, _ = try_sql(conn, "SELECT count(*) FROM flight.tpch.lineitem")
    res.add("tpch through lakeFS after the commits", ok and r[0][0] == 6001215, str(r)[:200])


# ---------------------------------------------------------------- check 11: Iceberg tables (P5)

def ref_query(conn, res, args, q, label):
    """TPC-H query q (unqualified, current database) vs tests/m4/reference/sf1."""
    sql = open(os.path.join(M4, "queries", f"{q}.sql")).read().strip().rstrip(";")
    cols, ref = load_ref(q, os.path.join(M4, "reference", "sf1"))
    t0 = time.time()
    got = sr(conn, sql)
    secs = time.time() - t0
    types = [c[1] for c in cols]
    g = [tuple(norm_sr_as(v, ty) for v, ty in zip(r, types)) for r in got]
    e = [tuple(norm_text(v, ty) for v, ty in zip(r, types)) for r in ref]
    det = f"rows {len(got)}/{len(ref)} {secs:.2f}s"
    if sorted(g) != sorted(e):
        det += f" | only in sr: {[r for r in g if r not in set(e)][:2]} | only in ref: {[r for r in e if r not in set(g)][:2]}"
    res.add(label, sorted(g) == sorted(e), det)


def check11(conn, args, res):
    """Iceberg (m4 input store=iceberg): REST catalog namespace `ice` served by the iceberg plugin next to the parquet
    directory. TPC-H lineitem/orders as Iceberg equal the parquet tables and the SF1 answers in both result modes;
    position deletes (Spark, merge-on-read) applied; a renamed column read by field id; an append between two queries
    is seen by the second one only, never half of it."""
    env = store_env()
    if env.get("M4_STORE") != "iceberg":
        res.add("store is iceberg", False, "run the m4 workflow with store=iceberg")
        return
    sys.path.insert(0, os.path.join(REPO, "ci", "m4"))
    import iceberg
    for line in open(os.path.join(os.environ.get("M4_STATE", os.path.expanduser("~/.m4-state")), "minio.env")):
        k, _, v = line.strip().partition("=")
        if k:
            os.environ.setdefault(k, v)
    ice = env.get("M4_ICEBERG_SCHEMA", "ice")
    make_catalogs(conn, args)
    dbs = [r[0] for r in sr(conn, "SHOW DATABASES FROM flight")]
    res.add(f"SHOW DATABASES has tpch and {ice}", {"tpch", ice} <= set(dbs), f"got {dbs}")
    tabs = sorted(r[0] for r in sr(conn, f"SHOW TABLES FROM flight.{ice}"))
    res.add(f"SHOW TABLES FROM flight.{ice}", {"del", "lineitem", "orders", "ren", "t"} <= set(tabs), f"got {tabs}")
    for t in ("lineitem", "orders"):
        def desc(t=t):
            a = [(r[0], r[1]) for r in sr(conn, f"DESC flight.{ice}.{t}")]
            b = [(r[0], r[1]) for r in sr(conn, f"DESC flight.tpch.{t}")]
            res.add(f"DESC flight.{ice}.{t} = DESC flight.tpch.{t}", a == b, f"{a[:4]} vs {b[:4]}")
        guarded(res, f"DESC {t}", desc)
    sums = {"lineitem": "count(*), sum(l_quantity), sum(l_extendedprice), max(l_shipdate), count(DISTINCT l_orderkey)",
            "orders": "count(*), sum(o_totalprice), min(o_orderdate), count(DISTINCT o_custkey)"}
    for cat in ("flight", "flight_c"):
        for t, agg in sums.items():
            def same(cat=cat, t=t, agg=agg):
                a = [tuple(norm(v) for v in r) for r in sr(conn, f"SELECT {agg} FROM {cat}.{ice}.{t}")]
                b = [tuple(norm(v) for v in r) for r in sr(conn, f"SELECT {agg} FROM {cat}.tpch.{t}")]
                res.add(f"{cat}.{ice}.{t} aggregates = parquet", a == b, f"{a} vs {b}")
            guarded(res, f"{cat} {t} aggregates", same)
        sr(conn, f"SET CATALOG {cat}")
        try:
            sr(conn, f"USE {ice}")
            for q in ("q01", "q04", "q12"):
                guarded(res, f"{cat} {q}", lambda q=q: ref_query(conn, res, args, q, f"{q} on {cat}.{ice} = reference"))
        finally:
            sr(conn, "SET CATALOG default_catalog")
        # 1000 rows, ids 1..1000, every 10th deleted by a position delete file
        def dels(cat=cat):
            got = tuple(int(x) for x in sr(conn, f"SELECT count(*), sum(id) FROM {cat}.{ice}.del")[0])
            n0 = sr(conn, f"SELECT count(*) FROM {cat}.{ice}.del WHERE id % 10 = 0")[0][0]
            res.add(f"{cat}.{ice}.del: position deletes applied", got == (900, 450000) and n0 == 0,
                    f"got {got}, deleted ids visible {n0}")
        guarded(res, f"{cat} del", dels)
        def ren(cat=cat):
            got = [tuple(r) for r in sr(conn, f"SELECT id, new_name FROM {cat}.{ice}.ren ORDER BY id")]
            one = sr(conn, f"SELECT id FROM {cat}.{ice}.ren WHERE new_name = 'b'")
            ok = got == [(1, "a"), (2, "b"), (3, "c"), (4, "d"), (5, "e")] and [tuple(r) for r in one] == [(2,)]
            res.add(f"{cat}.{ice}.ren: column renamed after the first append", ok, f"got {got}, filter {one}")
        guarded(res, f"{cat} ren", ren)
    try:
        res.notes.append(f"{ice}.del snapshot summary: {iceberg.summary('del')}")
    except Exception as e:
        res.notes.append(f"{ice}.del summary: {e}")
    if "_iceberg" in dbs:
        res.notes.append("the dataDir listing also shows the warehouse directory as schema _iceberg: tables "
                         f"{sorted(r[0] for r in sr(conn, 'SHOW TABLES FROM flight._iceberg'))}")
    rs, _ = remote_sql(conn, f"SELECT count(*) FROM flight.{ice}.del")
    res.notes.append(f"REMOTE SQL of count(*) on {ice}.del: {rs[:300]}")

    q = f"SELECT count(*), sum(id) FROM flight.{ice}.t"
    val = lambda: tuple(int(x or 0) for x in sr(conn, q)[0])
    first = val()
    res.add(f"{ice}.t before the append", first == (1, 1), f"got {first}")
    snap = iceberg.append_t([2, 3])
    t0, seen, last = time.time(), set(), None
    while time.time() - t0 < 90:
        last = val()
        seen.add(last)
        if last == (3, 6):
            break
        time.sleep(1)
    res.add("an append (one snapshot, 1 file) is seen by later queries", last == (3, 6),
            f"got {last} after {time.time() - t0:.1f} s, snapshot {snap}")
    res.add("no query saw a state other than before/after", seen <= {first, (3, 6)}, f"seen {sorted(seen)}")
    # complete mode reads the server's views, refreshed every 60 s
    t0 = time.time()
    while True:
        ok, r, _ = try_sql(conn, f"SELECT count(*), sum(id) FROM flight_c.{ice}.t")
        done = ok and tuple(int(x) for x in r[0]) == (3, 6)
        if done or time.time() - t0 > 90:
            break
        time.sleep(2)
    res.add("complete mode sees the append (views refresh every 60 s)", done,
            f"{str(r)[:200]} after {time.time() - t0:.1f} s")


# ---------------------------------------------------------------- check 12: Iceberg time travel

def check12(conn, args, res):
    """Iceberg time travel (m4 input store=iceberg, server 20b887839edf+): FOR VERSION / TIMESTAMP AS OF on ice.t,
    forwarded by the connector after the table name. One append to ice.t; every item queries the snapshot before or
    after it, in both result modes."""
    env = store_env()
    if env.get("M4_STORE") != "iceberg":
        res.add("store is iceberg", False, "run the m4 workflow with store=iceberg")
        return
    sys.path.insert(0, os.path.join(REPO, "ci", "m4"))
    import iceberg
    for line in open(os.path.join(os.environ.get("M4_STATE", os.path.expanduser("~/.m4-state")), "minio.env")):
        k, _, v = line.strip().partition("=")
        if k:
            os.environ.setdefault(k, v)
    ice = env.get("M4_ICEBERG_SCHEMA", "ice")
    make_catalogs(conn, args)
    t = f"flight.{ice}.t"

    def agg(sql):
        ok, r, _ = try_sql(conn, sql)
        return tuple(int(x or 0) for x in r[0]) if ok else r
    snap0, ts0 = iceberg.snapshot("t")
    # the reference values come from pyiceberg, not from the engine under test
    first = iceberg.count_sum("t")
    time.sleep(2)  # ts0 + 1.5 s below must stay before the append
    snap = iceberg.append_t([100])
    last = (first[0] + 1, first[1] + 100)
    for cat in ("flight", "flight_c"):
        for v, want, when in ((snap0, first, "before"), (snap, last, "after")):
            got = agg(f"SELECT count(*), sum(id) FROM {cat}.{ice}.t FOR VERSION AS OF {v}")
            res.add(f"{cat}: FOR VERSION AS OF the snapshot {when} the append", got == want, f"got {got}, want {want}")
    ok, r, _ = try_sql(conn, f"EXPLAIN SELECT id FROM {t} FOR VERSION AS OF {snap0}")
    rs = " | ".join(re.findall(r"REMOTE SQL:\s*(.*)", "\n".join(x[0] for x in r))) if ok else str(r)
    res.add("REMOTE SQL carries FOR VERSION AS OF", ok and f"FOR VERSION AS OF {snap0}" in rs, rs[:300])
    got = agg(f"SELECT (SELECT count(*) FROM {t} FOR VERSION AS OF {snap0}), "
              f"(SELECT count(*) FROM {t} FOR VERSION AS OF {snap})")
    res.add("two versions of one table in one query", got == (first[0], last[0]), f"got {got}")
    # the session time zone applies to the datetime; the server gets UTC
    tz = sr(conn, "SELECT @@time_zone")[0][0]
    sr(conn, "SET time_zone = 'Asia/Shanghai'")
    try:
        utc = datetime.datetime.fromtimestamp(ts0 / 1000 + 0.5, datetime.timezone.utc)
        for label, u in (("whole second", utc.replace(microsecond=0) + datetime.timedelta(seconds=1)),
                         ("with a fraction", utc)):
            local = (u + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S.%f")
            got = agg(f"SELECT count(*), sum(id) FROM {t} FOR TIMESTAMP AS OF '{local}'")
            res.add(f"FOR TIMESTAMP AS OF a time before the append ({label}, session zone +08:00)", got == first,
                    f"{local} -> got {got}, want {first}")
        got = agg(f"SELECT count(*), sum(id) FROM {t} FOR TIMESTAMP AS OF '2100-01-01 00:00:00'")
        res.add("FOR TIMESTAMP AS OF a later time sees the append", got == last, f"got {got}")
    finally:
        sr(conn, f"SET time_zone = '{tz}'")
    ok, r, _ = try_sql(conn, f"SELECT count(*) FROM {t} FOR VERSION BETWEEN {snap0} AND {snap}")
    res.add("a version range is refused by the connector", not ok and "support only" in str(r), str(r)[:200])


# ---------------------------------------------------------------- main

# ---------------------------------------------------------------- check 13: result compression (flight.compression)

# a wide lineitem read without aggregate pushdown: ~6M rows of comment, price, date go over the wire
SCAN13_Q = ("SELECT count(*), sum(length(l_comment)), sum(l_extendedprice), max(l_shipdate), min(l_shipmode) "
            "FROM {c}.tpch.lineitem")
NETEM = os.environ.get("M4_NETEM", "delay 10ms rate 1gbit")


def sr_host_veth():
    """Host side of the sr container's interface: its egress is everything sr receives (the Flight streams)."""
    idx = subprocess.run(["docker", "exec", "sr", "cat", "/sys/class/net/eth0/iflink"], capture_output=True,
                         text=True, check=True).stdout.strip()
    for line in subprocess.run(["ip", "-o", "link"], capture_output=True, text=True, check=True).stdout.splitlines():
        num, name = line.split(":")[0:2]
        if num.strip() == idx:
            return name.strip().split("@")[0]
    raise RuntimeError(f"no host interface with index {idx}")


def veth_tx_bytes(veth):
    return int(open(f"/sys/class/net/{veth}/statistics/tx_bytes").read())


def check13(conn, args, res):
    """flight.compression (opt-in, server cadd1aca9c23+): answers equal with none / lz4 / zstd (TPC-H q01–q22,
    types tables, a wide lineitem read), zstd and lz4 really shrink the stream (bytes into the sr container), and a
    slow-link comparison with `tc netem` on sr's host interface (informational MB/s)."""
    modes = ("none", "lz4", "zstd")
    for m in modes:
        catalog(conn, f"flight_z{m}", flight__compression=m, **({"flight__token": args.token} if args.token else {}))
    # TPC-H on both compressed catalogs against the reference (check 4's comparison)
    for m in ("lz4", "zstd"):
        sub = Result(13, "")
        a = argparse.Namespace(**vars(args))
        a.catalog, a.ref_catalog = f"flight_z{m}", ""
        check4(conn, a, sub)
        for name, ok, det in sub.items:
            if name.startswith("q") and "EXPLAIN" not in name:
                res.items.append((f"{m} {name}", ok, det))
        nfail = sum(1 for i in sub.items if not i[1])
        print(f"  TPC-H with {m}: {len(sub.items) - nfail}/{len(sub.items)}", flush=True)
    # every types table, all columns: compressed catalogs return what the uncompressed one returns
    tables = [r[0] for r in sr(conn, "SHOW TABLES FROM flight_znone.types")]
    for t in tables:
        def one(t=t):
            base = sorted(repr(r) for r in sr(conn, f"SELECT * FROM flight_znone.types.{t}"))
            for m in ("lz4", "zstd"):
                got = sorted(repr(r) for r in sr(conn, f"SELECT * FROM flight_z{m}.types.{t}"))
                res.add(f"types.{t} {m} = none", got == base, f"rows {len(got)}/{len(base)}")
        guarded(res, f"types.{t}", one)

    veth = sr_host_veth()
    sr(conn, "SET flight_aggregate_pushdown = false")
    sr(conn, "SET enable_profile = true")
    measured = {}

    def run(m, link):
        best = None
        for i in range(2):
            b0, t0 = veth_tx_bytes(veth), time.time()
            rows = sr(conn, SCAN13_Q.format(c=f"flight_z{m}"))
            secs, wire = time.time() - t0, veth_tx_bytes(veth) - b0
            qid = sr(conn, "SELECT last_query_id()")[0][0]
            if best is None or secs < best[0]:
                best = (secs, wire, qid, rows)
        p, _ = query_profile(conn, best[2], args.out, f"check13-{link}-{m}")
        decoded = sum(byte_values(p, "BytesRead"))
        measured[(link, m)] = (best[0], best[1], decoded, [tuple(norm(v) for v in r) for r in best[3]])

    try:
        for m in modes:
            guarded(res, f"scan {m} plain link", lambda m=m: run(m, "plain"))
        tc = ["sudo", "tc", "qdisc", "add", "dev", veth, "root", "netem", "limit", "100000", *NETEM.split()]
        p = subprocess.run(tc, capture_output=True, text=True)
        if p.returncode:
            # sch_netem may be in the kernel's extra modules package on the runner
            subprocess.run(f"sudo apt-get install -y -q linux-modules-extra-$(uname -r) && sudo modprobe sch_netem",
                           shell=True, capture_output=True)
            p = subprocess.run(tc, capture_output=True, text=True)
        res.add(f"tc netem on {veth}", p.returncode == 0, (p.stderr or "")[-300:])
        if p.returncode == 0:
            try:
                for m in modes:
                    guarded(res, f"scan {m} netem", lambda m=m: run(m, "netem"))
            finally:
                subprocess.run(["sudo", "tc", "qdisc", "del", "dev", veth, "root"], capture_output=True)
    finally:
        sr(conn, "SET enable_profile = false")
        sr(conn, "SET flight_aggregate_pushdown = true")
    exp = [tuple(norm(v) for v in r) for r in
           args.duck.execute(SCAN13_Q.format(c="x").replace("x.tpch.", "tpch.")).fetchall()] if args.duck else None
    for (link, m), (secs, wire, decoded, rows) in sorted(measured.items()):
        if exp is not None:
            res.add(f"scan {m} {link} = DuckDB", rows == exp, "" if rows == exp else f"sr={rows} duck={exp}")
        res.notes.append(f"{link} link ({'' if link == 'plain' else NETEM}) {m}: {secs:.2f} s, {wire / 1e6:.1f} MB "
                         f"into sr, {decoded / 1e6:.1f} MB decoded (BytesRead), "
                         f"{decoded / 1e6 / secs:.0f} MB/s decoded, {wire / 1e6 / secs:.0f} MB/s on the wire")
    for link in ("plain", "netem"):
        off = measured.get((link, "none"))
        for m in ("lz4", "zstd"):
            got = measured.get((link, m))
            if off and got:
                # the stream really is compressed: clearly fewer bytes reach sr (lineitem text compresses > 2x)
                res.add(f"{m} {link}: bytes into sr < 0.8 x none", got[1] < 0.8 * off[1],
                        f"{got[1] / 1e6:.1f} MB vs {off[1] / 1e6:.1f} MB")
    for m in modes:
        sr(conn, f"DROP CATALOG IF EXISTS flight_z{m}")


TITLES = {1: "catalog, SHOW, DESC, masking", 2: "types tables, every column", 3: "M4-TESTS §1–2 (EXPLAIN + results)",
          4: "TPC-H SF1 q01–q22, topn default and 0", 5: "sr-cases on SF1", 6: "failover (2 servers)",
          7: "KILL QUERY during a long scan", 8: "token and TLS", 9: "memory limit",
          10: "lakeFS: commits between queries", 11: "Iceberg: REST catalog tables, deletes, rename, appends", 12: "Iceberg time travel",
          13: "result compression (flight.compression none / lz4 / zstd)"}
FUNCS = {1: check1, 2: check2, 3: check3, 4: check4, 5: check5, 6: check6, 7: check7, 8: check8, 9: check9, 10: check10,
         11: check11, 12: check12, 13: check13}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checks", default="1,2,3,4,5")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tpch", help="TPC-H parquet dir (DuckDB side; needed by checks 1-3, 5 without "
                                   "--sr-cases-ref, 6)")
    ap.add_argument("--types", help="types tables parquet dir (checks 1-3)")
    ap.add_argument("--catalog", default="flight", help="catalog under test in checks 4 and 5")
    ap.add_argument("--existing-catalog", action="store_true",
                    help="use the existing catalog --catalog as is: check 1 is not run implicitly")
    ap.add_argument("--reference", default=os.path.join(M4, "reference", "sf1"),
                    help="TPC-H answers for check 4 (qNN.tsv + qNN.cols)")
    ap.add_argument("--ref-catalog", default="", help="check 4 also runs every query on this catalog "
                                                      "(e.g. the JDBC bridge) and compares rows and timings")
    ap.add_argument("--sr-cases-ref", default="", help="check 5 compares with this file (sr-cases.ref format) "
                                                       "instead of DuckDB")
    ap.add_argument("--token", default=os.environ.get("M4_TOKEN", ""))
    ap.add_argument("--series", default="")
    ap.add_argument("--assets", default=os.path.expanduser("~/m4-assets"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if os.path.abspath(args.reference) != os.path.join(M4, "reference", "sf1"):
        TITLES[4] = f"TPC-H q01–q22 vs {os.path.basename(os.path.normpath(args.reference))}, topn default and 0"
    if args.sr_cases_ref:
        TITLES[5] = f"sr-cases vs {os.path.basename(args.sr_cases_ref)}"
    args.duck = duck(args.tpch, args.types) if args.tpch and args.types else None
    conn = sr_connect()
    results = []
    nums = [int(x) for x in args.checks.split(",") if x.strip()]
    if any(n > 1 for n in nums) and 1 not in nums and not args.existing_catalog:
        nums = [1] + nums      # later checks need the catalog
    for n in nums:
        if n not in FUNCS:
            print(f"check {n}: not implemented yet")
            continue
        print(f"== check {n}: {TITLES[n]}", flush=True)
        res = Result(n, TITLES[n])
        t0 = time.time()
        try:
            FUNCS[n](conn, args, res)
        except Exception as e:
            traceback.print_exc()
            res.add("check aborted", False, f"{type(e).__name__}: {e}".replace("\n", " "))
            try:
                conn.close()
            except Exception:
                pass
            conn = sr_connect()
        res.secs = time.time() - t0
        results.append(res)

    run = os.environ.get("GITHUB_RUN_ID", "local")
    with open(os.path.join(args.out, "results.md"), "w") as f:
        f.write(f"# M4 run {run}\n\n{datetime.datetime.utcnow():%Y-%m-%d %H:%M} UTC, series `{args.series}`, "
                f"server `{os.environ.get('M4_SERVER_JAR', '?')}`, store `{store_env().get('M4_STORE', 's3')}: {store_env().get('M4_DATA_DIR', 's3://lake/parquet')}`, compression `{COMPRESSION}`, checks {args.checks}\n\n| # | Check | Result | Items | Time |\n|---|---|---|---|---|\n")
        for r in results:
            nfail = sum(1 for i in r.items if not i[1])
            f.write(f"| {r.num} | {r.title} | {'PASS' if r.ok else 'FAIL'} | {len(r.items) - nfail}/{len(r.items)} | "
                    f"{r.secs:.0f} s |\n")
        for r in results:
            f.write(f"\n## Check {r.num}: {r.title}\n\n")
            for name, ok, det in r.items:
                f.write(f"- {'PASS' if ok else '**FAIL**'} `{name[:200]}` {det}\n")
            for n in r.notes:
                f.write(f"- note: {n}\n")
    json.dump([{"check": r.num, "ok": r.ok, "items": r.items, "notes": r.notes} for r in results],
              open(os.path.join(args.out, "results.json"), "w"), indent=1, default=str)
    print(open(os.path.join(args.out, "results.md")).read())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
