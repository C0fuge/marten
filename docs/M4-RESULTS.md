# M4 results (CI)

Full per-item output of every run: branch `m4-results` (`runs/<run>.md`, `latest.md`), artifact `m4-<run>` (with
all logs, 7 days). This file keeps the summary per run. Workflow and checks: `docs/M4-CI.md` §4, §7.

## 2026-10-21, run 39658484728 — series `4a9848e-fl80f999` (first run), checks 1–5

| # | Result | Failures |
|---|---|---|
| 1 | 13/15 | `c_ubigint` shown as DECIMAL(20,0) (harness expected LARGEINT; the server itself reports decimal128(20,0)) |
| 2 | 37/49 | UInt64 values wrapped negative; pre-1970 timestamps with a fraction garbage (`Y222-05-09 N5:25:11…`, BE converter); harness: float32, UUID, non-ASCII JSON normalisation |
| 3 | 19/21 | 2.3 in result mode partial: server rejects `CAST(sum(..)) AS alias` (Binder Error); 2.5 harness rounding |
| 4 | 32/44 | q06/q15/q18/q20 same `CAST(sum)` error; q22 `substring(x FROM a FOR b)` not StarRocks syntax (harness rewrite); q01 harness rounding |
| 5 | 22/26 | same `CAST(sum)` error (3); harness rounding (1) |
| log masking | PASS | |

Fixes: 0004 renders `sum(CAST(x AS T))` (integer sums only in result mode complete), 0003 floors Arrow timestamps
(upstream converter), harness normalisation. New series `4a9848e-fla2cd40` (FE 39660196425 with the 7 Flight test
classes, BE 39660201177, be-ut 39660205090 19/19).

## 2026-10-21, run 39661743301 — series `4a9848e-fla2cd40`, checks 1–9

| # | Check | Result |
|---|---|---|
| 1 | catalog, SHOW, DESC, masking | 13/15: only the `c_ubigint` type expectation (harness now accepts DECIMAL(20,0)) |
| 2 | types tables, every column | 45/49: UInt64 values wrapped (open), `c_ts_ns` −1 ns: BE floors to …59.999999, DuckDB's Python conversion truncates (harness now floors) |
| 3 | M4-TESTS §1–2, both result modes, session switches, catalog switch | **PASS 21/21** |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | **PASS 44/44** (0.4–3.1 s per query on the shared runner) |
| 5 | sr-cases (26) on SF1 | **PASS 26/26** |
| 6 | failover | aborted: cluster servers were started one after another, each waits 60 s for the other (harness fixed) |
| 7 | KILL QUERY | **PASS**: query ended within 2 s of KILL, server log shows `backpressure=cancelled` |
| 8 | token / basic / TLS | **PASS 10/10** (right/wrong/missing token, basic user:token, password masked, TLS trusted / wrong host / untrusted / verify=false / plain vs TLS) |
| 9 | memory limit | **PASS 3/3**: clean memory-limit error, BE alive, next query works |
| log masking | dummy catalog token and server token in no log | **PASS** |

## 2026-10-21, run 39663221891 — series `4a9848e-fla2cd40`, checks 1, 2, 6

1 **PASS 15/15**; 6 **PASS 4/4** (servers now started together); 2: 47/49, UInt64 still wrapped. Diagnosis (ADBC
straight to the server): GetTables and result mode `complete` give `decimal128(20,0)` with correct values, result
mode `partial` streams `uint64` → the BE converter wrapped values ≥ 2^63. Fix in 0003: UInt64 arrays are widened
to decimal128(20,0) for DECIMAL slots (+ be-ut case). New series `4a9848e-fl598360` (FE 39664615702 forced,
BE 39664594320, be-ut 39664598409 20/20).

## 2026-10-21, run 39665941130 — series `4a9848e-fl598360`, checks 1–9: **all PASS**

| # | Check | Result |
|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS 15/15 |
| 2 | types tables, every column (49 columns, 5000 rows each) | PASS 49/49 (hidden as designed: TIME, INTERVAL) |
| 3 | M4-TESTS §1–2, result modes partial + complete, session and catalog switches | PASS 21/21 |
| 4 | TPC-H SF1 q01–q22, `cbo_push_down_topn_limit` default and 0 | PASS 44/44 (45 s in total) |
| 5 | sr-cases (26) | PASS 26/26 |
| 6 | failover, 2-server cluster: before / during a read | PASS 4/4 (stop before: 11.5 s via backups; kill 1.5 s into a 2.7 s read: correct result) |
| 7 | KILL QUERY | PASS (ends < 2 s, server stream cancelled) |
| 8 | token / basic / TLS | PASS 10/10 |
| 9 | memory limit | PASS 3/3 |
| log masking | tokens in fe.log / be.INFO / be.WARNING / container logs | PASS |

## 2026-10-21, run 39670612956 — series `4a9848e-fl598360`, checks 1, 3, 4 with `ref_catalog=flight_c`

Harness test for the local final check (`m4.py --ref-catalog`): 1 PASS 15/15, 3 PASS 21/21, 4 **PASS 88/88**
(44 against `reference/sf1`, 44 against the same query on catalog `flight_c`, result mode complete).

## 2026-10-21, run 39688089343 — series `4a9848e-fl598360`, checks 1, 6, 8 (hardened harness)

| # | Check | Result |
|---|---|---|
| 1 | + exact `DESC` vs the PLAN §2.2 mapping of the server's GetTables schema (all 10 tables) | PASS 25/25 (hidden as designed: `c_time` time64[us], `c_interval` month_day_nano_interval) |
| 6 | "during" now reads lineitem 3x (5.5 s), flight2 SIGKILLed at 35% (2.2 s in) | PASS 6/6: query ended 3.4 s after the kill with correct rows, **FailoverCount=3** in its profile (endpoints of flight2 failed over to flight1 before delivering data) |
| 8 | + token / password not in the query profiles of a token and a basic-auth scan | PASS 14/14 |
| log masking | | PASS |

## 2026-10-21, run 39695113106 — series `4a9848e-fl598360`, server **int2**, checks 1–9

All 9 checks **PASS** (25/25, 49/49, 21/21, 44/44, 26/26, 6/6, 2/2, 14/14, 3/3; log masking PASS) against
`arrow-flight-server-1.0.0-int2.jar` (the new `m4.yml` default). int2 streams `c_ubigint` as decimal128(20,0) in
partial mode too (server finding (b) fixed; the connector's UInt64 widening is now unused with int2 but kept for
older servers). TPC-H timings 0.3–3.2 s per query, as with int1. Run 39696030255 (checks 1,2, server int1):
PASS 25/25, 49/49 — int1 still streams `uint64` in partial mode and the connector still widens it, so int1 stays
supported and runnable (`m4 … server=arrow-flight-server-1.0.0-int1.jar`).

## 2026-10-22, local final check (maintainer's stand) — series `4a9848e-fl598360`, **FAILED (2 connector items, 3 server items)**

Build: draft `v4.1.4-flight.0-dryrun` downloaded, `sha256sum -c SHA256SUMS` OK, both build-info files
`commit_hash=4a9848e-fl598360`; allin1 overlay per INSTALL §2a (podman, `FROM docker.io/starrocks/allin1-ubuntu:latest`
= stock BE `4.1.4-4a9848e`); overlay BE `--version` and `current_version()` = `4.1.4-4a9848e-fl598360`.
Host: 16 cores, 30 GB, load 9–20 during the whole check (other agents' builds); StarRocks container 9 GB, never
together with Trino. Agent notes with every command: `bench/tools/agent-sr-final/NOTES.md` on the stand.

Deviations from `LOCAL-FINAL-CHECK.md`:
- Server build = the stand's production-like `arrow-flight-server-1.0.0-s3p4.jar` (not int2/int4). s3p4 has token
  auth (`FLIGHT_AUTH_TOKEN`) but **no server TLS** → C3 not applicable; s3p4 endpoints carry **one location each** (no
  backup locations; checked with a Flight SQL probe sending `x-flight-result-mode: partial` and
  `x-flight-location-failover: 1`).
- Section A ran on the stand's own single HDFS server (`grpc://dn:32010`, open mode, as the stand runs it) with
  catalogs `flight` and `jdbc` (the `sr.sh` bridge statement, catalog name `jdbc`); `cbo_push_down_topn_limit` not
  set globally. Sections B/C ran on a 3-node HDFS cluster (`c3-dn1..3`, one Flight server in the netns of each
  DataNode, HDFS replication 2, SF10 + types, Hazelcast cluster `--hosts c3-dn1,c3-dn2,c3-dn3`, token on) with
  catalog `fc3` (= `flight` of the checklist) and `jdbc3`; fs1..fs3 = `c3-flight1..3` (kill = `podman kill -s KILL`
  of the server JVM; the DataNode keeps the IP, so connects are refused).
- The stand's `be.conf` has `mem_limit = 4G`. With it 5 queries fail on memory (see A); A was re-run with
  `mem_limit = 6G` (still < 9 GB with FE ~1.4 GB) and the remaining 3 with `enable_spill = true`.
- `bench/reference/sf10` has **the same layout** as `tests/m4/reference/sf1` (`qNN.tsv` + `qNN.cols`
  `name<TAB>DuckDB type<TAB>key`, `MANIFEST.tsv`, `queries.tsv`); `load_ref` needs no change. Queries
  `bench/queries/tpch` = `tests/m4/queries` byte for byte.

| Section | Result | Notes |
|---|---|---|
| A: TPC-H SF10 vs reference (44) | **FAIL at the stand config, PASS with more memory** | BE 4G: 32/44 (q05/q08/q09/q18/q21 topn default, q05/q08/q09 topn 0 memory limit; q18 topn 0 + q20–q22 topn 0 server crash, see A-2). BE 6G: 38/44 (q05/q08/q09 both topn: memory limit). q05/q08/q09 with `enable_spill`: 6/6. All results that were produced are correct. |
| A: TPC-H SF10 vs JDBC (44) | same | every produced native result equals JDBC (38 at 6G + 6 with spill) |
| A: sr-cases SF10 (26) | PASS 26/26 (6G run) | 11/26 in the first run only because the server's DuckDB was invalidated (A-2) |
| A: timings flight / jdbc / trino (total s) | **165.9 / 497.5 / 180.1 cold, 146.7 2nd** | table below |
| A (extra): 3-node token cluster, checks 4,5, spill on | 43/44, 26/26 | q18 topn default: `keepalive watchdog timeout` (A-3), 3 re-runs OK |
| B1–B7 cluster kill tests | **FAIL: B2, B5** | B1 B3 B4×3 B6 B7 PASS; B5 = silent wrong result (server); B2 = no backup locations in s3p4 |
| C1–C5 auth, TLS, profile, logs | PASS (C3 n/a) | + basic auth user/password=token, optional 100 MB memory limit PASS |

### A. TPC-H SF10 (`m4.py --checks 4,5 --existing-catalog --catalog flight --reference bench/reference/sf10 --ref-catalog jdbc --sr-cases-ref tests/m4/sr-cases/sr-cases.ref`)

**A-1 (connector, FE): Flight scans have no statistics.** `EXPLAIN COSTS` of q05 on `flight` (after the tables had
been scanned many times): every `FlightScanNode` shows `cardinality: -1`, `stats source: NONE`, `avgRowSize=0.0`,
column statistics `[-Infinity, Infinity, 0.0, 1.0, 1.0] UNKNOWN`; the CBO therefore uses
`default_statistics_output_row_count` (= 1) for every table, estimates `orders ⋈ customer` = 1 row and builds a
PARTITIONED hash join with **lineitem as the build side** (`10:HASH JOIN … |----9:EXCHANGE` = lineitem). The JDBC
catalog on the same server gets `stats source: TABLE_METADATA` (lineitem 59986052 …), broadcast joins and lineitem
as probe. No FE warning `row count of … failed` / `Failed to get Flight table statistics` in `fe.log`, so
`FlightMetadata.getTableStatistics` (0002) / `computeFlightScanNode` (0004) do not reach the optimizer (or the
async row-count cache never completes). Effect at SF10:

```
q05/q08/q09/q18/q21 (BE mem_limit 4G): ProgrammingError: (1064, 'Memory of default_wg exceed limit. Pipeline Backend: 127.0.0.1, fragment: … Used: 3479789216, Limit: 3478923509. Mem usage has exceed the limit of query pool: BE:10001')
q05/q08/q09 (BE mem_limit 6G):        ProgrammingError: (1064, 'Memory of query_pool exceed limit. try consume:67108864 Backend: 127.0.0.1, Used: 5159636288, Limit: 5218385264. …')
```

JDBC at 4G: q05 OK (34.8 s); q18 also fails on JDBC at 4G. Reproduce: allin1 overlay with BE `mem_limit = 4G`,
catalog `flight` on an SF10 server, `SET CATALOG flight; USE tpch; EXPLAIN COSTS <q05>` → `cardinality: -1`;
run q05 → memory error. With `SET enable_spill = true` q05/q08/q09 pass (11.7–20.6 s).

**A-2 (server s3p4, not the connector):** during q18 (topn 0) the server's DuckDB failed fatally and stayed invalid
until restart: `qid=63f6fa48-du executionPath=duckdb-aggregation … INTERNAL Error: Attempted to dereference
unique_ptr that is NULL!`, then every DuckDB query: `FATAL Error: Failed: database has been invalidated because of a
previous fatal error`. Pushed SQL at that moment: `SELECT "l_orderkey", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS
"__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_orderkey" IS NOT NULL) GROUP BY "l_orderkey"` (15 M groups,
`duckDbMemoryLimit=1GB`) concurrently with plain scans of lineitem/orders/customer for the same query. Not
reproduced alone (3× OK, 8 s) nor with KILL QUERY at 2/4/6 s, nor in the second full run. The connector reported it
cleanly (`Flight endpoint 0 at grpc+tcp://dn:32010: IOError: Flight returned internal error …`).

**A-3 (connector, BE, intermittent):** on the 3-node cluster at host load ~20: q18 `Flight endpoint 0 at
grpc+tcp://c3-dn2:32010: IOError: Flight returned unavailable error, with message: keepalive watchdog timeout …
"grpc_status":14`. Memory was fine; 3 immediate re-runs passed. The keepalive (`grpc.keepalive_time_ms` 10 s,
`grpc.keepalive_timeout_ms` 5 s, 0003) kills a healthy but slow stream when the server (or host) does not answer a
ping within 5 s.

Timings (SF10, single HDFS server `dn`, topn default; native and JDBC from the BE-6G run, native q05/q08/q09 and
their JDBC times from the spill run; Trino 455 + plugin v10 via TpchBench, heap 6 GB, q21 with heap 8 GB because
6 GB fails `Query exceeded per-node memory limit of 4GB`; last column: native on the 3-node token cluster, spill on):

| q | native (s) | JDBC (s) | Trino v10 cold / 2nd (s) | native 3-node (s) |
|---|---|---|---|---|
| q01 | 14.30 | 117.29 | 10.06 / 5.45 | 7.66 |
| q02 | 2.45 | 3.86 | 6.27 / 3.21 | 1.55 |
| q03 | 10.79 | 38.96 | 10.34 / 6.75 | 5.82 |
| q04 | 6.99 | 42.67 | 7.99 / 6.07 | 3.78 |
| q05 | 14.25 | 34.81 | 13.47 / 10.61 | 7.98 |
| q06 | 4.56 | 2.98 | 3.68 / 4.69 | 2.22 |
| q07 | 8.97 | 20.87 | 9.29 / 6.52 | 5.80 |
| q08 | 13.12 | 35.27 | 6.08 / 5.02 | 25.49 |
| q09 | 20.64 | 55.61 | 9.43 / 7.37 | 32.23 |
| q10 | 8.23 | 9.77 | 6.15 / 6.32 | 6.74 |
| q11 | 1.43 | 3.60 | 1.68 / 1.47 | 1.27 |
| q12 | 4.67 | 4.81 | 6.35 / 4.39 | 5.50 |
| q13 | 8.43 | 7.19 | 5.53 / 5.14 | 4.04 |
| q14 | 3.50 | 3.76 | 3.58 / 4.04 | 1.68 |
| q15 | 3.73 | 3.83 | 4.08 / 2.18 | 1.74 |
| q16 | 1.29 | 1.51 | 3.14 / 1.75 | 1.02 |
| q17 | 8.04 | 27.02 | 7.17 / 6.68 | 7.19 |
| q18 | 8.40 | 19.61 | 14.14 / 10.97 | fail (A-3) |
| q19 | 6.47 | 5.22 | 7.10 / 7.80 | 3.59 |
| q20 | 6.71 | 9.22 | 7.07 / 5.16 | 3.17 |
| q21 | 7.46 | 48.11 | 35.32 / 33.89 | 19.81 |
| q22 | 1.47 | 1.50 | 2.15 / 1.20 | 2.60 |
| **total** | **165.9** | **497.5** | **180.1 / 146.7** | 150.9 (21 q) |

topn 0 totals: native 148.5 s, JDBC 487.9 s. `count(*)` of lineitem: native 0.21 s (pushdown), JDBC 33.4 s. Native
is 3× faster than the JDBC bridge overall (up to 8× on lineitem-heavy q01/q04/q21) and on par with Trino cold; the
slow native queries (q08/q09 on the cluster, q05/q09 single node) are the A-1 plans.

### B. 3-node cluster kill tests (`fc3`, `SET flight_aggregate_pushdown = false`; reference = DuckDB over the SF10 parquet = `jdbc3` = `(59986052, 1529738036.00, 1589702202)`; T = 6.3–9.7 s)

| # | Result | Detail |
|---|---|---|
| B1 | PASS | 6.28 s, equals the reference (3 endpoints) |
| B2 | **FAIL** | `podman stop c3-flight3`, scan right after: fails in 0.25 s `Flight endpoint 0 at grpc+tcp://c3-dn3:32010: IOError: Flight returned unavailable error, with message: failed to connect to all addresses …`; the next scan 13 s later is correct (12.3 s). s3p4 gives each endpoint a single location, so there is no backup to fail over to until Hazelcast drops the member. Trino plugin v10 on the same cluster: error too (`io exception (cause: ConnectException: Connection refused)`, also 6 s later). Connector behaviour is consistent with its rule; the checklist expectation needs a server with backup locations (int1+). |
| B3 | PASS | fs3 back (Members size 3): correct, 13.1 s |
| B4 | PASS ×3 | kill -9 fs2 at T/3 (2.4–2.5 s): clean error each time, e.g. `Flight endpoint 1 at grpc+tcp://c3-dn2:32010: IOError: Flight returned unavailable error, with message: Socket closed …`, `FailoverCount=0` (streams were delivering). Trino v10: error ×3 (`Network closed for unknown reason` / `Connection refused`). Never a different result. |
| B5 | **FAIL (server)** | kill -9 fs2 + fs3: the scan **succeeds with a wrong result** `(30126212, 768224684.00, 798410615)` in 8.0 s, again on the next scan. Flight SQL probe on fs1: right after the kill 1 endpoint `records=59986052` (correct); ~15 s later (fs1 log: `Removing Member [c3-dn2]`, `Removing Member [c3-dn3]`, `Promotion commit failed for 47 migrations`, `Members {size:1}`) 1 endpoint at c3-dn1 `records=30126212` delivering 30126212 rows. The s3p4 cluster file registry loses the files of two simultaneously lost members and the survivor plans a partial table silently. Trino v10: correct right after the kill, **same wrong result** 10 s later, and still wrong ~5 s after fs2+fs3 were restarted (Members 3); correct again ~10 s later. Server bug, not the connector. |
| B6 | PASS | KILL QUERY at T/2: query ended 0.02 s later (`killed manually`), fs2 log `backpressure=cancelled`, next query nation = 25 |
| B7 | PASS | `SHOW BACKENDS` Alive = true, nation = 25 |

Side finding (Trino plugin, not this repo): with token auth on the s3p4 cluster, plugin v10 and v9 fail every query
with `Error reading from Arrow Flight: Invalid Flight endpoint ticket` (the native connector and a Bearer probe work);
the Trino comparison above was therefore run with the cluster in open mode.

### C. Auth, TLS, profile, logs (`fc3`, token cluster)

| # | Result | Detail |
|---|---|---|
| C1 | PASS | nation = 25 |
| C2 | PASS | wrong token and no token: `Flight GetDbSchemas failed: UNAUTHENTICATED: Missing or wrong access token`; neither the real nor the wrong token in the text; `SHOW CREATE CATALOG` shows `"flight.token" = "******"`. Basic auth (`flight.user`/`flight.password` = token) works, password masked |
| C3 | n/a | s3p4 has no server TLS (CI check 8 covers TLS) |
| C4 | PASS | `enable_profile`: profiles of a token scan (25 k chars) and a basic-auth scan, `ANALYZE PROFILE`: no token |
| C5 | PASS | `grep -rlF $TOKEN fe/log be/log` + container log + all outputs: only `fe.audit.log` line of `CREATE EXTERNAL CATALOG jdbc3` (stock JDBC catalog, token inside `jdbc_uri` written by the tester); every flight catalog statement in the audit log is masked (`"flight.token" = ***`, `"flight.password" = ***`) |
| opt. | PASS | `query_mem_limit = 104857600` GROUP BY over lineitem: `Memory of Query… exceed limit … single query`, BE alive, next query OK |

## 2026-10-22, run 39730011530 — server candidate int4 (DuckDB 1.4.5, S3 plugin), series `4a9848e-fl598360`, checks 1–9

All PASS: 1 25/25, 2 49/49, 3 21/21, 4 44/44, 5 26/26, 6 6/6, 7 2/2, 8 14/14, 9 3/3. Setup: v1.4.5 httpfs (file name
must stay `httpfs.duckdb_extension`: DuckDB derives the entry point from it — run 39729516833 failed with
`did not contain the expected entrypoint function`), `-Darrowflight.plugins.dir=/srv/int4/plugins`.

## 2026-10-22, connector fixes for the local final check

- **A-1 root cause:** `MetadataMgr` calls `ConnectorMetadata.clear()` on the query-level metadata at the end of
  every query (`removeQueryMetadata` / cache eviction); `FlightMetadata` is the catalog's only metadata object and
  its `clear()` invalidated the row-count (and schema) caches, so every plan started cold and used
  `default_statistics_output_row_count` = 1 for every Flight table. No warning, because nothing failed. Fixed in
  0002 (`clear()` keeps the caches; the row count is started on `getTable` and the first caller of a cold load waits ≤ 250 ms, later callers never wait — a 1 s wait on every call failed m4 run 39732232288 check 6 with `planner use long time 3005 ms in memo phase`).
  `cardinality: -1` / `stats source: NONE` in EXPLAIN COSTS was a separate display gap: `PlanFragmentBuilder` did
  not call `computeStatistics` for the FlightScanNode (0004). Plan tests in 0006; m4 check 4 now asserts real row
  counts for the 6 Flight scans of q05 after a query.
- **Keepalive:** `grpc.keepalive_timeout_ms` = max(20 s, `flight.keepalive_ms`) instead of 5 s (0003).

## 2026-10-22, run 39828677269 — series `4a9848e-fl9ec2c3` (P1 converted types), server int4, checks 1–9

All PASS: 1 25/25, 2 52/52, 3 21/21, 4 45/45, 5 26/26, 6 6/6, 7 2/2, 8 14/14, 9 3/3. `c_time` (time64[us]) and
`c_interval` (month_day_nano) are now exposed as VARCHAR (`flight.converted_types=convert`, default); check 2
compares them with the server's own Arrow values (ADBC) formatted as the BE does: 0/5000 differ each. No hidden
columns left in the types tables.

## 2026-10-22, runs 39840237517 / 39841545485 / 39845020831 — P2 column min/max statistics, server int4

- 39840237517 (series `4a9848e-fl664138`, checks 1–9): all PASS except check 6 item "flight2 stopped before the
  query" (GetFlightInfo TIMED_OUT twice, 14.8 s); reproduced alone by 39841545485 (check 6, 15.2 s) → a P2
  regression, not a flake. Cause: a metadata stream read from ANOTHER server's endpoint (the new background
  `SELECT min(c), max(c) …` in partial mode streams from flight2 too) that failed was treated by `withFailover` as a
  failure of the catalog's own connection, which was then moved to the stopped flight2. Fix (0002): such a failure
  is a plain connector error (statistics stay unknown); the connection stays.
- 39845020831 (series `4a9848e-fl67776b`, checks 1–9): **all PASS**: 1 25/25, 2 52/52, 3 21/21, 4 46/46, 5 26/26,
  6 6/6 (flight2 stopped: 11.6 s, as before P2), 7 2/2, 8 14/14, 9 3/3. New item in check 4: q05's orders scan is
  estimated at 227651 rows from the o_orderdate min/max (one year of 1992-01-01..1998-08-02; without column
  statistics the default selectivities give 94K or 375K). Scan estimates (notes): q05 region 5, nation 25,
  supplier 10000, customer 150000, lineitem 6001215, orders 227651; q08 orders 455301, part 200000; q09 part 50000,
  partsupp 800000, orders 1500000, lineitem 6001215. The plan outlines of q05/q08/q09 are in the run's notes
  (`git show origin/m4-results:runs/39845020831.md`); CI has no JDBC catalog to compare join orders with.

## 2026-10-22, local re-check (maintainer's stand) — series `4a9848e-fl6b6a1d`, server int4 (fixed): **A-1 and A-3 fixed; q18 at BE 4G still fails on memory (A-4)**

Build: draft `v4.1.4-flight.0-dryrun` (refreshed for this series) downloaded, `sha256sum -c SHA256SUMS` OK, `fe-build-info.txt`
and `be-build-info.txt` both `commit_hash=4a9848e-fl6b6a1d` (FE run 39733048078, BE run 39733050937); allin1 overlay as before;
`current_version()` and BE `--version` = `4.1.4-4a9848e-fl6b6a1d`. Server: release candidate **int4, rebuilt with the cluster
fix** (member loss / ticket secret; jar md5 `ff3d6a72…`, the build expected as `int4b` in `m4-assets`), DuckDB 1.4.5 with
the v1.4.5 hadoopfs extension. Single HDFS server on the stand node `dn` (open mode, as the stand runs it) for A; 3-node HDFS
cluster `c3-dn1..3` with token auth for the cluster items. BE `mem_limit = 4G` (stand `be.conf`) throughout. Host load
4–7 during A, 18–50 during the load runs. Agent notes: `bench/tools/agent-sr-final/NOTES.md` ("re-check" section) on the stand.

| Item | Result | Notes |
|---|---|---|
| A-1: `EXPLAIN COSTS <q05>` | **PASS** | every FlightScanNode `stats source: TABLE_METADATA`; lineitem `ENDPOINTS: 1, records=59986052`, `cardinality: 53987447` (row count × 0.9 for the pushed `l_orderkey IS NOT NULL`), orders 3750000, customer 1350000, supplier 81000, nation 23, region 5; identical in the first and the second EXPLAIN after the catalog was created. lineitem is the **probe** side (`5:HASH JOIN` PARTITIONED, build = orders), supplier/nation/region broadcast. m4 item `q05 EXPLAIN COSTS: row counts of all 6 Flight scans` PASS |
| A: q05/q08/q09/q21 at BE 4G | **PASS** (both topn) | no spill; were memory failures in the first run |
| A: q18 at BE 4G | **FAIL (A-4)** | both topn: `Memory of query_pool exceed limit. try consume:83886080 Backend: 127.0.0.1, Used: 3096408392, Limit: 3478923509`. JDBC q18 at 4G passes (18.5 s). Native passes with `enable_spill = true` (13.9 s) or `pipeline_dop = 4` (12.0 s) |
| A: TPC-H SF10 22/22 vs reference + JDBC (single node, 4G) | 85/87 | `m4.py --checks 4,5 --existing-catalog --catalog flight --reference bench/reference/sf10 --ref-catalog jdbc …`: all 42 results produced equal the reference and JDBC; only the 2 q18 items fail. Check 5 sr-cases 26/26 |
| A-2: server DuckDB fatal in a pushed q18 aggregation | not seen | int4 (DuckDB 1.4.5); the stand's int4 check ran 70 stress rounds of the pushed q18/q04 aggregation without a fault (s3p4 with DuckDB 1.4.1 reproduced it as a SIGSEGV in `TupleDataCollection::Combine`) |
| A-3: q18 on the 3-node cluster under load (keepalive) | **PASS** | checks 4,5 on `fc3` (spill on, as in the first run): 45/45 + 26/26, q18 8.7 s both topn; q18 ×8 sequential at host load 36–47: 8/8 identical results, 11.6–15.4 s; q18 with one server frozen (`podman pause`) for 12 s mid-stream: 3/3 OK (23.9–37.2 s). Control: a 40 s freeze ends cleanly after ~36 s with `Flight endpoint 1 at grpc+tcp://c3-dn2:32010: IOError: … keepalive watchdog timeout` (10 s ping + 20 s timeout), next query OK. No `keepalive` line in `be.WARNING`/`be.INFO` in the load runs |
| B2 / B5 against int4 | **PASS** (by reference) | run on the stand by the server check (not redone here): B2 — `SIGTERM` of one of 3 servers: the next plan already drops it (member left), each endpoint carries 2 locations, Trino and a location probe correct right after and +6 s (the unfixed int4 also passed via its backup locations). B5 — `kill -9` of 2 of 3: 18/18 plans on the survivor correct (1 endpoint, 59986052 rows) at +1/+15/+30 s over 6 fresh clusters, plus Trino correct before / right after / +15 s, complete mode OK, after restart all nodes accept each other's tickets (9/9). Root cause of the first run's silent half table was in the server (Hazelcast maps with one backup lost the inventories of 2 simultaneously lost members); fixed in the rebuilt int4 |
| Token leak grep (srf fe/be logs, container log, outputs) | PASS | no hits |

Side observation: 2 parallel q18 sessions + a q21/q09 loop on the 4G BE fail with `Memory of process exceed limit` (3.87 GB) even
with spill — capacity, no keepalive error.

**A-4 (connector/BE memory footprint, q18 SF10 at 4G):** the plans of `flight` and `jdbc` now have the same shape and real
counts, but the native query peaks at 3.16 GB per node (pushdown on; 3.24 GB with `flight_aggregate_pushdown = false`) vs
1.84 GB for JDBC. Profile (pushdown on, query 01a16506-1293-77c8-a2d5-7d34c2cf367c): merge-finalize aggregation of the pushed
`l_orderkey` groups `HashTableMemoryUsage` 1.22 GB, `LOCAL_EXCHANGE_SINK` behind the lineitem scan (plan node 0)
`LocalExchangePeakMemoryUsage` 979 MB and behind the orders scan (node 2) 396 MB, all at the same time. JDBC has the same two
big consumers (aggregation 1.31 GB, lineitem local exchange 983 MB), orders is the local probe of its semi join (0.1 MB), and its
slow scans never overlap the peaks. The Flight scan delivers 59 M lineitem rows in ~6 s (`FlightReadTime` 4.0 s) and they pile
up in the local exchange while the join build sides are still being built. In the first run JDBC q18 also failed at 4G (under
load 11–16), so the stand's 4G is borderline for q18 at SF10 for both paths.

Timings, topn default, single node (1-node) and the 3-node token cluster (spill on), in s; first run in parentheses (its
single-node native values come from the BE 6G run, q05/q08/q09 from the spill rerun):

| q | native 1-node now (first run) | JDBC now (first run) | native 3-node now (first run) |
|---|---|---|---|
| q01 | 12.64 (14.30) | 105.38 (117.29) | 8.86 (7.66) |
| q02 | 2.09 (2.45) | 4.49 (3.86) | 1.67 (1.55) |
| q03 | 7.64 (10.79) | 37.91 (38.96) | 4.64 (5.82) |
| q04 | 4.48 (6.99) | 36.51 (42.67) | 2.23 (3.78) |
| q05 | 7.83 (14.25) | 33.11 (34.81) | 3.47 (7.98) |
| q06 | 3.12 (4.56) | 1.65 (2.98) | 1.02 (2.22) |
| q07 | 7.92 (8.97) | 19.72 (20.87) | 3.39 (5.80) |
| q08 | 10.85 (13.12) | 34.30 (35.27) | 4.69 (25.49) |
| q09 | 14.84 (20.64) | 53.72 (55.61) | 5.80 (32.23) |
| q10 | 8.35 (8.23) | 9.33 (9.77) | 4.06 (6.74) |
| q11 | 1.26 (1.43) | 3.51 (3.60) | 1.13 (1.27) |
| q12 | 3.13 (4.67) | 4.06 (4.81) | 2.63 (5.50) |
| q13 | 6.90 (8.43) | 6.81 (7.19) | 3.37 (4.04) |
| q14 | 4.68 (3.50) | 3.49 (3.76) | 3.39 (1.68) |
| q15 | 2.74 (3.73) | 2.82 (3.83) | 2.87 (1.74) |
| q16 | 1.00 (1.29) | 1.53 (1.51) | 1.45 (1.02) |
| q17 | 6.58 (8.04) | 27.65 (27.02) | 2.70 (7.19) |
| q18 | fail 4G (13.87 spill) (8.40) | 18.52 (19.61) | 8.74 (fail A-3) |
| q19 | 5.42 (6.47) | 4.46 (5.22) | 1.57 (3.59) |
| q20 | 5.20 (6.71) | 8.24 (9.22) | 2.39 (3.17) |
| q21 | 6.13 (7.46) | 42.47 (48.11) | 6.08 (19.81) |
| q22 | 1.16 (1.47) | 1.30 (1.50) | 1.06 (2.60) |
| **total 21 q (w/o q18)** | **124.0** (157.5) | **442.5** (477.9) | **68.5** (150.9) |

topn 0 totals (21 q without q18): native 116.2 s, JDBC 434.9 s; 3-node 22 q with q18: 77.2 s default / 81.2 s topn 0.

## 2026-10-22, CI: A-4 exchange cap — series `4a9848e-fld145f6`, m4 run 39873438298

Checks 1–9 all PASS against int4 (25/25, 52/52, 21/21, 46/46, 26/26, 6/6, 2/2, 14/14, 6/6). New check 9 items: q18 SF1
returns the same 57 rows with `flight.exchange_buffer_mb` 16 (default) and 0; `LocalExchangePeakMemoryUsage` 2.5 MB vs
2.7 MB, `QueryPeakMemoryUsagePerNode` 191.7 MB vs 188.6 MB (2 vCPUs). At SF1 the cap does not bind; the SF10 q18 effect
at BE 4G is for the stand (STATUS Next steps 1, draft `v4.1.4-flight.0-a4`).

## 2026-10-23, CI: lakeFS variant (P3) — series `4a9848e-fld145f6`, m4 run 39875156594

Server int4 with the lakefs plugin on `lakefs://m4lake/main/parquet` (lakeFS 1.38.0, local KV, MinIO blockstore): checks
1 (25/25), 3 (21/21), 4 (46/46) and the new check 10 (5/5) PASS. Check 10: `lfs.t` = (1 row) at the setup commit; a
staged, uncommitted file is not visible; a commit adding 2 files (6 rows) is seen 1.1 s later and no query saw only one
of the two files; a commit deleting a file is seen 1.1 s later; tpch lineitem 6001215 rows afterwards. First attempt
39874644488 failed in setup (repository name `m4` too short for lakeFS). Default S3 path re-checked after the
`stack.sh` change: run 39875877653, checks 1 and 6 PASS.

## 2026-10-23, CI: Iceberg variant (P5) — series `4a9848e-fld145f6`, server int6, m4 run 39882258299

Server int6 (int5 + refresh-recursion fix + hive plugin) with `-Dcatalog=iceberg-rest` against an Iceberg REST catalog
(`apache/iceberg-rest-fixture:1.9.2`, warehouse `s3://lake/parquet/_iceberg` on MinIO), DuckDB iceberg + avro v1.4.5
extensions: checks 1 (25/25) and the new check 11 (22/22) PASS. Schema `ice` appears next to `tpch`/`types`.
`ice.lineitem` / `ice.orders` (written by pyiceberg 0.10.0 in several appends) have the same DESC and aggregates as the
parquet tables, q01/q04/q12 equal the SF1 reference, in partial and complete mode. `ice.del` (Spark 3.5.6 + Iceberg
1.9.2, merge-on-read: 2 position delete files, 100 deletes) returns 900 rows in both modes. `ice.ren` (column renamed
between two appends) reads both files by field id, filter on the new name works. An append to `ice.t` was seen by
partial mode 5.4 s later (snapshot pinned per query; only before/after states seen) and by complete mode after 24.9 s
(view refresh, ≤ 60 s). Finding (server, minor): the dataDir listing also shows the warehouse directory as schema
`_iceberg` (table `ice`). Not covered: equality deletes (Spark cannot write them), Hive Metastore (int6 `catalog=hive`).
First attempt 39881458465: 19/20, the REST fixture's default in-memory SQLite is one database per JDBC connection, so
the check's own commit failed in the catalog (fixture now uses a SQLite file). Runs 39879641829 (int6, checks 1+3 on
the plain S3 store: PASS) and 39880765661 (int5, check 1: PASS) also printed the int6/int5 START-NOTES.
