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
| M4 | Bench tests, moved to CI as far as possible (`docs/M4-CI.md`); short final check on the maintainer's stand | **CI part green on series `4a9848e-fl6b6a1d` against server int4** (release candidate, now the m4 default): checks 1–9 all pass incl. the new q05 row-count item (run 39735198246). Local final check 2026-10-22 FAILED (A-1 no CBO stats, keepalive; server items); **local re-check 2026-10-22 (series `fl6b6a1d`, fixed int4): A-1, keepalive, B2/B5 PASS, SF10 85/87 + 26/26 single node, 45/45 + 26/26 3-node; q18 at BE 4G fails on memory (A-4, Next steps 1)**. Series `4a9848e-fl9ec2c3` (P1 converted types): checks 1–9 all pass (run 39828677269, check 2 now 52/52 incl. TIME and INTERVAL). Series `4a9848e-fl67776b` (P1 + P2 column min/max): checks 1–9 all pass (run 39845020831, check 4 46/46 incl. the q05 orders estimate). Newest series `4a9848e-fld145f6` (+ A-4 `flight.exchange_buffer_mb`): checks 1–9 all pass (run 39873438298, check 9 6/6 incl. the q18 exchange items); lakeFS variant checks 1,3,4,10 (run 39875156594); Iceberg variant on server int6 checks 1,11 (run 39882258299). **Local A-4 re-check 2026-10-23 (draft `v4.1.4-flight.0-a4`): q18 at BE 4G passes with the cap (14/14 single node, 6/6 3-node; fails with the cap off), checks 4,5 SF10 87/89 + 26/26 and 45/46 + 26/26 (3-node, no spill); headroom item: pre-agg above the pushed aggregation (Next steps 1)**. Newest series `4a9848e-fl4bda75` (+ force-streaming pre-aggregation above a pushed aggregation): checks 1–9 pass (run 39949914514: 1–8 all, 9 5/6 on a noise comparison, fixed in m4.py; run 39951241481: checks 4 46/46, 9 6/6). **Local A-4b re-check 2026-10-23 (draft `v4.1.4-flight.0-a4b`): q18 at BE 4G `force_streaming` pre-aggregation, pure passthrough, peak/node 2.25–2.38 GB single node (16/16) and 2.37–2.46 GB 3-node (8/8); checks 4,5 SF10 86/88 + 26/26 single node (both FAILs = the JDBC reference q18 at the process limit; Flight-only 46/46), 46/46 + 26/26 3-node — A-4 settled**. **Server int7 is the m4 default (2026-10-23): full suite PASS — S3 checks 1–9 (run 39984493363), Iceberg 1,11 (run 39984497103), lakeFS 1,3,4,10 (run 39987340277).** **Server build 4eaab052deaf is the m4 default (2026-10-25): full suite PASS on the rebuilt outputs of the public repo — S3 1–9 (run 40172422411), Iceberg 1,11 (run 40172423737), lakeFS 1,3,4,10 (run 40173169121).** **Server c3b276054cc3 is the m4 default (2026-10-25): S3 1–9 (m4 40227337083), Iceberg 1,11 (40227338512; on `fl536298`: 40229960640), lakeFS 1,3,4,10 (40228819006, `fl536298`) PASS; check 12 (time travel) fails on the server side.** **Server 20b887839edf (m4 default since 2026-10-26): S3 1–9 (40245888043), Iceberg 1,11,12 incl. time travel 10/10 (40245889746), lakeFS 1,3,4,10 (40248225183) all PASS on `fl536298`.** ~~Server 60e888bc26ec (2026-10-26): all PASS except check 6 (intermittent, 2 of 3 runs; m4 40255396864 / 40255398491 / 40259166769 / 40262586606) — not the default.~~ **Series `fldb9219` (FE: retry the connected catalog URI once) + server 60e888bc26ec = m4 default since 2026-10-26: S3 1–9 (40267917390), check 6 3/3 (40267918986, 40268961132), lakefs 1,3,4,10 (40268964021) all PASS; iceberg 1,11,12 PASS on `fl536298` (40255398491).** **Server 7fbe2d75827c = m4 default since 2026-10-26 07:30 UTC (series `fldb9219`): S3 1–9 (40281342490), iceberg 1,11,12 (40281344356), lakefs 1,3,4,10 (40284404496), check 6 (40284406938) all PASS; 40281342490 exercised the FE connected-URI retry (flight1 stalled ~10 s, retry succeeded).** **Server 4d707e2aedfc (+ DuckDB S3 connect retry) = m4 default since 2026-10-26 10:00 UTC (series `fldb9219`): S3 1–9 (40301602799), iceberg 1,11,12 (40294026200), lakefs 1,3,4,10 (40301606304) all PASS.** **Server 4e77c6bda59a = m4 default since 2026-10-27 22:10 UTC (series `fldb9219`): S3 1–9 (40588875084), iceberg 1,11,12 (40588877746), lakefs 1,3,4,10 (40590969944), check 6 (40590972986) all PASS.** **Server cadd1aca9c23 (opt-in result compression, size-aware `duckDbThreads`) = m4 default since 2026-10-28 02:35 UTC (series `fldb9219`): S3 1–9 (40616536538), iceberg 1,11,12 (40616538747), lakefs 1,3,4,10 (40619524251), check 6 (40619526598) all PASS.** Summary `docs/M4-RESULTS.md` |
| M5 | Package: patch series + artifacts + install guide | `docs/INSTALL.md` drafted; patch series of 7 patches, current series `4a9848e-fl6b6a1d` (FE 39733048078 with 32 Flight tests, BE 39733050937, be-ut 39730083877 on the same BE sources); draft release `v4.1.4-flight.0-dryrun` refreshed for it (release run 39735200365); publish after the local re-check. Newer series `4a9848e-fl9ec2c3` (P1): FE 39825739612 (Flight tests), BE 39825723550, be-ut 39825723598. Newest `4a9848e-fl67776b` (P1 + P2): FE 39842646955 (Flight tests), BE 39842650526 (ccache-only rebuild; BE sources unchanged since be-ut 39825723598) — the draft was deliberately NOT refreshed (it is the build under the maintainer's re-check). Newest `4a9848e-fld145f6` (P1 + P2 + A-4 exchange cap): FE 39847449823 (Flight tests), BE 39847433502, be-ut 39847433352; separate draft `v4.1.4-flight.0-a4` for the stand's q18 re-check (release run 39874283999). Newest `4a9848e-fl4bda75` (+ A-4 headroom): FE 39948153646 (39 Flight tests), BE 39948156366 (ccache-only rebuild; BE sources unchanged since be-ut 39847433352); draft `v4.1.4-flight.0-a4b` for the stand (release run 39952272222). Newest `4a9848e-fl536298` (+ time-travel forwarding, FE only): FE 40227477334 (42 Flight tests), BE 40228410632 (ccache-only rebuild); not released (v4.1.4-flight.1 = `fl4bda75`, released locally by the maintainer). Newest `4a9848e-fldb9219` (+ FE metadata client retries the connected URI once when no location answers): FE 40265894284 (44 Flight tests), BE 40267006057 (ccache-only rebuild); not released. Newest `4a9848e-flf41597` (+ `flight.compression` opt-in, 2026-10-28): FE 40668964365 (45/45), BE 40668967450 and be-ut 40668971169 running cold (no ccache in the Actions cache); not released |


## Patch series (on tag 4.1.4)

| Patch | Content | State |
|---|---|---|
| 0001 thrift | TFlightScanNode, TFlightScanRange, TTableType FLIGHT_TABLE (free ids per RESEARCH.md) | done |
| 0002 fe connector | `connector/flight/`: FlightConnector, FlightMetadata (row counts: `clear()` keeps the caches — MetadataMgr calls it after every query —, load started on `getTable`, first caller waits ≤ 250 ms; M4 fix 2026-10-22), FlightProperties (`flight.compression` none|zstd|lz4 → `arrow-compression` header only in the BE scan's call headers (`getScanCallHeaders`), `flight.header.arrow-compression` refused, 2026-10-28; `flight.converted_types`, 2026-10-22; `flight.column_stats`, P2 2026-10-22; `flight.exchange_buffer_mb`, A-4 2026-10-22), column min/max cache (`SELECT min(c), max(c), …` per table, endpoints combined, same bounded wait as row counts; only columns with a range get statistics, others stay UNKNOWN; P2 2026-10-22), FlightTypeMapper (converted top-level types: Time/Interval → VARCHAR, Duration → BIGINT, Decimal256 → DECIMAL(p≤38)/VARCHAR, *View → VARCHAR/VARBINARY/ARRAY; value-converted columns never pushed; P1 2026-10-22), FlightSqlMetadataClient (connect probe: ListActions bounded by `flight.connect_timeout_ms`; `queryRows` for statistics; a failed stream from another server's endpoint no longer moves the catalog connection — P2 regression found by m4 check 6; when every URI failed as unreachable but one was connected when its call failed, that URI is retried once — 2026-10-26, m4 check 6 on server 60e888bc26ec), FlightSqlRenderer (`timeTravel`: `FOR VERSION AS OF <id>` / `FOR TIMESTAMP AS OF TIMESTAMP '<UTC> UTC'`, session zone → UTC; 2026-10-25), FlightAggregationPushdown, FlightRemoteFileDesc, FlightGetRemoteFilesParams; `catalog/FlightTable` (`isTemporal()` = true, 2026-10-25), Table, ConnectorType; Authorizer, StmtExecutor (catalog type); masking (PrintableMap, CredentialUtil, SqlCredentialRedactor, CatalogMgr logs) | compiles (with the series) |
| 0003 be | `be/src/connector/flight_connector.{h,cpp}` (FlightConnector/DataSourceProvider/DataSource, cancel watcher, failover, connect timeout via `grpc.min_reconnect_backoff_ms`, Arrow→Chunk via ParquetScanner converters, conjuncts + LIMIT in the source; registered with the cancel watcher before the first connect; keepalive timeout max(20 s, `flight.keepalive_ms`), was 5 s — M4 fix 2026-10-22; `normalize_batch` rewrites Time/Duration/Interval/Decimal256/*View arrays before the converter — P1 2026-10-22; `exec/connector_scan_node.cpp`: local passthrough exchange behind a Flight scan capped per driver by the scan option `exchange_buffer_mb` — A-4 2026-10-22), ConnectorType FLIGHT + registration, CMakeLists, exec_node FLIGHT_SCAN_NODE (+ collect_scan_nodes), descriptors FLIGHT_TABLE → plain TableDescriptor (no descriptors.h change: ~840 TUs include it); UInt64 columns widened to decimal128(20,0) for DECIMAL slots (our server streams UInt64 in result mode partial where its metadata says decimal128(20,0)); `exec/arrow_to_starrocks_converter.cpp`: Arrow timestamp → DATETIME by floor division (upstream bug: pre-1970 values with a fraction became garbage; M4 fix 2026-10-21) | compiles + links (BE run 39847433502) |
| 0004 fe optimizer/planner | `planner/FlightScanNode` (plan statistics via `computeStatistics`, 2026-10-22); StatisticsCalculator: the connector's known column statistics replace UNKNOWN in `computeFlightScanNode` (P2); Logical/PhysicalFlightScanOperator, FlightScanImplementationRule, **FlightAggregationPushdownRule** (rewriteOnce in QueryOptimizer after RewriteSimpleAggToHDFSScanRule; remote items are bare `fn(expr)`, casts inside: `sum(CAST(x AS T))`; integer sums only in result mode complete — M4 fix 2026-10-21), edits in OperatorType, visitors, RuleSet/RuleType, MultiOpPattern, PushDownPredicateScanRule, PruneScanColumnRule, MergeLimitDirectRule, StatisticsCalculator, RelationTransformer, PlanFragmentBuilder, Explain, LogicalPlanPrinter; SessionVariable `flight_filter_pushdown`, `flight_aggregate_pushdown`; FlightScanNode passes `exchange_buffer_mb` in `TFlightScanNode.options` (A-4) and the scan call headers incl. `arrow-compression` (2026-10-28); PlanFragmentBuilder: the split local aggregation directly above a Flight scan with a pushed aggregation is `force_streaming` when the session mode is `auto` (A-4 headroom, 2026-10-23); time travel (2026-10-25): RelationTransformer resolves `FOR VERSION/TIMESTAMP AS OF` (only AS OF; ranges refused) into `LogicalFlightScanOperator.timeTravel` (part of equals/hashCode, kept by the aggregation rule) → Physical op → `FlightScanNode.setTimeTravel` → REMOTE SQL after the table name | compiles, tests pass (FE run 40227477334) |
| 0005 fe | PushDownTopNToPreAggRule: ORDER BY must cover all GROUP BY keys; PushDownTopNToPreAggRuleTest | test passes (run 39453420117) |
| 0006 fe tests | FlightTypeMapperTest, FlightSqlRendererTest, FlightPropertiesTest, FlightAggregationPushdownRuleTest, FlightScanPlanTest (+ MockedFlightSqlMetadataClient: Flight SQL metadata without a server), FlightSqlMetadataClientTest (in-process Java Flight server: failover from a silent / refused URI, no failover on server errors); FlightScanPlanTest: scan cardinality, small table as broadcast build side in both join orders, caches survive `clear()`; FlightTypeMapperTest/FlightPropertiesTest: converted types, `flight.converted_types`; P2: FlightScanPlanTest range selectivity, column ranges (endpoints combined), min/max values → optimizer doubles, `flight.column_stats=false`; FlightPropertiesTest: `flight.exchange_buffer_mb` default/0/range; FlightScanPlanTest `testPreAggregationAbovePushedAggregationStreams` (A-4 headroom); time travel: FlightSqlRendererTest `testTimeTravel`, FlightScanPlanTest `testTimeTravelIsForwarded` / `testTimeTravelRejectsRangesAndBadValues` (2026-10-25); FlightSqlMetadataClientTest: connected URI retried once / only once (2026-10-26); FlightPropertiesTest `testCompression` (2026-10-28) | all pass (FE run 40668964365, 45 tests incl. PushDownTopNToPreAggRuleTest) |
| 0007 be test | `be/test/connector/flight_connector_test.cpp` (standalone, own main; registered with ADD_BE_TEST): in-process `arrow::flight::FlightServerBase`; type conversion (incl. UInt64→LARGEINT, naive / zoned timestamps), chunk slicing, failover from a refused location, no failover when disabled / on server errors, wrong token, connect timeout against a silent listener, cancel of a blocked read, read limit, conjuncts; basic auth (handshake → bearer, wrong password not leaked), TLS with a self-signed cert generated at test time (root certs + override hostname, TLS + basic auth, hostname mismatch, untrusted cert, `tls_verify=false`, plain client vs TLS server); pre-1970 timestamps with a fraction (ms/us/ns); UInt64 stream into a DECIMAL(20,0) slot; converted types (time32/64, duration, intervals, decimal256 narrow/wide, string/binary/list views); `ReadsCompressedStreams` (server writes ZSTD / LZ4_FRAME IPC bodies when the call carries `arrow-compression`, 2026-10-28) | all pass (be-ut run 39825723598); with ReadsCompressedStreams: be-ut 40668971169 running |

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
- The repo is public since 2026-10-24 (free Actions minutes; see CLAUDE.md). A full BE build on the 4-vCPU runner is many hours; incremental BE builds with a warm ccache are short. Any change to patch 0001 (thrift) regenerates headers used
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

- 2026-10-22 17:39–18:25 UTC (cloud session): **P1 (types now hidden) done.** `flight.converted_types=convert`
  (default; `hide` = old behaviour) exposes top-level TIME32/64 → VARCHAR `HH:MM:SS[.f]`, DURATION → BIGINT (unit
  in the column comment), INTERVAL → VARCHAR ISO-8601, DECIMAL256 → DECIMAL(p≤38) or VARCHAR, Utf8View/BinaryView/
  ListView/LargeListView → VARCHAR/VARBINARY/ARRAY (0002); BE `normalize_batch` rewrites those arrays (0003, also
  absorbs the UInt64 widening); tests in 0006/0007 (BE conversion code pre-checked locally against pyarrow 19.0.1's
  libarrow). StarRocks TIME was not used: it is not a storable column type. Value-converted columns are never
  pushed (filters, aggregates). m4 check 1 `plan_type` and check 2 follow (TIME/INTERVAL compared with the server's
  raw Arrow values via ADBC). Builds: FE 39825739612 (tests green), BE 39825723550, be-ut 39825723598; m4
  39828677269 (int4, series `fl9ec2c3`): 1–9 all PASS (check 2 52/52). Release draft not refreshed (still the
  re-check build `fl6b6a1d`).

- 2026-10-22 18:40–20:15 UTC (cloud session): **P2 (column statistics for the CBO) done.** `flight.column_stats`
  (default true): per table one `SELECT min(c), max(c), …` over the filterable numeric/date columns (≤ 100),
  endpoints combined, cached like row counts (started on `getTable`, row count + min/max share one ≤ 250 ms wait);
  min/max + range NDV (`ConnectorNdvEstimator`) reach `computeFlightScanNode` for those columns, the others stay
  UNKNOWN as before (0002, 0004); plan tests (0006); m4 check 4 asserts the q05 orders estimate (227651). Null
  counts / real NDV not loaded (would need a scan). FE 39834423640 failed (new test allocated Arrow buffers, which
  FE unit tests cannot; moved to value-level test); m4 39840237517 + 39841545485: check 6 regression (see
  M4-RESULTS), fixed in 0002. Final: FE 39842646955, BE 39842650526, m4 39845020831 (series `fl67776b`) 1–9 all
  PASS.

- 2026-10-22 18:44–19:35 UTC (local agent on the maintainer's stand): **local re-check** of series `4a9848e-fl6b6a1d`
  (draft `v4.1.4-flight.0-dryrun`, both build-info files checked) against the rebuilt server int4 (cluster fix), BE
  4G: A-1 fixed (EXPLAIN COSTS q05 real counts, lineitem probe; m4 q05 item PASS), q05/q08/q09/q21 pass at 4G,
  SF10 single node 85/87 vs reference + JDBC (only q18 ×2: memory, A-4) + sr-cases 26/26, 3-node token cluster
  45/45 + 26/26, keepalive item PASS (q18 ×8 at load 36–47, 12 s server freeze ×3 OK; 40 s freeze → clean
  watchdog error), B2/B5 PASS by the stand's int4 server check. Native SF10 total 124.0 s (first run 157.5 s) vs
  JDBC 442.5 s; 3-node 68.5 s (150.9 s). Details `docs/M4-RESULTS.md`; A-4 → Next steps 1.

- 2026-10-22 23:40–00:10 UTC (cloud session): **A-4 fix verified in CI.** The 20:16 session pushed (without a Log
  line) `flight.exchange_buffer_mb` (default 16; 0 = StarRocks' 128 MB): FE passes it in the scan node options
  (0002/0004), the BE caps the local passthrough exchange behind a Flight scan per driver
  (`exec/connector_scan_node.cpp`, `FlightDataSourceProvider::exchange_buffer_bytes_per_driver`, 0003); m4 check 9
  runs q18 with 16 and 0 and compares `LocalExchangePeakMemoryUsage`. Builds: FE 39847449823 (Flight tests green),
  BE 39847433502, be-ut 39847433352; m4 39873438298 (int4, series `4a9848e-fld145f6`): 1–9 all PASS. At SF1 on the
  2-vCPU runner the cap does not bind (exchange peak 2.5 MB vs 2.7 MB, query peak 192 MB), so CI only shows no
  regression; the SF10 effect needs the stand. Draft release `v4.1.4-flight.0-a4` (separate tag, the re-checked
  `v4.1.4-flight.0-dryrun` stays as is) dispatched: release run 39874283999.

- 2026-10-23 00:00–00:15 UTC (cloud session): **P3 lakeFS in CI done.** m4 input `store=lakefs`: `stack.sh lakefs`
  starts `treeverse/lakefs:1.38.0` (local KV, MinIO blockstore), `ci/m4/lakefs.py` loads tpch + types + `lfs.t` into
  repository `m4lake` branch `main` and commits; every `stack.sh flight` then serves `lakefs://m4lake/main/parquet`
  (int4 lakefs plugin). New check 10: a 2-file commit is seen by the next query after 1.1 s, never half of it; a
  delete commit too; a staged (uncommitted) file is not visible (server pins the branch). m4 39874644488 failed at
  setup (lakeFS repo names need ≥ 3 chars) → renamed; m4 39875156594 (`store=lakefs`, checks 1,3,4,10): all PASS
  (25/25, 21/21, 46/46, 5/5); m4 39875877653 (default S3, checks 1,6): PASS after the stack.sh store change.

- 2026-10-23 00:40–01:35 UTC (cloud session): **P5 Iceberg in CI done.** Pinned the int4b/int5/int6 checksums (asset
  digests of `m4-assets`) in `ci/m4/server-jars.sha256`, assets cache key v4. m4 39879641829 (int6, plain S3, checks 1,3:
  PASS) and 39880765661 (int5, check 1: PASS) printed the START-NOTES (Iceberg settings). New m4 input `store=iceberg`
  (int6+): `stack.sh iceberg` starts `apache/iceberg-rest-fixture:1.9.2` (warehouse `s3://lake/parquet/_iceberg`, below
  the dataDir because the server refuses a second s3 store), `ci/m4/iceberg.py` writes namespace `ice` with pyiceberg
  (lineitem, orders, `ren` with a renamed column, `t`), a Spark 3.5.6 container writes `ice.del` with position deletes;
  `stack.sh assets` fetches DuckDB iceberg + avro v1.4.5; the server runs with `-Dcatalog=iceberg-rest`. New check 11.
  m4 39881458465: 19/20 (fixture's in-memory SQLite = one db per connection, the check's own append failed) → SQLite
  file; m4 39882258299: checks 1 (25/25) and 11 (22/22) PASS — deletes applied, rename by field id, append seen by
  partial mode after 5.4 s and complete mode after 24.9 s. Details `docs/M4-RESULTS.md`. Also dispatched m4 1,6,8 on
  int4b: run 39882298126 failed in setup (int4b has no own plugins asset → `stack.sh assets` now uses the base
  build's `int4-plugins.tar.zst` for lettered rebuilds); run 39883591960: checks 1 (25/25), 6 (6/6), 8 (14/14) PASS →
  int4b is now the m4 default (`m4.yml`, `stack.sh`). No patch changed; no fe/be build this session.

- 2026-10-23 01:40–02:10 UTC (cloud session): **P4 upgrade readiness done** (`docs/REBASE.md`). Newest 4.1.x tag is
  4.1.6 (`6862092f`, no 4.1.5). The series `fld145f6` applies with plain `git am` (no conflicts, no fuzz; offsets in
  0002/0004/0007). Semantic review: 7 shared files with harmless upstream changes; thrift ids/enums collision-free;
  FE base classes/SPI unchanged; BE headers additive; risk = FE gRPC 1.63 → 1.76 (grpc-bom) and a cold BE build
  in `dev-env-ubuntu:4.1.6` (thirdparty changed). No patch changed; no CI run this session.

- 2026-10-23 11:03–11:35 UTC (local agent on the maintainer's stand): **A-4 re-check** with draft `v4.1.4-flight.0-a4`
  (both build-info files `4a9848e-fld145f6`, SHA256SUMS OK), server int4 fixed, BE 4G, no spill. q18 SF10 with the default
  exchange cap: 14/14 OK single node, 6/6 OK on 3 nodes, LocalExchangePeak 128 + 128 MB, peak per node 2.35–3.08 GB; with
  `flight.exchange_buffer_mb = 0`: fails (972 + 367 MB, query_pool), i.e. the cap is the fix. Checks 4,5 SF10: 87/89 + 26/26
  single node vs reference + JDBC (fails: SF1-band q05 estimate item; one q18 topn=0 at the BE process limit), 45/46 + 26/26
  on 3 nodes without spill. Remaining peak: pre-aggregation above the pushed aggregation (Next steps 1 (a)). No patch changed.

- 2026-10-23 11:30–12:25 UTC (cloud session): **A-4 headroom items (a) and (b) done in CI.** (a) PlanFragmentBuilder (0004):
  the split local aggregation directly above a Flight scan with a pushed aggregation gets `force_streaming` when the
  session mode is `auto` (its input is partial groups, unique per endpoint; the hash table only doubled the merge's
  memory). Plan test in 0006. First FE run 39946846901 failed to compile (helper inserted between `@Override` and its
  method) → fixed; FE 39948153646: 39/39 Flight tests; BE 39948156366 (`be force`, ccache-only). (b) m4 check 4's q05
  orders band scales with `count(*)` of orders. m4 check 9 notes the q18 pre-aggregation modes (CI: `force_streaming`,
  aggregation pushed). m4 39949914514 (checks 1–9): all pass except check 9 item "exchange peak with the cap <= without"
  (3.5 vs 2.5 MB: at SF1 on 2 vCPUs neither run reaches the cap, noise) → the item now compares only when the uncapped
  peak exceeds 16 MB; m4 39951241481 (checks 4,9): 46/46, 6/6. Series `4a9848e-fl4bda75`; draft release
  `v4.1.4-flight.0-a4b` for the stand (release run 39952272222).

- 2026-10-23 15:26–16:10 UTC (local agent on the maintainer's stand): **A-4b re-check** with draft `v4.1.4-flight.0-a4b`
  (both build-info files `4a9848e-fl4bda75`, SHA256SUMS OK), server int4 fixed, BE 4G, no spill. `EXPLAIN VERBOSE` q18:
  `streaming preaggregation mode: force_streaming` above the pushed `GROUP BY l_orderkey` (single node and 3 nodes, both
  topn). q18 SF10: single node 16/16 OK, peak per node 2.249–2.382 GB, pre-aggregation hash table 192 B, 15 M / 15 M rows
  passed through every run; 3 nodes 8/8 OK, 2.371–2.458 GB; `force_preaggregation` restores the old 2.97–3.03 GB (1.428 GB
  hash table); cap off still fails (query_pool). Checks 4,5 SF10: single node vs reference + JDBC 86/88 + 26/26 (twice) — both
  FAILs are the JDBC reference q18 runs at the BE process limit (profiles: the Flight q18 finished at 2.36 GB, then the `jdbc`
  statement failed; m4.py reports ref-catalog errors under the item of the catalog under test), Flight-only check 4 46/46;
  3 nodes without spill 46/46 + 26/26. q05 orders band PASS at SF10. No patch changed.

- 2026-10-23 16:09–16:45 UTC (cloud session): **int7 in CI done.** `ci/m4/server-jars.sha256` pins
  `arrow-flight-server-1.0.0-int7.jar` (2b9595ab…06fa) and `int7-plugins.tar.zst` (4d2416f4…1af4), both equal to the
  release asset digests; int7 is the default of `m4.yml` / `stack.sh` for every store (int6 no longer needed for
  `store=iceberg`), assets cache key `m4-assets-v5`. Full suite once on series `fl4bda75`: m4 39984493363 (S3, 1–9) all
  PASS, 39984497103 (iceberg, 1 + 11 22/22) PASS, 39987340277 (lakefs, 1,3,4,10) PASS. Next step 1's check-script item done:
  `m4.py` check 4 reports an error of the `--ref-catalog` query as FAIL of `<q> topn=<x> = <ref>` (`ERROR of <ref> …`), the
  item of the catalog under test keeps its own reference comparison. Noticed: `ci-status` was not refreshed since 11:45 —
  `workflow_run` does not fire for runs dispatched by dispatch.yml (GITHUB_TOKEN); request `report` in `ci/dispatch.txt`
  (this session's last push does) or read run results from branch `m4-results`. No patch changed.

- 2026-10-24 22:35 UTC (cloud session): no open item in Next steps (all done; release made locally by the maintainer).
  Marked the release question as answered. No CI run, no patch changed.

- 2026-10-25 05:40–06:30 UTC (cloud session): **server 4eaab052deaf in CI, step 1.** Release `m4-assets` was re-uploaded
  for the public repo (int4/int5/int6 jars gone; `int7-plugins.tar.zst` now bad288e0…, listed in the new SHA256SUMS);
  `ci/m4/stack.sh` derives plugins/libs asset names for server repo CI builds (`arrow-flight-server-<ver>-<commit>-linux.jar`)
  and runs them with their own `libs/` (checked against `libs/SHA256SUMS`; `M4_LIBS` in server.env); assets cache key
  `m4-assets-v6`. m4 40166546587 (S3 1–9) failed before any check: no `fe-out-*` cache and no `fe-jars-*` artifact —
  the public repo has no caches/artifacts at all; m4 40166548012 (iceberg) cancelled. Dispatched fe 40166741833 and
  be 40166743137 (cold BE, part 1 building at session end); fe 40166741833 success. No patch changed.

- 2026-10-25 06:40–07:45 UTC (cloud session): **server 4eaab052deaf in CI, done.** be 40166743137 (cold, no ccache)
  finished in part 1 (Build BE 05:49–07:15 UTC, ~86 min). m4 40172153304 / 40172154565 failed in `stack.sh assets`:
  release asset `arrow-flight-server-1.0.0-int2.jar` of the re-created repo is an unfinished upload (state `starter`,
  download 404); `stack.sh` now skips assets whose state is not `uploaded`. Re-run on series `fl4bda75`: m4 40172422411
  (S3, 1–9) all PASS (202/202), 40172423737 (iceberg, 1 + 11 22/22) PASS (`_iceberg` schema still listed, Open questions),
  40173169121 (lakefs, 1,3,4,10) PASS. `arrow-flight-server-1.0.0-4eaab052deaf-linux.jar` is now the default of `m4.yml` /
  `stack.sh` (docs/M4-CI.md updated). `ci-status` again refreshes only through `report` in `ci/dispatch.txt`
  (`workflow_run` does not fire for GITHUB_TOKEN-dispatched runs); the GitHub MCP / REST runs API works too. No patch changed.

- 2026-10-25 19:35–20:40 UTC (cloud session): **server c3b276054cc3 in CI + time-travel forwarding.** m4 40226830782 /
  40226833988 failed in `stack.sh assets` (release `START-NOTES.md` is still the 4eaab05 copy, its new SHA256SUMS line does
  not match; 40226832318 was cancelled: the `m4` concurrency group keeps one pending run, a third dispatch cancels the
  second — dispatch at most two m4 runs per push); `stack.sh` now verifies only the assets a run uses; assets cache key
  `m4-assets-v7`. On series `fl4bda75`: m4 40227337083 (S3 1–9) all PASS (198/198), 40227338512 (iceberg 1,11) PASS.
  **Connector: `FOR VERSION AS OF <id>` / `FOR TIMESTAMP AS OF <datetime>` forwarded to the server** (0002: FlightTable
  temporal, `FlightSqlRenderer.timeTravel`; 0004: RelationTransformer → scan operators → FlightScanNode; 0006: tests) →
  series `fl536298`: FE 40227477334 (42/42 Flight tests), BE 40228410632 (`be force=true`, ccache-only, 5 min). m4 40228819006
  (lakefs 1,3,4,10) PASS on `fl536298` → **c3b276054cc3 is the m4 default**. m4 40228817126 (iceberg) died in MinIO setup
  (quay.io pull failed, fallback MinIO dropped a PutObject; one re-run); 40229432267 (iceberg 1,11 + time travel): check 1
  PASS, the REMOTE SQL is `SELECT "id" FROM "ice"."t" FOR VERSION AS OF <id>` as intended, but **the server rejects it**:
  partial mode `ParserException: Feature only supported in pro edition` (its SQL parser), complete mode DuckDB `syntax error
  at or near "VERSION"` (Open questions). Time-travel items moved to their own check 12 so check 11 stays a regression
  signal: m4 40229960640 (iceberg 1,11,12): checks 1, 11 PASS (22/22), check 12 1/10 — only the connector's own
  refusal of `FOR VERSION BETWEEN` passes; the session-zone conversion is right (`'2026-10-26 04:21:24'` at +08:00 →
  `TIMESTAMP '2026-10-25 20:21:24 UTC'`), every server path rejects the clause.
- 2026-10-25 23:40 – 2026-10-26 00:25 UTC (cloud session): **server 20b887839edf in CI.** Assets cache key
  `m4-assets-v8`. On series `fl536298`: m4 40245888043 (S3 1–9) all PASS (198/198), 40245889746 (iceberg 1,11,12) all
  PASS incl. **check 12 time travel 10/10** (`FOR VERSION AS OF` both modes, two versions in one query, `FOR TIMESTAMP
  AS OF` at +08:00), 40248225183 (lakefs 1,3,4,10) all PASS → **20b887839edf is the m4 default** (`m4.yml`, `stack.sh`,
  M4-CI, INSTALL). Time-travel open question closed. No patch change.
- 2026-10-26 01:40–03:35 UTC (cloud session): **server 60e888bc26ec (`duckDbThreads` 4) in CI — not the default.**
  Assets cache `m4-assets-v9`. Series `fl536298`: m4 40255396864 (S3 1–9) all PASS except check 6 5/6 ("flight2 stopped
  before the query": GetFlightInfo TIMED_OUT on both URIs, 15.2 s), 40255398491 (iceberg 1,11,12) PASS 57/57. Check 6
  alone: 40259166769 (60e888bc26ec) same FAIL; 40259168469 (20b887839edf) died in MinIO setup; 40262586606 (60e888bc26ec)
  PASS 10.9 s; 40262584557 (20b887839edf) PASS 11.0 s. m4.py check 6 now records fe.log failover lines and flight1
  WARN/SEVERE/member lines when the item fails (artifacts cannot be downloaded from the session: blob host blocked).
  Default stays 20b887839edf. Details `docs/M4-RESULTS.md`. No patch change.
- 2026-10-26 03:40–04:45 UTC (cloud session): **check 6 on server 60e888bc26ec: cause found, FE fix, server made the
  default.** Two more check-6 runs on `fl536298` both PASS (m4 40265277013, 40265278745; tally 3 of 5). The job log of the
  failing 40259166769 (readable via the GitHub API) shows the final error is the FE's 5 s connect probe of flight2, not a
  GetFlightInfo deadline: flight1's GetFlightInfo failed as unreachable during Hazelcast member loss (~10 s), then flight2's
  probe timed out and each URI had had its one try. Fix in 0002 `FlightSqlMetadataClient.withFailover`: if every URI failed
  as unreachable and one was connected when its call failed, retry that URI once; 0006 FlightSqlMetadataClientTest +2 tests
  → series `fldb9219`: FE 40265894284 (44/44; the push-triggered FE run 40265887451 was cancelled by the dispatched one —
  push the `[skip ci]` patch commit and the dispatch commit separately next time), BE 40267006057 (`be force=true`,
  ccache-only). On `fldb9219` / 60e888bc26ec: S3 1–9 40267917390 all PASS, check 6 40267918986 and 40268961132 PASS,
  lakefs 1,3,4,10 40268964021 PASS → **60e888bc26ec is the m4 default** (`m4.yml`, `stack.sh`, M4-CI). m4.py check 6 now
  always notes the query's UTC window and fe.log `trying next location` lines (none in passing runs: the ~5–7 s extra there
  is the BE's connect timeout on flight2's endpoints). Details `docs/M4-RESULTS.md`.
- 2026-10-26 04:40–05:20 UTC (cloud session): optional item done: m4 40270293499 (`store=iceberg`, checks 1,11,12) on
  series `fldb9219` / server 60e888bc26ec all PASS (25/25, 22/22, 10/10) → full suite green on `fldb9219`. No patch change;
  no open CI work left.
- 2026-10-26 06:41–07:35 UTC (cloud session): **server 7fbe2d75827c is the m4 default.** Assets cache `m4-assets-v10`.
  Series `fldb9219`: m4 40281342490 (S3 1–9) all PASS, 40281344356 (iceberg 1,11,12) PASS, 40284404496 (lakefs 1,3,4,10)
  PASS, 40284406938 (check 6) PASS. In 40281342490 check 6 hit the member-loss window (flight1 GetFlightInfo UNAVAILABLE
  after ~10 s, flight2 probe TIMED_OUT, retry of flight1 OK, 15.4 s) — first field confirmation of the `fldb9219` retry;
  server note under Open questions. `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS updated. No patch change.
- 2026-10-26 08:40–10:05 UTC (cloud session): **server 4d707e2aedfc is the m4 default.** Assets cache `m4-assets-v11`.
  Series `fldb9219`: m4 40294026200 (iceberg 1,11,12) PASS; 40294023782 (S3 1–9) died in MinIO setup (quay.io pull failed,
  fallback MinIO dropped a PutObject) → `stack.sh minio` retries each PUT up to 3 times; re-run 40301602799 (S3 1–9) all
  PASS (check 6 10.9 s, no FE failover), 40301606304 (lakefs 1,3,4,10) PASS. `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS
  updated. No patch change.

- 2026-10-26 10:40–11:25 UTC (cloud session): **server 57d252b1437f is the m4 default.** Assets cache `m4-assets-v12`.
  Series `fldb9219`: m4 40309379575 (S3 1–9) all PASS (check 6 10.7 s, no FE failover), 40309382938 (iceberg 1,11,12)
  PASS, 40312075792 (lakefs 1,3,4,10) PASS, 40312078753 (check 6 repeat) PASS but hit the member-loss stall again (flight1
  GetFlightInfo UNAVAILABLE ~10 s after the stop, retry OK, 16.3 s; Open questions). `m4.yml`, `stack.sh`, M4-CI,
  M4-RESULTS updated. No patch change.
- 2026-10-27 04:35–05:15 UTC (cloud session): **server 27f583adccd7 (DuckDB 1.5.6) is the m4 default.** `stack.sh assets`
  picks DuckDB 1.5.6 extensions (httpfs, iceberg, avro from extensions.duckdb.org) for server repo builds after
  57d252b1437f, 1.4.5 for the listed older ones (`M4_DUCKDB` overrides). Assets cache `m4-assets-v13`. Series `fldb9219`:
  m4 40450698707 (S3 1–9) all PASS, 40450700544 (iceberg 1,11,12) PASS, 40452023921 (lakefs 1,3,4,10) PASS, 40452025889
  (check 6 repeat) PASS (10.7 s, member-loss stall not hit). TPC-H check 4 sums: S3 21.3 s (was 27.1), lakeFS 35.0 s
  (was 25.2) — both inside the runners' earlier spread (S3 20.0–27.4, lakeFS 25.1–33.9), so no measurable change in CI.
  `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS updated. No patch change.
- 2026-10-27 05:40–06:20 UTC (cloud session): **server 775100bf923f is the m4 default.** Assets cache `m4-assets-v14`.
  Series `fldb9219`: m4 40456836388 (S3 1–9) all PASS, 40456838963 (iceberg 1,11,12) PASS, 40458183269 (lakefs 1,3,4,10)
  PASS, 40458185120 (check 6 repeat) PASS but hit the member-loss stall (flight1 GetFlightInfo UNAVAILABLE ~10 s after the
  stop, retry OK, 15.2 s; Open questions). TPC-H check 4 sums: S3 25.6 s, lakeFS 34.2 s — inside the runners' spread, so
  the per-query gain is not visible in CI. `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS updated. No patch change.
- 2026-10-27 07:40–08:20 UTC (cloud session): **server 45fc0a9e6e02 is the m4 default.** Assets cache `m4-assets-v15`.
  Series `fldb9219`: m4 40468685156 (S3 1–9) all PASS, 40468687485 (iceberg 1,11,12) PASS, 40470149119 (lakefs 1,3,4,10)
  PASS, 40470151963 (check 6 repeat) PASS but hit the member-loss stall (flight1 GetFlightInfo UNAVAILABLE ~10 s after the
  stop, retry OK, 16.4 s). TPC-H check 4 sums: S3 18.7 s, lakeFS 24.7 s (775100bf923f: 25.6 / 34.2 s) — lowest so far,
  at the edge of the runners' spread. `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS updated. No patch change.
- 2026-10-27 21:40–22:15 UTC (cloud session): **server 4e77c6bda59a is the m4 default.** New server build found in the
  `m4-assets` release (added 20:47 UTC, no STATUS note; DuckDB 1.5.6 default of `stack.sh` worked). Assets cache
  `m4-assets-v16`. Series `fldb9219`: m4 40588875084 (S3 1–9) all PASS, 40588877746 (iceberg 1,11,12) PASS, 40590969944
  (lakefs 1,3,4,10) PASS, 40590972986 (check 6 repeat) PASS (10.9 s, stall not hit); 40588875084 hit the member-loss stall
  (flight1 GetFlightInfo UNAVAILABLE ~10 s after the stop, retry OK, 16.2 s). TPC-H check 4 sums: S3 24.5 s, lakeFS 30.8 s
  (45fc0a9e6e02: 18.7 / 24.7 s) — inside the runners' spread. `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS updated. No patch change.
- 2026-10-28 01:40–02:40 UTC (cloud session): **server cadd1aca9c23 is the m4 default.** Assets cache `m4-assets-v17`.
  Series `fldb9219`: m4 40616536538 (S3 1–9) all PASS, 40616538747 (iceberg 1,11,12, time travel now planned in partial
  mode by the server) PASS, 40619524251 (lakefs 1,3,4,10) PASS, 40619526598 (check 6 repeat) PASS; check 6 "flight2
  stopped" 11.2 s / 10.7 s, the member-loss stall was not hit in either run. TPC-H check 4 sums: S3 25.0 s, lakeFS 23.6 s
  (4e77c6bda59a: 24.5 / 30.8 s) — inside the runners' spread. The connector does not ask for the new opt-in result
  compression, so CI does not exercise it (Open questions). `m4.yml`, `stack.sh`, M4-CI, M4-RESULTS updated. No patch change.
- 2026-10-28 09:59–10:45 UTC (cloud session): **result compression opt-in (maintainer item) implemented; BE builds running
  cold.** 0002: catalog property `flight.compression` = `none` (default) | `zstd` | `lz4`; only the BE scan's call headers
  (`FlightProperties.getScanCallHeaders`, used by FlightScanNode in 0004) carry `arrow-compression: <v>`; the FE's
  metadata/statistics calls never ask (Arrow Java in the FE has no codecs), `flight.header.arrow-compression` is refused.
  No BE source change: the builder's Arrow is built with `ARROW_WITH_ZSTD`/`ARROW_WITH_LZ4` and the IPC reader decodes
  compressed bodies. 0006 FlightPropertiesTest `testCompression`; 0007 BE `ReadsCompressedStreams` (test server writes
  ZSTD / LZ4_FRAME bodies on the header). Series `flf41597`: FE 40668964365 45/45 PASS; BE 40668967450 and be-ut
  40668971169 started 10:03 with **no ccache** (no `ccache-be-*` entry in the Actions cache any more — probably evicted by
  the two ~4 GB `m4-assets-v16/v17` caches), so both are cold builds, still running at session end. m4: new check 13
  (TPC-H on lz4/zstd catalogs vs reference, types tables equal to the uncompressed catalog, wide lineitem read on a plain
  link and under `tc netem delay 10ms rate 1gbit` on sr's host veth: bytes into sr, decoded MB/s; gate: lz4/zstd < 0.8 ×
  the bytes of none) and workflow input `compression` (all catalogs of a run). INSTALL, PLAN §2.1, M4-CI updated. Not yet
  run in CI.

## Next steps

> **Open, 2026-10-28 10:45 UTC: finish the compression item.** (1) Check BE 40668967450 and be-ut 40668971169 (series
> `flf41597`; cold builds, no ccache). If be-ut fails, fix 0007/0003 from its report (a missing codec would show in
> `ReadsCompressedStreams`). If BE fails for a reason unrelated to the patch (time budget of the chained parts), re-dispatch
> `be` once — its ccache is saved per part. (2) When both are green, dispatch `m4 checks=13` and
> `m4 checks=1,2,3,4,5,6,7,8,9 compression=zstd` (server cadd1aca9c23 default); fix m4.py check 13 if the harness itself
> fails (netem module, veth lookup, BytesRead parsing). Report the MB/s table (plain / netem × none / lz4 / zstd) in
> M4-RESULTS and the milestone row. (3) Cache space: `m4-assets-v16` (3.8 GB) is obsolete since v17; with it gone
> the BE ccache fits again — consider a step in m4.yml that deletes older `m4-assets-v*` keys (like be.yml's "Delete older
> ccache entries").
>
> **Maintainer, 2026-10-28: yes to result compression as a connector opt-in.** (implemented 2026-10-28, see Log; CI pending) Add a catalog property (off by default) that
> asks the server for `arrow-compression: zstd|lz4` and decodes compressed IPC bodies; never on unless set. Test: answers
> equal with and without (full suite on one setting), and a slow-link check in CI (`tc netem delay 10ms rate 1gbit` on the
> runner's loopback or between containers) reporting MB/s with off / lz4 / zstd. The server side is in builds since
> `cadd1aca9c23` (assets). Then continue with your own open items.

> **Done 2026-10-28 02:35 UTC (see Log):** server cadd1aca9c23 passes the full suite on series `fldb9219` (S3 1–9 m4
> 40616536538, iceberg 1,11,12 40616538747, lakefs 1,3,4,10 40619524251, check 6 repeat 40619526598) and is the m4
> default (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v17`). CI timings stay within the runners' noise.
> **No open CI work**: sessions stop early until the maintainer adds an item (e.g. answers the compression question in
> Open questions) or a new server build arrives (check the `m4-assets` release assets for a newer
> `arrow-flight-server-1.0.0-<commit>-linux.jar`, not only this file).

> ~~**New server build `server-1.0.0-cadd1aca9c23`**~~ (done, see above) (2026-10-28, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release). Since 7562a5bdb7b9 (so it also covers what 4e77c6bda59a brought): opt-in result
> stream compression ZSTD/LZ4 (stage 3 item 20; the client asks via call header or Flight SQL session option `arrow-compression`;
> buffers compressed in parallel, `flightCompressionThreads`; no default or wire change for clients that do not ask), opt-in S3
> read cache `arrowflight.s3.cacheMegabytes`, size-aware `duckDbThreads` default (cores/4, between 2 and 8; was 4), Iceberg time
> travel planned in partial mode, position deletes grouped. Needs the DuckDB 1.5.6 extension set (server repo `ci-assets`). Run
> the suite once on it (note timings) and make it the CI default if green.


> **Done 2026-10-27 22:10 UTC (see Log):** server 4e77c6bda59a (server repo build after 45fc0a9e6e02, in `m4-assets` since
> 20:47 UTC without a STATUS note — please add one line on what it changes) passes the full suite on series `fldb9219`
> (S3 1–9 m4 40588875084, iceberg 1,11,12 40588877746, lakefs 1,3,4,10 40590969944, check 6 repeat 40590972986) and is
> the m4 default (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v16`). CI timings stay within the runners' noise.
> **No open CI work**: sessions stop early until the maintainer adds an item or a new server build arrives (check the
> `m4-assets` release assets for a newer `arrow-flight-server-1.0.0-<commit>-linux.jar`, not only this file).

> **Done 2026-10-27 08:15 UTC (see Log):** server 45fc0a9e6e02 passes the full suite on series `fldb9219` (S3 1–9 m4
> 40468685156, iceberg 1,11,12 40468687485, lakefs 1,3,4,10 40470149119, check 6 repeat 40470151963) and is the m4
> default (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v15`). TPC-H check 4 sums are the lowest so far (S3
> 18.7 s, lakeFS 24.7 s) but at the edge of the runners' noise; the stand has to confirm. Check 6 repeat hit the
> member-loss stall again (retry OK). Candidate for the presentation build. **No open CI work**: sessions stop early
> until the maintainer adds an item or a new server build arrives.

> ~~**New server build `server-1.0.0-45fc0a9e6e02`**~~ (done, see above) (2026-10-27, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 27f583adccd7 + per-query overhead cuts (stage 2 item 15: describe once per views
> snapshot, parse check once per node, partial-mode sample-file cache, executionPath log line written asynchronously). Needs
> the DuckDB 1.5.6 extension set (server repo `ci-assets`). Candidate for the presentation build: run the suite once on it
> (note small-query timings) and make it the CI default if green.


> **Done 2026-10-27 06:15 UTC (see Log):** server 775100bf923f passes the full suite on series `fldb9219` (S3 1–9 m4
> 40456836388, iceberg 1,11,12 40456838963, lakefs 1,3,4,10 40458183269, check 6 repeat 40458185120) and is the m4
> default (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v14`). Small-query timings in CI stay within the runners'
> noise; the per-query gain needs the stand. **No open CI work**: sessions stop early until the maintainer adds an item
> or a new server build arrives.

> ~~**New server build `server-1.0.0-775100bf923f`**~~ (done, see above) (2026-10-27, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 27f583adccd7 + complete mode describes a query once per catalog-views snapshot
> (per-query overhead, stage 2 item 15 step 1). Needs the DuckDB 1.5.6 extension set (server repo `ci-assets`). Run the suite
> once on it (note small-query timings) and make it the CI default if green.


> **Done 2026-10-27 05:10 UTC (see Log):** server 27f583adccd7 (DuckDB 1.5.6) passes the full suite on series
> `fldb9219` (S3 1–9 m4 40450698707, iceberg 1,11,12 40450700544, lakefs 1,3,4,10 40452023921, check 6 repeat 40452025889)
> and is the m4 default (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v13`). CI timings stay within the runners'
> noise (Log); the small-query gain needs the stand to confirm. **No open CI work**: sessions stop early until the
> maintainer adds an item or a new server build arrives. A later server build with another DuckDB version: set its
> version in `stack.sh assets` (or `M4_DUCKDB`).

> ~~**New server build `server-1.0.0-27f583adccd7`**~~ (done, see above) (2026-10-27, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 57d252b1437f + **DuckDB 1.5.6** (was 1.4.5; upstream comparison: about half of
> the small-query latency gap) + HDFS Kerberos ticket cache from a keytab + cluster crashed-member wait documented. **It needs
> the DuckDB 1.5.6 extension set** (the server checks extension versions at startup): `duckdb-extensions-v1.5.6.tar.zst`
> (httpfs, iceberg, avro, hadoopfs `51b7220-afc3`, layout `extensions/v1.5.6/linux_amd64/`) and
> `hadoopfs-v1.5.6-afc3.duckdb_extension` are in the server repo's `ci-assets` release (sha256 in its SHA256SUMS); official
> httpfs/iceberg/avro 1.5.6 builds also work. Run the suite once on it (note small-query timings) and make it the CI default if green.


> **Done 2026-10-26 11:20 UTC (see Log):** server 57d252b1437f passes the full suite on series `fldb9219` (S3 1–9 m4
> 40309379575, iceberg 1,11,12 40309382938, lakefs 1,3,4,10 40312075792, check 6 repeat 40312078753) and is the m4
> default (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v12`). CI cannot reproduce the stand's 8 concurrent
> partial-mode scans on 3 nodes; that part of the fix needs the stand. **No open CI work**: sessions stop early until
> the maintainer adds an item or a new server build arrives.

> ~~**New server build `server-1.0.0-57d252b1437f`**~~ (done, see above) (2026-10-26, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 4d707e2aedfc + one outbound byte budget shared by all Flight streams
> (the stand saw CANCELLED streams and a dead node under 8 concurrent partial-mode scans on a 3-node cluster). Run the
> suite once on it (failover and concurrent-scan items especially) and make it the CI default if green.


> **Done 2026-10-26 10:00 UTC (see Log):** server 4d707e2aedfc passes the full suite on series `fldb9219` (S3 1–9 m4
> 40301602799, iceberg 1,11,12 40294026200, lakefs 1,3,4,10 40301606304) and is the m4 default (`m4.yml`, `stack.sh`,
> M4-CI; assets cache `m4-assets-v11`). **No open CI work**: sessions stop early until the maintainer adds an item or a
> new server build arrives.

> ~~**New server build `server-1.0.0-4d707e2aedfc`**~~ (done, see above) (2026-10-26, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 7fbe2d75827c + DuckDB retries S3 connect errors for ~6 s (the stand saw
> every complete-mode query fail with "Could not establish connection" on S3 at `duckDbThreads=8`). Run the suite once
> on it and make it the CI default if green.


> **Done 2026-10-26 07:30 UTC (see Log):** server 7fbe2d75827c passes the full suite on series `fldb9219` (S3 1–9 m4
> 40281342490, iceberg 1,11,12 40281344356, lakefs 1,3,4,10 40284404496, check 6 40284406938) and is the m4 default
> (`m4.yml`, `stack.sh`, M4-CI; assets cache `m4-assets-v10`). Check 6 in 40281342490 hit the member-loss window again
> (flight1 GetFlightInfo UNAVAILABLE after ~10 s) and the `fldb9219` retry rescued it — the server change does not remove
> that stall (Open questions). **No open CI work**: sessions stop early until the maintainer adds an item or a new server
> build arrives.

> ~~**New server build `server-1.0.0-7fbe2d75827c`**~~ (done, see above) (2026-10-26, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 60e888bc26ec + planning no longer waits for the cluster to settle after
> a node left (fixes the intermittent GetFlightInfo TIMED_OUT with a stopped member) + `s3a://`/`s3n://` catalog roots +
> the deployment's HDFS short-circuit setting is kept. Run the suite once on it and make it the CI default if green.


> **Done 2026-10-26 04:45 UTC (see Log):** check 6 on server 60e888bc26ec failed because flight1 itself failed
> GetFlightInfo as unreachable for ~10 s during Hazelcast member loss and the FE tried each URI only once; series
> `fldb9219` retries the connected URI once (unit-tested; no CI run hit the window afterwards). 60e888bc26ec is the m4
> default; full suite green (iceberg on `fl536298`). Nothing open on the connector side. If check 6 fails again, read the
> fe.log failover lines in the run's notes before changing anything. The optional iceberg run on `fldb9219` is done
> (m4 40270293499, 1,11,12 all PASS), so the full suite is green on series `fldb9219` / server 60e888bc26ec.
> **No open CI work**: sessions stop early until the maintainer adds an item or a new server build arrives.

> ~~**New server build `server-1.0.0-60e888bc26ec`**~~ (2026-10-26, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` in this repo's assets release) = 20b887839edf + **`duckDbThreads` default 4** (was 1 in code; maintainer
> decision after the perf campaign: SF10 ~1.8x, SF1 ~1.3x faster, small queries unchanged). No protocol change. Run the
> suite once on it and make it the CI default if green; note timings if they change noticeably.


> **Done 2026-10-26 (m4 40245888043 / 40245889746 / 40248225183, see Log):** server 20b887839edf passes the full suite
> (S3 1–9 198/198, iceberg 1,11,12 incl. **time travel 10/10**, lakefs 1,3,4,10) on series `fl536298` and is the m4
> default (`m4.yml`, `stack.sh`; assets cache `m4-assets-v8`). Nothing open on the connector side.

> ~~**New server build `server-1.0.0-20b887839edf`**~~ (done, see above) (2026-10-26, local coordinator; jar, plugins tar, libs tar + merged
> `SHA256SUMS` attached to this repo's assets release). = c3b276054cc3 + **Iceberg time travel** (`FOR VERSION AS OF` /
> `FOR TIMESTAMP AS OF`; c3b276054cc3 did **not** contain it — that earlier note was wrong, which is why the forwarded
> clause was rejected) + fix for parameterized prepared statements with `duckDbStatementCacheSize` 0/1 + Hive metastore
> Kerberos client + local catalog roots under a non-local `fs.defaultFS`. Run the suite once on it, retry the
> time-travel item, and make it the CI default if green. Server bugs → the server repo's Next steps via the coordinator.


> **Done 2026-10-25 (see Log):** server c3b276054cc3 passes the suite (S3 1–9, iceberg 1,11, lakefs 1,3,4,10) and is the
> m4 default. The connector forwards the time-travel clause (series `fl536298`, m4 check 12), but **the server rejects
> it** (Open questions); check 12 goes green once a server build accepts `"schema"."table" FOR VERSION/TIMESTAMP AS OF …`.
> Next: nothing open on the connector side; re-run `m4 checks=1,11,12 store=iceberg` when a fixed server build arrives.

> ~~**New server build `server-1.0.0-c3b276054cc3`**~~ (done, see above) (2026-10-25, local coordinator): = 4eaab052deaf + Iceberg time travel (`FOR VERSION AS OF <snapshot>` / `FOR TIMESTAMP AS OF TIMESTAMP '… UTC'` after an Iceberg table name) + ZooKeeper client and lz4-java back in the runtime libs set (production HA with ZooKeeper). Assets `arrow-flight-server-1.0.0-c3b276054cc3-linux.jar`, `flight-plugins-1.0.0-c3b276054cc3.tar.zst`, `flight-server-libs-1.0.0-c3b276054cc3.tar.zst` (sums in SHA256SUMS). Run the suite once against it; if green make it the default. Connector follow-up: forward the time-travel clause (Trino `FOR VERSION/TIMESTAMP AS OF`, StarRocks own syntax if any) to the server — additive, no approval needed.

> **Done 2026-10-25 (m4 40172422411 / 40172423737 / 40173169121, see Log):** server build 4eaab052deaf passes the full
> suite (S3 1–9, iceberg 1,11, lakefs 1,3,4,10) on series `fl4bda75` and is the default of `m4.yml` / `stack.sh`; int7
> stays available as `server=arrow-flight-server-1.0.0-int7.jar`. The public repo now has FE/BE output caches again
> (`fe-out-436f972b3c05a7ba`, `be-out-9dba754829d38a31`) and a ccache; they expire after 7 days without access.

> ~~**New server build `server-1.0.0-4eaab052deaf`**~~ (done, see above) (2026-10-25, local coordinator; built by the server repo CI from main 4eaab05 = int7 + hadoopfs timeout defaults 3 s / 10 s + dependency security upgrades (Jackson 2.21, Netty 4.2.19, Parquet codecs, Hive libthrift, upstream-sync items) + a fresh, much smaller runtime libs set): assets `arrow-flight-server-1.0.0-4eaab052deaf-linux.jar`, `flight-plugins-1.0.0-4eaab052deaf.tar.zst`, `flight-server-libs-1.0.0-4eaab052deaf.tar.zst` (replaces flight-server-libs.tar.zst for this build), START-NOTES.md (sums in SHA256SUMS). Not stand-verified yet: run your full suite once against it (keep int7 as the fallback default until it is green); report regressions under Open questions.

> **Done 2026-10-23 (m4 39984493363 / 39984497103 / 39987340277, see Log):** ~~**Use server int7** (2026-10-23, local coordinator): `arrow-flight-server-1.0.0-int7.jar` sha256 2b9595ab…06fa + `int7-plugins.tar.zst` sha256 4d2416f4…1af4 (plugins s3/lakefs/iceberg/hive + START-NOTES.txt) = int6b + all stand fixes (lakeFS: JOIN commit mixing, complete-mode lag, tags; Iceberg: file:/s3a roots, LocalFileSystem, Gravitino errors; Hive: HDFS paths with space/%, out-of-root partitions hidden, metastore fail-fast, UNAVAILABLE on outage; Iceberg equality deletes read all columns — correct, slow). Replace int6/int6b in CI with int7; rerun the full suite once.~~

> **Use server int6 instead of int5** (2026-10-22, local coordinator): int5 overflows its stack on the first table refresh ~30 s after start when any catalog is configured AND the data dir has a table (then every call fails "Application error processing RPC"). int6 = int5 + fix + catalog plugin `hive` (Hive Metastore; SPI 1.1): assets `arrow-flight-server-1.0.0-int6.jar` sha256 78f06212…8d09, `int6-plugins.tar.zst` sha256 fa870ddb…adaf (plugins s3/lakefs/iceberg/hive + START-NOTES.txt). With the iceberg plugin present, `catalog=hive` needs the iceberg+avro extensions or `hive.icebergTables=skip`.

1. **A-4 (q18 SF10 at BE `mem_limit = 4G`, memory) — settled on the stand 2026-10-23 (draft `v4.1.4-flight.0-a4b`,
   series `fl4bda75`, see Log and `docs/M4-RESULTS.md`).** q18: `force_streaming` pre-aggregation above the pushed
   `GROUP BY l_orderkey`, pure passthrough, peak per node 2.25–2.38 GB single node (16/16) and 2.37–2.46 GB on 3 nodes
   (8/8), no ~3.0 GB mode; checks 4,5 SF10 = reference (= JDBC) apart from the JDBC reference's own q18 at the process
   limit; 3 nodes 46/46 + 26/26. The check-script item (ref-catalog errors under their own item) is done (2026-10-23).
   Nothing open; the release (item 2) waits on the maintainer.
2. **Done 2026-10-25 by the maintainer: v4.1.4-flight.1 released LOCALLY (not on GitHub) from the stand-verified build of series `fl4bda75`. Do not create a public GitHub release.** ~~After item 1 is settled (stand re-check of `v4.1.4-flight.0-a4b`) and the maintainer agrees: refresh the draft for the
   newest series (now `fl4bda75`, adds P1 + P2 + A-4 cap + force-streaming pre-aggregation; or release `fl6b6a1d` if the maintainer prefers the re-checked build — see Open questions), then
   `release tag=v4.1.4-flight.1 draft=false prerelease=false`; delete the `v4.1.4-flight.0-dryrun`, `v4.1.4-flight.0-a4` and `v4.1.4-flight.0-a4b` drafts. Retention: CI artifacts 7 days, caches evicted
   after 7 days without access — after a long pause expect a full BE rebuild (~90 min). Every patch change needs
   FE **and** BE outputs of the new series before `m4` or `release` (the other side: `fe/be force=true`).
3. Done by P2 (column min/max + range NDV in `computeFlightScanNode`, series `fl67776b`).


### Parallel work while the local re-check is pending (maintainer, 2026-10-22 evening)

Item 1 waits for the maintainer's stand; do these in the meantime, one per session, in this order. Each must keep
`m4` green; batch BE changes (one BE build per session at most).

P1. **Done 2026-10-22 (series `fl9ec2c3`, see Log).** ~~**Types now hidden** (`docs/M4-RESULTS.md`: TIME, INTERVAL hidden; PLAN §1.5: DECIMAL256, TIME32/64, DURATION,
    INTERVAL, *View types and UNION not covered). Map what StarRocks can represent: TIME32/64 → TIME (or VARCHAR
    'HH:MM:SS[.ffffff]' if TIME is not usable for external tables), DURATION → BIGINT (unit in the column comment),
    INTERVAL → VARCHAR (ISO-8601), DECIMAL256 → DECIMAL256/LARGEINT where precision allows else VARCHAR,
    Utf8View/BinaryView/ListView → their non-view equivalents (cast in the BE converter). Catalog option to keep
    hiding them. FE type mapping + BE converters + be-ut + m4 check 2 (the alltypes tables already carry TIME and
    INTERVAL; extend the expected list).~~ Not covered by the CI data: DURATION, DECIMAL256 and *View columns
    (DuckDB/our server never produce them); covered by be-ut/FE unit tests only.
P2. **Done 2026-10-22 (series `fl67776b`, see Log).** ~~**Column statistics for the CBO** (Next steps 3 made concrete): our servers answer `SELECT count(*), min(c),
    max(c)` from Parquet footers cheaply (the Trino plugin uses that); use per-column min/max/null counts (and an
    NDV estimate when available) in `computeFlightScanNode`, cached like row counts, bounded wait, off by catalog
    option. Plan tests: join order for TPC-H q05/q08/q09 at SF1 in m4 equals the JDBC catalog's or better.~~ CI has
    no JDBC catalog: m4 records the q05/q08/q09 plan outlines and scan estimates as notes; the join-order comparison
    with the JDBC bridge belongs to the local re-check (`m4.py --ref-catalog`, EXPLAIN of q05/q08/q09 on both).
P3. **Done 2026-10-23 (m4 input `store=lakefs`, check 10, see Log).** ~~lakeFS through the connector in CI: lakeFS
    container in front of MinIO, checks 1, 3, 4 there plus a "commit to main between two queries" check.~~
P5. **Done 2026-10-23 (m4 input `store=iceberg`, check 11, server int6, see Log).** ~~**Server int5 with Iceberg** (release asset `arrow-flight-server-1.0.0-int5.jar` sha256 01feeb77…5808 +
    `int5-plugins.tar.zst` sha256 f600585d…5f68 with `plugins/{s3,lakefs,iceberg}` and START-NOTES.txt = int4 + catalog
    plugin `iceberg`: kinds `iceberg-hadoop` (warehouse dir on local/HDFS/S3) and `iceberg-rest` (Gravitino/Polaris);
    `-Dcatalog=` list; partial mode pins the snapshot per query, falls back to a complete answer with delete files /
    nested schema changes / joins). Add an Iceberg variant to CI: generate Iceberg tables in the job (e.g. pyiceberg
    with a local SQL catalog writing parquet into the S3 bucket, or Spark/iceberg if simpler): TPC-H SF1 lineitem/orders
    as Iceberg + a table with position/equality deletes + a renamed column; check the engine sees them, results equal
    the parquet tables / DuckDB, partial and complete modes; a commit between two queries is seen by the second only.~~
    Not covered: equality deletes (Spark cannot write them), `catalog=hive` (int6; needs a Hive Metastore container).
P4. **Done 2026-10-23 (`docs/REBASE.md`, see Log).** ~~**Upgrade readiness**: try the patch series on the newest 4.1.x tag (`git am` only, no build unless it applies
    with small fixes); write `docs/REBASE.md` with conflicts and effort. Do not change the release target (4.1.4).~~
    Newest tag 4.1.6: all 7 patches apply unchanged (offsets only); no 4.1.6 build run (see Open questions).

All parallel items P1–P5 are done (2026-10-23); until the stand reports on item 1, sessions have no open CI work.

Done 2026-10-23: server `int4b` (cluster fixes B5 / ticket secret) is the m4 default; checks 1, 6, 8 PASS on it (run
39883591960). Checks 2–5, 7, 9 last ran on int4 (same build apart from the cluster fixes).

## Open questions for the maintainer

- ~~**Result compression**~~ answered 2026-10-28 (yes, opt-in): implemented as `flight.compression` (see Log).

- **Server 45fc0a9e6e02 (2026-10-27), for the server repo (no decision needed):** the ~10 s member-loss stall is still
  there: in m4 40470151963 flight1 answered GetFlightInfo UNAVAILABLE at 08:06:41.6 UTC, ~10 s into the query after
  flight2 was stopped (query 08:06:31–08:06:47, rescued by the connector's retry; 4th hit in the last 8 check-6 runs).
  Logs in artifact `m4-40470151963` (7 days).
- **Server 775100bf923f (2026-10-27), for the server repo (no decision needed):** the ~10 s member-loss stall is still
  there: in m4 40458185120 flight1 answered GetFlightInfo UNAVAILABLE at 06:06:32.3 UTC, ~10 s into the query after
  flight2 was stopped (query 06:06:22–06:06:38, rescued by the connector's retry; 3rd hit in the last 6 check-6 runs).
  Logs in artifact `m4-40458185120` (7 days).
- **Server 57d252b1437f (2026-10-26), for the server repo (no decision needed):** the ~10 s member-loss stall is
  unchanged: in m4 40312078753 flight1 answered GetFlightInfo UNAVAILABLE at 11:12:05.9 UTC, ~10 s after flight2 was
  stopped (query 11:11:55–11:12:11, rescued by the connector's retry). Logs in artifact `m4-40312078753` (7 days). The
  shared outbound byte budget (8 concurrent partial-mode scans on 3 nodes) is not reproducible in CI; please confirm it
  on the stand.
- **Server 7fbe2d75827c (2026-10-26), for the server repo (no decision needed):** the ~10 s stall is still there with
  a stopped member: in m4 40281342490 flight1 failed GetFlightInfo as UNAVAILABLE ~10 s after flight2 was stopped
  (06:47:31 → 06:47:41.6 UTC; fe.log). The connector's retry of the connected URI made the query succeed (15.4 s); the
  repeat check-6 run 40284406938 did not hit it (10.9 s). The fix "planning no longer waits for the cluster to settle"
  apparently does not cover this path (maybe the `server-registry` PutIfAbsent retry seen on 60e888bc26ec). Logs of
  flight1 are in artifact `m4-40281342490` (7 days).
- **Server 60e888bc26ec (2026-10-26), for the server repo (no decision needed):** during member loss (flight2 stopped)
  flight1 failed a GetFlightInfo as unreachable after ~10 s while its `server-registry` PutIfAbsent was retried
  (02:31:59–02:32:08, SEVERE `NormalResponse already responseReceived`, m4 40259166769). The connector now retries the
  connected URI once, so the query survives; a server that kept answering (or answered UNAVAILABLE fast) would avoid the
  ~10 s stall. 60e888bc26ec is the CI default now.

- ~~**Server c3b276054cc3, time travel (2026-10-25, m4 40229960640 check 12):**~~ **Answered 2026-10-26:** server 20b887839edf accepts the clause in both modes (m4 40245889746 check 12 10/10). Original note: the connector sends e.g.
  `SELECT "id" FROM "ice"."t" FOR VERSION AS OF 2502034534997902380` and `… FOR TIMESTAMP AS OF TIMESTAMP '2026-10-25 20:21:24 UTC'`
  (Iceberg REST catalog table `ice.t`). Partial mode answers `INVALID_ARGUMENT: ParserException: Feature only supported in pro
  edition: [1:32] … FOR [*]VERSION AS OF …` (the server's SQL parser), complete mode `Parser Error: syntax error at or near
  "VERSION"` (DuckDB). So the clause is not handled before parsing, at least with quoted identifiers. Please check on the
  server side (or tell me another syntax to send; the connector renders it in one place, `FlightSqlRenderer.timeTravel`).
- Release `m4-assets` (2026-10-25): `START-NOTES.md` is still the 4eaab05 upload (05:24 UTC) while SHA256SUMS (18:26 UTC) lists
  a different hash for it; re-upload the c3b276054cc3 START-NOTES.md if you want it there (`stack.sh` no longer checks it).

- Release `m4-assets` (2026-10-25): the asset `arrow-flight-server-1.0.0-int2.jar` is an unfinished upload (state `starter`,
  404 on download; `stack.sh` skips it). Only needed for `server=…-int2.jar` runs; re-upload it or delete it, as you prefer.
  The int4/int5/int6 jars and plugins are gone from the release, so `server=` works with int1, int7 and 4eaab052deaf only (int4b needs the missing `int4-plugins.tar.zst`).

- ~~**Release (2026-10-23):** waiting for your go on `v4.1.4-flight.1`.~~ **Answered 2026-10-25:** released locally by
  the maintainer from series `fl4bda75`; no public GitHub release (the only GitHub release is `m4-assets`; no drafts left).

- A-4 headroom (2026-10-23): **answered by the stand re-check** of `v4.1.4-flight.0-a4b` — peak per node 2.25–2.46 GB on
  every run, `force_streaming` in `EXPLAIN VERBOSE`, q05 orders band passes at SF10 (see Log). Nothing open on A-4.

- P4 (2026-10-23): the series applies unchanged to 4.1.6 (`docs/REBASE.md`). Do you want a trial build on 4.1.6
  (first FE-only compile + Flight unit tests ≈ 15 min after making the tag a workflow input; a full BE build is
  cold, ≈ 90+ min)? Default plan: no build until you ask; release target stays 4.1.4.

- P5 (2026-10-23), server finding (minor): with `-Dcatalog=iceberg-rest` and the warehouse below the dataDir (required:
  a second s3 store is refused), the dataDir listing also shows the warehouse directory as a schema (`_iceberg`, table
  `ice`; still so with int7, m4 39984497103). The server could skip catalog roots (or `_`/`.` directories) in the dataDir listing. No connector change needed.

- A-4 (2026-10-22): `flight.exchange_buffer_mb` defaults to 16 MB per driver (StarRocks uses 128 MB for every scan).
  A smaller buffer can make a fast Flight scan wait more often for slow consumers; m4 timings did not move at SF1.
  Please re-check q18 at 4G with draft `v4.1.4-flight.0-a4` (Next steps 1). Keep 16 as the default? Default plan: yes.
- P2 (2026-10-22) adds a background `SELECT min(c), max(c), …` per table (default on, `flight.column_stats=false`
  turns it off). Our servers answer it from Parquet footers; on a backend without footer statistics it is a full
  scan per table every `flight.stats_cache_ttl_s` (600 s). Keep it on by default? Default plan: on.
- P1 (2026-10-22) changed the visible schema: TIME and INTERVAL columns now appear as VARCHAR by default (option
  `flight.converted_types=hide` restores the old schema). The local re-check runs on the draft of series
  `fl6b6a1d` (without P1). Release the re-checked build, or the newest series (m4 1–9 green)? Default plan: the
  newest series, since m4 covers the changed paths.

- Server findings (a) partial mode rejecting `CAST(sum(x))`, (b) UBIGINT streamed as `uint64` in partial mode:
  fixed in server int2 (verified by m4 run 39695113106). The connector keeps its workarounds (no integer
  `sum` push in partial mode, UInt64 → DECIMAL(20,0) widening) so int1-era servers stay supported. If you want
  integer sums pushed in partial mode for int2+ servers, say so (it would need a server-version or catalog switch).
- Release `m4-assets`: its SHA256SUMS does not list the int2/int4 jars and `int4-plugins.tar.zst`; their hashes
  are pinned in `ci/m4/server-jars.sha256` (int4 values checked against the asset digests of the release). If you
  re-upload SHA256SUMS with them, nothing needs to change here.
- **Server (s3p4 / check int4) items from the local final check, not fixable in the connector:** B5 silent
  partial result after losing 2 of 3 members (Hazelcast "Promotion commit failed"), B2 no backup locations, A-2
  DuckDB fatal error in a pushed q18 aggregation. **Re-check 2026-10-22:** B2/B5 pass against the rebuilt int4 (jar md5 `ff3d6a72…`, cluster fix for member loss / ticket secret = the expected `int4b`); A-2 not seen with DuckDB 1.4.5 (70 stress rounds on the stand; s3p4/DuckDB 1.4.1 reproduced it).

- **Done 2026-10-22 (FAILED, see Next steps 1a):** **`docs/LOCAL-FINAL-CHECK.md`** (≈2–3 h on the stand: SF10 hadoopfs vs `bench/reference/sf10`
  and the JDBC catalog with `ci/m4/m4.py`, Trino timings, 3-node kill tests, auth/TLS/profile/log grep). Build
  under test: draft release `v4.1.4-flight.0-dryrun` (series `4a9848e-fl598360`). It assumes `bench/reference/sf10`
  has the layout of `tests/m4/reference/sf1` (`qNN.tsv` + `qNN.cols`); if not, the JDBC comparison still covers
  correctness — tell me the layout and I adapt the harness. The allin1 paths of `docs/INSTALL.md` §2a are verified
  by `m4.yml`.
- Release naming: the workflow takes any tag `v…`; proposed `v4.1.4-flight.N`. Publishing (draft → public, which
  creates the git tag) is left to you after M4.
- 2026-10-21 (maintainer): M4 moves to CI as far as possible (docs/M4-CI.md); only a short final check runs on
  the local stand. The repo is public since 2026-10-24.
- 2026-10-22 02:30 MSK (local coordinator): server fixes for both M4 findings are in int2 (now the m4 default; all checks pass, m4 run 39695113106). The local final check (agent on the maintainer's stand) starts after the running speed benchmark; it writes its results here and to M4-RESULTS.md.
