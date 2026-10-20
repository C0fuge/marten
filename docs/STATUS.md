# Status

Kept up to date after every work session so the work can be resumed from this repository alone.
Design: `docs/PLAN.md`. Source survey: `docs/RESEARCH.md`. CI state: branch `ci-status`, file `STATUS-CI.md`.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | FE done (run 39408957469, 12 min). BE run 39408952022 (started 10:35 UTC) is most likely the resumability PROBE (budget 10 min × 2 parts: part1 took 13 min); check its result, then start the full M0 BE build |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | code written, **not compiled yet** (patch 0002, WIP) |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | thrift part done (patch 0001); BE code todo |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | FE parts started inside patch 0002 (FlightSqlRenderer, FlightAggregationPushdown); todo |
| M4 | Bench tests on the maintainer's local stand | not in the cloud; done locally after M3 |
| M5 | Package: patch series + artifacts + install guide | todo |

## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe (WIP) | `connector/flight/`: FlightConnector, FlightMetadata, FlightProperties, FlightTypeMapper, FlightSqlMetadataClient, FlightSqlRenderer, FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable`; optimizer: Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, edits in OperatorType, visitors, RuleSet/RuleType, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, StmtExecutor, Authorizer, Table, ConnectorType | written in one go, never compiled; FlightScanNode (planner → TPlanNode/scan ranges) and FE unit tests still missing |

Planned final split (PLAN.md §4 M5): thrift, FE connector, FE optimizer/planner, BE connector, TOP-N fix, tests.
Split 0002 into "FE connector" and "FE optimizer/planner" once it compiles.

## CI

- `fe.yml`: FE jars (~12 min with warm Maven cache). `be.yml`: `starrocks_be`, chained jobs `part1..part4` (each
  < 6 h, ccache carried in actions/cache); if 4 parts are not enough the run re-dispatches itself.
- Builds are skipped when an output for the same input hash is cached (`fe-out-<hash>`, `be-out-<hash>`).
- Push-triggered builds (branches `main` and `claude/**`) react only to their patch areas (`*-thrift-*`,
  `*-fe-*`, `*-be-*`). `concurrency: cancel-in-progress` — a new push touching BE patches CANCELS a running BE
  build on the same branch.
- Budget: private repo, about 2000 Actions minutes per month. A full BE build on the 4-vCPU runner is many hours;
  incremental BE builds with a warm ccache are short. Any change to patch 0001 (thrift) regenerates headers used
  everywhere = near-full BE rebuild, so batch thrift changes and avoid them.

## Log

- 2026-10-20 13:31 MSK: CI scripts and workflows. FE M0 build OK. BE M0 build started.
- 2026-10-20 14:00 MSK: handoff from the local session to the cloud routine. WIP FE code exported as patch 0002.
  Added `dispatch.yml`, `ci-report.yml`, `scripts/export-patches.sh`, docs/PLAN.md, docs/RESEARCH.md.

## Next steps

1. When probe run 39408952022 is finished and shows ccache resume worked, start the full unmodified M0 BE build. NOTE: `be.yml` builds the CURRENT patch series (0001 thrift is in it), so a build now is "4.1.4 + thrift patch", not unmodified — that is fine and more useful (it warms ccache for the patched tree); request it via `ci/dispatch.txt` with `be parts=4 budget_min=0`. Record time and minutes. Do not push BE/thrift patch changes while it runs.
2. Make patch 0002 compile: FE CI build (push the patch; the push triggers `fe`). Fix errors from STATUS-CI.md.
3. Add FlightScanNode (FE planner) + FE unit tests (type mapping, masking, SQL renderer, pushdown), run them via
   `ci/dispatch.txt` (`fe tests=...`).
4. BE connector `be/src/connector/flight/` (PLAN.md §2.7) as patch `be:`; one BE build after M0 is cached.
5. TOP-N: reproduce by reasoning/unit test in FE (PLAN.md §2.6), then a separate patch.
6. Install guide `docs/INSTALL.md` (overlay starrocks_be + starrocks-fe.jar onto `starrocks/allin1-ubuntu` 4.1.4).

## Open questions for the maintainer

(none yet)
