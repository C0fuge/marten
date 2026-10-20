# Status

Kept up to date after every work session so the work can be resumed from this repository alone.
Design: `docs/PLAN.md`. Source survey: `docs/RESEARCH.md`. CI state: branch `ci-status`, file `STATUS-CI.md`.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | **done**: FE run 39408957469; full BE (4.1.4 + thrift patch) run 39412648088, one job, Build BE 11:10–12:40 UTC (90 min, 4 vCPU, partly warm ccache); incremental BE with patch 0003: run 39447876098, Build BE 7 min |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | **done in CI** (compile + unit tests FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest: 14/14, run 39447425479); functional check is M4 |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | thrift (0001), FE FlightScanNode (0002), BE connector patch 0003 **compiles and links** (run 39447876098, artifact `starrocks_be-4071a9de033827c6`); untested until M4 |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | projection/filters/LIMIT in 0002; `FlightAggregationPushdownRule` (GROUP BY + count/sum/min/max, also covers count(*)) and session switches in 0002; TOP-N fix patch 0004 (unit test); CI results see Log |
| M4 | Bench tests on the maintainer's local stand | not in the cloud; test SQL prepared in `docs/M4-TESTS.md` |
| M5 | Package: patch series + artifacts + install guide | `docs/INSTALL.md` drafted; patch split and release todo |

## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe (WIP) | `connector/flight/`: FlightConnector, FlightMetadata, FlightProperties, FlightTypeMapper, FlightSqlMetadataClient, FlightSqlRenderer, FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable`; `planner/FlightScanNode`; optimizer: Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, **FlightAggregationPushdownRule** (rewriteOnce in QueryOptimizer after RewriteSimpleAggToHDFSScanRule), edits in OperatorType, visitors, RuleSet/RuleType, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, PlanFragmentBuilder, StmtExecutor, Authorizer, Table, ConnectorType, Explain, LogicalPlanPrinter; SessionVariable `flight_filter_pushdown`, `flight_aggregate_pushdown`; masking (PrintableMap, CredentialUtil, SqlCredentialRedactor, CatalogMgr logs); tests FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest, FlightAggregationPushdownRuleTest | compiles; 14 tests pass (run 39447425479); rule test see Log |
| 0003 be | `be/src/connector/flight_connector.{h,cpp}` (FlightConnector/DataSourceProvider/DataSource, cancel watcher, failover, Arrow→Chunk via ParquetScanner converters, conjuncts + LIMIT in the source), ConnectorType FLIGHT + registration, CMakeLists, exec_node FLIGHT_SCAN_NODE (+ collect_scan_nodes), descriptors FLIGHT_TABLE → plain TableDescriptor (no descriptors.h change: ~840 TUs include it) | compiles + links (run 39447876098) |
| 0004 fe | PushDownTopNToPreAggRule: ORDER BY must cover all GROUP BY keys; PushDownTopNToPreAggRuleTest | see Log |

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

## Next steps

1. Check FE run 39414525761 (build + FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest); fix
   failures. Check full BE run 39412648088 (record time); do not push BE/thrift patch changes while it runs.
2. FE: Explain/LogicalPlanPrinter entries if needed, aggregation pushdown rule (FlightAggregationPushdown has no
   rule setting it yet), count(*) rule, session switch `flight_filter_pushdown`.
3. Finish the BE connector from `wip/be-flight-connector.wip.diff` (still missing: register in connector.cpp +
   ConnectorType FLIGHT, CMakeLists, exec_node.cpp FLIGHT_SCAN_NODE, FlightTableDescriptor in descriptors.{h,cpp});
   make it patch `0003-be-...` once BE M0 is cached, one BE build.
4. BE connector `be/src/connector/flight/` (PLAN.md §2.7) as patch `be:`; one BE build after M0 is cached.
5. TOP-N: reproduce by reasoning/unit test in FE (PLAN.md §2.6), then a separate patch.
6. Install guide `docs/INSTALL.md` (overlay starrocks_be + starrocks-fe.jar onto `starrocks/allin1-ubuntu` 4.1.4).

## Open questions for the maintainer

(none yet)
