# M4 in GitHub Actions

Goal: run as much of M4 (PLAN.md §4) as possible in CI, so connector bugs are found and fixed without the
maintainer's stand. The maintainer only runs a short final check locally (section 6). This file is the brief for
the cloud sessions that build this; extend it as the workflow takes shape.

**The repo is private again (2026-10-21) because of the assets below. Never make it public, never attach these
assets to a product release, never copy the server jar anywhere else.**

## 1. Inputs

Release `m4-assets` (prerelease, not a product release; download in a workflow with
`gh release download m4-assets -R "$GITHUB_REPOSITORY"` and `GH_TOKEN: ${{ github.token }}`, `contents: read`):

| Asset | Content |
|---|---|
| `arrow-flight-server-1.0.0-int1.jar` | our Arrow Flight SQL server (DuckDB 1.4.1 inside), shaded, Linux only. Needs **JDK 21** (not 24+) |
| `flight-server-libs.tar.zst` | `libs/` — runtime jars that must be on the classpath next to the server jar (`-cp "server.jar:libs/*"`) |
| `tpch-sf1-parquet.tar.zst` | `sf1/tpch/<table>/data_N.parquet` — TPC-H SF1, the exact files `tests/m4/reference/sf1` was computed from |
| `SHA256SUMS` | checksums |

In the repo, `tests/m4/`:

| Path | Content |
|---|---|
| `queries/q01..q22.sql` | TPC-H queries as used on the bench (schema `tpch`) |
| `reference/sf1/` | DuckDB 1.4.1 answers on the SF1 data: `qNN.tsv` (rows, tab-separated), `qNN.cols` (name, type, `key` = sort key), `MANIFEST.tsv` (rows, columns, sha256 prefix) |
| `data/types/alltypes*/…parquet` | the bench "all types" tables (every Arrow type the server can produce) |
| `sr-cases/` | 26 StarRocks spot checks (`sr-cases.sql`) used against the JDBC bridge; `sr-cases.ref` is for **SF10** — regenerate the reference on SF1 with DuckDB (same SQL on the parquet files), keep the comparison logic of `sr_cases.py` (decimal rounding to 4 places, sort unless ORDER BY) |
| `starrocks/fe.conf`, `be.conf` | the bench StarRocks configuration (all-in-one image) |

## 2. Server start (as on the bench; S3 mode through MinIO is the proven path)

```bash
# MinIO (any recent image), bucket `lake`; upload sf1/ contents to s3://lake/parquet/ (→ schema tpch) and the
# types tables the same way (check the resulting schema/table names with SHOW DATABASES / SHOW TABLES).
# DuckDB httpfs for the server's DuckDB 1.4.1:
curl -sSfL http://extensions.duckdb.org/v1.4.1/linux_amd64/httpfs.duckdb_extension.gz | gunzip > httpfs.duckdb_extension

LANG=C.UTF-8 MALLOC_ARENA_MAX=4 FLIGHT_ALLOW_INSECURE=true \
FLIGHT_S3_ACCESS_KEY=<minio user> FLIGHT_S3_SECRET_KEY=<minio password> \
java --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED \
  --add-opens java.base/java.nio=ALL-UNNAMED -Darrow.enable_unsafe_memory_access=true -DmetricsEnabled=false \
  -DdataDir=s3://lake/parquet -Ds3Endpoint=http://<minio host>:9000 \
  -DduckDbHttpfsExtension=$PWD/httpfs.duckdb_extension \
  -DioParallelism=4 -DduckDbMemoryLimit=1GB -DduckDbThreads=2 -DflightBackpressureThresholdBytes=16777216 \
  -Xmx2g -XX:MaxDirectMemorySize=1g \
  -cp "arrow-flight-server-1.0.0-int1.jar:libs/*" pro.surpin.data.arrowflight.server.HadoopArrowFlightServer \
  --localhost <this host name> --hosts <comma-separated host names of all servers>
# ready when the log shows "Server Arrow Flight SQL started"; port 32010; "Error starting" / SIGSEGV = failed.
```

- The MinIO credentials are throwaway values generated in the job (never a real secret, never in the repo).
- Auth modes (server env): open `FLIGHT_ALLOW_INSECURE=true`; token `FLIGHT_AUTH_PROVIDER=token FLIGHT_AUTH_TOKEN=<t>`
  (Bearer `<t>` or Basic user:`<t>`); TLS `FLIGHT_TLS_CERT=<crt> FLIGHT_TLS_KEY=<pkcs8 key> FLIGHT_BEARER_TOKEN=<t>`
  (self-signed cert generated in the job, SAN = the server host names).
- Result mode / backups are `-D` flags (env vars are shadowed by the bundled properties): `-DresultMode=partial|complete`.
- Two servers (`--hosts a,b`, each with its own `--localhost`) form a cluster: GetFlightInfo returns endpoints on
  both, each endpoint lists the other node as a backup location. That is what failover tests need.
- Metadata endpoints carry no location by default (`-DmetadataEndpointLocation=advertised` to change).
- After a DuckDB FATAL error the server replaces that thread's DuckDB (log `duckdb=sessionDropped`).

Runner budget (ubuntu-latest: 4 vCPU, 16 GB): StarRocks ≤ 7 GB, each server ≤ 3 GB; start the second server only
for the failover/partial tests. Free disk first if needed (the allin1 image is ~3.2 GB).

## 3. StarRocks under test

`docker.io/starrocks/allin1-ubuntu:4.1.4` (BE reports `4.1.4-4a9848e`) with our FE jars and `starrocks_be` copied
over it (docs/INSTALL.md §2a; take the FE/BE outputs of the current series, same as release.yml). Bench configs
from `tests/m4/starrocks/`. Clients via `mysql -h127.0.0.1 -P9030 -uroot`.

## 4. What to check (PLAN.md §4 M4 + docs/M4-TESTS.md)

| # | Check | Pass |
|---|---|---|
| 1 | catalog create, SHOW DATABASES/TABLES, DESC on tpch + types tables, SHOW CREATE CATALOG | types as designed (PLAN §2), token masked |
| 2 | every column of the types tables `SELECT *` | values equal DuckDB reading the same parquet (normalised) |
| 3 | docs/M4-TESTS.md §1–2 (EXPLAIN `REMOTE SQL` + results, both session switches, `result_mode` partial and complete) | as listed there; results = DuckDB |
| 4 | TPC-H SF1 q01–q22, `cbo_push_down_topn_limit` default and 0 | 22/22 equal `reference/sf1` (same normalisation as sr_cases.py) |
| 5 | sr-cases (26) | all equal the SF1 DuckDB reference |
| 6 | failover: 2 servers, stop one **before** a query (endpoint + backup) and **during** a long read | before: query succeeds via backup; during: clean error, never wrong/duplicate rows |
| 7 | KILL QUERY during a long scan | stops within ~1 s, server-side stream cancelled |
| 8 | token: right / wrong / missing; TLS: trusted, wrong host, `tls_verify=false` | as in BE unit test 0007; no token or password in fe.log, be.INFO, be.WARNING, query profile (grep) |
| 9 | memory: big scan under a small `query_mem_limit` | clean error, BE stays up |
| 10 | timings (informational only, shared runner): TPC-H per query | recorded, not a gate |

Write the results of every run to `docs/M4-RESULTS.md` (date, run id, series, pass/fail per check, failures with
the error text). Each failure becomes a "Next steps" item in STATUS.md.

## 5. Budget

Private repo again: ~2000 Actions minutes per month shared with all builds. One full M4 run ≈ 45–75 min. Make
the workflow selectable (`checks=1,2,3…`) and rerun only what a fix touches; full run only for a new series
before the final local check. Cache the docker images / assets with actions/cache where it saves time.

## 6. Final local check (maintainer's stand, after CI M4 is green)

Only what CI cannot do: HDFS data path (hadoopfs) at SF10 with `bench/reference/sf10`, 3-node server cluster
kill tests, speed vs the JDBC bridge and the Trino plugin on the same machine, the stand's production-like server
build. Prepare a short script/checklist for it in `docs/LOCAL-FINAL-CHECK.md`.
