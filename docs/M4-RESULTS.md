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

## 2026-10-23, CI: server int4b as the m4 default — series `4a9848e-fld145f6`, m4 run 39883591960

int4b (int4 rebuilt with the cluster fixes for B5 member loss and the ticket secret; plugins of int4): checks 1 (25/25),
6 failover (6/6, FailoverCount 3 after the kill during the read) and 8 token/TLS (14/14) PASS. int4b is the m4 default.

## 2026-10-23, local A-4 re-check (maintainer's stand) — series `4a9848e-fld145f6`, server int4 (fixed): **A-4 fixed by the exchange cap; q18 at 4G passes, but peaks at up to 3.05 GB (pre-aggregation above the pushed aggregation)**

Build: draft `v4.1.4-flight.0-a4` downloaded, `sha256sum -c SHA256SUMS` OK, `fe-build-info.txt` and `be-build-info.txt` both
`commit_hash=4a9848e-fld145f6` (FE run 39847449823, BE run 39847433502), `starrocks_be` sha256 `29897679…` = be-build-info;
allin1 overlay as before; `current_version()` and `SHOW BACKENDS` Version = `4.1.4-4a9848e-fld145f6`. Server int4 (fixed, jar md5
`ff3d6a72…`, DuckDB 1.4.5): single HDFS server on `dn` (open mode) and the 3-node HDFS cluster `c3-dn1..3` (token auth).
BE `mem_limit = 4G` (stand `be.conf`, MemLimit 3.6 GB), **no spill anywhere**. Host load 5–7. Catalogs `flight` (default cap,
16 MB per driver) and `flight0` (`"flight.exchange_buffer_mb" = "0"`, cap off); the same pair `fc3` / `fc30` on the cluster.
Agent notes: `bench/tools/agent-sr-final/NOTES.md` ("A-4 re-check").

q18 SF10 at BE 4G (`QueryPeakMemoryUsagePerNode`; `LocalExchangePeakMemoryUsage` of the two big exchanges behind the lineitem / orders scans):

| Catalog | Runs | Result | Peak per node | LocalExchangePeak (lineitem, orders) |
|---|---|---|---|---|
| `flight` (cap 16 MB), single node | 14 (7 per topn) | 14/14 OK, 4.9–6.7 s, = reference | 2.35–3.05 GB | 128 MB + 128 MB (16 MB × dop 8), sum of all ~265 MB |
| `flight0` (cap off), single node | 2 (both topn) | FAIL `Memory of query_pool exceed limit … Used: 3185975568 / 3090642232, Limit: 3478923509` | 3.20 / 3.18 GB | 972 + 367 MB / 976 + 383 MB (= the 979 + 396 MB of the 2026-10-22 profile) |
| `fc3` (cap), 3 nodes | 6 | 6/6 OK, 4.2–7.9 s, = reference | 2.36–3.08 GB | 128 MB + 128 MB |
| `fc30` (cap off), 3 nodes | 2 | FAIL `query_pool` (3.14 / 3.11 GB used) | 3.19 / 3.18 GB | 977 + 396 MB / 904 + 382 MB |
| `jdbc` (bridge), single node | 2 | topn default FAIL `Memory of process exceed limit` (3.6 of 3.87 GB, right after the `flight0` failures); topn 0 OK 9.0 s | 0.84 / 0.94 GB | 398 MB / 983 + 397 MB |

Checks 4,5 at SF10 (`m4.py --checks 4,5 --existing-catalog --reference bench/reference/sf10`):

| Run | Check 4 | Check 5 | Notes |
|---|---|---|---|
| single node, `flight`, `--ref-catalog jdbc` | 87/89 | 26/26 | every produced result = reference = JDBC (q18 topn default 4.74 s). FAIL 1: `q05 EXPLAIN COSTS: orders estimate from o_orderdate min/max` orders=2276507 — the check's band 150K–320K is for SF1; at SF10 2.28 M (15 % of 15 M) is the correct estimate (check-script item). FAIL 2: `q18 topn=0` `Memory of process exceed limit … Used: 3507291128, Limit: 3865470566` (see below) |
| 3 nodes, `fc3`, no spill (first runs used spill) | 45/46 | 26/26 | only the SF1-band q05 item; totals 22 q 42.7 s (topn default) / 42.2 s (topn 0), q18 3.74 / 3.36 s |

Single node, 22 q topn default: native 60.5 s, JDBC 191.5 s (q18 4.74 vs 13.26 s; lower host load than on 2026-10-22).

**Why q18 still peaks near 3 GB (remaining headroom item):** the peaks are bimodal (2.35 GB in 2 of 8 repeated runs, 2.96–3.05 GB
in 6 of 8). The difference is the local streaming pre-aggregation above the pushed aggregation (plan fragment 4: Flight scan
with `SELECT l_orderkey, sum(…) … GROUP BY l_orderkey` → `7:AGGREGATE (update serialize) STREAMING`). Its input is already
grouped by the server (15 M unique keys per endpoint), so it can never reduce; in the 3 GB runs it nonetheless put all 15 M keys
into hash tables (`HashTableMemoryUsage` 1.428 GB = 8 × 183 MB, `AggComputeTime` 281 ms) while the merge-finalize aggregation
(node 9) holds another 1.427 GB; in the 2.35 GB runs it switched to passthrough (28 MB, 4.7 ms). With other memory resident in
the BE process (the m4 sequence) a 3 GB peak can hit the process limit — the one m4 failure above. Fix candidate: when the
aggregation is pushed into the Flight scan, force the pre-aggregation above it to streaming passthrough (or drop it).

## 2026-10-23, CI: A-4 headroom (force-streaming pre-aggregation) — series `4a9848e-fl4bda75`, m4 runs 39949914514 / 39951241481

- The local aggregation directly above a Flight scan with a pushed aggregation is planned `force_streaming` (session
  mode `auto` only); check 9 note: `q18 pre-aggregation modes: force_streaming; aggregation pushed`.
- Run 39949914514 (checks 1–9, server int4b): 1–8 PASS (25/25, 52/52, 21/21, 46/46, 26/26, 6/6, 2/2, 14/14); check 9 5/6:
  "exchange peak with the cap <= without" 3.5 vs 2.5 MB — at SF1 on 2 vCPUs neither run reaches the 16 MB cap, so the
  comparison is noise (earlier 2.5 vs 2.7 MB). The item now compares only when the uncapped peak exceeds 16 MB.
- Run 39951241481 (checks 4,9): 46/46 (q05 orders band now scaled by the orders row count: 227651 in 150000..320000),
  6/6 (exchange 3.4 vs 4.6 MB, query peak/node 189 MB).
- The SF10 memory effect needs the stand (draft `v4.1.4-flight.0-a4b`).

## 2026-10-23, local A-4b re-check (maintainer's stand) — series `4a9848e-fl4bda75`, server int4 (fixed): **A-4 headroom confirmed: q18 at BE 4G peaks at 2.25–2.46 GB on every run, the pre-aggregation above the pushed aggregation is pure passthrough**

Build: draft `v4.1.4-flight.0-a4b` downloaded, `sha256sum -c SHA256SUMS` OK, `fe-build-info.txt` and `be-build-info.txt` both
`commit_hash=4a9848e-fl4bda75` (FE run 39948153646, BE run 39948156366), `starrocks_be` sha256 `11af5a4c…` = be-build-info, the 9
FE jar sha256s = fe-build-info; allin1 overlay as before; `current_version()` = `4.1.4-4a9848e-fl4bda75`. Server int4 (fixed, jar
md5 `ff3d6a72…`, DuckDB 1.4.5): single HDFS server on `dn` (open mode) and the 3-node HDFS cluster `c3-dn1..3` (token auth). BE
`mem_limit = 4G` (stand `be.conf`), **no spill**. Catalogs `flight` / `fc3` (default cap 16 MB) and `flight0` / `fc30`
(`"flight.exchange_buffer_mb" = "0"`), `jdbc` (bridge). Agent notes: `bench/tools/agent-sr-final/NOTES.md` ("A-4b re-check").

Plan: `EXPLAIN VERBOSE` q18 (single node and `fc3`, both topn settings, session `streaming_preaggregation_mode = auto`) shows
`5:AGGREGATE (update serialize)` directly above the Flight scan with `GROUP BY "l_orderkey"` pushed, with
`streaming preaggregation mode: force_streaming`; `SET streaming_preaggregation_mode = 'force_preaggregation'` turns every
aggregation to `force_preaggregation` (the old plan).

q18 SF10 at BE 4G (`QueryPeakMemoryUsagePerNode`; pre-aggregation = the `AGGREGATE_STREAMING_SINK` above the pushed
aggregation; `LocalExchangePeakMemoryUsage` of the two big exchanges):

| Catalog / mode | Runs | Result | Peak per node | Pre-aggregation (hash table, passthrough rows) | LocalExchangePeak |
|---|---|---|---|---|---|
| `flight`, auto (= `force_streaming`), single node | 14 (7 per topn) + 2 warm-up | 16/16 OK, 3.0–4.7 s, = reference | **2.249–2.382 GB** (no ~3.0 GB mode) | 192 B, 15.0 M / 15.0 M every run | 128 + 128 MB, sum 259–265 MB |
| `flight`, `force_preaggregation` (comparison) | 4 (2 per topn) | 4/4 OK, 3.6–4.1 s, = reference | 2.965–3.032 GB | 1.428 GB, 0 / 15.0 M | 128 + 128 MB |
| `flight0` (cap off), single node | 2 | FAIL `query_pool` (Used 3.13 / 3.18 GB, Limit 3478923509), as before | 3.18 / 3.19 GB | passthrough | 974 + 376 / 974 + 391 MB |
| `fc3`, auto, 3 nodes | 8 (4 per topn) | 8/8 OK, 1.9–2.9 s, = reference | **2.371–2.458 GB** | 192 B, 15.0 M / 15.0 M every run | 128 + 128 MB |
| `fc30` (cap off), 3 nodes | 2 | FAIL `query_pool`, as before | 3.19 / 3.18 GB | passthrough | 955 + 378 / 980 + 391 MB |

Checks 4,5 at SF10 (`m4.py --checks 4,5 --existing-catalog --reference bench/reference/sf10`):

| Run | Check 4 | Check 5 | Notes |
|---|---|---|---|
| single node, `flight`, `--ref-catalog jdbc` | 86/88 (twice) | 26/26 | every Flight result = reference = JDBC; q05 orders-estimate item PASS (2276507 in 1500000..3200000, scale 10). The 2 FAILs `q18 topn=default/0 … Memory of process exceed limit (Used 3.48–3.87 GB, Limit 3865470566)` are the **JDBC reference runs**: with `enable_profile` on globally, `SHOW PROFILELIST` shows the Flight q18 of both topn `Finished` (peak/node 2.363 / 2.366 GB) and the failing statement right after it on `catalog = jdbc` (`JDBCDataSource` scans, query peak 0.77–0.88 GB). `m4.py` check 4 runs the `--ref-catalog` query inside the same item and reports its exception under the catalog under test (check-script item). The 2026-10-23 a4 run's `q18 topn=0` process-limit FAIL has the same signature and was most likely the JDBC run too. |
| single node, `flight`, no `--ref-catalog` | 46/46 | — | q18 3.73 / 3.81 s; 22 q totals 35.2 s (topn default) / 34.7 s (topn 0) |
| 3 nodes, `fc3`, no spill | **46/46** | 26/26 | q05 orders item PASS (scale 10); 22 q totals 19.9 / 24.1 s, q18 1.85 / 2.39 s |

JDBC bridge (single node, same m4 run): 21 q (q18 failed) 167.7 / 168.5 s.

## 2026-10-23, CI: server int7 as the m4 default — series `4a9848e-fl4bda75`, m4 runs 39984493363 / 39984497103 / 39987340277

int7 (= int6b + the stand fixes for lakeFS, Iceberg and Hive; plugins s3/lakefs/iceberg/hive; sha256 pinned in
`ci/m4/server-jars.sha256`, equal to the asset digests) is the m4 default for every store; assets cache `m4-assets-v5`.
Full suite once, all PASS:

| Run | Store | Checks |
|---|---|---|
| 39984493363 | s3 | 1 25/25, 2 52/52, 3 21/21, 4 46/46, 5 26/26, 6 6/6, 7 2/2, 8 14/14, 9 6/6 |
| 39984497103 | iceberg | 1 25/25, 11 22/22 (append seen by partial mode after 5.3 s, complete mode after 20.7 s) |
| 39987340277 | lakefs | 1 25/25, 3 21/21, 4 46/46, 10 5/5 |

Unchanged with int7: the dataDir listing still shows the Iceberg warehouse directory as schema `_iceberg` (Open
questions). Harness: check 4 now reports an error of the `--ref-catalog` query under its own item
`<q> topn=<x> = <ref>` (FAIL with `ERROR of <ref>`) instead of under the item of the catalog under test.


## 2026-10-25, CI: server build 4eaab052deaf as the m4 default — series `4a9848e-fl4bda75`, m4 runs 40172422411 / 40172423737 / 40173169121

First server repo CI build (main 4eaab05 = int7 + hadoopfs timeout defaults 3 s / 10 s + dependency security
upgrades; own `flight-plugins-1.0.0-4eaab052deaf.tar.zst` and `flight-server-libs-1.0.0-4eaab052deaf.tar.zst`), run on
FE/BE outputs rebuilt in the re-created public repo (fe 40166741833, be 40166743137, same input hashes as before).

| Run | Store | Checks | Result |
|---|---|---|---|
| 40172422411 | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6) |
| 40172423737 | iceberg | 1, 11 | PASS (25/25, 22/22) |
| 40173169121 | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5) |

No regression against int7. Still listed: the Iceberg warehouse directory as schema `_iceberg` (Open questions).


## 2026-10-26, CI: server build 60e888bc26ec (`duckDbThreads` default 4) — series `4a9848e-fl536298`: **not made the default (check 6 intermittent)**

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40255396864 | 60e888bc26ec | s3 | 1–9 | all PASS except check 6 5/6 (25 + 52 + 21 + 46 + 26 + 5/6 + 2 + 14 + 6); check 4 28 s (29 s on 20b887839edf) |
| 40255398491 | 60e888bc26ec | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10) |
| 40259166769 | 60e888bc26ec | s3 | 6 | 5/6, same item (15.1 s) |
| 40259168469 | 20b887839edf | s3 | 6 | setup failed (MinIO: quay.io pull failed, fallback dropped a PutObject) |
| 40262586606 | 60e888bc26ec | s3 | 6 | 6/6 (flight2 stopped: 10.9 s) |
| 40262584557 | 20b887839edf | s3 | 6 | 6/6 (11.0 s) |

The failing item is "flight2 stopped before the query: succeeds via backup locations": `GetFlightInfo` times out on both
catalog URIs (`TIMED_OUT … waiting_for_connection`, 5 s each, 15 s total). In passing runs the same item also spends one
5 s timeout (10.9–12.5 s) before the second URI answers. flight1's log at the failure (40259166769): Hazelcast suspects
flight2 ~10 s after the stop, promotes 135 backups, and a `PutIfAbsentOperation` on the `server-registry` map was
retried 9 times from 02:31:59 to 02:32:08 (SEVERE `NormalResponse already responseReceived`). On 20b887839edf the item passed in every one of
~20 runs since 2026-10-21 (the two earlier failures, 39840237517 / 39841545485, were the P2 connector bug, fixed).
Working assumption: with 4 DuckDB threads per server on the 4-vCPU runner (two servers + allin1), flight1 is slower to
accept a new connection during member loss, so the FE's second attempt also misses its 5 s deadline. Not settled:
whether the FE's catalog connection should sit on flight2 at that point (the first attempt goes to the stopped server).
Harness: check 6 now writes the fe.log failover lines and flight1's WARN/SEVERE/member lines into the notes when the
item fails (the run artifacts are not reachable from the cloud sessions).


**Follow-up 2026-10-26 04:00 UTC — cause and connector fix (series `4a9848e-fldb9219`).** The job log of 40259166769
(readable through the GitHub API although the artifact is not) shows the final error is the FE's **connect probe**
(`CallOptions deadline exceeded after 4.999 s … waiting_for_connection`, thrown from `withFailover` → `current()`), not
a GetFlightInfo deadline (30 s). Reading: the catalog connection is on flight1 (URI 1); flight1's GetFlightInfo, started
02:31:59 right after the stop, failed as unreachable after ~10 s while its Hazelcast cluster was still dropping flight2
(the `server-registry` PutIfAbsent was retried from 02:31:59 to 02:32:08, flight2 suspected at 02:32:08); the FE then
probed flight2 (stopped: 5 s timeout) and, with each URI tried once, failed at 02:32:13 (15.1 s = ~10 s + 5 s). The earlier
reading (FE connection on flight2) was wrong. In passing runs the FE does not fail over at all (no `trying next location`
line in fe.log: m4 40267917390, 40267918986); the extra ~5–7 s over the 3–4 s baseline is the BE's connect timeout on
flight2's endpoint locations before their backups. Fix (0002 `withFailover`): when every URI failed as unreachable and
one of them was connected when its call failed, that URI is retried once (FlightSqlMetadataClientTest: retried once /
only once; FE 40265894284, 44/44). This is a transient server-side condition (a live server failing calls for ~10 s
during member loss), so it stays a server note too.

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40265277013 | 60e888bc26ec | s3 | 6 | 6/6 (flight2 stopped: 10.1 s; series `fl536298`) |
| 40265278745 | 60e888bc26ec | s3 | 6 | 6/6 (11.3 s; series `fl536298`) |
| 40267917390 | 60e888bc26ec | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6), series `fldb9219`; check 4 19 s |
| 40267918986 | 60e888bc26ec | s3 | 6 | 6/6 (10.9 s), series `fldb9219` |
| 40268961132 | 60e888bc26ec | s3 | 6 | 6/6 (10.0 s), series `fldb9219` |
| 40268964021 | 60e888bc26ec | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5), series `fldb9219` |
| 40270293499 | 60e888bc26ec | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10), series `fldb9219` |

**60e888bc26ec is the m4 default from 2026-10-26 04:40 UTC** (full suite green on series `fldb9219`; iceberg 1,11,12 green on
`fl536298`, m4 40255398491 — the FE change only touches failure paths). The fix itself is covered by the unit test only: none
of the runs after it hit the member-loss window. If check 6 fails again, the notes now carry the fe.log failover lines and
the query's UTC window.

## 2026-10-26, CI: server 7fbe2d75827c as the m4 default — series `4a9848e-fldb9219`

Server 7fbe2d75827c = 60e888bc26ec + planning no longer waits for the cluster to settle after a node left + `s3a://` /
`s3n://` catalog roots + HDFS short-circuit setting kept. Assets cache `m4-assets-v10`.

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40281342490 | 7fbe2d75827c | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6); check 4 21 s; check 6 "flight2 stopped": 15.4 s |
| 40281344356 | 7fbe2d75827c | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10) |
| 40284404496 | 7fbe2d75827c | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5) |
| 40284406938 | 7fbe2d75827c | s3 | 6 | 6/6 ("flight2 stopped": 10.9 s, no FE failover) |

**First CI hit of the member-loss window since the `fldb9219` fix, and the fix worked.** In 40281342490 the query after
stopping flight2 ran 06:47:31–06:47:47 UTC: fe.log shows flight1's GetFlightInfo failing UNAVAILABLE at 06:47:41.6 (~10 s
after the start, the same stall as on 60e888bc26ec), then flight2's connect probe TIMED_OUT at 06:47:46.6, then the retry of
the connected flight1 succeeded (15.4 s total, correct rows). Before `fldb9219` this sequence failed the query. So the
server change in 7fbe2d75827c does not remove the ~10 s stall in this case (a server note, Open questions in STATUS); the
connector handles it. **7fbe2d75827c is the m4 default from 2026-10-26 07:30 UTC.**

## 2026-10-26, CI: server 4d707e2aedfc as the m4 default — series `4a9848e-fldb9219`

Server 4d707e2aedfc = 7fbe2d75827c + DuckDB retries S3 connect errors for ~6 s. Assets cache `m4-assets-v11`.

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40294023782 | 4d707e2aedfc | s3 | 1–9 | setup failed before the checks (quay.io pull failed, the fallback MinIO dropped a PutObject: `ClientDisconnected`); `stack.sh minio` now retries each PUT up to 3 times |
| 40294026200 | 4d707e2aedfc | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10) |
| 40301602799 | 4d707e2aedfc | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6); check 4 29 s; check 6 "flight2 stopped": 10.9 s, no FE failover |
| 40301606304 | 4d707e2aedfc | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5) |

TPC-H timings unchanged (q01–q22 0.2–1.3 s). CI does not exercise the new S3 retry (MinIO on the runner never refuses
connections). **4d707e2aedfc is the m4 default from 2026-10-26 10:00 UTC.**

## 2026-10-26, CI: server 57d252b1437f as the m4 default — series `4a9848e-fldb9219`

Server 57d252b1437f = 4d707e2aedfc + one outbound byte budget shared by all Flight streams. Assets cache `m4-assets-v12`.

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40309379575 | 57d252b1437f | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6); check 4 29 s; check 6 "flight2 stopped": 10.7 s, no FE failover; "flight2 killed during the read": FailoverCount=3, correct rows |
| 40309382938 | 57d252b1437f | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10) |
| 40312075792 | 57d252b1437f | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5) |
| 40312078753 | 57d252b1437f | s3 | 1, 6 | PASS (25/25, 6/6); "flight2 stopped": 16.3 s — flight1 GetFlightInfo UNAVAILABLE ~10 s after the stop (11:12:05.9), flight2 probe TIMED_OUT, the `fldb9219` retry of flight1 succeeded |

TPC-H timings unchanged (q01–q22 0.1–1.1 s). The member-loss stall of ~10 s on the surviving server is still there on
this build (second hit in 4 check-6 runs since 7fbe2d75827c); the connector handles it. CI runs one Flight server per
query path and never 8 concurrent partial-mode scans on 3 nodes, so the new shared byte budget is exercised only by the
ordinary scans (no regression). **57d252b1437f is the m4 default from 2026-10-26 11:20 UTC.**

## 2026-10-27, CI: server 27f583adccd7 (DuckDB 1.5.6) as the m4 default — series `4a9848e-fldb9219`

Server 27f583adccd7 = 57d252b1437f + DuckDB 1.5.6 (was 1.4.5) + HDFS Kerberos ticket cache from a keytab. `stack.sh
assets` now fetches the v1.5.6 httpfs/iceberg/avro extensions for it (official builds from extensions.duckdb.org).
Assets cache `m4-assets-v13`.

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40450698707 | 27f583adccd7 | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6); check 4 22 s; check 6 "flight2 stopped": 10.8 s, no FE failover; "flight2 killed during the read": FailoverCount=3, correct rows |
| 40450700544 | 27f583adccd7 | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10) |
| 40452023921 | 27f583adccd7 | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5) |
| 40452025889 | 27f583adccd7 | s3 | 1, 6 | PASS (25/25, 6/6); "flight2 stopped": 10.7 s, no FE failover (member-loss stall not hit) |

Timings (sum of the 44 TPC-H query times of check 4): S3 21.3 s (57d252b1437f 27.1 s; earlier S3 runs 20.0–27.4 s),
lakeFS 35.0 s (57d252b1437f 25.2 s; earlier lakeFS runs 25.1–33.9 s). Both lie within the spread of the shared runners,
so CI shows neither the small-query gain nor a regression; per-query S3 times 0.13–1.00 s (before 0.18–1.29 s).
**27f583adccd7 is the m4 default from 2026-10-27 05:10 UTC.**

## 2026-10-27, CI: server 775100bf923f as the m4 default — series `4a9848e-fldb9219`

Server 775100bf923f = 27f583adccd7 + complete mode describes a query once per catalog-views snapshot (per-query
overhead, server stage 2 item 15 step 1). Same DuckDB 1.5.6 extension set. Assets cache `m4-assets-v14`.

| Run | Server | Store | Checks | Result |
|---|---|---|---|---|
| 40456836388 | 775100bf923f | s3 | 1–9 | all PASS (25 + 52 + 21 + 46 + 26 + 6 + 2 + 14 + 6); check 6 "flight2 stopped": 11.3 s, no FE failover; "flight2 killed during the read": FailoverCount=3, correct rows |
| 40456838963 | 775100bf923f | iceberg | 1, 11, 12 | PASS (25/25, 22/22, 10/10) |
| 40458183269 | 775100bf923f | lakefs | 1, 3, 4, 10 | PASS (25/25, 21/21, 46/46, 5/5) |
| 40458185120 | 775100bf923f | s3 | 1, 6 | PASS (25/25, 6/6); "flight2 stopped": 15.2 s — member-loss stall hit again (flight1 GetFlightInfo UNAVAILABLE at 06:06:32.3 UTC, ~10 s into the query; flight2 probe TIMED_OUT; connector retry of flight1 OK) |

Timings (sum of the 44 TPC-H query times of check 4): S3 25.6 s (27f583adccd7 21.3 s), lakeFS 34.2 s (35.0 s); per-query
S3 times 0.16–1.21 s. Within the shared runners' spread (S3 20.0–27.4 s, lakeFS 25.1–35.0 s); CI does not resolve the
per-query gain, the stand has to measure it. **775100bf923f is the m4 default from 2026-10-27 06:15 UTC.**
