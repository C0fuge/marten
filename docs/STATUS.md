# Status

Kept up to date after every work session so the work can be resumed from this repository alone.
Design: `docs/PLAN.md`. Source survey: `docs/RESEARCH.md`. CI state: branch `ci-status`, file `STATUS-CI.md`.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | **done**: FE run 39408957469; full BE (4.1.4 + thrift patch) run 39412648088, one job, Build BE 11:10–12:40 UTC (90 min, 4 vCPU, partly warm ccache); incremental BE with patch 0003: run 39447876098, Build BE 7 min |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | **done in CI** (compile + unit tests FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest: 14/14, run 39447425479); functional check is M4 |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | thrift (0001), FE FlightScanNode (0004), BE connector 0003 compiles and links (current: run 39484148997); BE unit test 0007 against an in-process Flight server **10/10 green** (be-ut run 39489468073); functional check is M4 |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | **done in CI**: projection/filters/LIMIT, `FlightAggregationPushdownRule` (GROUP BY + count/sum/min/max, also covers count(*)), session switches (0004); TOP-N fix (0005). Unit tests + plan test FlightScanPlanTest (7/7, EXPLAIN REMOTE SQL) green (run 39465778230); functional check is M4 |
| M4 | Bench tests on the maintainer's local stand | not in the cloud; test SQL prepared in `docs/M4-TESTS.md` |
| M5 | Package: patch series + artifacts + install guide | `docs/INSTALL.md` drafted; patch series of 7 patches (0007 = BE unit test); release workflow todo |

## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe connector | `connector/flight/`: FlightConnector, FlightMetadata, FlightProperties, FlightTypeMapper, FlightSqlMetadataClient (connect probe: ListActions bounded by `flight.connect_timeout_ms`), FlightSqlRenderer, FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable`, Table, ConnectorType; Authorizer, StmtExecutor (catalog type); masking (PrintableMap, CredentialUtil, SqlCredentialRedactor, CatalogMgr logs) | compiles (with the series) |
| 0003 be | `be/src/connector/flight_connector.{h,cpp}` (FlightConnector/DataSourceProvider/DataSource, cancel watcher, failover, connect timeout via `grpc.min_reconnect_backoff_ms`, Arrow→Chunk via ParquetScanner converters, conjuncts + LIMIT in the source; registered with the cancel watcher before the first connect), ConnectorType FLIGHT + registration, CMakeLists, exec_node FLIGHT_SCAN_NODE (+ collect_scan_nodes), descriptors FLIGHT_TABLE → plain TableDescriptor (no descriptors.h change: ~840 TUs include it) | compiles + links (run 39484148997, artifact of the current version) |
| 0004 fe optimizer/planner | `planner/FlightScanNode`; Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, **FlightAggregationPushdownRule** (rewriteOnce in QueryOptimizer after RewriteSimpleAggToHDFSScanRule), edits in OperatorType, visitors, RuleSet/RuleType, MultiOpPattern, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, PlanFragmentBuilder, Explain, LogicalPlanPrinter; SessionVariable `flight_filter_pushdown`, `flight_aggregate_pushdown` | compiles |
| 0005 fe | PushDownTopNToPreAggRule: ORDER BY must cover all GROUP BY keys; PushDownTopNToPreAggRuleTest | test passes (run 39453420117) |
| 0006 fe tests | FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest, FlightAggregationPushdownRuleTest, FlightScanPlanTest (+ MockedFlightSqlMetadataClient: Flight SQL metadata without a server), FlightSqlMetadataClientTest (in-process Java Flight server: failover from a silent / refused URI, no failover on server errors) | all pass (FE run 39484391882) |
| 0007 be test | `be/test/connector/flight_connector_test.cpp` (standalone, own main; registered with ADD_BE_TEST): in-process `arrow::flight::FlightServerBase`; type conversion (incl. UInt64→LARGEINT, naive / zoned timestamps), chunk slicing, failover from a refused location, no failover when disabled / on server errors, wrong token, connect timeout against a silent listener, cancel of a blocked read, read limit, conjuncts | 10/10 pass (be-ut run 39489468073) |

The split (2026-10-20) left the patched source tree byte-identical; 0001 and 0003 files are unchanged. Patches 0002
and 0004 are only built as part of the whole series (0002 alone has no reference to 0004's classes).


## CI

- `fe.yml`: FE jars (~12 min with warm Maven cache). `be-ut.yml`: `flight_connector_test` (~6 min: restores
  the newest `ccache-be-*` read-only, builds the Release tree with the test target appended to be/CMakeLists.txt
  by `ci/build-be-ut.sh` — the upstream MAKE_TEST/ASAN UT build would share nothing with our ccache — and runs
  it; report artifact `be-ut-report-<run>`). Runs on pushes of thrift/be patches or its own files, or via
  `be-ut` in `ci/dispatch.txt` (input `filter` = gtest filter). `be.yml`: `starrocks_be`, chained jobs `part1..part4` (each
  < 6 h, ccache carried in actions/cache); if 4 parts are not enough the run re-dispatches itself.
- Builds are skipped when an output for the same input hash is cached (`fe-out-<hash>`, `be-out-<hash>`).
- Push-triggered builds (branches `main` and `claude/**`) react only to their patch areas (`*-thrift-*`,
  `*-fe-*`, `*-be-*`). `concurrency: cancel-in-progress` — a new push touching BE patches CANCELS a running BE
  build on the same branch.
- The repo is public (free Actions minutes). A full BE build on the 4-vCPU runner is many hours; incremental BE builds with a warm ccache are short. Any change to patch 0001 (thrift) regenerates headers used
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

## Next steps

1. M5: release workflow (manual dispatch only: GitHub Release with fe-jars + starrocks_be.zst + patches +
   build-info) — can be written and dry-run now (e.g. as a draft release), published once M4 passes;
   README/INSTALL final check (patch list now 7 files, 0007 = BE test only, not needed at runtime).
2. Optional hardening while M4 is pending: BE test cases for basic auth (user/password handshake) and TLS
   (`grpc+tls` with a generated self-signed cert and `tls_root_certs` / `tls_verify=false`); reuse
   `flight_connector_test` (only patch 0007 changes → BE build is a ccache-only rebuild, be-ut ~4 min).
3. React to M4 results from the maintainer (failures go here as new steps).

## Open questions for the maintainer

- Not a decision, a heads-up: a first M4 smoke is possible now with the `fe-jars-*` artifact of FE run 39484391882
  and the `starrocks_be-*` artifact of BE run 39484148997 (artifacts kept 7 days; both from the current series),
  installed per `docs/INSTALL.md` (the allin1 image paths there are unverified), queries in `docs/M4-TESTS.md`.
  Nothing in the cloud work depends on it.
