# Connector comparison (maintainer item 2026-11-02)

Three StarRocks paths to the same Arrow Flight SQL server, on the same GitHub runner type (ubuntu-latest, 4 vCPU,
16 GB), TPC-H SF1 and SF10, q01–q22, each query run 3 times (1st = cold, median of the 2 warm runs), every answer
checked against DuckDB on the same parquet files (row count + checksum of the normalised rows; ordered queries also
by order), peak resident memory of the FE and BE processes sampled every second.

**State (2026-11-02 13:50 UTC): interim — ours and jdbc measured at SF1 and SF10; the upstream native BE (`up-be`
41446753059, cold) is still compiling, so `up` has no numbers yet.** The final tables come from one run per SF with all
three paths (Next steps in `docs/STATUS.md`).

## Paths and versions

| path | StarRocks | connector | catalog |
|---|---|---|---|
| **ours** | 4.1.4 (allin1 image) + this repo's patch series (m4 default build) | native `flight` catalog, `patches/` | `type=flight`, `flight.uri=grpc://flight1:32010`, all else default |
| **up** | fork `VadimSurpin/starrocks` `feat/flight-connector` @ `4b3497def80e` (2026-10-23, on `branch-4.0` @ `1c10db3edc77`), FE `fe/lib` + `bin/start_fe.sh` and BE replaced in allin1 4.0.17 | native `flight` catalog of the fork; FE needs `arrow-flight-starrocks-connector` 1.0.0 from `VadimSurpin/arrow-flight-server` `feat/starrocks-native-integration` @ `6e264c10f403` | `type=flight`, `flight.uri=grpc://flight1:32010` (auth none; `flight.aggregation_pushdown`, `flight.statistics`, `flight.join_key_reduction` at their defaults) |
| **jdbc** | stock allin1 4.0.17 | StarRocks JDBC catalog + shaded `FlightSqlPostgresqlDriver` (`flight-starrocks` module, classifier `starrocks-driver`, same commit) on the FE classpath and as `driver_url` | `type=jdbc`, `jdbc_uri=jdbc:arrow-flight-sql://flight1:32010/?useEncryption=0`, `driver_url=file:///opt/flight-starrocks/driver.jar`, empty user/password |

Server for all: `arrow-flight-server-1.0.0-f06b5834e76e-linux.jar` (release `m4-assets`), started fresh before each
path with none of the m4 tuning flags (server defaults; container limit 6 GB), data on MinIO (`s3://lake/parquet`);
a second pass per path adds `-DresourceProfile=speed`. StarRocks: one allin1 container, FE heap 3 GB, BE
`mem_limit = 5G` (same `fe.conf` / `be.conf` for all paths, `tests/m4/starrocks/`).

## How it runs

- `up-fe.yml`: builds `arrow-flight-starrocks-connector` (mvn install) and the fork's FE in `dev-env-ubuntu:4.0.17`;
  output `up-fe-lib.tar.zst` + `flight-starrocks-driver.jar` (artifact `up-fe-<hash>`).
- `up-be.yml` / `up-be-part.yml`: the fork's BE, chained < 6 h jobs with its own ccache (`ccache-up-*`), cold
  (other base than ours); output artifact `up-starrocks_be-<hash>`. Pinned commits and images: `ci/up/env.sh`.
- `compare.yml` (`compare sf=1 paths=ours,up,jdbc profiles=default,speed` in `ci/dispatch.txt`): data (SF1 from the
  m4 assets, SF10 generated with DuckDB `dbgen`), DuckDB reference answers, then per profile and path: fresh
  Flight server, StarRocks variant (`ci/m4/stack.sh starrocks` with `SR_VARIANT`), `ci/m4/compare.py run`.
  Results: artifact `compare-<run>`, branch `m4-results` `compare/<run>.md` + per-run JSON.

## Results (interim)

Runs: SF1 41447501206 (default profile), SF10 41451137029 (default + speed); raw JSON and per-query tables on branch
`m4-results`, `compare/<run>.md`. Warm sums count only the queries a path answered.

| SF | run | path | correct | sum of warm medians (s) | sum of cold (s) | FE peak MB | BE peak MB |
|---|---|---|---|---|---|---|---|
| 1 | sf1-ours-default | ours | 22/22 | 12.30 | 16.36 | 570 | 685 |
| 1 | sf1-jdbc-default | jdbc | 3/22 | 2.67 (q12, q13, q16 only) | 5.96 | 623 | 972 |
| 10 | sf10-ours-default | ours | 22/22 | 79.98 | 87.69 | 690 | 3808 |
| 10 | sf10-ours-speed | ours | 22/22 | 60.68 | 66.75 | 813 | 3313 |
| 10 | sf10-jdbc-default | jdbc | 3/22 | 12.81 (q12, q13, q16 only) | 17.23 | 645 | 1533 |
| 10 | sf10-jdbc-speed | jdbc | 3/22 | 11.85 (q12, q13, q16 only) | 15.18 | 761 | 1466 |

Same three queries side by side at SF10 (warm median, s): q12 jdbc 4.63 / ours 2.09, q13 6.25 / 3.05, q16 1.94 / 0.63
(default profile); the speed profile helps ours by ~24 % overall (79.98 → 60.68 s) and jdbc little.

**JDBC adapter finding:** with its documented properties, StarRocks 4.0.17's JDBC catalog refuses every TPC-H table
column of type DECIMAL at analysis ("Datatype of external table column [l_quantity] is not supported"), so 19 of 22
queries fail (all but q12, q13, q16, which read no DECIMAL column). Cause (checked in the StarRocks 4.0.17 sources,
`fe/fe-core/.../connector/jdbc/PostgresSchemaResolver.java`, `convertColumnType`): the driver presents itself to the
PostgreSQL schema resolver (class name match), which maps only `java.sql.Types.NUMERIC` to DECIMAL; the Arrow Flight
SQL JDBC metadata reports decimal128 columns as `Types.DECIMAL`, which falls to `default` → `UNKNOWN_TYPE`, and the
analyzer refuses the column. It is the adapter path's behaviour with its documented setup (a fix belongs in the
driver's metadata, reporting NUMERIC, or in the resolver), not a harness error (the same tables pass for ours).

## Verdict

(pending the `up` numbers)
