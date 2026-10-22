# Status

Kept up to date after every work session so the work can be resumed from this repository alone.
Design: `docs/PLAN.md`. Source survey: `docs/RESEARCH.md`. CI state: branch `ci-status`, file `STATUS-CI.md`.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | **done**: FE run 39408957469; full BE (4.1.4 + thrift patch) run 39412648088, one job, Build BE 11:10–12:40 UTC (90 min, 4 vCPU, partly warm ccache); incremental BE with patch 0003: run 39447876098, Build BE 7 min |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | **done in CI** (compile + unit tests FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest: 14/14, run 39447425479); functional check is M4 |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | thrift (0001), FE FlightScanNode (0004), BE connector 0003 compiles and links (current: run 39484148997); BE unit test 0007 against an in-process Flight server **18/18 green** incl. basic auth and TLS (be-ut run 39514450368); functional check is M4 |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | **done in CI**: projection/filters/LIMIT, `FlightAggregationPushdownRule` (GROUP BY + count/sum/min/max, also covers count(*)), session switches (0004); TOP-N fix (0005). Unit tests + plan test FlightScanPlanTest (7/7, EXPLAIN REMOTE SQL) green (run 39465778230); functional check is M4 |
| M4 | Bench tests, moved to CI as far as possible (`docs/M4-CI.md`); short final check on the maintainer's stand | **CI part green on series `4a9848e-fl6b6a1d` against server int4** (release candidate, now the m4 default): checks 1–9 all pass incl. the new q05 row-count item (run 39735198246). Local final check 2026-10-22 FAILED (A-1 no CBO stats, keepalive; server items) — connector items fixed this session, local re-check pending (Next steps 1). Summary `docs/M4-RESULTS.md` |
| M5 | Package: patch series + artifacts + install guide | `docs/INSTALL.md` drafted; patch series of 7 patches, current series `4a9848e-fl6b6a1d` (FE 39733048078 with 32 Flight tests, BE 39733050937, be-ut 39730083877 on the same BE sources); draft release `v4.1.4-flight.0-dryrun` refreshed for it (release run 39735200365); publish after the local re-check |

## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe connector | `connector/flight/`: FlightConnector, FlightMetadata (row counts: `clear()` keeps the caches — MetadataMgr calls it after every query —, load started on `getTable`, first caller waits ≤ 250 ms; M4 fix 2026-10-22), FlightProperties, FlightTypeMapper, FlightSqlMetadataClient (connect probe: ListActions bounded by `flight.connect_timeout_ms`), FlightSqlRenderer, FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable`, Table, ConnectorType; Authorizer, StmtExecutor (catalog type); masking (PrintableMap, CredentialUtil, SqlCredentialRedactor, CatalogMgr logs) | compiles (with the series) |
| 0003 be | `be/src/connector/flight_connector.{h,cpp}` (FlightConnector/DataSourceProvider/DataSource, cancel watcher, failover, connect timeout via `grpc.min_reconnect_backoff_ms`, Arrow→Chunk via ParquetScanner converters, conjuncts + LIMIT in the source; registered with the cancel watcher before the first connect; keepalive timeout max(20 s, `flight.keepalive_ms`), was 5 s — M4 fix 2026-10-22), ConnectorType FLIGHT + registration, CMakeLists, exec_node FLIGHT_SCAN_NODE (+ collect_scan_nodes), descriptors FLIGHT_TABLE → plain TableDescriptor (no descriptors.h change: ~840 TUs include it); UInt64 columns widened to decimal128(20,0) for DECIMAL slots (our server streams UInt64 in result mode partial where its metadata says decimal128(20,0)); `exec/arrow_to_starrocks_converter.cpp`: Arrow timestamp → DATETIME by floor division (upstream bug: pre-1970 values with a fraction became garbage; M4 fix 2026-10-21) | compiles + links (BE run 39664594320) |
| 0004 fe optimizer/planner | `planner/FlightScanNode` (plan statistics via `computeStatistics`, 2026-10-22); Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, **FlightAggregationPushdownRule** (rewriteOnce in QueryOptimizer after RewriteSimpleAggToHDFSScanRule; remote items are bare `fn(expr)`, casts inside: `sum(CAST(x AS T))`; integer sums only in result mode complete — M4 fix 2026-10-21), edits in OperatorType, visitors, RuleSet/RuleType, MultiOpPattern, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, PlanFragmentBuilder, Explain, LogicalPlanPrinter; SessionVariable `flight_filter_pushdown`, `flight_aggregate_pushdown` | compiles |
| 0005 fe | PushDownTopNToPreAggRule: ORDER BY must cover all GROUP BY keys; PushDownTopNToPreAggRuleTest | test passes (run 39453420117) |
| 0006 fe tests | FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest, FlightAggregationPushdownRuleTest, FlightScanPlanTest (+ MockedFlightSqlMetadataClient: Flight SQL metadata without a server), FlightSqlMetadataClientTest (in-process Java Flight server: failover from a silent / refused URI, no failover on server errors); FlightScanPlanTest: scan cardinality, small table as broadcast build side in both join orders, caches survive `clear()` | all pass (FE run 39484391882) |
| 0007 be test | `be/test/connector/flight_connector_test.cpp` (standalone, own main; registered with ADD_BE_TEST): in-process `arrow::flight::FlightServerBase`; type conversion (incl. UInt64→LARGEINT, naive / zoned timestamps), chunk slicing, failover from a refused location, no failover when disabled / on server errors, wrong token, connect timeout against a silent listener, cancel of a blocked read, read limit, conjuncts; basic auth (handshake → bearer, wrong password not leaked), TLS with a self-signed cert generated at test time (root certs + override hostname, TLS + basic auth, hostname mismatch, untrusted cert, `tls_verify=false`, plain client vs TLS server); pre-1970 timestamps with a fraction (ms/us/ns); UInt64 stream into a DECIMAL(20,0) slot | 20/20 pass (be-ut run 39664598409) |

The split (2026-10-20) left the patched source tree byte-identical; 0001 and 0003 files are unchanged. Patches 0002
and 0004 are only built as part of the whole series (0002 alone has no reference to 0004's classes).


## CI

- `fe.yml`: FE jars (~12 min with warm Maven cache). `be-ut.yml`: `flight_connector_test` (~6 min: restores
  the newest `ccache-be-*` read-only, builds the Release tree with the test target appended to be/CMakeLists.txt
  by `ci/build-be-ut.sh` — the upstream MAKE_TEST/ASAN UT build would share nothing with our ccache — and runs
  it; report artifact `be-ut-report-<run>`). Runs on pushes of thrift/be patches or its own files, or via
  `be-ut` in `ci/dispatch.txt` (input `filter` = gtest filter). `be.yml`: `starrocks_be`, chained jobs `part1..part4` (each
  < 6 h, ccache carried in actions/cache); if 4 parts are not enough the run re-dispatches itself.
- Builds are skipped when an output for the same input hash is cached (`fe-out-<hash>`, `be-out-<hash>`); a
  forced rebuild (or an FE build with tests) replaces the cache entry.
- `m4.yml` (manual, `m4 checks=1,2,3` in `ci/dispatch.txt`): MinIO + our Flight server (release `m4-assets`) +
  allin1 4.1.4 overlaid with the current series' FE/BE outputs, checks `ci/m4/m4.py`; results artifact `m4-<run>`
  and branch `m4-results` (`git show origin/m4-results:latest.md`). Details: `docs/M4-CI.md` §7.
- `m4.yml` input `ref_catalog` (`m4 checks=1,3,4 ref_catalog=flight_c`): check 4 also compares every TPC-H query
  with that catalog (path used by the local final check against the JDBC bridge).
- `release.yml` (manual, `release tag=v… draft=true prerelease=true` in `ci/dispatch.txt`): builds nothing; takes
  the FE/BE outputs of the current input hashes from the caches (or the newest `fe-jars-*` / `starrocks_be-*`
  artifact when the cache is missing or stale), requires both to report the series hash `4.1.4-<base>-fl<patches>`
  (`ci/release.sh`; after an FE-only patch change run `be force=true`, a ccache-only rebuild, and vice versa) and
  creates the GitHub Release (assets: fe-jars tar, starrocks_be.zst, patches tar.gz, INSTALL.md, build-info files,
  SHA256SUMS). A draft creates no git tag; re-running with a draft's tag replaces it, published ones are refused.
- Push-triggered builds (branches `main` and `claude/**`) react only to their patch areas (`*-thrift-*`,
  `*-fe-*`, `*-be-*`). `concurrency: cancel-in-progress` — a new push touching BE patches CANCELS a running BE
  build on the same branch.
- The repo is private again since 2026-10-21 (~2000 Actions minutes/month; see CLAUDE.md). A full BE build on the 4-vCPU runner is many hours; incremental BE builds with a warm ccache are short. Any change to patch 0001 (thrift) regenerates headers used
  everywhere = near-full BE rebuild, so batch thrift changes and avoid them.

## Log

- 2026-10-20 13:31 MSK: CI scripts and workflows. FE M0 build OK. BE M0 build started.
- 2026-10-20 14:00 MSK: handoff from the local session to the cloud routine. WIP FE code exported as patch 0002.
  Added `dispatch.yml`, `ci-report.yml`, `scripts/export-patches.sh`, docs/PLAN.md, docs/RESEARCH.md.

- 2026-10-20 11:05–11:40 UTC (cloud session): probe OK; dispatched full BE build run 39412648088. FE build of
  patch 0002 OK (run 39412699319). Added FlightScanNode, masking, quoting fix, 3 test classes; FE build+tests
  dispatched (run 39414525761, result not seen). BE connector draft saved to `wip/` (kept out of `patches/` so the
  running BE build is not cancelled). Session stopped early on the maintainer's request.

- 2026-10-20 15:17–16:12 UTC (cloud session): BE M0 confirmed (run 39412648088, 90 min). FE test run 39414525761
  had failed on a duplicate `package` line in FlightSqlRendererTest; fixed, 14/14 tests pass (run 39447425479).
  BE connector moved from `wip/` into patch 0003 with connector/exec_node/descriptors/CMake wiring; compiles and
  links (run 39447876098, 7 min incremental). Added FlightAggregationPushdownRule (GROUP BY + count/sum/min/max,
  count(*) included), session switches `flight_filter_pushdown` / `flight_aggregate_pushdown`, Explain and
  LogicalPlanPrinter entries, FlightAggregationPushdownRuleTest (run 39449820889 failed: count(NULL) was rendered;
  fixed, run 39451627570 green). TOP-N fix as patch 0004 with PushDownTopNToPreAggRuleTest (run 39453420117 green;
  current FE artifact `fe-jars-e0cd7c224349f274`).
  Wrote `docs/M4-TESTS.md` and `docs/INSTALL.md`. Review of 0003 found that `flight.rpc_timeout_ms` (default 0 =
  none) was also the deadline of the streaming DoGet, so with a timeout set any longer endpoint read would have
  failed: now only the basic-auth handshake uses it. Arrow converters are now built once per stream instead of per
  chunk (BE run 39453716203 green, 7 min).

- 2026-10-20 17:15–18:07 UTC (cloud session): FlightScanPlanTest (PlanTestBase + MockedMetadataMgr + a
  FlightSqlMetadataClient stub with two endpoints): EXPLAIN REMOTE SQL for projection, pushed WHERE (BE re-check
  kept), LIMIT only with all conjuncts pushed, count(*) → `count(*) AS "__flight_agg_0"` + coalesce, GROUP BY with
  WHERE/HAVING (scan without predicate), avg / count(distinct) / unpushable conjunct not pushed, both session
  switches; 7/7 green on the first run (FE run 39465778230, artifact `fe-jars-a98b4da77859eeaf`). BE:
  `flight.connect_timeout_ms` now bounds each connect attempt via `grpc.min_reconnect_backoff_ms` (min 100 ms;
  calls are not wait-for-ready, so an unreachable location fails over after it); BE run 39465826698 green (5 min).
  Split the FE patch into 0002 connector / 0004 optimizer+planner / 0006 tests (BE now 0003, TOP-N 0005; source
  tree identical, same FE input hash);
  the split series applies and builds, and the 6 FE test classes pass (FE run 39470578122). Session ended 18:07 UTC.

- 2026-10-20 19:16–20:20 UTC (cloud session): Next step 1 done. BE unit test `flight_connector_test` (new patch
  0007) against an in-process `arrow::flight::FlightServerBase`: all mapped types convert as designed (UInt8→SMALLINT
  and UInt64→LARGEINT widen, naive timestamp keeps its wall clock, zoned timestamp is shown in the session zone,
  DECIMAL128→DECIMAL64, VARBINARY), batches are sliced to chunk_size, failover from a refused location (1 DoGet),
  none when disabled or on a server error, wrong token fails without the token in the message, a silent location
  (TCP accepted, no HTTP/2) fails over after 1004 ms with `connect_timeout_ms`=1000 (so
  `grpc.min_reconnect_backoff_ms` does bound the connect on gRPC 1.43; risk R3 settled), cancel wakes a blocked
  read in ~400 ms, read limit and conjuncts work: 10/10 (be-ut run 39489468073). Found while writing it: a stalled
  connect/first read in `open()` was not cancellable (the source registered with the cancel watcher only after
  the stream started); fixed in 0003 (BE run 39484148997 green). New CI job `be-ut.yml` + `ci/build-be-ut.sh`
  (Release tree + appended test target, BE ccache read-only, ~4 min); runs 39484149185, 39484779489, 39486204186,
  39487039672, 39487742279, 39488591786 failed on CI plumbing (build.sh `--module` takes no argument, protected
  member → `-fno-access-control`, libjvm/libjemalloc path, config env vars). Next step 2 done as well: the FE
  metadata client probes a new connection with ListActions bounded by `flight.connect_timeout_ms` (any answer =
  reachable) and fails over otherwise; FlightSqlMetadataClientTest (in-process Java Flight server, silent /
  refused URI, no failover on server errors) + the other 6 FE test classes green (FE run 39484391882).

- 2026-10-20 21:16–21:35 UTC (cloud session): Next step 1 (M5 release workflow). New `.github/workflows/release.yml`
  + `ci/release.sh` (see CI above); `ci-report` also follows release runs. First dry run 39499303111 failed on its
  consistency check: the cached `starrocks_be` (run 39484148997) reports series `4a9848e-fl76a25f`, built before
  the last FE-only 0002 change, the jars `fl14c16b`. Forced BE rebuild (run 39499533941, same BE sources, Build BE
  74 s) — and fe.yml / be-part.yml now replace an existing output cache entry on a rebuild (the old one could not
  be overwritten). Second dry run 39500542342 green: **draft** pre-release `v4.1.4-flight.0-dryrun` (no git tag
  yet) with fe-jars tar, starrocks_be.zst (sha256 60e1a2bc…), patches tar.gz, INSTALL.md, build-info files,
  SHA256SUMS; FE from run 39484391882, BE from run 39499533941. INSTALL.md describes the release assets. No patch
  changed (no source preparation needed).
- 2026-10-20 23:15–23:35 UTC (cloud session): Next step 1 (BE auth/TLS tests) done. Patch 0007 gained 8 cases:
  a Basic-auth server middleware (Handshake `authorization: Basic …` → `Bearer` header) checks the user/password
  handshake path and that a wrong password fails before DoGet without appearing in the status; TLS uses an EC
  P-256 self-signed cert generated with OpenSSL at test time (no key material in the repo): root certs + override
  hostname OK, with basic auth OK, hostname mismatch and untrusted cert fail, `tls_verify=false` OK without
  root certs, plain client vs TLS server fails. TLS errors arrive as UNAVAILABLE, so with several locations a
  misconfigured TLS location is failed over like an unreachable one (acceptable; noted for M4). Pre-checked locally
  against pyarrow 19.0.1's libarrow_flight. CI: be-ut run 39514450368 18/18 green on the first run; BE run
  39514450436 green (Build BE 81 s, ccache-only). No connector code changed.

- 2026-10-21 01:15–01:40 UTC (cloud session): no M4 results yet (step 1 waits). Old step 2 done: forced FE rebuild
  for the series hash after the 0007 change (FE run 39526375694, 5 min, no tests), then the draft
  `v4.1.4-flight.0-dryrun` re-created for series `4a9848e-fl80f999` (release run 39527877395 green; FE 39526375694,
  BE 39514450436). No patch changed.
- 2026-10-21 16:27 UTC (cloud session): no M4 results yet; noted the 7-day artifact/cache retention under Next
  step 2. No patch changed, no CI run.
- 2026-10-21 18:41–20:08 UTC (cloud session): M4 moved into CI. New `m4.yml` + `ci/m4/stack.sh` (MinIO —
  docker.io/minio is gone, quay.io/bitnamilegacy/chainguard fallbacks, boto3 single-PUT upload —, our Flight
  server from release `m4-assets` on JDK 21, allin1 4.1.4 overlay) + `ci/m4/m4.py` (checks 1–9 vs DuckDB 1.4.1 /
  SF1 reference); results on branch `m4-results`, summary `docs/M4-RESULTS.md`. Plumbing runs 39655898917
  (cancelled), 39656305326, 39656873818, 39657625118 failed (MinIO image, multipart upload, read-only server cwd).
  First real run 39658484728 found: (1) result mode partial rejects `CAST(sum(..))` → 0004 renders
  `sum(CAST(x AS T))`, integer sums only in complete mode; (2) Arrow timestamps before 1970 with a fraction were
  garbage (upstream converter, truncating division) → 0003 floors; (3) UInt64 wrapped: the server streams
  `uint64` in partial mode where its metadata says decimal128(20,0) → 0003 widens. Tests in 0006/0007. Builds:
  FE 39660196425 (7 Flight test classes green), BE 39660201177, be-ut 39660205090; then FE 39664615702, BE
  39664594320, be-ut 39664598409 (20/20). M4 runs 39661743301, 39663221891, and **39665941130: all 9 checks pass**
  on series `4a9848e-fl598360`. ci-report now follows m4 and prints billable minutes correctly (was ms).
- 2026-10-21 20:26–20:45 UTC (cloud session): Next step 1 done. `docs/LOCAL-FINAL-CHECK.md` for the maintainer
  (SF10 hadoopfs vs `bench/reference/sf10` + JDBC catalog, Trino timings, 3-node kill tests B1–B7, auth/TLS/
  profile/log grep C1–C5, report table). `ci/m4/m4.py` gained the options it uses (`--existing-catalog`,
  `--catalog`, `--reference`, `--ref-catalog`, `--sr-cases-ref`, `M4_SR_*` connection; CI defaults unchanged),
  `m4.yml` the input `ref_catalog`; tested by m4 run 39670612956 (checks 1,3,4 vs `flight_c`: 15/15, 21/21,
  88/88). Draft release `v4.1.4-flight.0-dryrun` refreshed for series `4a9848e-fl598360` (release run
  39670616758). No patch changed.
- 2026-10-21 22:36–23:00 UTC (cloud session): Next step 1 (M4 CI hardening) done, harness only (`ci/m4/m4.py`, no
  patch change): check 1 compares every DESC exactly with the PLAN §2.2 mapping (`plan_type`, mirrors
  FlightTypeMapper) of the server's GetTables schema; check 6 "during" reads lineitem 3x and kills flight2 at 35%
  of the measured read, and requires proof that the kill hit the read (error, or `FailoverCount` > 0 in the query
  profile); check 8 fetches the query profiles (`get_query_profile`) of a token and a basic-auth scan and greps
  them for the token. m4 run 39688089343 (checks 1,6,8): all PASS — 25/25, 6/6 (FailoverCount=3, correct rows,
  query ended 3.4 s after the kill), 14/14. Side note: PLAN §2.2 lists Decimal256 p≤38 → DECIMAL, the code hides
  every Decimal256 (BE has no Decimal256 converter); no effect with DuckDB (max precision 38 → decimal128).

- 2026-10-21 23:40–00:05 UTC (cloud session): old Next step 0 done. `m4.yml` input `server` (jar asset of
  `m4-assets`, default `arrow-flight-server-1.0.0-int2.jar`, name validated), assets cache key `m4-assets-v2`
  (all jars), `stack.sh assets DIR [JAR]` re-downloads when the jar is missing and checks jars absent from the
  release's SHA256SUMS against `ci/m4/server-jars.sha256` (int2 pinned); results.md names the server. m4 run
  39695113106 (int2, checks 1–9): all PASS; m4 run 39696030255 (int1, checks 1,2): PASS. Connector workarounds
  kept. No patch changed (no source preparation needed). Note: a `[skip ci]` commit does not trigger dispatch.yml.
- 2026-10-22 00:40 UTC (cloud session): no local final check results yet (step 1 waits on the maintainer). No patch
  changed, no CI run.

- 2026-10-22 02:53–04:45 MSK (local agent on the maintainer's stand): **local final check FAILED** — 2 connector
  items (no Flight CBO statistics → lineitem as hash build side → memory errors at SF10; keepalive watchdog kills a
  slow stream) and 3 server-side (s3p4) items (silent partial result after losing 2 of 3 members, no backup
  locations, one DuckDB fatal error). Details and timings: `docs/M4-RESULTS.md` "local final check"; items under
  Next steps 1a. No patch changed.

- 2026-10-22 05:40–06:55 UTC (cloud session; the locks of 01:34 and 03:41 were stale, those sessions left no
  work): **Next step 0b done:** `stack.sh assets` picks DuckDB httpfs version and plugin dir from the jar name
  (int1/int2: 1.4.1; int4+: 1.4.5 + `<tag>-plugins.tar.zst`, `-Darrowflight.plugins.dir`), int4 jar + plugins
  pinned in `ci/m4/server-jars.sha256` (equal to the release asset digests), cache key `m4-assets-v3`; m4 run
  39729516833 failed (renamed httpfs file → wrong entry point), 39730011530 int4 checks 1–9 all PASS; int4 is now
  the m4 default. **1a connector items fixed:** A-1 root cause = `FlightMetadata.clear()` (called by MetadataMgr
  after every query) emptied the row-count cache → `clear()` keeps caches, count started on `getTable`, first
  caller waits ≤ 250 ms (0002); FlightScanNode `computeStatistics` (0004); plan tests (0006); keepalive timeout
  max(20 s, keepalive_ms) (0003); m4 check 4 asserts q05 row counts. A 1 s wait on every call broke check 6
  (memo > 3 s, m4 39732232288) → once per load, 250 ms. Builds: FE 39730095868 / 39733048078 (32/32 tests), BE
  39730083919 / 39733050937, be-ut 39730083877 (20/20); m4 39735198246 (int4, series `fl6b6a1d`): 1–9 all PASS;
  release dry run 39735200365.
- 2026-10-22 07:40 UTC (cloud session): no local re-check results yet (step 1 waits on the maintainer); Next step 1
  named the old series `flf35d9a`, corrected to `fl6b6a1d` (the dry-run draft's series). No patch changed, no CI run.

## Next steps

1. **Local re-check of the 2026-10-22 failures** (maintainer's stand, short; `docs/LOCAL-FINAL-CHECK.md`), build
   under test: draft `v4.1.4-flight.0-dryrun` for series `4a9848e-fl6b6a1d` (A-1 + keepalive fixes):
   - A: q05/q08/q09/q18/q21 at SF10 with BE `mem_limit = 4G`; `EXPLAIN COSTS <q05>` must show real
     `cardinality` (lineitem 59986052) for every FlightScanNode and lineitem on the probe side.
   - q18 on the 3-node cluster under load (keepalive): no `keepalive watchdog timeout`.
   - B2/B5 against the release-candidate server **int4** (backup locations; partial result after losing 2 of 3
     members is a server bug, see Open questions).
   When reported: record in `docs/M4-RESULTS.md`; fix failures in the patches.
2. After the re-check passes and the maintainer agrees: `release tag=v4.1.4-flight.1 draft=false
   prerelease=false`; delete the `v4.1.4-flight.0-dryrun` draft. Retention: CI artifacts 7 days, caches evicted
   after 7 days without access — after a long pause expect a full BE rebuild (~90 min). Every patch change needs
   FE **and** BE outputs of the new series before `m4` or `release` (the other side: `fe/be force=true`).
3. Optional (only if A-1 plans are still poor at SF10): use the connector's column NDV estimates in
   `computeFlightScanNode` (today column stats come from `estimateScanColumns`, UNKNOWN, as for JDBC).


### Parallel work while the local re-check is pending (maintainer, 2026-10-22 evening)

Item 1 waits for the maintainer's stand; do these in the meantime, one per session, in this order. Each must keep
`m4` green; batch BE changes (one BE build per session at most).

P1. **Types now hidden** (`docs/M4-RESULTS.md`: TIME, INTERVAL hidden; PLAN §1.5: DECIMAL256, TIME32/64, DURATION,
    INTERVAL, *View types and UNION not covered). Map what StarRocks can represent: TIME32/64 → TIME (or VARCHAR
    'HH:MM:SS[.ffffff]' if TIME is not usable for external tables), DURATION → BIGINT (unit in the column comment),
    INTERVAL → VARCHAR (ISO-8601), DECIMAL256 → DECIMAL256/LARGEINT where precision allows else VARCHAR,
    Utf8View/BinaryView/ListView → their non-view equivalents (cast in the BE converter). Catalog option to keep
    hiding them. FE type mapping + BE converters + be-ut + m4 check 2 (the alltypes tables already carry TIME and
    INTERVAL; extend the expected list).
P2. **Column statistics for the CBO** (Next steps 3 made concrete): our servers answer `SELECT count(*), min(c),
    max(c)` from Parquet footers cheaply (the Trino plugin uses that); use per-column min/max/null counts (and an
    NDV estimate when available) in `computeFlightScanNode`, cached like row counts, bounded wait, off by catalog
    option. Plan tests: join order for TPC-H q05/q08/q09 at SF1 in m4 equals the JDBC catalog's or better.
P3. **lakeFS through the connector in CI**: `int4-plugins.tar.zst` has `plugins/lakefs`; add an m4 variant with a
    lakeFS container (docker.io/treeverse/lakefs:1.38.0, local KV, MinIO blockstore) in front of MinIO, server
    `-DdataDir=lakefs://<repo>/main/...` (START-NOTES.txt in the plugins tarball), and run checks 1, 3, 4 there plus
    a "commit to main between two queries" check (a query sees one commit).
P4. **Upgrade readiness**: try the patch series on the newest 4.1.x tag (`git am` only, no build unless it applies
    with small fixes); write `docs/REBASE.md` with conflicts and effort. Do not change the release target (4.1.4).

A new server build with cluster fixes (B5, ticket secret) will appear in `m4-assets` (name `…-int4b…` or
newer) — when it does, make it the m4 default and rerun checks 6 and 8.

## Open questions for the maintainer

- Server findings (a) partial mode rejecting `CAST(sum(x))`, (b) UBIGINT streamed as `uint64` in partial mode:
  fixed in server int2 (verified by m4 run 39695113106). The connector keeps its workarounds (no integer
  `sum` push in partial mode, UInt64 → DECIMAL(20,0) widening) so int1-era servers stay supported. If you want
  integer sums pushed in partial mode for int2+ servers, say so (it would need a server-version or catalog switch).
- Release `m4-assets`: its SHA256SUMS does not list the int2/int4 jars and `int4-plugins.tar.zst`; their hashes
  are pinned in `ci/m4/server-jars.sha256` (int4 values checked against the asset digests of the release). If you
  re-upload SHA256SUMS with them, nothing needs to change here.
- **Server (s3p4 / check int4) items from the local final check, not fixable in the connector:** B5 silent
  partial result after losing 2 of 3 members (Hazelcast "Promotion commit failed"), B2 no backup locations, A-2
  DuckDB fatal error in a pushed q18 aggregation. Please re-run B2/B5 against int4 on the stand (step 1).

- **Done 2026-10-22 (FAILED, see Next steps 1a):** **`docs/LOCAL-FINAL-CHECK.md`** (≈2–3 h on the stand: SF10 hadoopfs vs `bench/reference/sf10`
  and the JDBC catalog with `ci/m4/m4.py`, Trino timings, 3-node kill tests, auth/TLS/profile/log grep). Build
  under test: draft release `v4.1.4-flight.0-dryrun` (series `4a9848e-fl598360`). It assumes `bench/reference/sf10`
  has the layout of `tests/m4/reference/sf1` (`qNN.tsv` + `qNN.cols`); if not, the JDBC comparison still covers
  correctness — tell me the layout and I adapt the harness. The allin1 paths of `docs/INSTALL.md` §2a are verified
  by `m4.yml`.
- Release naming: the workflow takes any tag `v…`; proposed `v4.1.4-flight.N`. Publishing (draft → public, which
  creates the git tag) is left to you after M4.
- 2026-10-21 (maintainer): M4 moves to CI as far as possible (docs/M4-CI.md); only a short final check runs on
  the local stand. The repo is private again because the `m4-assets` release holds our server build.
- 2026-10-22 02:30 MSK (local coordinator): server fixes for both M4 findings are in int2 (now the m4 default; all checks pass, m4 run 39695113106). The local final check (agent on the maintainer's stand) starts after the running speed benchmark; it writes its results here and to M4-RESULTS.md.
