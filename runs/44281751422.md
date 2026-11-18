# M4 run 44281751422

2026-11-18 10:47 UTC, series `4.1.4-4a9848e-fl234f9b`, server `arrow-flight-server-1.0.0-36f3302321ba-linux.jar`, store `s3: s3://lake/parquet`, compression `none`, runtime_filters `default`, checks 13, runner 4 x AMD EPYC 7763 64-Core Processor

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 3 s |
| 13 | result compression (flight.compression none / lz4 / zstd) | PASS | 103/103 | 91 s |

## Check 1: catalog, SHOW, DESC, masking

- PASS `create catalog` 
- PASS `SHOW CREATE CATALOG masks the token` flight CREATE EXTERNAL CATALOG `flight` PROPERTIES ("type"  =  "flight", "flight.token"  =  "******", "flight.uri"  =  "grpc://flight1:32010" )
- PASS `SHOW DATABASES has tpch and types` got ['information_schema', 'tpch', 'types']
- PASS `SHOW TABLES FROM flight.tpch` got ['customer', 'lineitem', 'nation', 'orders', 'part', 'partsupp', 'region', 'supplier']
- PASS `SHOW TABLES FROM flight.types` got ['alltypes', 'alltypes_full']
- PASS `DESC flight.tpch.customer` 
- PASS `DESC flight.tpch.lineitem` 
- PASS `DESC flight.tpch.nation` 
- PASS `DESC flight.tpch.orders` 
- PASS `DESC flight.tpch.part` 
- PASS `DESC flight.tpch.partsupp` 
- PASS `DESC flight.tpch.region` 
- PASS `DESC flight.tpch.supplier` 
- PASS `DESC flight.types.alltypes` 
- PASS `DESC flight.types.alltypes_full` 
- PASS `DESC flight.tpch.customer = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.lineitem = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.nation = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.orders = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.part = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.partsupp = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.region = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.tpch.supplier = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.types.alltypes = PLAN §2.2 mapping of the server schema` 
- PASS `DESC flight.types.alltypes_full = PLAN §2.2 mapping of the server schema` 
- note: DESC flight.types.alltypes: id INT, c_bool BOOLEAN, c_tinyint TINYINT, c_smallint SMALLINT, c_int INT, c_bigint BIGINT, c_utinyint SMALLINT, c_usmallint INT, c_uinteger BIGINT, c_ubigint DECIMAL(20,0), c_hugeint DOUBLE, c_float FLOAT, c_double DOUBLE, c_dec9_2 DECIMAL(9,2), c_dec18_4 DECIMAL(18,4), c_dec38_10 DECIMAL(38,10), c_varchar VARCHAR(1073741824), c_date DATE, c_time VARCHAR(1073741824), c_ts DATETIME, c_ts_ms DATETIME, c_ts_ns DATETIME, c_tstz DATETIME
- note: DESC flight.types.alltypes_full: id INT, c_bool BOOLEAN, c_tinyint TINYINT, c_smallint SMALLINT, c_int INT, c_bigint BIGINT, c_utinyint SMALLINT, c_usmallint INT, c_uinteger BIGINT, c_ubigint DECIMAL(20,0), c_hugeint DOUBLE, c_float FLOAT, c_double DOUBLE, c_dec9_2 DECIMAL(9,2), c_dec18_4 DECIMAL(18,4), c_dec38_10 DECIMAL(38,10), c_varchar VARCHAR(1073741824), c_blob VARBINARY, c_date DATE, c_time VARCHAR(1073741824), c_ts DATETIME, c_ts_ms DATETIME, c_ts_ns DATETIME, c_tstz DATETIME, c_uuid VARCHAR(1073741824), c_interval VARCHAR(1073741824), c_list ARRAY<BIGINT>, c_struct struct<`a` int(11), `b` varchar(1073741824)>, c_map MAP<VARCHAR(1073741824),INT>

## Check 13: result compression (flight.compression none / lz4 / zstd)

- PASS `lz4 q01 topn=default` rows 4/4 0.82s
- PASS `lz4 q02 topn=default` rows 100/100 0.30s
- PASS `lz4 q03 topn=default` rows 10/10 0.99s
- PASS `lz4 q04 topn=default` rows 5/5 0.73s
- PASS `lz4 q05 topn=default` rows 5/5 0.93s
- PASS `lz4 q06 topn=default` rows 1/1 0.27s
- PASS `lz4 q07 topn=default` rows 4/4 0.67s
- PASS `lz4 q08 topn=default` rows 2/2 1.28s
- PASS `lz4 q09 topn=default` rows 175/175 1.37s
- PASS `lz4 q10 topn=default` rows 20/20 0.87s
- PASS `lz4 q11 topn=default` rows 1048/1048 0.21s
- PASS `lz4 q12 topn=default` rows 2/2 0.43s
- PASS `lz4 q13 topn=default` rows 42/42 0.69s
- PASS `lz4 q14 topn=default` rows 1/1 0.44s
- PASS `lz4 q15 topn=default` rows 1/1 0.55s
- PASS `lz4 q16 topn=default` rows 18314/18314 1.48s
- PASS `lz4 q17 topn=default` rows 1/1 0.32s
- PASS `lz4 q18 topn=default` rows 57/57 1.30s
- PASS `lz4 q19 topn=default` rows 1/1 0.53s
- PASS `lz4 q20 topn=default` rows 186/186 0.60s
- PASS `lz4 q21 topn=default` rows 100/100 1.46s
- PASS `lz4 q22 topn=default` rows 7/7 0.23s
- PASS `lz4 q01 topn=0` rows 4/4 0.71s
- PASS `lz4 q02 topn=0` rows 100/100 0.20s
- PASS `lz4 q03 topn=0` rows 10/10 0.87s
- PASS `lz4 q04 topn=0` rows 5/5 0.65s
- PASS `lz4 q05 topn=0` rows 5/5 0.85s
- PASS `lz4 q06 topn=0` rows 1/1 0.24s
- PASS `lz4 q07 topn=0` rows 4/4 0.53s
- PASS `lz4 q08 topn=0` rows 2/2 1.23s
- PASS `lz4 q09 topn=0` rows 175/175 1.17s
- PASS `lz4 q10 topn=0` rows 20/20 0.87s
- PASS `lz4 q11 topn=0` rows 1048/1048 0.18s
- PASS `lz4 q12 topn=0` rows 2/2 0.41s
- PASS `lz4 q13 topn=0` rows 42/42 0.61s
- PASS `lz4 q14 topn=0` rows 1/1 0.37s
- PASS `lz4 q15 topn=0` rows 1/1 0.39s
- PASS `lz4 q16 topn=0` rows 18314/18314 0.68s
- PASS `lz4 q17 topn=0` rows 1/1 0.26s
- PASS `lz4 q18 topn=0` rows 57/57 1.02s
- PASS `lz4 q19 topn=0` rows 1/1 0.43s
- PASS `lz4 q20 topn=0` rows 186/186 0.48s
- PASS `lz4 q21 topn=0` rows 100/100 1.49s
- PASS `lz4 q22 topn=0` rows 7/7 0.18s
- PASS `zstd q01 topn=default` rows 4/4 0.73s
- PASS `zstd q02 topn=default` rows 100/100 0.17s
- PASS `zstd q03 topn=default` rows 10/10 0.96s
- PASS `zstd q04 topn=default` rows 5/5 0.67s
- PASS `zstd q05 topn=default` rows 5/5 0.85s
- PASS `zstd q06 topn=default` rows 1/1 0.22s
- PASS `zstd q07 topn=default` rows 4/4 0.52s
- PASS `zstd q08 topn=default` rows 2/2 1.42s
- PASS `zstd q09 topn=default` rows 175/175 1.56s
- PASS `zstd q10 topn=default` rows 20/20 0.92s
- PASS `zstd q11 topn=default` rows 1048/1048 0.18s
- PASS `zstd q12 topn=default` rows 2/2 0.43s
- PASS `zstd q13 topn=default` rows 42/42 0.75s
- PASS `zstd q14 topn=default` rows 1/1 0.34s
- PASS `zstd q15 topn=default` rows 1/1 0.39s
- PASS `zstd q16 topn=default` rows 18314/18314 0.88s
- PASS `zstd q17 topn=default` rows 1/1 0.26s
- PASS `zstd q18 topn=default` rows 57/57 1.56s
- PASS `zstd q19 topn=default` rows 1/1 0.48s
- PASS `zstd q20 topn=default` rows 186/186 0.55s
- PASS `zstd q21 topn=default` rows 100/100 1.40s
- PASS `zstd q22 topn=default` rows 7/7 0.21s
- PASS `zstd q01 topn=0` rows 4/4 0.71s
- PASS `zstd q02 topn=0` rows 100/100 0.14s
- PASS `zstd q03 topn=0` rows 10/10 1.05s
- PASS `zstd q04 topn=0` rows 5/5 0.66s
- PASS `zstd q05 topn=0` rows 5/5 0.90s
- PASS `zstd q06 topn=0` rows 1/1 0.24s
- PASS `zstd q07 topn=0` rows 4/4 0.48s
- PASS `zstd q08 topn=0` rows 2/2 1.45s
- PASS `zstd q09 topn=0` rows 175/175 1.51s
- PASS `zstd q10 topn=0` rows 20/20 0.87s
- PASS `zstd q11 topn=0` rows 1048/1048 0.19s
- PASS `zstd q12 topn=0` rows 2/2 0.44s
- PASS `zstd q13 topn=0` rows 42/42 0.72s
- PASS `zstd q14 topn=0` rows 1/1 0.36s
- PASS `zstd q15 topn=0` rows 1/1 0.37s
- PASS `zstd q16 topn=0` rows 18314/18314 0.69s
- PASS `zstd q17 topn=0` rows 1/1 0.27s
- PASS `zstd q18 topn=0` rows 57/57 1.33s
- PASS `zstd q19 topn=0` rows 1/1 0.60s
- PASS `zstd q20 topn=0` rows 186/186 0.50s
- PASS `zstd q21 topn=0` rows 100/100 1.42s
- PASS `zstd q22 topn=0` rows 7/7 0.20s
- PASS `types.alltypes lz4 = none` rows 5000/5000
- PASS `types.alltypes zstd = none` rows 5000/5000
- PASS `types.alltypes_full lz4 = none` rows 5000/5000
- PASS `types.alltypes_full zstd = none` rows 5000/5000
- PASS `tc netem on veth1a287ff` 
- PASS `scan lz4 netem = DuckDB` 
- PASS `scan none netem = DuckDB` 
- PASS `scan zstd netem = DuckDB` 
- PASS `scan lz4 plain = DuckDB` 
- PASS `scan none plain = DuckDB` 
- PASS `scan zstd plain = DuckDB` 
- PASS `lz4 plain: bytes into sr < 0.8 x none` 172.2 MB vs 356.5 MB
- PASS `zstd plain: bytes into sr < 0.8 x none` 115.4 MB vs 356.5 MB
- PASS `lz4 netem: bytes into sr < 0.8 x none` 172.2 MB vs 356.5 MB
- PASS `zstd netem: bytes into sr < 0.8 x none` 115.4 MB vs 356.5 MB
- note: netem link (delay 10ms rate 1gbit) lz4: 1.59 s, 172.2 MB into sr, 352.7 MB decoded (BytesRead), 221 MB/s decoded, 108 MB/s on the wire
- note: netem link (delay 10ms rate 1gbit) none: 3.15 s, 356.5 MB into sr, 352.7 MB decoded (BytesRead), 112 MB/s decoded, 113 MB/s on the wire
- note: netem link (delay 10ms rate 1gbit) zstd: 1.90 s, 115.4 MB into sr, 352.7 MB decoded (BytesRead), 185 MB/s decoded, 61 MB/s on the wire
- note: plain link () lz4: 1.42 s, 172.2 MB into sr, 352.7 MB decoded (BytesRead), 249 MB/s decoded, 121 MB/s on the wire
- note: plain link () none: 1.15 s, 356.5 MB into sr, 352.7 MB decoded (BytesRead), 307 MB/s decoded, 311 MB/s on the wire
- note: plain link () zstd: 1.78 s, 115.4 MB into sr, 352.7 MB decoded (BytesRead), 199 MB/s decoded, 65 MB/s on the wire

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
