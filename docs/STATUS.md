# Status

Kept up to date after every work session so the work can be resumed from this repository alone.
Design: `docs/PLAN.md`. Source survey: `docs/RESEARCH.md`. CI state: branch `ci-status`, file `STATUS-CI.md`.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | FE done (run 39408957469). ccache resume probe OK (run 39408952022: part2 hit all 50 part1 objects). Full BE build (4.1.4 + thrift patch) run **39412648088** started 11:07 UTC |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | patch 0002 **compiles** (run 39412699319); masking added in PrintableMap, CredentialUtil, SqlCredentialRedactor, CatalogMgr logs; unit tests running (run 39414525761) |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | thrift done (0001); FE FlightScanNode done; BE connector first draft in `wip/be-flight-connector.wip.diff` (not compiled, not yet a patch) |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | FE parts started inside patch 0002 (FlightSqlRenderer, FlightAggregationPushdown); todo |
| M4 | Bench tests on the maintainer's local stand | not in the cloud; done locally after M3 |
| M5 | Package: patch series + artifacts + install guide | todo |

## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe (WIP, compiles) | `connector/flight/`: FlightConnector, FlightMetadata, FlightProperties, FlightTypeMapper, FlightSqlMetadataClient, FlightSqlRenderer, FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable`; optimizer: Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, edits in OperatorType, visitors, RuleSet/RuleType, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, StmtExecutor, Authorizer, Table, ConnectorType | compiles (run 39412699319, without the 2nd-session additions); now also FlightScanNode + PlanFragmentBuilder.visitPhysicalFlightScan, masking, renderer fix (pushed column names were unquoted), tests FlightTypeMapperTest/FlightSqlRendererTest/FlightPropertiesTest |

Planned final split (PLAN.md §4 M5): thrift, FE connector, FE optimizer/planner, BE connector, TOP-N fix, tests.
Split 0002 into "FE connector" and "FE optimizer/planner" once it compiles.

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
