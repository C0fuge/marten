# M4 in GitHub Actions

Goal: run as much of M4 (PLAN.md §4) as possible in CI, so connector bugs are found and fixed without the
maintainer's stand. The maintainer only runs a short final check locally (section 6). This file is the brief for
the cloud sessions that build this; extend it as the workflow takes shape.

The repo is public (since 2026-10-24). Don't attach these assets to a product release.

## 1. Inputs

Release `m4-assets` (prerelease, not a product release; download in a workflow with
`gh release download m4-assets -R "$GITHUB_REPOSITORY"` and `GH_TOKEN: ${{ github.token }}`, `contents: read`):

| Asset | Content |
|---|---|
| `arrow-flight-server-1.0.0-int1.jar` | our Arrow Flight SQL server (DuckDB 1.4.1 inside), shaded, Linux only. Needs **JDK 21** (not 24+) |
| `arrow-flight-server-1.0.0-int2.jar` | (since the repo re-creation 2026-10-25 the asset is an unfinished upload, state `starter`: 404, skipped by `stack.sh assets`) same, branch integration ac20b00: partial mode answers expressions over aggregates as one complete endpoint; UBIGINT → decimal128(20,0) in every mode. Not in the release's SHA256SUMS: pinned in `ci/m4/server-jars.sha256` |
| `arrow-flight-server-1.0.0-int4.jar` + `int4-plugins.tar.zst` | branch integration-2: int2 fixes + DuckDB **1.4.5** + plugin SPI; S3 and lakeFS are plugins (`plugins/s3`, `plugins/lakefs`, START-NOTES.txt), loaded with `-Darrowflight.plugins.dir=<dir>/plugins`, NOT on the classpath (`flight-server-libs` stays). Needs the **v1.4.5** httpfs (v1.4.1 extensions: refuses to start). Release candidate of the server. Both pinned in `ci/m4/server-jars.sha256`; `stack.sh assets` picks httpfs version and plugin dir from the jar name (int1/int2: 1.4.1, no plugins; later: 1.4.5 + `<tag>-plugins.tar.zst`) |
| `arrow-flight-server-1.0.0-int4b.jar` | int4 rebuilt with the cluster fixes (B5 member loss, ticket secret); uses `int4-plugins.tar.zst` (`stack.sh assets`: a lettered rebuild without its own plugins asset takes the base's). m4 default 2026-10-23 (run 39883591960) until int7 |
| `arrow-flight-server-1.0.0-int6.jar` + `int6-plugins.tar.zst` | int4b + table catalogs (plugins `iceberg`: iceberg-hadoop / iceberg-rest, `hive`: Hive Metastore) + refresh-recursion fix of int5 (int5: do not use). Needs DuckDB iceberg + avro v1.4.5 for catalogs. Used by `store=iceberg` (check 11) until int7 |
| `arrow-flight-server-1.0.0-int7.jar` + `int7-plugins.tar.zst` | int6b + all stand fixes (lakeFS: JOIN commit mixing, complete-mode lag, tags; Iceberg: file:/s3a roots, LocalFileSystem, Gravitino errors; Hive: HDFS paths with space/%, out-of-root partitions hidden, metastore fail-fast, UNAVAILABLE on outage; Iceberg equality deletes). Plugins s3/lakefs/iceberg/hive. Pinned in `ci/m4/server-jars.sha256` (= asset digests). **m4 default** since 2026-10-23 for every store |
| `arrow-flight-server-1.0.0-4eaab052deaf-linux.jar` + `flight-plugins-1.0.0-4eaab052deaf.tar.zst` + `flight-server-libs-1.0.0-4eaab052deaf.tar.zst` | first server repo CI build (main 4eaab05): int7 + hadoopfs timeout defaults 3 s / 10 s + dependency security upgrades; ships its own plugins and runtime libs (`stack.sh` derives both names from the jar). m4 default 2026-10-25 (full suite PASS: m4 40172422411, 40172423737, 40173169121) until c3b276054cc3. START-NOTES.md |
| `arrow-flight-server-1.0.0-c3b276054cc3-linux.jar` + `flight-plugins-1.0.0-c3b276054cc3.tar.zst` + `flight-server-libs-1.0.0-c3b276054cc3.tar.zst` | 4eaab052deaf + ZooKeeper client and lz4-java in the runtime libs (announced with Iceberg time travel, but its parser rejects the clause: m4 40229960640 check 12 1/10). m4 default 2026-10-25 until 20b887839edf (S3 1–9 m4 40227337083, iceberg 1,11 m4 40227338512, lakefs 1,3,4,10 m4 40228819006). The release's START-NOTES.md is still the 4eaab05 copy (its SHA256SUMS line does not match; `stack.sh` verifies only the assets a run uses) |
| `arrow-flight-server-1.0.0-20b887839edf-linux.jar` + `flight-plugins-1.0.0-20b887839edf.tar.zst` + `flight-server-libs-1.0.0-20b887839edf.tar.zst` | c3b276054cc3 + **Iceberg time travel** (`FOR VERSION AS OF` / `FOR TIMESTAMP AS OF` after an Iceberg table name) + parameterized prepared statements with `duckDbStatementCacheSize` 0/1 + Hive metastore Kerberos client + local catalog roots under a non-local `fs.defaultFS`. **m4 default** since 2026-10-26 (S3 1–9 m4 40245888043, iceberg 1,11,12 m4 40245889746 incl. time travel 10/10, lakefs 1,3,4,10 m4 40248225183); assets cache `m4-assets-v8` |
| `arrow-flight-server-1.0.0-60e888bc26ec-linux.jar` + `flight-plugins-1.0.0-60e888bc26ec.tar.zst` + `flight-server-libs-1.0.0-60e888bc26ec.tar.zst` | 20b887839edf + `duckDbThreads` default 4 (was 1). m4 default 2026-10-26 04:40–07:30 UTC (series `fldb9219`: S3 1–9 m4 40267917390, check 6 m4 40267918986 / 40268961132, lakefs 1,3,4,10 m4 40268964021; iceberg 1,11,12 m4 40255398491 on `fl536298`). Check 6 had failed 2 of 5 runs on series `fl536298` (flight1 failed GetFlightInfo during Hazelcast member loss, then the FE's one try per URI was used up); series `fldb9219` retries the connected URI once (`docs/M4-RESULTS.md`). Assets cache `m4-assets-v9` holds it and 20b887839edf |
| `arrow-flight-server-1.0.0-7fbe2d75827c-linux.jar` + `flight-plugins-1.0.0-7fbe2d75827c.tar.zst` + `flight-server-libs-1.0.0-7fbe2d75827c.tar.zst` | 60e888bc26ec + planning does not wait for the cluster to settle after a node left + `s3a://`/`s3n://` catalog roots + the HDFS short-circuit setting is kept. **m4 default since 2026-10-26 07:30 UTC** (series `fldb9219`: S3 1–9 m4 40281342490, iceberg 1,11,12 m4 40281344356, lakefs 1,3,4,10 m4 40284404496, check 6 m4 40284406938). Assets cache `m4-assets-v10` holds it and 60e888bc26ec |
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
| 10 | lakeFS (`store=lakefs` only, P3): `lfs.t` before / with a staged file / after a 2-file commit / after a delete commit; tpch through lakeFS | each commit seen by the next queries (≤ 60 s), never half a commit; staged-file visibility recorded as a note |
| 11 | Iceberg (`store=iceberg` only, P5): schema `ice` from an Iceberg REST catalog next to the parquet schemas; `lineitem`/`orders` (pyiceberg, several snapshots) vs the parquet tables and q01/q04/q12 vs `reference/sf1` in both result modes; `del` with Spark position deletes; `ren` with a column renamed between two appends; an append to `t` between two queries | equal to parquet / reference; deletes applied; rename read by field id; append seen by partial mode within 90 s and by complete mode after the 60 s view refresh, never another state |
| – | timings (informational only, shared runner): TPC-H per query, recorded by check 4 | recorded, not a gate |

Write the results of every run to `docs/M4-RESULTS.md` (date, run id, series, pass/fail per check, failures with
the error text). Each failure becomes a "Next steps" item in STATUS.md.

## 5. Budget

Public repo: Actions minutes are free, but keep runs short. One full M4 run ≈ 45–75 min. Make
the workflow selectable (`checks=1,2,3…`) and rerun only what a fix touches; full run only for a new series
before the final local check. Cache the docker images / assets with actions/cache where it saves time.

## 6. Final local check (maintainer's stand, after CI M4 is green)

Only what CI cannot do: HDFS data path (hadoopfs) at SF10 with `bench/reference/sf10`, 3-node server cluster
kill tests, speed vs the JDBC bridge and the Trino plugin on the same machine, the stand's production-like server
build. Prepare a short script/checklist for it in `docs/LOCAL-FINAL-CHECK.md`.

## 7. Implementation (state)

- `.github/workflows/m4.yml` (dispatch `m4 checks=1,2,3` in `ci/dispatch.txt`): prepares the source only for the
  input hashes, takes the FE/BE outputs of the current series like `release.yml` (cache, else newest artifact;
  both must report the current series hash), downloads `m4-assets` (draft release: looked up through the release
  list, cached as `m4-assets-v8` with all server jars; bump the key when the assets change; input `server` picks the
  jar, default `arrow-flight-server-1.0.0-7fbe2d75827c-linux.jar` (since 2026-10-26 07:30 UTC; 60e888bc26ec, 20b887839edf, c3b276054cc3, 4eaab052deaf and int7 before), e.g. `m4 checks=1,2 server=arrow-flight-server-1.0.0-int1.jar`;
  results.md names it), then `ci/m4/stack.sh`: docker network
  `m4` with `minio` (throwaway credentials, `s3://lake/parquet/{tpch,types}`), `flight1` (eclipse-temurin:21-jre,
  open mode; flight1 also on 127.0.0.1:32010 for ADBC probes), `sr` (allin1 4.1.4 overlay + bench configs, ports 9030/8030/8040 on the runner).
- `ci/m4/m4.py` runs the checks with pymysql against 127.0.0.1:9030 and DuckDB 1.4.1 on the same parquet files
  (types tables, M4-TESTS §1–2, sr-cases) or `tests/m4/reference/sf1` (TPC-H). Implemented: checks 1–5 (+ the
  log grep of check 8 for the dummy catalog token, + TPC-H timings in check 4). Normalisation: decimals
  rounded to 4 places (exact for the types tables), DOUBLE 9 / FLOAT 6 significant digits, timestamps in UTC
  (session `time_zone='UTC'`), binary/UUID as hex; TPC-H rows compared as multisets plus the order of the `key`
  columns.
- Output: artifact `m4-<run>` (results.md/json, all container logs, fe/be logs) and branch `m4-results`
  (`latest.md`, `runs/<run>.md`): `git fetch origin m4-results && git show origin/m4-results:latest.md`.
- Checks 6–9 (all green since run 39665941130) restart the Flight server through `stack.sh`: 6 = cluster flight1+flight2,
  full lineitem scan with `flight_aggregate_pushdown=false`, flight2 stopped before; "during" reads lineitem 3x (UNION ALL), SIGKILLs flight2 at 35% of the measured read time and requires proof that the kill hit the read (query error, or `FailoverCount` > 0 in its profile);
  7 = 8-way UNION ALL scan, `KILL QUERY` after 4 s, must end < 2 s; 8 = token server (right / wrong / missing
  token, basic user:<token>, password masked, token absent from the query profiles of both catalogs), TLS server with a job-generated cert (CA file copied into `sr`,
  host alias `flight1-alias` for the mismatch, untrusted, `tls.verify=false`, plain client); 9 = 3-key GROUP BY
  over lineitem under `query_mem_limit`=100 MB must fail with a memory error, BE alive. Each restores the open
  single-server setup at the end.
- Input `store=lakefs` (P3, server int4+; `m4 checks=1,3,4,10 store=lakefs`): `stack.sh lakefs` starts
  `treeverse/lakefs:1.38.0` (local KV, MinIO blockstore `s3://lakefs/m4lake`, admin key from `installation.*`, throwaway
  values in `$M4_STATE/lakefs.env`), `ci/m4/lakefs.py setup` uploads tpch + types + `lfs/t` through the S3 gateway to
  repository `m4lake` branch `main` and commits; `$M4_STATE/store.env` then makes every `stack.sh flight` serve
  `lakefs://m4lake/main/parquet` (`-Darrowflight.lakefs.endpoint=http://lakefs:8000`, `FLIGHT_LAKEFS_ACCESS_KEY/SECRET_KEY`).
  results.md names the store.
- Input `store=iceberg` (P5, server **int6**+, default 7fbe2d75827c; `m4 checks=1,11 store=iceberg`, `1,11,12` with time travel):
  `stack.sh iceberg` starts `apache/iceberg-rest-fixture:1.9.2` (in-memory catalog, S3FileIO on MinIO, warehouse
  `s3://lake/parquet/_iceberg` — below the dataDir, since a second s3 store is refused by the server),
  `ci/m4/iceberg.py setup` writes namespace `ice` with pyiceberg 0.10.0, and a one-shot `apache/spark:3.5.6` container
  (iceberg-spark-runtime 1.9.2) writes `ice.del` with merge-on-read deletes. `stack.sh assets` puts DuckDB's iceberg +
  avro v1.4.5 extensions into `x/duckdb-ext/v1.4.5/linux_amd64` for plugin builds; the server gets `-Dcatalog=iceberg-rest
  -Darrowflight.iceberg-rest.uri=http://iceberg-rest:8181 -Darrowflight.iceberg-rest.roots=s3://lake/parquet/_iceberg
  -Darrowflight.duckdb.extensionDir=/srv/duckdb-ext`. Not covered: equality deletes (Spark cannot write them).
  Check 12 (time travel, 2026-10-25; connector series `fl536298`+, server 20b887839edf+): one append to `ice.t`, then
  `FOR VERSION AS OF` both snapshots in both result modes, the REMOTE SQL, two versions in one query, `FOR TIMESTAMP AS OF`
  (whole second, with a fraction, later time; session zone +08:00) and the refused `FOR VERSION BETWEEN`.
- Check 1 also compares each `DESC` exactly (order, names, types) with the PLAN §2.2 mapping (`plan_type` in
  m4.py, mirroring FlightTypeMapper with `flight.nested_types=native`, `flight.converted_types=convert`) of the Arrow schema the server returns in
  GetTables(include_schema).
