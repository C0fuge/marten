# M4 run 39987340277

2026-10-23 16:36 UTC, series `4.1.4-4a9848e-fl4bda75`, server `arrow-flight-server-1.0.0-int7.jar`, store `lakefs: lakefs://m4lake/main/parquet`, checks 1,3,4,10

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 5 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | PASS | 21/21 | 12 s |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | PASS | 46/46 | 45 s |
| 10 | lakeFS: commits between queries | PASS | 5/5 | 6 s |

## Check 1: catalog, SHOW, DESC, masking

- PASS `create catalog` 
- PASS `SHOW CREATE CATALOG masks the token` flight CREATE EXTERNAL CATALOG `flight` PROPERTIES ("type"  =  "flight", "flight.token"  =  "******", "flight.uri"  =  "grpc://flight1:32010" )
- PASS `SHOW DATABASES has tpch and types` got ['information_schema', 'lfs', 'tpch', 'types']
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

## Check 3: M4-TESTS §1–2 (EXPLAIN + results)

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (0.72s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.07s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.13s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.28s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (1.38s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.10s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.16s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.16s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.19s)
- PASS `2.3 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.38s)
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.35s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.06s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.04s)
- PASS `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_quantity" FROM "tpch"."lineitem" | rows 1 (0.59s)
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.28s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.56s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.05s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.16s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.12s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (0.98s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.03s)

## Check 4: TPC-H SF1 q01–q22, topn default and 0

- PASS `q05 EXPLAIN COSTS: row counts of all 6 Flight scans` tpch.region=5, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.lineitem=6001215, tpch.orders=227651
- PASS `q05 EXPLAIN COSTS: orders estimate from o_orderdate min/max` orders=[227651], band 150000..320000 (scale 1)
- PASS `q01 topn=default` rows 4/4 1.73s
- PASS `q02 topn=default` rows 100/100 0.36s
- PASS `q03 topn=default` rows 10/10 1.12s
- PASS `q04 topn=default` rows 5/5 0.80s
- PASS `q05 topn=default` rows 5/5 1.28s
- PASS `q06 topn=default` rows 1/1 0.51s
- PASS `q07 topn=default` rows 4/4 1.20s
- PASS `q08 topn=default` rows 2/2 1.53s
- PASS `q09 topn=default` rows 175/175 1.85s
- PASS `q10 topn=default` rows 20/20 1.25s
- PASS `q11 topn=default` rows 1048/1048 0.32s
- PASS `q12 topn=default` rows 2/2 0.59s
- PASS `q13 topn=default` rows 42/42 0.65s
- PASS `q14 topn=default` rows 1/1 0.63s
- PASS `q15 topn=default` rows 1/1 0.92s
- PASS `q16 topn=default` rows 18314/18314 0.38s
- PASS `q17 topn=default` rows 1/1 0.93s
- PASS `q18 topn=default` rows 57/57 1.73s
- PASS `q19 topn=default` rows 1/1 0.83s
- PASS `q20 topn=default` rows 186/186 0.97s
- PASS `q21 topn=default` rows 100/100 2.70s
- PASS `q22 topn=default` rows 7/7 0.34s
- PASS `q01 topn=0` rows 4/4 1.70s
- PASS `q02 topn=0` rows 100/100 0.23s
- PASS `q03 topn=0` rows 10/10 1.19s
- PASS `q04 topn=0` rows 5/5 0.69s
- PASS `q05 topn=0` rows 5/5 1.25s
- PASS `q06 topn=0` rows 1/1 0.41s
- PASS `q07 topn=0` rows 4/4 1.23s
- PASS `q08 topn=0` rows 2/2 1.47s
- PASS `q09 topn=0` rows 175/175 1.67s
- PASS `q10 topn=0` rows 20/20 1.07s
- PASS `q11 topn=0` rows 1048/1048 0.50s
- PASS `q12 topn=0` rows 2/2 0.71s
- PASS `q13 topn=0` rows 42/42 0.62s
- PASS `q14 topn=0` rows 1/1 0.66s
- PASS `q15 topn=0` rows 1/1 0.87s
- PASS `q16 topn=0` rows 18314/18314 0.31s
- PASS `q17 topn=0` rows 1/1 0.87s
- PASS `q18 topn=0` rows 57/57 1.63s
- PASS `q19 topn=0` rows 1/1 0.87s
- PASS `q20 topn=0` rows 186/186 0.84s
- PASS `q21 topn=0` rows 100/100 2.03s
- PASS `q22 topn=0` rows 7/7 0.25s
- note: q05 scans: tpch.region=5, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.lineitem=6001215, tpch.orders=227651
- note: q05 plan outline: PLAN FRAGMENT 0 / 28:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 28 / 25:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 25 / 22:HASH JOIN / |----21:EXCHANGE / 17:HASH JOIN / |----16:EXCHANGE / 13:HASH JOIN / |----12:EXCHANGE / 9:HASH JOIN / |----8:EXCHANGE / 6:EXCHANGE / PLAN FRAGMENT 3 / EXCHANGE ID: 21 / TABLE: tpch.region / PLAN FRAGMENT 4 / EXCHANGE ID: 16 / TABLE: tpch.nation / PLAN FRAGMENT 5 / EXCHANGE ID: 12 / TABLE: tpch.supplier / PLAN FRAGMENT 6 / EXCHANGE ID: 08 / TABLE: tpch.customer / PLAN FRAGMENT 7 / EXCHANGE ID: 06 / 4:HASH JOIN / |----3:EXCHANGE / TABLE: tpch.lineitem / PLAN FRAGMENT 8 / EXCHANGE ID: 03 / TABLE: tpch.orders
- note: q08 scans: tpch.lineitem=6001215, tpch.region=5, tpch.nation=25, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.part=200000, tpch.orders=455301
- note: q08 plan outline: PLAN FRAGMENT 0 / 36:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 36 / 32:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 32 / 29:HASH JOIN / |----28:EXCHANGE / 24:HASH JOIN / |----23:EXCHANGE / 20:HASH JOIN / |----19:EXCHANGE / 16:HASH JOIN / |----15:EXCHANGE / 12:HASH JOIN / |----11:EXCHANGE / 8:HASH JOIN / |----7:EXCHANGE / 3:HASH JOIN / |----2:EXCHANGE / TABLE: tpch.lineitem / PLAN FRAGMENT 3 / EXCHANGE ID: 28 / TABLE: tpch.region / PLAN FRAGMENT 4 / EXCHANGE ID: 23 / TABLE: tpch.nation / PLAN FRAGMENT 5 / EXCHANGE ID: 19 / TABLE: tpch.nation / PLAN FRAGMENT 6 / EXCHANGE ID: 15 / TABLE: tpch.supplier / PLAN FRAGMENT 7 / EXCHANGE ID: 11 / TABLE: tpch.customer / PLAN FRAGMENT 8 / EXCHANGE ID: 07 / TABLE: tpch.part / PLAN FRAGMENT 9 / EXCHANGE ID: 02 / TABLE: tpch.orders
- note: q09 scans: tpch.nation=25, tpch.supplier=10000, tpch.part=50000, tpch.partsupp=800000, tpch.orders=1500000, tpch.lineitem=6001215
- note: q09 plan outline: PLAN FRAGMENT 0 / 28:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 28 / 25:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 25 / 22:HASH JOIN / |----21:EXCHANGE / 18:HASH JOIN / |----17:EXCHANGE / 14:HASH JOIN / |----13:EXCHANGE / 9:HASH JOIN / |----8:EXCHANGE / 6:EXCHANGE / PLAN FRAGMENT 3 / EXCHANGE ID: 21 / TABLE: tpch.nation / PLAN FRAGMENT 4 / EXCHANGE ID: 17 / TABLE: tpch.supplier / PLAN FRAGMENT 5 / EXCHANGE ID: 13 / TABLE: tpch.part / PLAN FRAGMENT 6 / EXCHANGE ID: 08 / TABLE: tpch.partsupp / PLAN FRAGMENT 7 / EXCHANGE ID: 06 / 4:HASH JOIN / |----3:EXCHANGE / 1:EXCHANGE / PLAN FRAGMENT 8 / EXCHANGE ID: 03 / TABLE: tpch.orders / PLAN FRAGMENT 9 / EXCHANGE ID: 01 / TABLE: tpch.lineitem
- note: timings flight (s): q01/default=1.73, q02/default=0.36, q03/default=1.12, q04/default=0.80, q05/default=1.28, q06/default=0.51, q07/default=1.20, q08/default=1.53, q09/default=1.85, q10/default=1.25, q11/default=0.32, q12/default=0.59, q13/default=0.65, q14/default=0.63, q15/default=0.92, q16/default=0.38, q17/default=0.93, q18/default=1.73, q19/default=0.83, q20/default=0.97, q21/default=2.70, q22/default=0.34, q01/0=1.70, q02/0=0.23, q03/0=1.19, q04/0=0.69, q05/0=1.25, q06/0=0.41, q07/0=1.23, q08/0=1.47, q09/0=1.67, q10/0=1.07, q11/0=0.50, q12/0=0.71, q13/0=0.62, q14/0=0.66, q15/0=0.87, q16/0=0.31, q17/0=0.87, q18/0=1.63, q19/0=0.87, q20/0=0.84, q21/0=2.03, q22/0=0.25

## Check 10: lakeFS: commits between queries

- PASS `lfs.t at the setup commit` got (1, 1), head 481defd27d2d
- PASS `a commit with 2 files is seen after the commit` got (7, 28) after 1.1 s, commit 9157bd8ced5a
- PASS `no query saw half of the commit` seen [(1, 1), (7, 28)]
- PASS `a commit deleting a file is seen` got (6, 27) after 1.1 s, commit 81a038242365
- PASS `tpch through lakeFS after the commits` [(6001215,)]
- note: with part-1 staged (uncommitted) a query returns (1, 1) (not visible)

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
