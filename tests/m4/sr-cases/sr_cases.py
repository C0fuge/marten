"""sr_cases.py <catalog> <queries> <refOut> <outPrefix>: run TPC-H spot checks through StarRocks <catalog>, compare with DuckDB reference."""
import sys, subprocess, re
from decimal import Decimal, InvalidOperation
cat, qf, ref, out = sys.argv[1:5]
def run(q):
    p = subprocess.run(["podman", "exec", "starrocks", "mysql", "-h127.0.0.1", "-P9030", "-uroot", "-B", "-N", "-e", q], capture_output=True, timeout=900)
    return p.returncode, p.stdout.decode(), p.stderr.decode().strip()
refs, cur = {}, None
for l in open(ref):
    l = l.rstrip("\n")
    if l.startswith("### "): cur = l[4:]; refs[cur] = []
    else: refs[cur].append(l)
def norm(cell):
    try:
        d = Decimal(cell); return str(round(d, 4).normalize()) if d != 0 else "0"
    except InvalidOperation: return cell
def rows(lines, ordered):
    r = ["\t".join(norm(c) for c in l.split("\t")) for l in lines if l != ""]
    return r if ordered else sorted(r)
ok = bad = 0; log = []
for q in [l.rstrip("\n") for l in open(qf) if l.strip()]:
    sq = q if "'" in q else q.replace('"', '`')
    sq = re.sub(r"\btpch\.", f"{cat}.tpch.", sq).replace("`tpch`.", f"{cat}.tpch.")
    rc, so, se = run(sq)
    ordered = "ORDER BY" in q.upper()
    if rc: res = f"ERROR {se}"; good = False
    else:
        g, e = rows(so.split("\n"), ordered), rows(refs.get(q, ["<no ref>"]), ordered)
        good = g == e; res = ("MATCH" if good else f"DIFF got={g[:3]} exp={e[:3]}") + f" rows={len(g)}"
    ok += good; bad += not good
    log.append(f"{'OK  ' if good else 'BAD '} {sq}\n     {res}")
open(out + ".txt", "w").write("\n".join(log) + f"\nok={ok} bad={bad}\n")
print("\n".join(log)); print(f"ok={ok} bad={bad}")
