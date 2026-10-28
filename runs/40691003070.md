# M4 run 40691003070

2026-10-28 12:56 UTC, series `4.1.4-4a9848e-flf41597`, server `arrow-flight-server-1.0.0-cadd1aca9c23-linux.jar`, store `s3: s3://lake/parquet`, compression `none`, checks 13

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 4 s |
| 13 | result compression (flight.compression none / lz4 / zstd) | PASS | 103/103 | 94 s |

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

- PASS `lz4 q01 topn=default` rows 4/4 1.48s
- PASS `lz4 q02 topn=default` rows 100/100 0.37s
- PASS `lz4 q03 topn=default` rows 10/10 0.77s
- PASS `lz4 q04 topn=default` rows 5/5 0.52s
- PASS `lz4 q05 topn=default` rows 5/5 0.93s
- PASS `lz4 q06 topn=default` rows 1/1 0.27s
- PASS `lz4 q07 topn=default` rows 4/4 0.83s
- PASS `lz4 q08 topn=default` rows 2/2 1.23s
- PASS `lz4 q09 topn=default` rows 175/175 1.33s
- PASS `lz4 q10 topn=default` rows 20/20 0.79s
- PASS `lz4 q11 topn=default` rows 1048/1048 0.39s
- PASS `lz4 q12 topn=default` rows 2/2 0.56s
- PASS `lz4 q13 topn=default` rows 42/42 0.68s
- PASS `lz4 q14 topn=default` rows 1/1 0.35s
- PASS `lz4 q15 topn=default` rows 1/1 0.38s
- PASS `lz4 q16 topn=default` rows 18314/18314 0.30s
- PASS `lz4 q17 topn=default` rows 1/1 0.67s
- PASS `lz4 q18 topn=default` rows 57/57 1.02s
- PASS `lz4 q19 topn=default` rows 1/1 0.47s
- PASS `lz4 q20 topn=default` rows 186/186 0.51s
- PASS `lz4 q21 topn=default` rows 100/100 1.36s
- PASS `lz4 q22 topn=default` rows 7/7 0.21s
- PASS `lz4 q01 topn=0` rows 4/4 1.12s
- PASS `lz4 q02 topn=0` rows 100/100 0.21s
- PASS `lz4 q03 topn=0` rows 10/10 0.69s
- PASS `lz4 q04 topn=0` rows 5/5 0.46s
- PASS `lz4 q05 topn=0` rows 5/5 0.83s
- PASS `lz4 q06 topn=0` rows 1/1 0.23s
- PASS `lz4 q07 topn=0` rows 4/4 0.72s
- PASS `lz4 q08 topn=0` rows 2/2 1.14s
- PASS `lz4 q09 topn=0` rows 175/175 1.35s
- PASS `lz4 q10 topn=0` rows 20/20 0.80s
- PASS `lz4 q11 topn=0` rows 1048/1048 0.28s
- PASS `lz4 q12 topn=0` rows 2/2 0.48s
- PASS `lz4 q13 topn=0` rows 42/42 0.62s
- PASS `lz4 q14 topn=0` rows 1/1 0.32s
- PASS `lz4 q15 topn=0` rows 1/1 0.37s
- PASS `lz4 q16 topn=0` rows 18314/18314 0.24s
- PASS `lz4 q17 topn=0` rows 1/1 0.64s
- PASS `lz4 q18 topn=0` rows 57/57 1.05s
- PASS `lz4 q19 topn=0` rows 1/1 0.42s
- PASS `lz4 q20 topn=0` rows 186/186 0.46s
- PASS `lz4 q21 topn=0` rows 100/100 1.37s
- PASS `lz4 q22 topn=0` rows 7/7 0.20s
- PASS `zstd q01 topn=default` rows 4/4 1.32s
- PASS `zstd q02 topn=default` rows 100/100 0.20s
- PASS `zstd q03 topn=default` rows 10/10 0.75s
- PASS `zstd q04 topn=default` rows 5/5 0.54s
- PASS `zstd q05 topn=default` rows 5/5 0.98s
- PASS `zstd q06 topn=default` rows 1/1 0.24s
- PASS `zstd q07 topn=default` rows 4/4 0.75s
- PASS `zstd q08 topn=default` rows 2/2 1.29s
- PASS `zstd q09 topn=default` rows 175/175 1.50s
- PASS `zstd q10 topn=default` rows 20/20 0.80s
- PASS `zstd q11 topn=default` rows 1048/1048 0.26s
- PASS `zstd q12 topn=default` rows 2/2 0.57s
- PASS `zstd q13 topn=default` rows 42/42 0.71s
- PASS `zstd q14 topn=default` rows 1/1 0.32s
- PASS `zstd q15 topn=default` rows 1/1 0.35s
- PASS `zstd q16 topn=default` rows 18314/18314 0.22s
- PASS `zstd q17 topn=default` rows 1/1 0.92s
- PASS `zstd q18 topn=default` rows 57/57 1.19s
- PASS `zstd q19 topn=default` rows 1/1 0.59s
- PASS `zstd q20 topn=default` rows 186/186 0.50s
- PASS `zstd q21 topn=default` rows 100/100 1.31s
- PASS `zstd q22 topn=default` rows 7/7 0.22s
- PASS `zstd q01 topn=0` rows 4/4 1.29s
- PASS `zstd q02 topn=0` rows 100/100 0.17s
- PASS `zstd q03 topn=0` rows 10/10 0.74s
- PASS `zstd q04 topn=0` rows 5/5 0.50s
- PASS `zstd q05 topn=0` rows 5/5 1.02s
- PASS `zstd q06 topn=0` rows 1/1 0.22s
- PASS `zstd q07 topn=0` rows 4/4 0.73s
- PASS `zstd q08 topn=0` rows 2/2 1.30s
- PASS `zstd q09 topn=0` rows 175/175 1.55s
- PASS `zstd q10 topn=0` rows 20/20 0.84s
- PASS `zstd q11 topn=0` rows 1048/1048 0.24s
- PASS `zstd q12 topn=0` rows 2/2 0.47s
- PASS `zstd q13 topn=0` rows 42/42 0.72s
- PASS `zstd q14 topn=0` rows 1/1 0.32s
- PASS `zstd q15 topn=0` rows 1/1 0.38s
- PASS `zstd q16 topn=0` rows 18314/18314 0.22s
- PASS `zstd q17 topn=0` rows 1/1 0.83s
- PASS `zstd q18 topn=0` rows 57/57 1.05s
- PASS `zstd q19 topn=0` rows 1/1 0.48s
- PASS `zstd q20 topn=0` rows 186/186 0.53s
- PASS `zstd q21 topn=0` rows 100/100 1.75s
- PASS `zstd q22 topn=0` rows 7/7 0.17s
- PASS `types.alltypes lz4 = none` rows 5000/5000
- PASS `types.alltypes zstd = none` rows 5000/5000
- PASS `types.alltypes_full lz4 = none` rows 5000/5000
- PASS `types.alltypes_full zstd = none` rows 5000/5000
- PASS `tc netem on vethcab6000` 
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
- note: netem link (delay 10ms rate 1gbit) lz4: 1.63 s, 172.2 MB into sr, 352.7 MB decoded (BytesRead), 217 MB/s decoded, 106 MB/s on the wire
- note: netem link (delay 10ms rate 1gbit) none: 3.16 s, 356.5 MB into sr, 352.7 MB decoded (BytesRead), 112 MB/s decoded, 113 MB/s on the wire
- note: netem link (delay 10ms rate 1gbit) zstd: 1.90 s, 115.4 MB into sr, 352.7 MB decoded (BytesRead), 185 MB/s decoded, 61 MB/s on the wire
- note: plain link () lz4: 1.51 s, 172.2 MB into sr, 352.7 MB decoded (BytesRead), 233 MB/s decoded, 114 MB/s on the wire
- note: plain link () none: 1.22 s, 356.5 MB into sr, 352.7 MB decoded (BytesRead), 290 MB/s decoded, 293 MB/s on the wire
- note: plain link () zstd: 1.85 s, 115.4 MB into sr, 352.7 MB decoded (BytesRead), 191 MB/s decoded, 62 MB/s on the wire

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
