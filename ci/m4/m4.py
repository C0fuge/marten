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
import argparse, datetime, decimal, json, os, re, struct, sys, time, traceback, uuid
from decimal import Decimal

decimal.getcontext().prec = 80

import duckdb
import pymysql

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M4 = os.path.join(REPO, "tests", "m4")
FLIGHT_URI = os.environ.get("M4_FLIGHT_URI", "grpc://flight1:32010")


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
    sr(conn, "CREATE EXTERNAL CATALOG flight PROPERTIES (" + ", ".join(props) + ")")
    res.add("create catalog", True)

    def show_create():
        txt = " ".join(str(c) for r in sr(conn, "SHOW CREATE CATALOG flight") for c in r)
        leaked = bool(args.token) and args.token in txt
        res.add("SHOW CREATE CATALOG masks the token", not leaked, txt.replace("\n", " ")[:400])
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
        "TIME": [None, ""], "INTERVAL": [None, ""],
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
                if dk.get(c) == "TIMESTAMP_NS":
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


def check4(conn, args, res):
    sr(conn, f"SET CATALOG {args.catalog}")
    sr(conn, "USE tpch")
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
                        # same query on the other catalog (e.g. the JDBC bridge): equal rows, timing for comparison
                        sr(conn, f"SET CATALOG {args.ref_catalog}")
                        try:
                            sr(conn, "USE tpch")
                            t1 = time.time()
                            other = sr(conn, sql)
                            ref_timings.append((q, topn, time.time() - t1))
                        finally:
                            sr(conn, f"SET CATALOG {args.catalog}")
                            sr(conn, "USE tpch")
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


# ---------------------------------------------------------------- check 6: failover (two servers)

def check6(conn, args, res):
    exp = [tuple(norm(v) for v in r) for r in args.duck.execute(SCAN_Q.format(c="x").replace("x.tpch.", "tpch.")).fetchall()]
    try:
        flight_restart(args, ("flight1", "flight2"))
        catalog(conn, "flight_fo", "grpc://flight1:32010,grpc://flight2:32010")
        sr(conn, "SET flight_aggregate_pushdown = false")   # the BE must read every endpoint
        q = SCAN_Q.format(c="flight_fo")
        ok, r, secs = try_sql(conn, q)
        got = [tuple(norm(v) for v in x) for x in r] if ok else r
        res.add("both servers up: full scan correct", ok and got == exp, f"{secs:.1f}s got={got} exp={exp}")
        n_ep = remote_sql(conn, q)[1].count("flight")  # informational
        res.notes.append(f"plan of the failover scan mentions 'flight' {n_ep}x")

        stack("stop", "flight2")
        ok, r, secs = try_sql(conn, q)
        got = [tuple(norm(v) for v in x) for x in r] if ok else r
        res.add("flight2 stopped before the query: succeeds via backup locations", ok and got == exp,
                f"{secs:.1f}s got={got}")

        stack("flight", args.assets, "flight2", "flight1,flight2")
        time.sleep(10)
        out = {}
        def run():
            c2 = sr_connect()
            sr(c2, "SET flight_aggregate_pushdown = false")
            out["r"] = try_sql(c2, q)
            c2.close()
        th = threading.Thread(target=run)
        th.start()
        time.sleep(1.5)
        stack("kill", "flight2")
        th.join(600)
        ok, r, secs = out.get("r", (False, "no result (hung)", 0))
        if ok:
            got = [tuple(norm(v) for v in x) for x in r]
            res.add("flight2 killed during the read: no wrong/duplicate rows", got == exp,
                    f"query succeeded in {secs:.1f}s got={got} exp={exp}")
        else:
            res.add("flight2 killed during the read: clean error", "hung" not in r, f"{secs:.1f}s {r}")
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


# ---------------------------------------------------------------- main

TITLES = {1: "catalog, SHOW, DESC, masking", 2: "types tables, every column", 3: "M4-TESTS §1–2 (EXPLAIN + results)",
          4: "TPC-H SF1 q01–q22, topn default and 0", 5: "sr-cases on SF1", 6: "failover (2 servers)",
          7: "KILL QUERY during a long scan", 8: "token and TLS", 9: "memory limit"}
FUNCS = {1: check1, 2: check2, 3: check3, 4: check4, 5: check5, 6: check6, 7: check7, 8: check8, 9: check9}


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
                f"checks {args.checks}\n\n| # | Check | Result | Items | Time |\n|---|---|---|---|---|\n")
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
