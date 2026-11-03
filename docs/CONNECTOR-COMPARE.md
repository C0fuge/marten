# Connector comparison (maintainer item 2026-11-02)

Three StarRocks paths to the same Arrow Flight SQL server, on the same GitHub runner type (ubuntu-latest, 4 vCPU,
16 GB), TPC-H SF1 and SF10, q01–q22, each query run 3 times (1st = cold, median of the 2 warm runs), every answer
checked against DuckDB on the same parquet files (row count + checksum of the normalised rows; ordered queries also
by order), peak resident memory of the FE and BE processes sampled every second.


**State (2026-11-03 05:55 UTC): "after" pass done (SF1 41580201961, SF10 41582285095), see "After the improvements".** Before (2026-11-02 15:45 UTC): Final runs: SF1 41466070831, SF10 41466074590 (all three paths, default
and speed profile, one runner each, consecutive). Interim runs 41447501206 / 41451137029 (ours + jdbc only) agree with
them within ~1 %.

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


## After the improvements (series `4a9848e-flded1b0`, 2026-11-03)

Re-run of ours vs up only (jdbc unchanged) after `avg()` pushdown and join-key pushdown (STATUS Log 2026-11-03), same
server `f06b5834e76e`, same harness: SF1 run **41580201961**, SF10 run **41582285095** (FE 41578204766, BE 41579557200;
m4 41580199568 checks 1–9 PASS on the same series). The runner of this pass was faster than the one of the "before"
runs (up, unchanged, SF1 12.82 → 8.87 s), so compare ours with up *within* a run, not across runs.

| run | correct | ours warm, common (s) | up warm, common (s) | ours / up | before: ours / up |
|---|---|---|---|---|---|
| SF1 default (common 19) | ours 22/22, up 19/22 | 8.30 (cold 10.88) | 8.87 (cold 12.25) | 0.94 | 0.85 (10.91 / 12.82) |
| SF1 speed (common 19) | ours 22/22, up 19/22 | 7.55 (cold 9.79) | 8.98 (cold 11.83) | 0.84 | 0.79 (10.22 / 12.98) |
| SF10 default (common 20) | ours 22/22, up 20/22 | 68.28 (cold 74.70) | 56.17 (cold 69.42) | 1.22 | 1.18 (69.56 / 59.05) |
| SF10 speed (common 20) | ours 22/22, up 20/22 | 52.70 (cold 57.72) | 53.33 (cold 66.56) | 0.99 | 0.95 (53.35 / 56.34) |

Peak memory (MB, FE / BE): SF10 ours default 686 / 3711, speed 733 / 2014; up default 1574 / 2179, speed 1329 / 1496.

SF10 default, warm median (s) of the queries that moved, ours before → after (up after):

| q | ours before | ours after | up after | why |
|---|---|---|---|---|
| q01 | 6.08 | **2.69** | 2.60 | `avg()` pushed as sum + count: the aggregation runs remotely (item 1 works) |
| q17 | 3.19 | **1.03** | 1.06 | `p_partkey IN (…)` from the filtered `part` cuts the lineitem scan (item 2 works) |
| q19 | 3.36 | 3.21 | 1.92 | no change: likely because the part filters sit in an OR across both sides (q19 shape), so no reducing filter lands on the part scan alone — not verified with EXPLAIN |
| q12 | 1.88 | **4.15** ↑ | 1.92 | regression: source = filtered `lineitem` (the only filtered side), > 10 000 distinct `l_orderkey` → the key query is an extra planning-time scan of lineitem and ends in a range over almost all of `orders` |
| q14 | 1.28 | **2.44** ↑ | 1.15 | regression, same pattern: filtered `lineitem` (one month) as source for `part` |

**Verdict after:** items 1 and 2 close the q01 and q17 gaps completely. The net SF10 gain is eaten by the new q12 / q14
regressions (+3.4 s together): the join-key query must not run when the source side is large (it is a second remote scan
of the big table, and its key set exceeds the IN limit anyway, so only an ineffective range remains). With those two
back at their old times ours would be ~64.9 s vs up 56.2 s at SF10 default, and ~50 s vs 53.3 s with the speed profile.
Next fix: STATUS Next steps.

## Before the improvements (2026-11-02)

### Results (before)

Warm = median of runs 2 and 3, cold = run 1; sums over the queries a path answered correctly. "Common" = the queries
both native paths answered (SF1: 19, without q10 q14 q19; SF10: 20, without q11 q21), the like-for-like comparison.
Raw JSON, logs and the per-run tables: branch `m4-results`, `compare/<run>.md` / `compare/*-<run>.json`.

### SF1 (run 41466070831)

| path / profile | correct | warm sum, all answered (s) | warm sum, common 19 (s) | cold sum, common 19 (s) | FE peak MB | BE peak MB |
|---|---|---|---|---|---|---|
| ours default | **22/22** | 12.38 | **10.91** | 14.58 | 574 | 672 |
| ours speed | **22/22** | 11.39 | **10.22** | 12.66 | 725 | 669 |
| up default | 19/22 | 12.81 | 12.82 | 17.90 | 1219 | 768 |
| up speed | 19/22 | 13.00 | 12.98 | 17.59 | 783 | 791 |
| jdbc default | 3/22 | 2.72 (q12 q13 q16; ours 1.10, up 2.17) | – | – | 748 | 1010 |
| jdbc speed | 3/22 | 2.62 (q12 q13 q16; ours 0.96, up 2.37) | – | – | 625 | 983 |

Per query, warm median / cold (s), `x` = error:

| q | sf1-jdbc-default | sf1-jdbc-speed | sf1-ours-default | sf1-ours-speed | sf1-up-default | sf1-up-speed |
|---|---|---|---|---|---|---|
| q01 | x - / - | x - / - | 1.25 / 3.20 | 1.27 / 2.78 | 0.65 / 1.09 | 0.54 / 1.19 |
| q02 | x - / - | x - / - | 0.26 / 1.03 | 0.27 / 0.65 | 0.38 / 1.11 | 0.35 / 1.07 |
| q03 | x - / - | x - / - | 0.60 / 0.98 | 0.67 / 0.87 | 0.72 / 1.62 | 0.86 / 1.58 |
| q04 | x - / - | x - / - | 0.39 / 0.46 | 0.37 / 0.42 | 0.36 / 0.61 | 0.39 / 0.64 |
| q05 | x - / - | x - / - | 0.80 / 0.77 | 0.70 / 0.67 | 0.83 / 1.13 | 0.85 / 1.27 |
| q06 | x - / - | x - / - | 0.20 / 0.23 | 0.20 / 0.22 | 0.22 / 0.24 | 0.19 / 0.22 |
| q07 | x - / - | x - / - | 0.69 / 0.74 | 0.55 / 0.66 | 0.78 / 1.01 | 0.70 / 1.00 |
| q08 | x - / - | x - / - | 1.02 / 1.02 | 0.78 / 0.88 | 1.08 / 1.57 | 1.01 / 1.55 |
| q09 | x - / - | x - / - | 1.07 / 1.10 | 0.87 / 0.91 | 1.19 / 1.46 | 1.11 / 1.39 |
| q10 | x - / - | x - / - | 0.74 / 0.74 | 0.56 / 0.59 | x - / - | x - / - |
| q11 | x - / - | x - / - | 0.23 / 0.24 | 0.19 / 0.23 | 0.78 / 1.11 | 0.81 / 0.96 |
| q12 | 1.01 / 4.30 | 0.95 / 4.88 | 0.39 / 0.44 | 0.32 / 0.41 | 1.05 / 1.17 | 1.17 / 1.06 |
| q13 | 1.19 / 1.29 | 1.19 / 1.34 | 0.47 / 0.51 | 0.40 / 0.40 | 0.38 / 0.39 | 0.36 / 0.38 |
| q14 | x - / - | x - / - | 0.28 / 0.25 | 0.23 / 0.26 | x - / - | x - / - |
| q15 | x - / - | x - / - | 0.33 / 0.41 | 0.41 / 0.40 | 0.34 / 0.37 | 0.38 / 0.39 |
| q16 | 0.52 / 0.80 | 0.48 / 0.55 | 0.24 / 0.24 | 0.24 / 0.23 | 0.74 / 0.99 | 0.84 / 0.86 |
| q17 | x - / - | x - / - | 0.53 / 0.58 | 0.45 / 0.45 | 0.24 / 0.49 | 0.22 / 0.52 |
| q18 | x - / - | x - / - | 0.87 / 0.92 | 0.98 / 0.88 | 0.86 / 1.02 | 0.86 / 1.05 |
| q19 | x - / - | x - / - | 0.46 / 0.48 | 0.37 / 0.43 | x - / - | x - / - |
| q20 | x - / - | x - / - | 0.41 / 0.41 | 0.43 / 0.41 | 0.53 / 0.62 | 0.62 / 0.65 |
| q21 | x - / - | x - / - | 1.00 / 1.13 | 0.97 / 1.02 | 1.52 / 1.69 | 1.55 / 1.62 |
| q22 | x - / - | x - / - | 0.16 / 0.17 | 0.15 / 0.17 | 0.17 / 0.21 | 0.17 / 0.19 |

### SF10 (run 41466074590)

| path / profile | correct | warm sum, all answered (s) | warm sum, common 20 (s) | cold sum, common 20 (s) | FE peak MB | BE peak MB |
|---|---|---|---|---|---|---|
| ours default | **22/22** | 79.47 | 69.56 | 77.67 | 725 | 2733 |
| ours speed | **22/22** | 60.40 | **53.35** | 66.40 | 757 | 3582 |
| up default | 20/22 | 59.04 | **59.05** | 73.99 | 1469 | 2230 |
| up speed | 20/22 | 56.33 | 56.34 | 70.90 | 1370 | 1516 |
| jdbc default | 3/22 | 13.77 (q12 q13 q16; ours 5.54, up 5.11) | – | – | 684 | 1540 |
| jdbc speed | 3/22 | 12.64 (q12 q13 q16; ours 4.78, up 5.00) | – | – | 680 | 1571 |

Per query, warm median / cold (s), `x` = error:

| q | sf10-jdbc-default | sf10-jdbc-speed | sf10-ours-default | sf10-ours-speed | sf10-up-default | sf10-up-speed |
|---|---|---|---|---|---|---|
| q01 | x - / - | x - / - | 6.08 / 10.19 | 5.19 / 9.81 | 2.67 / 3.11 | 2.60 / 3.13 |
| q02 | x - / - | x - / - | 0.70 / 1.60 | 0.71 / 1.14 | 0.98 / 1.54 | 0.88 / 1.47 |
| q03 | x - / - | x - / - | 5.00 / 5.87 | 3.72 / 4.53 | 4.21 / 5.93 | 4.20 / 5.63 |
| q04 | x - / - | x - / - | 2.79 / 2.70 | 1.98 / 2.01 | 2.29 / 3.33 | 2.24 / 3.24 |
| q05 | x - / - | x - / - | 5.52 / 5.36 | 4.00 / 4.10 | 5.00 / 5.96 | 4.66 / 5.55 |
| q06 | x - / - | x - / - | 1.00 / 1.03 | 1.06 / 1.07 | 1.05 / 1.11 | 1.01 / 1.19 |
| q07 | x - / - | x - / - | 4.85 / 5.24 | 3.06 / 8.02 | 4.39 / 5.71 | 4.53 / 5.46 |
| q08 | x - / - | x - / - | 6.80 / 6.79 | 4.27 / 4.51 | 5.80 / 7.34 | 5.47 / 7.23 |
| q09 | x - / - | x - / - | 7.89 / 8.03 | 5.45 / 5.84 | 7.30 / 8.55 | 6.49 / 8.31 |
| q10 | x - / - | x - / - | 4.41 / 5.27 | 2.97 / 3.37 | 4.48 / 5.20 | 4.41 / 4.98 |
| q11 | x - / - | x - / - | 0.90 / 0.94 | 0.69 / 0.72 | x - / - | x - / - |
| q12 | 4.76 / 8.12 | 4.69 / 8.09 | 1.88 / 2.18 | 1.97 / 1.95 | 2.11 / 3.29 | 2.08 / 3.05 |
| q13 | 7.05 / 6.32 | 6.06 / 6.29 | 3.01 / 3.21 | 2.26 / 2.39 | 2.35 / 2.52 | 2.32 / 2.41 |
| q14 | x - / - | x - / - | 1.28 / 1.23 | 1.27 / 1.30 | 1.30 / 2.19 | 1.20 / 1.96 |
| q15 | x - / - | x - / - | 2.11 / 2.37 | 2.23 / 2.31 | 2.11 / 2.30 | 2.35 / 2.35 |
| q16 | 1.97 / 2.08 | 1.89 / 2.00 | 0.65 / 0.63 | 0.55 / 0.56 | 0.65 / 0.82 | 0.60 / 0.85 |
| q17 | x - / - | x - / - | 3.19 / 3.23 | 2.44 / 2.37 | 1.13 / 2.17 | 1.04 / 2.16 |
| q18 | x - / - | x - / - | 6.15 / 6.35 | 5.38 / 5.36 | 6.13 / 6.55 | 5.41 / 5.88 |
| q19 | x - / - | x - / - | 3.36 / 3.25 | 2.13 / 2.67 | 2.01 / 3.05 | 1.95 / 2.98 |
| q20 | x - / - | x - / - | 2.28 / 2.46 | 2.15 / 2.50 | 2.40 / 2.61 | 2.31 / 2.38 |
| q21 | x - / - | x - / - | 9.00 / 9.02 | 6.36 / 6.39 | x - / - | x - / - |
| q22 | x - / - | x - / - | 0.61 / 0.68 | 0.56 / 0.59 | 0.69 / 0.71 | 0.59 / 0.69 |

### Failures

- **up**, both profiles, the same queries in both: SF1 q10 q14 q19, SF10 q11 q21 — all at planning time, `Failed to
  plan Flight scan of <table>: ... Out of Memory Error: failed to allocate data of size 16–64 MiB (… /244.1 MiB used)`.
  That is DuckDB's per-connection `memory_limit` on the server, which this server build sizes from the host by default
  (244 MiB in the 6 GB container). Ours and jdbc never hit it on the same server and data. The fork's FE sends extra
  planning-time requests: table statistics (`flight.statistics`, default true) and join-key reduction
  (`flight.join_key_reduction`, default true: up to 100 000 keys of the build side pushed as a filter into the probe
  scan, 1 s budget). The failing scans are probe sides of selective joins (customer, part, partsupp, lineitem), so the
  join-key filter is the likely trigger (not verified; the fork's code was not changed or debugged here, as asked).
  Workarounds that were NOT measured: `flight.join_key_reduction=false` on the catalog or a larger
  `duckDbMemoryLimit` on the server.
- **jdbc**: 19 of 22 at analysis, see below.

**JDBC adapter finding:** with its documented properties, StarRocks 4.0.17's JDBC catalog refuses every TPC-H table
column of type DECIMAL at analysis ("Datatype of external table column [l_quantity] is not supported"), so 19 of 22
queries fail (all but q12, q13, q16, which read no DECIMAL column). Cause (checked in the StarRocks 4.0.17 sources,
`fe/fe-core/.../connector/jdbc/PostgresSchemaResolver.java`, `convertColumnType`): the driver presents itself to the
PostgreSQL schema resolver (class name match), which maps only `java.sql.Types.NUMERIC` to DECIMAL; the Arrow Flight
SQL JDBC metadata reports decimal128 columns as `Types.DECIMAL`, which falls to `default` → `UNKNOWN_TYPE`, and the
analyzer refuses the column. It is the adapter path's behaviour with its documented setup (a fix belongs in the
driver's metadata, reporting NUMERIC, or in the resolver), not a harness error (the same tables pass for ours).

## Verdict (before)

- **Correctness:** only ours answers all 44 query runs per profile (22/22 at SF1 and SF10, default and speed). The
  upstream native fork answers 19/22 (SF1) and 20/22 (SF10), failing at planning on the server's default DuckDB memory
  limit; the JDBC adapter answers 3/22 (DECIMAL columns unsupported by the 4.0 JDBC catalog).
- **SF1 (small, latency-bound):** ours is faster: common-19 warm sum 10.9 s vs 12.8 s (−15 %), cold 14.6 vs 17.9 s,
  faster on 9 queries by >10 % vs 3 for up. Up pays per query for its planning-time round trips (statistics, join-key
  reduction): e.g. q11 0.23 vs 0.78 s, q16 0.24 vs 0.74 s, q12 0.39 vs 1.05 s. Up wins q01 (0.65 vs 1.25 s) and q17.
- **SF10 (scan-bound), server default profile:** up is faster on the common 20: 59.0 vs 69.6 s (−15 %), 7 queries
  faster by >10 % vs 3 for ours. The gains are concentrated: q01 2.67 vs 6.08 s (single-table aggregation over lineitem: q01 has `avg()`, and our `FlightAggregationPushdownRule` pushes only
  count/sum/min/max, so ours streams the filtered lineitem into the BE while the fork aggregates remotely — likely,
  not verified with EXPLAIN here), q17 1.13 vs 3.19 s and q19 2.01 vs 3.36 s (the
  join-key filter cuts the lineitem scan). On the other joins (q03–q10, q18, q20) the two are within ~10 %.
- **SF10, `-DresourceProfile=speed`:** ours profits much more from the faster server profile (69.6 → 53.4 s, −23 %)
  than up (59.0 → 56.3 s, −5 %), and is then the fastest: 53.4 vs 56.3 s on the common 20, and ours additionally answers
  q11 and q21. Ours moves more data through the BE (scan, not remote aggregation/filtering), so it gains when the
  server streams faster.
- **Memory:** ours has the leanest FE (0.6–0.8 GB vs 0.8–1.5 GB for up — up keeps statistics and key sets in the FE);
  the BE peak is higher for ours at SF10 (2.7–3.6 GB vs 1.5–2.2 GB) because more rows arrive in the BE when the work is
  not pushed down; all within the 5 GB BE limit.
- **JDBC adapter:** not usable for TPC-H as documented (DECIMAL); on the three queries it can answer it is 2–3× slower
  than either native path (SF10 q12 q13 q16: 13.8 s vs 5.5 s ours, 5.1 s up), rows go through the BE's JNI JDBC scanner
  (Java, row by row) instead of Arrow batches straight into the native BE scan.
- **Take-aways for ours** (not done here; candidates for the maintainer): aggregate pushdown of `avg()` (as sum + count,
  q01) and a bounded join-key / runtime-filter pushdown into the remote SQL (q17, q19) are the two places
  where the fork is clearly ahead.
