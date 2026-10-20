# starrocks-flight

StarRocks **4.1.4** with a native **Arrow Flight SQL external catalog** (`"type" = "flight"`): the FE reads
metadata over Flight SQL, the BE reads the result endpoints directly with Arrow Flight C++ (DoGet) and converts
Arrow batches into StarRocks chunks. No JVM in the scan path.

This repository holds only our changes, as a patch series on top of the upstream tag, plus the build scripts and
CI. It does not contain a copy of StarRocks.

| Path | Content |
|---|---|
| `patches/` | `git format-patch` series on tag `4.1.4` (commit `4a9848edf03f`), applied in file-name order |
| `scripts/prepare-source.sh` | shallow-clones tag 4.1.4 and applies the series (`git am`) |
| `scripts/input-hash.sh` | content hash of the FE / BE build inputs (used to skip unchanged builds) |
| `ci/` | build scripts run inside the official builder image `starrocks/dev-env-ubuntu:4.1.4` |
| `.github/workflows/fe.yml` | FE build → `starrocks-fe.jar`, `fe-core-4.1.4.jar`, other `fe-*` jars |
| `.github/workflows/be.yml` | BE build → `starrocks_be` (Release, no debug info), resumable across up to 4 jobs |
| `.github/workflows/be-ut.yml` | BE unit test `flight_connector_test` (in-process Flight server), built in the Release tree with the BE ccache (`ci/build-be-ut.sh`) |
| `.github/workflows/dispatch.yml` | starts fe / be / be-ut / report runs from `ci/dispatch.txt` (for sessions that can only push) |
| `.github/workflows/ci-report.yml` | publishes CI state to branch `ci-status` (`STATUS-CI.md`) |
| `docs/` | `STATUS.md` (current state), `PLAN.md` (design), `RESEARCH.md` (source survey), install guide |

## Building

CI (GitHub Actions) builds on push when the relevant patches change, or manually (`gh workflow run fe` /
`gh workflow run be`). Outputs are workflow artifacts (`fe-jars-<hash>`, `starrocks_be-<hash>`) and, for
releases, GitHub Release assets.

Local build (needs ~40 GB disk, Docker or Podman):

```bash
scripts/prepare-source.sh src
. ci/env.sh
docker run --rm -v "$PWD/src:/workspace" -v "$PWD/ci:/ci:ro" -v "$HOME/.m2:/root/.m2" "$DEV_IMAGE" /ci/build-fe.sh
docker run --rm -v "$PWD/src:/workspace" -v "$PWD/ci:/ci:ro" -v "$HOME/.ccache-sr:/ccache" -e JOBS=8 "$DEV_IMAGE" /ci/build-be.sh
# results: src/output/fe/lib/*.jar, src/output/be/lib/starrocks_be
```

Install: see `docs/INSTALL.md`.

## Patch naming

Each patch subject starts with its area (`thrift:`, `fe:`, `be:`), so the file names select which CI build a
change triggers (`*-thrift-*` → FE and BE, `*-fe-*` → FE, `*-be-*` → BE). Regenerate the series with

```bash
scripts/export-patches.sh src
```
