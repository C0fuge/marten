# M4 run 42236969873

2026-11-06 15:30 UTC, series `4.1.4-4a9848e-fl1eb792`, server `arrow-flight-server-1.0.0-deafc861cce3-linux.jar`, store `s3: s3://lake/parquet`, compression `none`, checks 13, runner 4 x AMD EPYC 7763 64-Core Processor

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

- PASS `lz4 q01 topn=default` rows 4/4 0.79s
- PASS `lz4 q02 topn=default` rows 100/100 0.30s
- PASS `lz4 q03 topn=default` rows 10/10 0.92s
- PASS `lz4 q04 topn=default` rows 5/5 0.63s
- PASS `lz4 q05 topn=default` rows 5/5 1.12s
- PASS `lz4 q06 topn=default` rows 1/1 0.25s
- PASS `lz4 q07 topn=default` rows 4/4 0.73s
- PASS `lz4 q08 topn=default` rows 2/2 1.30s
- PASS `lz4 q09 topn=default` rows 175/175 1.31s
- PASS `lz4 q10 topn=default` rows 20/20 0.91s
- PASS `lz4 q11 topn=default` rows 1048/1048 0.22s
- PASS `lz4 q12 topn=default` rows 2/2 0.54s
- PASS `lz4 q13 topn=default` rows 42/42 0.64s
- PASS `lz4 q14 topn=default` rows 1/1 0.33s
- PASS `lz4 q15 topn=default` rows 1/1 0.36s
- PASS `lz4 q16 topn=default` rows 18314/18314 1.72s
- PASS `lz4 q17 topn=default` rows 1/1 0.29s
- PASS `lz4 q18 topn=default` rows 57/57 1.09s
- PASS `lz4 q19 topn=default` rows 1/1 0.55s
- PASS `lz4 q20 topn=default` rows 186/186 0.52s
- PASS `lz4 q21 topn=default` rows 100/100 1.38s
- PASS `lz4 q22 topn=default` rows 7/7 0.20s
- PASS `lz4 q01 topn=0` rows 4/4 0.70s
- PASS `lz4 q02 topn=0` rows 100/100 0.22s
- PASS `lz4 q03 topn=0` rows 10/10 0.82s
- PASS `lz4 q04 topn=0` rows 5/5 0.56s
- PASS `lz4 q05 topn=0` rows 5/5 0.90s
- PASS `lz4 q06 topn=0` rows 1/1 0.22s
- PASS `lz4 q07 topn=0` rows 4/4 0.68s
- PASS `lz4 q08 topn=0` rows 2/2 1.23s
- PASS `lz4 q09 topn=0` rows 175/175 1.17s
- PASS `lz4 q10 topn=0` rows 20/20 0.82s
- PASS `lz4 q11 topn=0` rows 1048/1048 0.23s
- PASS `lz4 q12 topn=0` rows 2/2 0.45s
- PASS `lz4 q13 topn=0` rows 42/42 0.60s
- PASS `lz4 q14 topn=0` rows 1/1 0.30s
- PASS `lz4 q15 topn=0` rows 1/1 0.37s
- PASS `lz4 q16 topn=0` rows 18314/18314 0.76s
- PASS `lz4 q17 topn=0` rows 1/1 0.27s
- PASS `lz4 q18 topn=0` rows 57/57 0.96s
- PASS `lz4 q19 topn=0` rows 1/1 0.43s
- PASS `lz4 q20 topn=0` rows 186/186 0.45s
- PASS `lz4 q21 topn=0` rows 100/100 1.57s
- PASS `lz4 q22 topn=0` rows 7/7 0.20s
- PASS `zstd q01 topn=default` rows 4/4 0.75s
- PASS `zstd q02 topn=default` rows 100/100 0.25s
- PASS `zstd q03 topn=default` rows 10/10 0.98s
- PASS `zstd q04 topn=default` rows 5/5 0.65s
- PASS `zstd q05 topn=default` rows 5/5 1.09s
- PASS `zstd q06 topn=default` rows 1/1 0.21s
- PASS `zstd q07 topn=default` rows 4/4 0.69s
- PASS `zstd q08 topn=default` rows 2/2 1.36s
- PASS `zstd q09 topn=default` rows 175/175 1.50s
- PASS `zstd q10 topn=default` rows 20/20 0.88s
- PASS `zstd q11 topn=default` rows 1048/1048 0.23s
- PASS `zstd q12 topn=default` rows 2/2 0.45s
- PASS `zstd q13 topn=default` rows 42/42 0.73s
- PASS `zstd q14 topn=default` rows 1/1 0.28s
- PASS `zstd q15 topn=default` rows 1/1 0.34s
- PASS `zstd q16 topn=default` rows 18314/18314 0.87s
- PASS `zstd q17 topn=default` rows 1/1 0.32s
- PASS `zstd q18 topn=default` rows 57/57 1.17s
- PASS `zstd q19 topn=default` rows 1/1 0.48s
- PASS `zstd q20 topn=default` rows 186/186 0.52s
- PASS `zstd q21 topn=default` rows 100/100 1.46s
- PASS `zstd q22 topn=default` rows 7/7 0.17s
- PASS `zstd q01 topn=0` rows 4/4 0.69s
- PASS `zstd q02 topn=0` rows 100/100 0.22s
- PASS `zstd q03 topn=0` rows 10/10 0.87s
- PASS `zstd q04 topn=0` rows 5/5 0.57s
- PASS `zstd q05 topn=0` rows 5/5 1.09s
- PASS `zstd q06 topn=0` rows 1/1 0.22s
- PASS `zstd q07 topn=0` rows 4/4 0.76s
- PASS `zstd q08 topn=0` rows 2/2 1.36s
- PASS `zstd q09 topn=0` rows 175/175 1.44s
- PASS `zstd q10 topn=0` rows 20/20 0.88s
- PASS `zstd q11 topn=0` rows 1048/1048 0.25s
- PASS `zstd q12 topn=0` rows 2/2 0.46s
- PASS `zstd q13 topn=0` rows 42/42 0.71s
- PASS `zstd q14 topn=0` rows 1/1 0.33s
- PASS `zstd q15 topn=0` rows 1/1 0.33s
- PASS `zstd q16 topn=0` rows 18314/18314 0.78s
- PASS `zstd q17 topn=0` rows 1/1 0.25s
- PASS `zstd q18 topn=0` rows 57/57 1.00s
- PASS `zstd q19 topn=0` rows 1/1 0.41s
- PASS `zstd q20 topn=0` rows 186/186 0.58s
- PASS `zstd q21 topn=0` rows 100/100 1.73s
- PASS `zstd q22 topn=0` rows 7/7 0.17s
- PASS `types.alltypes lz4 = none` rows 5000/5000
- PASS `types.alltypes zstd = none` rows 5000/5000
- PASS `types.alltypes_full lz4 = none` rows 5000/5000
- PASS `types.alltypes_full zstd = none` rows 5000/5000
- PASS `tc netem on veth5daeb5b` 
- PASS `scan lz4 netem = DuckDB` 
- PASS `scan none netem = DuckDB` 
- PASS `scan zstd netem = DuckDB` 
- PASS `scan lz4 plain = DuckDB` 
- PASS `scan none plain = DuckDB` 
- PASS `scan zstd plain = DuckDB` 
- PASS `lz4 plain: bytes into sr < 0.8 x none` 172.2 MB vs 358.3 MB
- PASS `zstd plain: bytes into sr < 0.8 x none` 115.4 MB vs 358.3 MB
- PASS `lz4 netem: bytes into sr < 0.8 x none` 172.2 MB vs 356.5 MB
- PASS `zstd netem: bytes into sr < 0.8 x none` 115.4 MB vs 356.5 MB
- note: netem link (delay 10ms rate 1gbit) lz4: 1.59 s, 172.2 MB into sr, 352.7 MB decoded (BytesRead), 222 MB/s decoded, 108 MB/s on the wire
- note: netem link (delay 10ms rate 1gbit) none: 3.13 s, 356.5 MB into sr, 352.7 MB decoded (BytesRead), 113 MB/s decoded, 114 MB/s on the wire
- note: netem link (delay 10ms rate 1gbit) zstd: 1.88 s, 115.4 MB into sr, 352.7 MB decoded (BytesRead), 188 MB/s decoded, 61 MB/s on the wire
- note: plain link () lz4: 1.48 s, 172.2 MB into sr, 352.7 MB decoded (BytesRead), 238 MB/s decoded, 116 MB/s on the wire
- note: plain link () none: 1.21 s, 358.3 MB into sr, 352.7 MB decoded (BytesRead), 292 MB/s decoded, 296 MB/s on the wire
- note: plain link () zstd: 1.80 s, 115.4 MB into sr, 352.7 MB decoded (BytesRead), 196 MB/s decoded, 64 MB/s on the wire

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
