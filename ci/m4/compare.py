#!/usr/bin/env python3
"""Connector comparison (docs/CONNECTOR-COMPARE.md): TPC-H q01-q22 through one StarRocks path to the Flight server.

    compare.py reference --tpch DIR --out FILE.json
        DuckDB answers of q01-q22 on the parquet files (rows + checksum + column types); run before StarRocks starts.
    compare.py run --path ours|ours_rf|up|jdbc --label L --ref FILE.json --out DIR [--runs 3] [--timeout 900]
        creates catalog `cmp` for the path, runs every query --runs times (1st = cold, the rest warm), checks each
        answer against the reference, samples FE / BE resident memory (docker exec sr ps) every second;
        writes DIR/L.json.
    compare.py report --out FILE.md DIR/*.json
        tables: correct answers, sum of warm medians, per query, memory.

Expects StarRocks (container `sr`) on 127.0.0.1:9030 and the Flight server at $M4_FLIGHT_URI (grpc://flight1:32010).
"""
import argparse, hashlib, json, os, re, statistics, subprocess, sys, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m4  # noqa: E402  (sr_connect, sr, norm helpers)

QUERIES = os.path.join(m4.M4, "queries")
FLIGHT_URI = m4.FLIGHT_URI
JDBC_URI = os.environ.get("CMP_JDBC_URI", "jdbc:arrow-flight-sql://flight1:32010/?useEncryption=0")
JDBC_DRIVER = "pro.surpin.data.arrowflight.starrocks.jdbc.postgresql.FlightSqlPostgresqlDriver"


def query_sql(q):
    return open(os.path.join(QUERIES, f"{q}.sql")).read().strip().rstrip(";")


def sr_sql(sql):
    # StarRocks has no SQL-standard substring(x FROM a FOR b) (q22); same rewrite as m4.py check 4
    return re.sub(r"substring\(\s*([\w.]+)\s+FROM\s+(\d+)\s+FOR\s+(\d+)\s*\)", r"substring(\1, \2, \3)", sql, flags=re.I)


def checksum(rows):
    h = hashlib.sha256()
    for r in sorted(rows):
        h.update(("\t".join(r) + "\n").encode())
    return h.hexdigest()[:16]


def reference(args):
    import duckdb
    d = duckdb.connect()
    d.execute("SET TimeZone = 'UTC'")
    d.execute(f"SET memory_limit = '{os.environ.get('CMP_DUCK_MEM', '6GB')}'")
    d.execute("CREATE SCHEMA tpch")
    for t in sorted(os.listdir(args.tpch)):
        d.execute(f"CREATE VIEW tpch.{t} AS SELECT * FROM read_parquet('{args.tpch}/{t}/*.parquet')")
    out = {"rows": {t: d.execute(f"SELECT count(*) FROM tpch.{t}").fetchone()[0] for t in sorted(os.listdir(args.tpch))},
           "queries": {}}
    for i in range(1, 23):
        q = f"q{i:02d}"
        t0 = time.time()
        d.execute("USE tpch")
        cur = d.execute(query_sql(q))
        types = [str(c[1]) for c in cur.description]
        raw = cur.fetchall()
        rows = [[m4.norm_sr_as(v, ty) for v, ty in zip(r, types)] for r in raw]
        out["queries"][q] = {"types": types, "nrows": len(rows), "checksum": checksum(rows),
                             "ordered": "ORDER BY" in query_sql(q).upper(), "rows": rows if len(rows) <= 200 else rows[:200],
                             "duck_s": round(time.time() - t0, 3)}
        print(f"{q}: {len(rows)} rows {out['queries'][q]['checksum']} ({time.time() - t0:.1f}s)", flush=True)
    json.dump(out, open(args.out, "w"), indent=1)


class MemSampler(threading.Thread):
    """Peak resident memory (MB) of the FE (java StarRocksFE) and BE (starrocks_be) processes in container sr."""

    def __init__(self):
        super().__init__(daemon=True)
        self.fe = self.be = 0
        self.stop = False

    def sample(self):
        p = subprocess.run(["docker", "exec", "sr", "ps", "-eo", "rss=,args="], capture_output=True, text=True)
        fe = be = 0
        for line in p.stdout.splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            if "StarRocksFE" in parts[1]:
                fe += int(parts[0])
            elif "starrocks_be" in parts[1]:
                be += int(parts[0])
        return fe // 1024, be // 1024

    def reset(self):
        self.fe = self.be = 0

    def run(self):
        while not self.stop:
            fe, be = self.sample()
            self.fe, self.be = max(self.fe, fe), max(self.be, be)
            time.sleep(1)


# path ours_rf: ours plus explicit join runtime filters on the ticket (docs/UPSTREAM-REVIEW.md; since series fl234f9b
# path ours already sends them: connector default max_keys 4096, wait_ms 500); CMP_RF_PROPS
# ("k=v,k=v") replaces the default
RF_PROPS = dict(kv.split("=", 1) for kv in os.environ.get(
    "CMP_RF_PROPS", "flight.runtime_filters.max_keys=4096,flight.runtime_filters.wait_ms=500").split(",") if kv)


def make_catalog(conn, path):
    if path in ("ours", "ours_rf", "up"):
        props = {"type": "flight", "flight.uri": FLIGHT_URI}       # all: no auth, everything else default
        if path == "ours_rf":
            props.update(RF_PROPS)
    else:
        props = {"type": "jdbc", "user": "", "password": "", "jdbc_uri": JDBC_URI,
                 "driver_url": "file:///opt/flight-starrocks/driver.jar", "driver_class": JDBC_DRIVER}
    m4.sr(conn, "DROP CATALOG IF EXISTS cmp")
    m4.sr(conn, "CREATE EXTERNAL CATALOG cmp PROPERTIES (" + ", ".join(f'"{k}" = "{v}"' for k, v in props.items()) + ")")
    return props


EXPLAIN_QUERIES = ["q12", "q14", "q17", "q19"]


def selected(args):
    qs = [f"q{i:02d}" for i in range(1, 23)]
    if args.queries:
        want = {f"q{int(x.strip().lstrip('qQ')):02d}" for x in args.queries.split(",") if x.strip()}
        qs = [q for q in qs if q in want]
    return qs


def server_log(since, until, pattern, container="flight1"):
    """Lines of the Flight server's container log written between two unix times that match pattern."""
    try:
        p = subprocess.run(["docker", "logs", "--since", f"{since:.3f}", "--until", f"{until:.3f}", container],
                           capture_output=True, text=True, timeout=60)
        lines = (p.stdout + p.stderr).splitlines()
    except Exception as e:
        return [f"(docker logs failed: {type(e).__name__}: {e})"]
    rx = re.compile(pattern)
    return [ln[:600] for ln in lines if rx.search(ln)][:120]


def run(args):
    ref = json.load(open(args.ref))
    log_qs = set(selected(argparse.Namespace(queries=args.server_log_queries))) if args.server_log_queries else set()
    conn = m4.sr_connect()
    m4.sr(conn, f"SET query_timeout = {args.timeout}")
    version = m4.sr(conn, "SELECT current_version()")[0][0]
    props = make_catalog(conn, args.path)
    res = {"path": args.path, "label": args.label, "version": version, "catalog": props, "queries": {},
           "selected": selected(args), "server": os.environ.get("CMP_SERVER", ""),
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t0 = time.time()
    try:
        m4.sr(conn, "SET CATALOG cmp")
        m4.sr(conn, "USE tpch")
        res["tables"] = sorted(r[0] for r in m4.sr(conn, "SHOW TABLES"))
        res["setup_s"] = round(time.time() - t0, 2)
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"[:600]
        json.dump(res, open(os.path.join(args.out, f"{args.label}.json"), "w"), indent=1)
        print(res["error"])
        return
    if log_qs:   # server start-up lines (resource profile, DuckDB sizing) before the first query
        res["server_log"] = {"startup": server_log(0, time.time(), r"duckdb=sizing|resourceProfile|[Pp]rofile|memory budget")}
    mem = MemSampler()
    mem.start()
    total_fe = total_be = 0
    for q in selected(args):
        exp = ref["queries"][q]
        q_t0 = time.time()
        sql = sr_sql(query_sql(q))
        mem.reset()
        times, ok, detail = [], None, ""
        for k in range(args.runs):
            t1 = time.time()
            try:
                got = m4.sr(conn, sql)
            except Exception as e:
                times.append(None)
                detail = f"{type(e).__name__}: {e}".replace("\n", " ")[:400]
                ok = False
                try:     # a broken connection must not fail the remaining queries
                    conn.ping(reconnect=True)
                    m4.sr(conn, f"SET query_timeout = {args.timeout}")
                    m4.sr(conn, "SET CATALOG cmp")
                    m4.sr(conn, "USE tpch")
                except Exception:
                    conn = m4.sr_connect()
                    m4.sr(conn, f"SET query_timeout = {args.timeout}")
                    m4.sr(conn, "SET CATALOG cmp")
                    m4.sr(conn, "USE tpch")
                break    # a failed (or timed-out) query is not repeated
            times.append(round(time.time() - t1, 3))
            rows = [[m4.norm_sr_as(v, ty) for v, ty in zip(r, exp["types"])] for r in got]
            good = len(rows) == exp["nrows"] and checksum(rows) == exp["checksum"]
            if good and exp["ordered"] and len(rows) <= 200:
                # same rows (checksum); the order must match too, at least in the first column (ties may differ)
                good = rows == exp["rows"] or [r[0] for r in rows] == [r[0] for r in exp["rows"]]
            if not good and ok is not False:
                detail = f"rows {len(rows)}/{exp['nrows']} checksum {checksum(rows)}/{exp['checksum']}"
                if len(rows) <= 200:
                    only = [r for r in rows if r not in exp["rows"]][:2]
                    detail += f" | first differing: {only}"
            ok = good if ok is None else (ok and good)
        if q in log_qs:
            time.sleep(1.5)      # the server writes some lines (executionPath) asynchronously
            res.setdefault("server_log", {})[q] = server_log(q_t0 - 0.5, time.time(), args.server_log_re)
        time.sleep(1.2)
        warm = [t for t in times[1:] if t is not None]
        res["queries"][q] = {"ok": bool(ok), "times": times, "cold": times[0] if times else None,
                             "warm_median": round(statistics.median(warm), 3) if warm else None,
                             "fe_peak_mb": mem.fe, "be_peak_mb": mem.be, "detail": detail}
        total_fe, total_be = max(total_fe, mem.fe), max(total_be, mem.be)
        print(f"{args.label} {q}: {'OK ' if ok else 'BAD'} {times} fe {mem.fe} MB be {mem.be} MB {detail}", flush=True)
    mem.stop = True
    if args.path in ("ours", "ours_rf"):
        # remote SQL of the join-key-pushdown queries (STATUS Next steps (b)), after the timed runs
        res["explain"] = {}
        for q in [x for x in EXPLAIN_QUERIES if x in selected(args)]:
            try:
                plan = "\n".join(r[0] for r in m4.sr(conn, "EXPLAIN " + sr_sql(query_sql(q))))
                res["explain"][q] = re.findall(r"REMOTE SQL:\s*(.*)", plan)
            except Exception as e:
                res["explain"][q] = [f"{type(e).__name__}: {e}"[:400]]
            print(f"{args.label} {q} REMOTE SQL: {res['explain'][q]}", flush=True)
    res["fe_peak_mb"], res["be_peak_mb"] = total_fe, total_be
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(res, open(os.path.join(args.out, f"{args.label}.json"), "w"), indent=1)


def fmt(v):
    return "-" if v is None else f"{v:.2f}"


def report(args):
    rs = [json.load(open(f)) for f in args.files]
    L = ["| run | path | correct | sum of warm medians (s) | sum of cold (s) | FE peak MB | BE peak MB | version |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rs:
        qs = r.get("queries", {})
        n = sum(1 for v in qs.values() if v["ok"])
        allw = all(v["warm_median"] is not None for v in qs.values()) and len(qs) == len(r.get("selected", qs) or qs)
        sw = sum(v["warm_median"] or 0 for v in qs.values())
        sc = sum(v["cold"] or 0 for v in qs.values())
        L.append(f"| {r['label']} | {r['path']} | {n}/{len(r.get('selected') or range(22))}{'' if 'error' not in r else ' (' + r['error'][:120] + ')'} | "
                 f"{sw:.2f}{'' if allw else ' (incomplete)'} | {sc:.2f} | {r.get('fe_peak_mb', '-')} | "
                 f"{r.get('be_peak_mb', '-')} | {r.get('version', '')} |")
    L += ["", "Per query: warm median / cold (s), `x` = wrong answer or error", "",
          "| q | " + " | ".join(r["label"] for r in rs) + " |", "|---|" + "---|" * len(rs)]
    for i in range(1, 23):
        q = f"q{i:02d}"
        if not any(q in r.get("queries", {}) for r in rs):
            continue
        cells = []
        for r in rs:
            v = r.get("queries", {}).get(q)
            cells.append("-" if not v else f"{'' if v['ok'] else 'x '}{fmt(v['warm_median'])} / {fmt(v['cold'])}")
        L.append(f"| {q} | " + " | ".join(cells) + " |")
    L += ["", "Errors / wrong answers:", ""]
    for r in rs:
        for q, v in r.get("queries", {}).items():
            if not v["ok"]:
                L.append(f"- {r['label']} {q}: {v['detail']}")
    for r in rs:
        for q, sqls in r.get("explain", {}).items():
            if f"REMOTE SQL ({r['label']}):" not in L:
                L += ["", f"REMOTE SQL ({r['label']}):", ""]
            L += [f"- {q}: " + " | ".join(f"`{x}`" for x in sqls)]
    for r in rs:
        for q, lines in r.get("server_log", {}).items():
            L += ["", f"<details><summary>Server log {r['label']} {q} ({len(lines)} matching lines)</summary>", "",
                  "```"] + [x.replace("```", "'''") for x in lines] + ["```", "", "</details>"]
    open(args.out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["reference", "run", "report"])
    ap.add_argument("--tpch")
    ap.add_argument("--out")
    ap.add_argument("--ref")
    ap.add_argument("--path", choices=["ours", "ours_rf", "up", "jdbc"])
    ap.add_argument("--label")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--queries", default="", help="comma-separated subset, e.g. q04,q14 (default: all 22)")
    ap.add_argument("--server-log-queries", default="", help="queries whose server log lines go into the result")
    ap.add_argument("--server-log-re", default=r"duckdb=sizing|resourceProfile|executionPath|plan")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args()
    {"reference": reference, "run": run, "report": report}[args.mode](args)


if __name__ == "__main__":
    main()
