# Local final check (maintainer's stand)

Everything else of M4 is green in CI (`docs/M4-RESULTS.md`, run 39665941130, series `4a9848e-fl598360`). This
checklist covers only what CI cannot do (`docs/M4-CI.md` §6): the HDFS data path (hadoopfs) at SF10, a 3-node
server cluster for kill tests, speed against the JDBC bridge and the Trino plugin, and the stand's
production-like server build. Budget: about 2–3 hours, most of it waiting for queries.

Names used below (change them if the stand differs): StarRocks MySQL port `9030`, user `root`; catalogs `flight`
(this connector) and `jdbc` (the existing JDBC bridge catalog on the same server), schema `tpch` in both; Flight
servers `fs1`, `fs2`, `fs3` on port `32010`. No credentials in this repository: tokens go into the catalog
statements and environment variables on the stand only.

## 0. Prepare

1. **Build under test.** Release `v4.1.4-flight.0-dryrun` (draft, series `4a9848e-fl598360`; check that
   `fe-build-info.txt` and `be-build-info.txt` both name this series) or the CI artifacts of FE run 39664615702 /
   BE run 39664594320. Install as in `docs/INSTALL.md` §2a (allin1 overlay) or §2b (existing deployment).
   Check: `SELECT current_version();` and `be/lib/starrocks_be --version` → `4.1.4-4a9848e`.
2. **Servers.** The stand's production-like server build, 3 nodes in one cluster (`--hosts fs1,fs2,fs3`),
   hadoopfs data with TPC-H **SF10** in schema `tpch`, token auth on (TLS too if the stand normally runs it),
   result mode default (partial).
3. **Client tools** on the machine that runs the checks (any host that reaches port 9030):

   ```bash
   git clone <this repo> starrocks-flight && cd starrocks-flight     # the harness is ci/m4/m4.py
   python3 -m venv ~/m4venv && . ~/m4venv/bin/activate && pip install pymysql duckdb==1.4.1
   export M4_SR_HOST=<fe host> M4_SR_PORT=9030 M4_SR_USER=root M4_SR_PASSWORD=<password or empty>
   export TOKEN=<flight token>                                        # shell only, never commit it
   ```
4. **Catalogs** (TLS: `grpc+tls://…` plus `"flight.tls.ca_file" = "<pem path on FE and BE>"`):

   ```sql
   CREATE EXTERNAL CATALOG flight PROPERTIES (
     "type" = "flight",
     "flight.uri" = "grpc://fs1:32010,grpc://fs2:32010,grpc://fs3:32010",
     "flight.token" = "<token>"
   );
   SHOW CREATE CATALOG flight;        -- token shown masked
   SHOW DATABASES FROM flight;        -- tpch
   SELECT count(*) FROM flight.tpch.lineitem;   -- 59986052, well under 1 s (count pushdown); JDBC: ~12 s
   ```

## 1. TPC-H SF10: correctness against the truth and the JDBC bridge, timings (A)

```bash
python3 ci/m4/m4.py --checks 4,5 --out ~/m4-local --existing-catalog --catalog flight \
  --reference <bench>/reference/sf10 --ref-catalog jdbc --sr-cases-ref tests/m4/sr-cases/sr-cases.ref
```

- Check 4 runs q01–q22 (`tests/m4/queries`) on `flight` with `cbo_push_down_topn_limit` at its default and at 0,
  compares each result with `<bench>/reference/sf10` (expected layout as `tests/m4/reference/sf1`: `qNN.tsv` +
  `qNN.cols`; decimals rounded to 4 places, order checked on the `key` columns) **and** runs the same query on
  `jdbc` and compares rows. Timings of both catalogs end up in `~/m4-local/results.md` (notes of check 4).
  If the bench reference has another layout, the `qNN topn=…` items fail with a file error; the
  `qNN topn=… = jdbc` items are then the comparison that counts.
- Check 5 runs the 26 sr-cases on `flight` and compares them with `sr-cases.ref` (the SF10 answers of the JDBC
  bridge).
- **Pass:** every item PASS (44 reference + 44 jdbc items in check 4, 26 in check 5). The JDBC side makes this
  slow (each query twice per topn setting); drop `--ref-catalog jdbc` for a quick rerun.

**Trino plugin timings** (same queries; q22 needs no rewrite in Trino):

```bash
for q in tests/m4/queries/q*.sql; do
  s=$(date +%s.%N); trino --server <trino> --catalog <flight catalog> --schema tpch -f "$q" > /dev/null
  echo "$(basename "$q" .sql) $(echo "$(date +%s.%N) - $s" | bc)"
done | tee ~/m4-local/trino-timings.txt
```

## 2. 3-node cluster: kill tests (B)

Reference value first (JDBC, or the truth):

```sql
SELECT count(*), sum(l_quantity), sum(length(l_comment)) FROM jdbc.tpch.lineitem;
```

The scan under test reads every endpoint in the BE (aggregate pushdown off):

```sql
SET flight_aggregate_pushdown = false;
SELECT count(*), sum(l_quantity), sum(length(l_comment)) FROM flight.tpch.lineitem;   -- note the time T
```

| # | Step | Pass |
|---|---|---|
| B1 | all 3 servers up: run the scan | equals the reference |
| B2 | stop `fs3` (clean stop), run the scan | equals the reference via the backup locations; planning may take up to ~11 s while the cluster notices (risk R7) — note the time |
| B3 | start `fs3` again, wait until the cluster lists it, run the scan | equals the reference |
| B4 | start the scan, `kill -9` the `fs2` process after about T/3 | either equals the reference or ends with a clean error naming the endpoint; **never** a different result. Repeat 3× (the outcome depends on whether a stream of `fs2` was already delivering) |
| B5 | `kill -9` two servers, run the scan | clean error (or the correct result if the remaining server still holds every endpoint), no hang: connects give up after `flight.connect_timeout_ms` per location (5 s default), planning may add up to ~11 s (R7) |
| B6 | restart all, start the scan, `KILL QUERY <connection id>` from a second session after ~T/2 | the query ends within ~1 s; the server log shows the stream cancelled; next query works |
| B7 | after all of it | `SHOW BACKENDS` all `Alive = true`; `SELECT count(*) FROM flight.tpch.nation` = 25 |

Compare B2/B4 with the Trino plugin v10 on the same cluster (same kill points): the connector follows the same
rule (fail over only when nothing was delivered yet and the error is "unreachable"; server errors are not failed
over), so the outcome per step should match.

## 3. Production-like server: auth, TLS, logs, profile (C)

| # | Step | Pass |
|---|---|---|
| C1 | catalog with the right token (and TLS if used): `SELECT count(*) FROM <c>.tpch.nation` | 25 |
| C2 | same catalog with a wrong token / without a token | fails; the token is not in the error text |
| C3 | TLS only: `flight.tls.verify` default with the right CA file / without it / with `"flight.tls.verify" = "false"` | ok / fails / ok |
| C4 | query profile: `SET enable_profile = true;` run C1, then `SHOW PROFILELIST LIMIT 1;` and `SELECT get_query_profile('<query id>');` (or `ANALYZE PROFILE FROM '<query id>';`) | the token does not appear |
| C5 | log grep (below) after all steps of this file | no hits |

```bash
grep -rlF -- "$TOKEN" "$STARROCKS_HOME"/fe/log "$STARROCKS_HOME"/be/log ~/m4-local && echo "TOKEN LEAKED" || echo "no hits"
# allin1 overlay: docker exec <container> grep -rlF -- "$TOKEN" /data/deploy/starrocks/fe/log /data/deploy/starrocks/be/log
```

Optional (CI covers it on SF1): memory under a small limit at SF10 —
`SET flight_aggregate_pushdown = false; SET query_mem_limit = 104857600;` then
`SELECT count(*) FROM (SELECT l_comment, l_orderkey, l_partkey FROM flight.tpch.lineitem GROUP BY 1, 2, 3) t;`
→ clean memory-limit error, BE stays up; `SET query_mem_limit = 0;` afterwards.

## 4. Report back

Commit nothing secret. Send (or add to `docs/M4-RESULTS.md` under a new heading "local final check"):

- `~/m4-local/results.md` (check 4 and 5 items, timings of `flight` and `jdbc`) and `trino-timings.txt`;
- the B and C tables with PASS/FAIL and, for failures, the error text and the query id;
- for any failure: `fe.log` / `be.INFO` / `be.WARNING` excerpts around it and the server log of the node(s).

| Section | Result | Notes |
|---|---|---|
| A: TPC-H SF10 vs reference (44) | | |
| A: TPC-H SF10 vs JDBC (44) | | |
| A: sr-cases SF10 (26) | | |
| A: timings flight / jdbc / trino (total s) | | |
| B1–B7 cluster kill tests | | |
| C1–C5 auth, TLS, profile, logs | | |

If all pass, the next session publishes `v4.1.4-flight.1` once you say so (STATUS.md Next steps).
