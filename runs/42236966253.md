# M4 run 42236966253

2026-11-06 15:07 UTC, series `4.1.4-4a9848e-fl1eb792`, server `arrow-flight-server-1.0.0-deafc861cce3-linux.jar`, store `lakefs: lakefs://m4lake/main/parquet`, compression `none`, checks 1,3,4,10, runner 4 x AMD EPYC 9V74 80-Core Processor

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 3 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | PASS | 27/27 | 11 s |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | PASS | 46/46 | 29 s |
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

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (0.42s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.04s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.05s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.11s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (0.78s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.07s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.06s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.10s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.08s)
- PASS `2.3 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.41s)
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.36s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.03s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.03s)
- PASS `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", count("l_quantity") AS "__flight_agg_1" FROM "tpch"."lineitem" | rows 1 (0.15s)
- PASS `2.5 (complete) SELECT avg(l_quantity) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", count("l_quantity") AS "__flight_agg_1" FROM "tpch"."lineitem" | rows 1 (0.18s)
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.21s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.32s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.04s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.12s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.09s)
- PASS `2.12 SELECT l_returnflag, l_linestatus, sum(l_quantity), sum(l_extendedprice * (1 - l_discount)), avg(l_quantity), avg(l_extendedprice), avg(l_discount), count(*) FROM flight.tpch.lineitem WHERE l_shi` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", sum(CAST((CAST("l_extendedprice" AS DECIMAL(15,2)) * CAST((1 - CAST("l_discount" AS DECIMAL(16,2))) AS DECIMAL(16,2))) AS DECIMAL(38,4))) AS "__flight_agg_1", sum(CAST("l_quantity" AS DECIMAL(38,2))) | rows 4 (0.65s)
- PASS `2.12 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), sum(l_extendedprice * (1 - l_discount)), avg(l_quantity), avg(l_extendedprice), avg(l_discount), count(*) FROM flight_c.tpch.lineite` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", sum(CAST((CAST("l_extendedprice" AS DECIMAL(15,2)) * CAST((1 - CAST("l_discount" AS DECIMAL(16,2))) AS DECIMAL(16,2))) AS DECIMAL(38,4))) AS "__flight_agg_1", sum(CAST("l_quantity" AS DECIMAL(38,2))) | rows 4 (0.63s)
- PASS `2.13 SELECT count(*), sum(l_quantity) FROM flight.tpch.lineitem, flight.tpch.part WHERE p_partkey = l_partkey AND p_brand = 'Brand#23' AND p_container = 'MED BOX'` REMOTE SQL: SELECT "p_partkey", "p_brand", "p_container" FROM "tpch"."part" WHERE ("p_brand" = 'Brand#23') AND ("p_container" = 'MED BOX') | SELECT "l_partkey", "l_quantity" FROM "tpch"."lineitem" WHERE ("l_partkey" IS NOT NULL) AND ("l_partkey" IN (2409, 2425, 4880, 5627, 6079, 7682, 10687, 11200, 11256, 11816 | rows 1 (0.31s)
- PASS `2.14 SELECT count(*), sum(l_quantity) FROM flight.tpch.lineitem, flight.tpch.part WHERE p_partkey = l_partkey AND p_brand = 'Brand#23' AND p_container = 'MED BOX'` REMOTE SQL: SELECT "l_partkey", "l_quantity" FROM "tpch"."lineitem" WHERE ("l_partkey" IS NOT NULL) | SELECT "p_partkey", "p_brand", "p_container" FROM "tpch"."part" WHERE ("p_brand" = 'Brand#23') AND ("p_container" = 'MED BOX') | rows 1 (0.42s)
- PASS `2.15 SELECT count(*), sum(l_extendedprice) FROM flight.tpch.lineitem, flight.tpch.part WHERE l_partkey = p_partkey AND l_shipdate >= DATE '1995-09-01' AND l_shipdate < DATE '1995-10-01'` REMOTE SQL: SELECT "l_partkey", "l_extendedprice", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1995-09-01') AND ("l_shipdate" < DATE '1995-10-01') | SELECT "p_partkey" FROM "tpch"."part" WHERE ("p_partkey" IS NOT NULL) | rows 1 (0.30s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (0.71s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (0.73s)

## Check 4: TPC-H SF1 q01–q22, topn default and 0

- PASS `q05 EXPLAIN COSTS: row counts of all 6 Flight scans` tpch.region=5, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.lineitem=6001215, tpch.orders=227651
- PASS `q05 EXPLAIN COSTS: orders estimate from o_orderdate min/max` orders=[227651], band 150000..320000 (scale 1)
- PASS `q01 topn=default` rows 4/4 0.72s
- PASS `q02 topn=default` rows 100/100 0.37s
- PASS `q03 topn=default` rows 10/10 0.90s
- PASS `q04 topn=default` rows 5/5 0.55s
- PASS `q05 topn=default` rows 5/5 0.88s
- PASS `q06 topn=default` rows 1/1 0.29s
- PASS `q07 topn=default` rows 4/4 0.74s
- PASS `q08 topn=default` rows 2/2 1.09s
- PASS `q09 topn=default` rows 175/175 1.02s
- PASS `q10 topn=default` rows 20/20 0.94s
- PASS `q11 topn=default` rows 1048/1048 0.21s
- PASS `q12 topn=default` rows 2/2 0.56s
- PASS `q13 topn=default` rows 42/42 0.43s
- PASS `q14 topn=default` rows 1/1 0.32s
- PASS `q15 topn=default` rows 1/1 0.40s
- PASS `q16 topn=default` rows 18314/18314 1.32s
- PASS `q17 topn=default` rows 1/1 0.31s
- PASS `q18 topn=default` rows 57/57 0.84s
- PASS `q19 topn=default` rows 1/1 0.57s
- PASS `q20 topn=default` rows 186/186 0.52s
- PASS `q21 topn=default` rows 100/100 1.21s
- PASS `q22 topn=default` rows 7/7 0.14s
- PASS `q01 topn=0` rows 4/4 0.70s
- PASS `q02 topn=0` rows 100/100 0.15s
- PASS `q03 topn=0` rows 10/10 0.74s
- PASS `q04 topn=0` rows 5/5 0.47s
- PASS `q05 topn=0` rows 5/5 0.85s
- PASS `q06 topn=0` rows 1/1 0.27s
- PASS `q07 topn=0` rows 4/4 0.68s
- PASS `q08 topn=0` rows 2/2 1.10s
- PASS `q09 topn=0` rows 175/175 0.99s
- PASS `q10 topn=0` rows 20/20 0.78s
- PASS `q11 topn=0` rows 1048/1048 0.16s
- PASS `q12 topn=0` rows 2/2 0.45s
- PASS `q13 topn=0` rows 42/42 0.42s
- PASS `q14 topn=0` rows 1/1 0.32s
- PASS `q15 topn=0` rows 1/1 0.36s
- PASS `q16 topn=0` rows 18314/18314 0.64s
- PASS `q17 topn=0` rows 1/1 0.34s
- PASS `q18 topn=0` rows 57/57 0.85s
- PASS `q19 topn=0` rows 1/1 0.46s
- PASS `q20 topn=0` rows 186/186 0.46s
- PASS `q21 topn=0` rows 100/100 1.08s
- PASS `q22 topn=0` rows 7/7 0.14s
- note: q05 scans: tpch.region=5, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.lineitem=6001215, tpch.orders=227651
- note: q05 plan outline: PLAN FRAGMENT 0 / 28:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 28 / 25:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 25 / 22:HASH JOIN / |----21:EXCHANGE / 17:HASH JOIN / |----16:EXCHANGE / 13:HASH JOIN / |----12:EXCHANGE / 9:HASH JOIN / |----8:EXCHANGE / 6:EXCHANGE / PLAN FRAGMENT 3 / EXCHANGE ID: 21 / TABLE: tpch.region / PLAN FRAGMENT 4 / EXCHANGE ID: 16 / TABLE: tpch.nation / PLAN FRAGMENT 5 / EXCHANGE ID: 12 / TABLE: tpch.supplier / PLAN FRAGMENT 6 / EXCHANGE ID: 08 / TABLE: tpch.customer / PLAN FRAGMENT 7 / EXCHANGE ID: 06 / 4:HASH JOIN / |----3:EXCHANGE / TABLE: tpch.lineitem / PLAN FRAGMENT 8 / EXCHANGE ID: 03 / TABLE: tpch.orders
- note: q08 scans: tpch.lineitem=6001215, tpch.region=5, tpch.nation=25, tpch.nation=25, tpch.supplier=10000, tpch.customer=150000, tpch.part=200000, tpch.orders=455301
- note: q08 plan outline: PLAN FRAGMENT 0 / 36:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 36 / 32:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 32 / 29:HASH JOIN / |----28:EXCHANGE / 24:HASH JOIN / |----23:EXCHANGE / 20:HASH JOIN / |----19:EXCHANGE / 16:HASH JOIN / |----15:EXCHANGE / 12:HASH JOIN / |----11:EXCHANGE / 8:HASH JOIN / |----7:EXCHANGE / 3:HASH JOIN / |----2:EXCHANGE / TABLE: tpch.lineitem / PLAN FRAGMENT 3 / EXCHANGE ID: 28 / TABLE: tpch.region / PLAN FRAGMENT 4 / EXCHANGE ID: 23 / TABLE: tpch.nation / PLAN FRAGMENT 5 / EXCHANGE ID: 19 / TABLE: tpch.nation / PLAN FRAGMENT 6 / EXCHANGE ID: 15 / TABLE: tpch.supplier / PLAN FRAGMENT 7 / EXCHANGE ID: 11 / TABLE: tpch.customer / PLAN FRAGMENT 8 / EXCHANGE ID: 07 / TABLE: tpch.part / PLAN FRAGMENT 9 / EXCHANGE ID: 02 / TABLE: tpch.orders
- note: q09 scans: tpch.nation=25, tpch.supplier=10000, tpch.part=50000, tpch.partsupp=800000, tpch.orders=1500000, tpch.lineitem=6001215
- note: q09 plan outline: PLAN FRAGMENT 0 / 28:MERGING-EXCHANGE / PLAN FRAGMENT 1 / EXCHANGE ID: 28 / 25:EXCHANGE / PLAN FRAGMENT 2 / EXCHANGE ID: 25 / 22:HASH JOIN / |----21:EXCHANGE / 18:HASH JOIN / |----17:EXCHANGE / 14:HASH JOIN / |----13:EXCHANGE / 9:HASH JOIN / |----8:EXCHANGE / 6:EXCHANGE / PLAN FRAGMENT 3 / EXCHANGE ID: 21 / TABLE: tpch.nation / PLAN FRAGMENT 4 / EXCHANGE ID: 17 / TABLE: tpch.supplier / PLAN FRAGMENT 5 / EXCHANGE ID: 13 / TABLE: tpch.part / PLAN FRAGMENT 6 / EXCHANGE ID: 08 / TABLE: tpch.partsupp / PLAN FRAGMENT 7 / EXCHANGE ID: 06 / 4:HASH JOIN / |----3:EXCHANGE / 1:EXCHANGE / PLAN FRAGMENT 8 / EXCHANGE ID: 03 / TABLE: tpch.orders / PLAN FRAGMENT 9 / EXCHANGE ID: 01 / TABLE: tpch.lineitem
- note: timings flight (s): q01/default=0.72, q02/default=0.37, q03/default=0.90, q04/default=0.55, q05/default=0.88, q06/default=0.29, q07/default=0.74, q08/default=1.09, q09/default=1.02, q10/default=0.94, q11/default=0.21, q12/default=0.56, q13/default=0.43, q14/default=0.32, q15/default=0.40, q16/default=1.32, q17/default=0.31, q18/default=0.84, q19/default=0.57, q20/default=0.52, q21/default=1.21, q22/default=0.14, q01/0=0.70, q02/0=0.15, q03/0=0.74, q04/0=0.47, q05/0=0.85, q06/0=0.27, q07/0=0.68, q08/0=1.10, q09/0=0.99, q10/0=0.78, q11/0=0.16, q12/0=0.45, q13/0=0.42, q14/0=0.32, q15/0=0.36, q16/0=0.64, q17/0=0.34, q18/0=0.85, q19/0=0.46, q20/0=0.46, q21/0=1.08, q22/0=0.14

## Check 10: lakeFS: commits between queries

- PASS `lfs.t at the setup commit` got (1, 1), head db171aada8c0
- PASS `a commit with 2 files is seen after the commit` got (7, 28) after 1.1 s, commit a192c6c7634b
- PASS `no query saw half of the commit` seen [(1, 1), (7, 28)]
- PASS `a commit deleting a file is seen` got (6, 27) after 1.1 s, commit aa071715b0ec
- PASS `tpch through lakeFS after the commits` [(6001215,)]
- note: with part-1 staged (uncommitted) a query returns (1, 1) (not visible)

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
