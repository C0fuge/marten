# Status

Kept up to date after every work session so the work can be resumed from this repository alone.
Design: `docs/PLAN.md`. Source survey: `docs/RESEARCH.md`. CI state: branch `ci-status`, file `STATUS-CI.md`.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | **done**: FE run 39408957469; full BE (4.1.4 + thrift patch) run 39412648088, one job, Build BE 11:10–12:40 UTC (90 min, 4 vCPU, partly warm ccache); incremental BE with patch 0003: run 39447876098, Build BE 7 min |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | **done in CI** (compile + unit tests FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest: 14/14, run 39447425479); functional check is M4 |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | thrift (0001), FE FlightScanNode (0002), BE connector patch 0003 **compiles and links** (runs 39447876098, 39453716203 after the DoGet-timeout fix); untested until M4 |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | FE code complete: projection/filters/LIMIT, `FlightAggregationPushdownRule` (GROUP BY + count/sum/min/max, also covers count(*)), session switches (0002); TOP-N fix (0004). Unit tests green (runs 39451627570, 39453420117); plan-level test still todo |
| M4 | Bench tests on the maintainer's local stand | not in the cloud; test SQL prepared in `docs/M4-TESTS.md` |
| M5 | Package: patch series + artifacts + install guide | `docs/INSTALL.md` drafted; patch split and release todo |

## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe (WIP) | `connector/flight/`: FlightConnector, FlightMetadata, FlightProperties, FlightTypeMapper, FlightSqlMetadataClient, FlightSqlRenderer, FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable`; `planner/FlightScanNode`; optimizer: Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, **FlightAggregationPushdownRule** (rewriteOnce in QueryOptimizer after RewriteSimpleAggToHDFSScanRule), edits in OperatorType, visitors, RuleSet/RuleType, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, PlanFragmentBuilder, StmtExecutor, Authorizer, Table, ConnectorType, Explain, LogicalPlanPrinter; SessionVariable `flight_filter_pushdown`, `flight_aggregate_pushdown`; masking (PrintableMap, CredentialUtil, SqlCredentialRedactor, CatalogMgr logs); tests FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest, FlightAggregationPushdownRuleTest | compiles; 17 tests pass (run 39451627570) |
| 0003 be | `be/src/connector/flight_connector.{h,cpp}` (FlightConnector/DataSourceProvider/DataSource, cancel watcher, failover, Arrow→Chunk via ParquetScanner converters, conjuncts + LIMIT in the source), ConnectorType FLIGHT + registration, CMakeLists, exec_node FLIGHT_SCAN_NODE (+ collect_scan_nodes), descriptors FLIGHT_TABLE → plain TableDescriptor (no descriptors.h change: ~840 TUs include it) | compiles + links (run 39453716203, artifact of the current version) |
| 0004 fe | PushDownTopNToPreAggRule: ORDER BY must cover all GROUP BY keys; PushDownTopNToPreAggRuleTest | test passes (run 39453420117) |

Planned final split (PLAN.md §4 M5): thrift, FE connector, FE optimizer/planner, BE connector, TOP-N fix, tests.
Split 0002 into "FE connector" and "FE optimizer/planner" (it compiles now).

## CI

- `fe.yml`: FE jars (~12 min with warm Maven cache). `be.yml`: `starrocks_be`, chained jobs `part1..part4` (each
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

## Next steps

1. FE plan test for the Flight scan (mock FlightTable/metadata, e.g. on top of PlanTestBase): EXPLAIN shows the
   REMOTE SQL for projection, WHERE, LIMIT and the aggregation rule (count(*), GROUP BY with HAVING, avg not
   pushed); checks that the pushed scan has no predicate and that count without GROUP BY gets coalesce(…, 0).
2. BE: `connect_timeout_ms` is sent but not used (PLAN §2.7 timeouts: gRPC arg or a short probe before DoGet).
   A BE unit test for FlightDataSource against an in-process Arrow Flight server (arrow::flight::FlightServerBase
   is in the thirdparty build) would cover conversion, failover and cancellation before M4; needs a be-ut CI job.
3. Split 0002 into "FE connector" and "FE optimizer/planner" (+ tests) per the planned final split; keep 0001 and
   0003 byte-identical.
4. M5: release workflow (GitHub Release with fe-jars + starrocks_be.zst + patches) once M4 passes; README/INSTALL
   final check.

## Open questions for the maintainer

- Not a decision, a heads-up: a first M4 smoke is possible now with `fe-jars-e0cd7c224349f274` (run 39453420117)
  and `starrocks_be-*` of run 39453716203 (artifacts kept 7 days), installed per `docs/INSTALL.md` (the allin1
  image paths there are unverified), queries in `docs/M4-TESTS.md`. Nothing in the cloud work depends on it.
