# Rebase readiness (newest 4.1.x)

Checked 2026-10-23 (STATUS P4). The release target stays **4.1.4**; this file only records what moving the series
to a newer 4.1.x tag would take.

## Target

- Newest 4.1.x tag upstream: **4.1.6** (commit `6862092fd57e95a892fdfd465ac4ae3a9beefbe1`, 2026-09-29). There is no
  4.1.5 tag (and no `dev-env-ubuntu:4.1.5` / `allin1-ubuntu:4.1.5` image); `starrocks/dev-env-ubuntu:4.1.6` and
  `starrocks/allin1-ubuntu:4.1.6` exist on Docker Hub.
- 4.1.4 → 4.1.6: 3678 files changed (+98k / −12k lines).

## Result: the series applies unchanged

Series as of 2026-10-23 (`fld145f6`, patches 0001–0007) on a shallow clone of 4.1.6:

- `git am` (exact context, no `-3`): all 7 patches apply, no conflicts, no fuzz. `git am -3` gives the same tree.
- Hunk offsets only (`git apply -v`): 0001 none; 0002 two (+4, +53 lines); 0003 none; 0004 five (+1…+26);
  0005, 0006 none; 0007 one (+18, `be/test/CMakeLists.txt`).

Reproduce:

```sh
scripts/prepare-source.sh src
git -C src fetch --depth 1 origin tag 4.1.6
git -C src checkout -B rebase 4.1.6
git -C src am --keep-cr --whitespace=nowarn ../patches/*.patch
```

## Semantic review (no build)

Files touched by both the series and upstream 4.1.4..4.1.6 (7 of our 61):

| File | Upstream change | Effect on us |
|---|---|---|
| `qe/SessionVariable.java` | +26: new variables (e.g. `enable_explain_in_profile`) | none; no name clash with `flight_*` |
| `qe/StmtExecutor.java` | +94/−7 | none (our hunk is elsewhere; applies at offset) |
| `sql/analyzer/Authorizer.java` | +275/−15 (Ranger 2.9 work) | none seen; our hunk applies unchanged |
| `sql/optimizer/QueryOptimizer.java` | +10 | none; our `FlightAggregationPushdownRule` rewrite stays at its place |
| `sql/optimizer/transformer/RelationTransformer.java` | USING full-outer-join refactor, CTE inline fix | none; Flight scan case untouched |
| `sql/plan/PlanFragmentBuilder.java` | +35/−10 | none; helpers we call (`prepareContextSlots`, `ScalarOperatorToExpr`) unchanged |
| `be/test/CMakeLists.txt` | new upstream tests | none (offset only) |

Other checks:

- **Thrift**: `PlanNodes.thrift` and `Types.thrift` unchanged upstream; `Descriptors.thrift` only adds
  `TIcebergSchemaField.is_optional`. Our appended ids (`TScanRange` 31, `TPlanNode` 86, `FLIGHT_SCAN_NODE`,
  `FLIGHT_TABLE` at the enum ends) do not collide.
- **FE base classes / SPI** we extend or implement (`ScanNode`, `LogicalScanOperator`, `PhysicalScanOperator`,
  `Table`, `Connector`, `ConnectorMetadata`, `TransformationRule`, `ImplementationRule`, `GetRemoteFilesParams`,
  `RemoteFileDesc`): unchanged. Of the 99 StarRocks classes we import, 6 changed upstream (`FunctionSet`,
  `Config`, `ConnectContext`, `GlobalStateMgr`, `ConstantOperator`, `Type`); none removed a member we use.
- **FE dependencies**: `grpc.version` 1.63.0 → **1.76.0**, now managed by `grpc-bom` (upstream did it because Arrow
  flight-core pulled `grpc-netty` at its own version); `arrow.version` stays 18.0.0, netty 4.1.136 → 4.1.137.
  Our FE Flight client uses flight-core 18.0.0 + `CredentialCallOption`; it compiles against the same Arrow API,
  but the gRPC jump is the main runtime risk (TLS, keepalive, headers) → m4 checks 1, 6, 7, 8 needed.
- **BE**: the 28 StarRocks headers we include: only `common/config.h` (configs moved/added; we use none of the
  removed ones), `util/logging.h` (`update_logging()` now returns `Status`; we do not call it), `util/mem_info.h`
  (additive) changed. `exec/connector_scan_node.*`, `connector/connector.h`, the local exchange memory manager
  (A-4 cap) and the Chunk/column APIs we use are unchanged or additive (`BinaryColumn` adds methods;
  `ChunkSource` normalizes heavy-expr columns, generic). Arrow C++ in thirdparty is unchanged.
- **Thirdparty / builder**: starcache v4.1-rc3 → v4.1.4, starlet v4.1.1 → v4.1.4, pprof, new jemalloc/poco patches
  → the BE must be built in `dev-env-ubuntu:4.1.6`, i.e. a cold BE build (no usable ccache, ~90 min+ on 4 vCPU,
  probably more than one `be-part`).

## What an upgrade would change in this repo

Effort estimate: patches **none expected**; repo plumbing ~1 session; CI one cold BE build + FE build + m4 1–9.

1. `scripts/prepare-source.sh`: `TAG`, `TAG_COMMIT` (the script already takes `STARROCKS_TAG` /
   `STARROCKS_TAG_COMMIT` from the environment).
2. `ci/env.sh`: `DEV_IMAGE` (4.1.6 tag + digest), `STARROCKS_VERSION`.
3. Workflows with a literal `4.1.4`: `fe.yml` (4: version string, `fe-*-4.1.4.jar` copy, `git log 4.1.4..`),
   `be.yml`, `be-part.yml`, `release.yml` (3), `m4.yml` (2, allin1 image); `ci/release.sh` (series string
   `4.1.4-<base>-fl…`), `ci/m4/stack.sh` (2), `scripts/export-patches.sh` (base tag). Better: read all of them from
   `ci/env.sh` first, then the upgrade is a two-line change.
4. Docs: INSTALL (7 mentions), README, M4-CI, LOCAL-FINAL-CHECK.
5. Caches: new input hashes → `fe-out-*`/`be-out-*` rebuild; `m2-*` Maven cache key changes with the pom (new grpc).

## Not done

No 4.1.6 build was run (P4 says no build unless the series needs fixes, and it needs none; a cold BE build costs
~90+ Actions minutes). A cheap first step if wanted: FE-only compile + Flight unit tests on 4.1.6 (~15 min) after
step 3 above makes the tag a workflow input.
