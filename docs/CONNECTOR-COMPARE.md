# Connector comparison (maintainer item 2026-11-02)

Three StarRocks paths to the same Arrow Flight SQL server, on the same GitHub runner type (ubuntu-latest, 4 vCPU,
16 GB), TPC-H SF1 and SF10, q01–q22, each query run 3 times (1st = cold, median of the 2 warm runs), every answer
checked against DuckDB on the same parquet files (row count + checksum of the normalised rows; ordered queries also
by order), peak resident memory of the FE and BE processes sampled every second.

**State: harness and builds in progress — no results yet** (see `docs/STATUS.md` Log).

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

## Results

(pending)

## Verdict

(pending)
