# M4 run 40694415405

2026-10-28 13:20 UTC, series `4.1.4-4a9848e-flf41597`, server `arrow-flight-server-1.0.0-a9e43ca5e296-linux.jar`, store `s3: s3://lake/parquet`, compression `none`, checks 1,2,3,4,5,6,7,8,9

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 3 s |
| 2 | types tables, every column | PASS | 52/52 | 6 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | PASS | 21/21 | 7 s |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | PASS | 46/46 | 26 s |
| 5 | sr-cases on SF1 | PASS | 26/26 | 4 s |
| 6 | failover (2 servers) | PASS | 6/6 | 62 s |
| 7 | KILL QUERY during a long scan | PASS | 2/2 | 6 s |
| 8 | token and TLS | PASS | 14/14 | 18 s |
| 9 | memory limit | PASS | 6/6 | 10 s |

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

## Check 2: types tables, every column

- PASS `types.alltypes SELECT * row count` got 5000 expected 5000
- PASS `types.alltypes.c_bool (BOOLEAN)` 0/5000 differ
- PASS `types.alltypes.c_tinyint (TINYINT)` 0/5000 differ
- PASS `types.alltypes.c_smallint (SMALLINT)` 0/5000 differ
- PASS `types.alltypes.c_int (INTEGER)` 0/5000 differ
- PASS `types.alltypes.c_bigint (BIGINT)` 0/5000 differ
- PASS `types.alltypes.c_utinyint (UTINYINT)` 0/5000 differ
- PASS `types.alltypes.c_usmallint (USMALLINT)` 0/5000 differ
- PASS `types.alltypes.c_uinteger (UINTEGER)` 0/5000 differ
- PASS `types.alltypes.c_ubigint (UBIGINT)` 0/5000 differ
- PASS `types.alltypes.c_hugeint (DOUBLE)` 0/5000 differ
- PASS `types.alltypes.c_float (FLOAT)` 0/5000 differ
- PASS `types.alltypes.c_double (DOUBLE)` 0/5000 differ
- PASS `types.alltypes.c_dec9_2 (DECIMAL(9,2))` 0/5000 differ
- PASS `types.alltypes.c_dec18_4 (DECIMAL(18,4))` 0/5000 differ
- PASS `types.alltypes.c_dec38_10 (DECIMAL(38,10))` 0/5000 differ
- PASS `types.alltypes.c_varchar (VARCHAR)` 0/5000 differ
- PASS `types.alltypes.c_date (DATE)` 0/5000 differ
- PASS `types.alltypes.c_time (TIME)` 0/5000 differ
- PASS `types.alltypes.c_ts (TIMESTAMP)` 0/5000 differ
- PASS `types.alltypes.c_ts_ms (TIMESTAMP)` 0/5000 differ
- PASS `types.alltypes.c_ts_ns (TIMESTAMP_NS)` 0/5000 differ
- PASS `types.alltypes.c_tstz (TIMESTAMP WITH TIME ZONE)` 0/5000 differ
- PASS `types.alltypes_full SELECT * row count` got 5000 expected 5000
- PASS `types.alltypes_full.c_bool (BOOLEAN)` 0/5000 differ
- PASS `types.alltypes_full.c_tinyint (TINYINT)` 0/5000 differ
- PASS `types.alltypes_full.c_smallint (SMALLINT)` 0/5000 differ
- PASS `types.alltypes_full.c_int (INTEGER)` 0/5000 differ
- PASS `types.alltypes_full.c_bigint (BIGINT)` 0/5000 differ
- PASS `types.alltypes_full.c_utinyint (UTINYINT)` 0/5000 differ
- PASS `types.alltypes_full.c_usmallint (USMALLINT)` 0/5000 differ
- PASS `types.alltypes_full.c_uinteger (UINTEGER)` 0/5000 differ
- PASS `types.alltypes_full.c_ubigint (UBIGINT)` 0/5000 differ
- PASS `types.alltypes_full.c_hugeint (DOUBLE)` 0/5000 differ
- PASS `types.alltypes_full.c_float (FLOAT)` 0/5000 differ
- PASS `types.alltypes_full.c_double (DOUBLE)` 0/5000 differ
- PASS `types.alltypes_full.c_dec9_2 (DECIMAL(9,2))` 0/5000 differ
- PASS `types.alltypes_full.c_dec18_4 (DECIMAL(18,4))` 0/5000 differ
- PASS `types.alltypes_full.c_dec38_10 (DECIMAL(38,10))` 0/5000 differ
- PASS `types.alltypes_full.c_varchar (VARCHAR)` 0/5000 differ
- PASS `types.alltypes_full.c_blob (BLOB)` 0/5000 differ
- PASS `types.alltypes_full.c_date (DATE)` 0/5000 differ
- PASS `types.alltypes_full.c_time (TIME)` 0/5000 differ
- PASS `types.alltypes_full.c_ts (TIMESTAMP)` 0/5000 differ
- PASS `types.alltypes_full.c_ts_ms (TIMESTAMP)` 0/5000 differ
- PASS `types.alltypes_full.c_ts_ns (TIMESTAMP_NS)` 0/5000 differ
- PASS `types.alltypes_full.c_tstz (TIMESTAMP WITH TIME ZONE)` 0/5000 differ
- PASS `types.alltypes_full.c_uuid (UUID)` 0/5000 differ
- PASS `types.alltypes_full.c_interval (INTERVAL)` 0/5000 differ
- PASS `types.alltypes_full.c_list (BIGINT[])` 0/5000 differ
- PASS `types.alltypes_full.c_struct (STRUCT(a INTEGER, b VARCHAR))` 0/5000 differ
- PASS `types.alltypes_full.c_map (MAP(VARCHAR, INTEGER))` 0/5000 differ
- note: server direct (ADBC, headers {}): SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: decimal128(20, 0); rows [{'id': 2, 'c_ubigint': Decimal('18446744073709551615')}, {'id': 3, 'c_ubigint': Decimal('9223372036854775808')}]
- note: server direct (ADBC, headers {'x-flight-result-mode': 'partial'}): SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: decimal128(20, 0); rows [{'id': 2, 'c_ubigint': Decimal('18446744073709551615')}, {'id': 3, 'c_ubigint': Decimal('9223372036854775808')}]
- note: server direct (ADBC, headers {'x-flight-result-mode': 'complete'}): SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: decimal128(20, 0); rows [{'id': 2, 'c_ubigint': Decimal('18446744073709551615')}, {'id': 3, 'c_ubigint': Decimal('9223372036854775808')}]
- note: StarRocks, result_mode=complete: c_ubigint id 2,3 = [(2, Decimal('18446744073709551615')), (3, Decimal('9223372036854775808'))]
- note: types.alltypes: hidden columns []
- note: types.alltypes_full: hidden columns []

## Check 3: M4-TESTS §1–2 (EXPLAIN + results)

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (0.17s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.03s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.03s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.09s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (0.79s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.09s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.06s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.10s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.11s)
- PASS `2.3 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.32s)
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.30s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.04s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.03s)
- PASS `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_quantity" FROM "tpch"."lineitem" | rows 1 (0.27s)
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.22s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.34s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.03s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.08s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.09s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (0.70s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (0.77s)

## Check 4: TPC-H SF1 q01–q22, topn default and 0

- PASS `q05 EXPLAIN COSTS: row counts of all 6 Flight scans` tpch.region=5, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.lineitem=6001215, tpch.orders=227651
- PASS `q05 EXPLAIN COSTS: orders estimate from o_orderdate min/max` orders=[227651], band 150000..320000 (scale 1)
- PASS `q01 topn=default` rows 4/4 1.00s
- PASS `q02 topn=default` rows 100/100 0.31s
- PASS `q03 topn=default` rows 10/10 0.61s
- PASS `q04 topn=default` rows 5/5 0.40s
- PASS `q05 topn=default` rows 5/5 0.73s
- PASS `q06 topn=default` rows 1/1 0.25s
- PASS `q07 topn=default` rows 4/4 0.69s
- PASS `q08 topn=default` rows 2/2 0.95s
- PASS `q09 topn=default` rows 175/175 1.05s
- PASS `q10 topn=default` rows 20/20 0.74s
- PASS `q11 topn=default` rows 1048/1048 0.21s
- PASS `q12 topn=default` rows 2/2 0.49s
- PASS `q13 topn=default` rows 42/42 0.50s
- PASS `q14 topn=default` rows 1/1 0.30s
- PASS `q15 topn=default` rows 1/1 0.44s
- PASS `q16 topn=default` rows 18314/18314 0.23s
- PASS `q17 topn=default` rows 1/1 0.55s
- PASS `q18 topn=default` rows 57/57 0.94s
- PASS `q19 topn=default` rows 1/1 0.48s
- PASS `q20 topn=default` rows 186/186 0.44s
- PASS `q21 topn=default` rows 100/100 1.09s
- PASS `q22 topn=default` rows 7/7 0.19s
- PASS `q01 topn=0` rows 4/4 1.14s
- PASS `q02 topn=0` rows 100/100 0.18s
- PASS `q03 topn=0` rows 10/10 0.67s
- PASS `q04 topn=0` rows 5/5 0.35s
- PASS `q05 topn=0` rows 5/5 0.72s
- PASS `q06 topn=0` rows 1/1 0.24s
- PASS `q07 topn=0` rows 4/4 0.62s
- PASS `q08 topn=0` rows 2/2 0.97s
- PASS `q09 topn=0` rows 175/175 1.17s
- PASS `q10 topn=0` rows 20/20 0.76s
- PASS `q11 topn=0` rows 1048/1048 0.22s
- PASS `q12 topn=0` rows 2/2 0.47s
- PASS `q13 topn=0` rows 42/42 0.47s
- PASS `q14 topn=0` rows 1/1 0.27s
- PASS `q15 topn=0` rows 1/1 0.35s
- PASS `q16 topn=0` rows 18314/18314 0.19s
- PASS `q17 topn=0` rows 1/1 0.53s
- PASS `q18 topn=0` rows 57/57 0.89s
- PASS `q19 topn=0` rows 1/1 0.44s
- PASS `q20 topn=0` rows 186/186 0.43s
- PASS `q21 topn=0` rows 100/100 1.00s
- PASS `q22 topn=0` rows 7/7 0.13s
- note: q05 scans: tpch.region=5, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.lineitem=6001215, tpch.orders=227651
- note: q05 plan outline: PLAN FRAGMENT 0 / 28:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 28 / 25:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 25 / 22:HASH JOIN / |----21:EXCHANGE / 17:HASH JOIN / |----16:EXCHANGE / 13:HASH JOIN / |----12:EXCHANGE / 9:HASH JOIN / |----8:EXCHANGE / 6:EXCHANGE / PLAN FRAGMENT 3 / EXCHANGE ID: 21 / TABLE: tpch.region / PLAN FRAGMENT 4 / EXCHANGE ID: 16 / TABLE: tpch.nation / PLAN FRAGMENT 5 / EXCHANGE ID: 12 / TABLE: tpch.supplier / PLAN FRAGMENT 6 / EXCHANGE ID: 08 / TABLE: tpch.customer / PLAN FRAGMENT 7 / EXCHANGE ID: 06 / 4:HASH JOIN / |----3:EXCHANGE / TABLE: tpch.lineitem / PLAN FRAGMENT 8 / EXCHANGE ID: 03 / TABLE: tpch.orders
- note: q08 scans: tpch.lineitem=6001215, tpch.region=5, tpch.nation=25, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.part=200000, tpch.orders=455301
- note: q08 plan outline: PLAN FRAGMENT 0 / 36:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 36 / 32:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 32 / 29:HASH JOIN / |----28:EXCHANGE / 24:HASH JOIN / |----23:EXCHANGE / 20:HASH JOIN / |----19:EXCHANGE / 16:HASH JOIN / |----15:EXCHANGE / 12:HASH JOIN / |----11:EXCHANGE / 8:HASH JOIN / |----7:EXCHANGE / 3:HASH JOIN / |----2:EXCHANGE / TABLE: tpch.lineitem / PLAN FRAGMENT 3 / EXCHANGE ID: 28 / TABLE: tpch.region / PLAN FRAGMENT 4 / EXCHANGE ID: 23 / TABLE: tpch.nation / PLAN FRAGMENT 5 / EXCHANGE ID: 19 / TABLE: tpch.nation / PLAN FRAGMENT 6 / EXCHANGE ID: 15 / TABLE: tpch.supplier / PLAN FRAGMENT 7 / EXCHANGE ID: 11 / TABLE: tpch.customer / PLAN FRAGMENT 8 / EXCHANGE ID: 07 / TABLE: tpch.part / PLAN FRAGMENT 9 / EXCHANGE ID: 02 / TABLE: tpch.orders
- note: q09 scans: tpch.nation=25, tpch.supplier=10000, tpch.part=50000, tpch.partsupp=800000, tpch.orders=1500000, tpch.lineitem=6001215
- note: q09 plan outline: PLAN FRAGMENT 0 / 28:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 28 / 25:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 25 / 22:HASH JOIN / |----21:EXCHANGE / 18:HASH JOIN / |----17:EXCHANGE / 14:HASH JOIN / |----13:EXCHANGE / 9:HASH JOIN / |----8:EXCHANGE / 6:EXCHANGE / PLAN FRAGMENT 3 / EXCHANGE ID: 21 / TABLE: tpch.nation / PLAN FRAGMENT 4 / EXCHANGE ID: 17 / TABLE: tpch.supplier / PLAN FRAGMENT 5 / EXCHANGE ID: 13 / TABLE: tpch.part / PLAN FRAGMENT 6 / EXCHANGE ID: 08 / TABLE: tpch.partsupp / PLAN FRAGMENT 7 / EXCHANGE ID: 06 / 4:HASH JOIN / |----3:EXCHANGE / 1:EXCHANGE / PLAN FRAGMENT 8 / EXCHANGE ID: 03 / TABLE: tpch.orders / PLAN FRAGMENT 9 / EXCHANGE ID: 01 / TABLE: tpch.lineitem
- note: timings flight (s): q01/default=1.00, q02/default=0.31, q03/default=0.61, q04/default=0.40, q05/default=0.73, q06/default=0.25, q07/default=0.69, q08/default=0.95, q09/default=1.05, q10/default=0.74, q11/default=0.21, q12/default=0.49, q13/default=0.50, q14/default=0.30, q15/default=0.44, q16/default=0.23, q17/default=0.55, q18/default=0.94, q19/default=0.48, q20/default=0.44, q21/default=1.09, q22/default=0.19, q01/0=1.14, q02/0=0.18, q03/0=0.67, q04/0=0.35, q05/0=0.72, q06/0=0.24, q07/0=0.62, q08/0=0.97, q09/0=1.17, q10/0=0.76, q11/0=0.22, q12/0=0.47, q13/0=0.47, q14/0=0.27, q15/0=0.35, q16/0=0.19, q17/0=0.53, q18/0=0.89, q19/0=0.44, q20/0=0.43, q21/0=1.00, q22/0=0.13

## Check 5: sr-cases on SF1

- PASS `SELECT count(*), sum(l_extendedprice) FROM flight.tpch.lineitem WHERE l_orderkey IN (SELECT o_orderkey FROM flight.tpch.orders WHERE o_orderdate = DATE '1995-03-15')` rows 1
- PASS `SELECT count(*), sum(o_totalprice) FROM flight.tpch.orders WHERE o_orderdate >= DATE '1998-07-01'` rows 1
- PASS `SELECT o_orderpriority, count(*), sum(o_totalprice) FROM flight.tpch.orders WHERE o_orderdate >= DATE '1997-01-01' GROUP BY o_orderpriority` rows 5
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_orderdate >= '1998-08-01'` rows 1
- PASS `SELECT n_name FROM flight.tpch.nation WHERE (n_name = 'O''Brien')` rows 0
- PASS `SELECT n_name FROM flight.tpch.nation WHERE (n_name = 'O\'Brien')` rows 0
- PASS `SELECT n_name FROM flight.tpch.nation WHERE (n_name = 'a "tpch" b')` rows 0
- PASS `SELECT n_regionkey FROM flight.tpch.`nation`` rows 25
- PASS `SELECT `n_name` FROM flight.tpch.`nation` WHERE (`n_nationkey` = 5)` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_orderkey < 1000` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_custkey = 370` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_orderdate = DATE '1995-03-15'` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_orderdate >= DATE '1998-08-01'` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1995-01-31'` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_orderpriority IN ('1-URGENT','2-HIGH')` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_totalprice > 500000.00` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_totalprice BETWEEN 1000.00 AND 1100.50` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_clerk LIKE 'Clerk#00000000%'` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%special requests%'` rows 1
- PASS `SELECT count(*) FROM flight.tpch.orders WHERE o_comment IS NULL` rows 1
- PASS `SELECT o_orderstatus, count(*), sum(o_totalprice), min(o_orderdate), max(o_orderdate) FROM flight.tpch.orders GROUP BY o_orderstatus ORDER BY o_orderstatus` rows 3
- PASS `SELECT l_returnflag, l_linestatus, count(*), sum(l_quantity), sum(l_extendedprice), min(l_shipdate), max(l_shipdate), avg(l_discount) FROM flight.tpch.lineitem GROUP BY l_returnflag, l_linestatus ORDE` rows 4
- PASS `SELECT o_orderkey, o_totalprice, o_orderdate FROM flight.tpch.orders ORDER BY o_totalprice DESC, o_orderkey LIMIT 5` rows 5
- PASS `SELECT l_orderkey, l_linenumber, l_extendedprice FROM flight.tpch.lineitem ORDER BY l_extendedprice DESC, l_orderkey, l_linenumber LIMIT 5` rows 5
- PASS `SELECT n_name, count(*), sum(o_totalprice) FROM flight.tpch.orders JOIN flight.tpch.customer ON o_custkey = c_custkey JOIN flight.tpch.nation ON c_nationkey = n_nationkey WHERE o_orderdate >= DATE '19` rows 5
- PASS `SELECT count(*), sum(l_extendedprice) FROM flight.tpch.lineitem JOIN flight.tpch.orders ON l_orderkey = o_orderkey WHERE o_orderdate = DATE '1995-03-15'` rows 1

## Check 6: failover (2 servers)

- PASS `both servers up: full scan correct` 3.5s got=[('6001215', '153078795', '158997209')] exp=[('6001215', '153078795', '158997209')]
- PASS `both servers up: 3x lineitem read correct` 2.7s got=[('18003645', '459236385', '476991627')]
- PASS `flight2 stopped before the query: succeeds via backup locations` 15.6s got=[('6001215', '153078795', '158997209')]
- PASS `flight2 killed during the read: no wrong/duplicate rows` query succeeded in 2.7s got=[('18003645', '459236385', '476991627')] exp=[('18003645', '459236385', '476991627')]
- PASS `the kill overlapped the read (query ended after it; error or FailoverCount > 0)` ended 1.5s after the kill, success, FailoverCount=3
- PASS `BE alive after failover tests` 
- note: plan of the failover scan mentions 'flight' 0x
- note: query after the stop ran 13:19:02–13:19:17 UTC; fe.log failover lines: 2026-10-28 13:19:11.791Z WARN (starrocks-mysql-nio-pool-1|156) [FlightSqlMetadataClient.withFailover():258] Flight GetFlightInfo failed on grpc://flight1:32010 (UNAVAILABLE), trying next location / 2026-10-28 13:19:16.799Z WARN (starrocks-mysql-nio-pool-1|156) [FlightSqlMetadataClient.withFailover():238] Flight GetFlightInfo: cannot connect to grpc://flight2:32010 (TIMED_OUT), trying next location
- note: during: read time with both servers 2.7s; flight2 killed 1.2s into the query; query ended 1.5s after the kill

## Check 7: KILL QUERY during a long scan

- PASS `KILL QUERY stops the scan within ~1 s` 0.01s after KILL: OperationalError: (1317, 'killed manually: KILL QUERY 33554443')
- PASS `next query works` [(25,)]
- note: flight1 log lines with 'cancel' after the KILL: 24; [flight-server-default-executor-2] INFO pro.surpin.data.arrowflight.server.adapters.DuckDbAdapter - qid=1ec42d6c-1 node=flight1 backpressure=cancelled waited=18.1us / [flight-server-default-executor-2] INFO pro.surpin.data.arrowflight.server.adapters.FlightSqlProducer - qid=1ec42d6c-1 node=flight1 thread=flight-server-default-executor-2 execution=failed server=grpc+tcp://flight1:32010 elapsedMs=28

## Check 8: token and TLS

- PASS `token server, right token` ok [(25,)]
- PASS `token server, wrong token fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAUTHENTICATED: Missing or wrong access token\nFlightRuntimeException: Missing or wrong access token')
- PASS `token server, no token fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAUTHENTICATED: Missing or wrong access token\nFlightRuntimeException: Missing or wrong access token')
- PASS `token server, basic auth user:<token>` ok [(25,)]
- PASS `SHOW CREATE CATALOG masks the password` f_basic CREATE EXTERNAL CATALOG `f_basic`
PROPERTIES ("flight.password"  =  "******",
"type"  =  "flight",
"flight.uri"  =  "grpc://flight1:32010",
"flight.user"  =  "m4"
)
- PASS `query profile of a f_tok scan has the Flight scan` 16829 chars
- PASS `query profile of a f_tok scan: token not in it` 
- PASS `query profile of a f_basic scan has the Flight scan` 16937 chars
- PASS `query profile of a f_basic scan: token not in it` 
- PASS `TLS, trusted CA file` ok [(25,)]
- PASS `TLS, wrong host name fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAVAILABLE: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline$TailContext#0]\nFlightRuntimeException: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline
- PASS `TLS, untrusted certificate fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAVAILABLE: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline$TailContext#0]\nFlightRuntimeException: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline
- PASS `TLS, flight.tls.verify=false` ok [(25,)]
- PASS `plain client against the TLS server fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAVAILABLE: Network closed for unknown reason\nFlightRuntimeException: Network closed for unknown reason')

## Check 9: memory limit

- PASS `big aggregation under query_mem_limit=100MB fails cleanly` 1.3s ProgrammingError: (1064, 'Memory of Query01a182aa-fcff-7ade-9872-61b14f2ecfda exceed limit. Pipeline Backend: 127.0.0.1, fragment: 01a182aa-fcff-7ade-9872-61b14f2ecfdd Used: 105072880, Limit: 104857600. Mem usage has exceed the limit of single query, You can change the limit by set session variable query_mem_limit.: BE:10001')
- PASS `BE alive afterwards` 
- PASS `next query works` [(25,)]
- PASS `q18 same rows with flight.exchange_buffer_mb=16 and 0` rows 57/57
- PASS `q18 local exchange peak with the cap <= without (when the uncapped peak exceeds 16 MB)` flight (16 MB/driver): exchange peak 32.1 MB, query peak/node 277.1 MB; exchange_buffer_mb=0: exchange peak 49.0 MB, query peak/node 246.6 MB; cpus 4
- PASS `q18 local exchange peak <= 16 MB x cpus (+16 MB)` flight (16 MB/driver): exchange peak 32.1 MB, query peak/node 277.1 MB; exchange_buffer_mb=0: exchange peak 49.0 MB, query peak/node 246.6 MB; cpus 4
- note: q18 pre-aggregation modes: force_streaming; aggregation pushed

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
