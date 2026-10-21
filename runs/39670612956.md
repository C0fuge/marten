# M4 run 39670612956

2026-10-21 20:35 UTC, series `4.1.4-4a9848e-fl598360`, checks 1,3,4

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 15/15 | 2 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | PASS | 21/21 | 14 s |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | PASS | 88/88 | 83 s |

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
- note: DESC flight.types.alltypes: id INT, c_bool BOOLEAN, c_tinyint TINYINT, c_smallint SMALLINT, c_int INT, c_bigint BIGINT, c_utinyint SMALLINT, c_usmallint INT, c_uinteger BIGINT, c_ubigint DECIMAL(20,0), c_hugeint DOUBLE, c_float FLOAT, c_double DOUBLE, c_dec9_2 DECIMAL(9,2), c_dec18_4 DECIMAL(18,4), c_dec38_10 DECIMAL(38,10), c_varchar VARCHAR(1073741824), c_date DATE, c_ts DATETIME, c_ts_ms DATETIME, c_ts_ns DATETIME, c_tstz DATETIME
- note: DESC flight.types.alltypes_full: id INT, c_bool BOOLEAN, c_tinyint TINYINT, c_smallint SMALLINT, c_int INT, c_bigint BIGINT, c_utinyint SMALLINT, c_usmallint INT, c_uinteger BIGINT, c_ubigint DECIMAL(20,0), c_hugeint DOUBLE, c_float FLOAT, c_double DOUBLE, c_dec9_2 DECIMAL(9,2), c_dec18_4 DECIMAL(18,4), c_dec38_10 DECIMAL(38,10), c_varchar VARCHAR(1073741824), c_blob VARBINARY, c_date DATE, c_ts DATETIME, c_ts_ms DATETIME, c_ts_ns DATETIME, c_tstz DATETIME, c_uuid VARCHAR(1073741824), c_list ARRAY<BIGINT>, c_struct struct<`a` int(11), `b` varchar(1073741824)>, c_map MAP<VARCHAR(1073741824),INT>

## Check 3: M4-TESTS §1–2 (EXPLAIN + results)

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (1.19s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.14s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.13s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.31s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (1.25s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.16s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.17s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.18s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.18s)
- PASS `2.3 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.48s)
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.40s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.10s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.08s)
- PASS `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_quantity" FROM "tpch"."lineitem" | rows 1 (0.77s)
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.35s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.86s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.08s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.18s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.14s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.17s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (0.96s)

## Check 4: TPC-H SF1 q01–q22, topn default and 0

- PASS `q01 topn=default = flight_c` rows 4/4
- PASS `q01 topn=default` rows 4/4 1.65s
- PASS `q02 topn=default = flight_c` rows 100/100
- PASS `q02 topn=default` rows 100/100 0.62s
- PASS `q03 topn=default = flight_c` rows 10/10
- PASS `q03 topn=default` rows 10/10 1.12s
- PASS `q04 topn=default = flight_c` rows 5/5
- PASS `q04 topn=default` rows 5/5 0.73s
- PASS `q05 topn=default = flight_c` rows 5/5
- PASS `q05 topn=default` rows 5/5 1.33s
- PASS `q06 topn=default = flight_c` rows 1/1
- PASS `q06 topn=default` rows 1/1 0.32s
- PASS `q07 topn=default = flight_c` rows 4/4
- PASS `q07 topn=default` rows 4/4 1.03s
- PASS `q08 topn=default = flight_c` rows 2/2
- PASS `q08 topn=default` rows 2/2 1.62s
- PASS `q09 topn=default = flight_c` rows 175/175
- PASS `q09 topn=default` rows 175/175 2.58s
- PASS `q10 topn=default = flight_c` rows 20/20
- PASS `q10 topn=default` rows 20/20 0.98s
- PASS `q11 topn=default = flight_c` rows 1048/1048
- PASS `q11 topn=default` rows 1048/1048 0.40s
- PASS `q12 topn=default = flight_c` rows 2/2
- PASS `q12 topn=default` rows 2/2 0.61s
- PASS `q13 topn=default = flight_c` rows 42/42
- PASS `q13 topn=default` rows 42/42 0.65s
- PASS `q14 topn=default = flight_c` rows 1/1
- PASS `q14 topn=default` rows 1/1 0.51s
- PASS `q15 topn=default = flight_c` rows 1/1
- PASS `q15 topn=default` rows 1/1 0.66s
- PASS `q16 topn=default = flight_c` rows 18314/18314
- PASS `q16 topn=default` rows 18314/18314 0.32s
- PASS `q17 topn=default = flight_c` rows 1/1
- PASS `q17 topn=default` rows 1/1 0.73s
- PASS `q18 topn=default = flight_c` rows 57/57
- PASS `q18 topn=default` rows 57/57 1.55s
- PASS `q19 topn=default = flight_c` rows 1/1
- PASS `q19 topn=default` rows 1/1 1.07s
- PASS `q20 topn=default = flight_c` rows 186/186
- PASS `q20 topn=default` rows 186/186 0.81s
- PASS `q21 topn=default = flight_c` rows 100/100
- PASS `q21 topn=default` rows 100/100 2.07s
- PASS `q22 topn=default = flight_c` rows 7/7
- PASS `q22 topn=default` rows 7/7 0.39s
- PASS `q01 topn=0 = flight_c` rows 4/4
- PASS `q01 topn=0` rows 4/4 1.45s
- PASS `q02 topn=0 = flight_c` rows 100/100
- PASS `q02 topn=0` rows 100/100 0.30s
- PASS `q03 topn=0 = flight_c` rows 10/10
- PASS `q03 topn=0` rows 10/10 1.04s
- PASS `q04 topn=0 = flight_c` rows 5/5
- PASS `q04 topn=0` rows 5/5 0.62s
- PASS `q05 topn=0 = flight_c` rows 5/5
- PASS `q05 topn=0` rows 5/5 1.45s
- PASS `q06 topn=0 = flight_c` rows 1/1
- PASS `q06 topn=0` rows 1/1 0.37s
- PASS `q07 topn=0 = flight_c` rows 4/4
- PASS `q07 topn=0` rows 4/4 1.09s
- PASS `q08 topn=0 = flight_c` rows 2/2
- PASS `q08 topn=0` rows 2/2 1.47s
- PASS `q09 topn=0 = flight_c` rows 175/175
- PASS `q09 topn=0` rows 175/175 1.93s
- PASS `q10 topn=0 = flight_c` rows 20/20
- PASS `q10 topn=0` rows 20/20 0.93s
- PASS `q11 topn=0 = flight_c` rows 1048/1048
- PASS `q11 topn=0` rows 1048/1048 0.33s
- PASS `q12 topn=0 = flight_c` rows 2/2
- PASS `q12 topn=0` rows 2/2 0.78s
- PASS `q13 topn=0 = flight_c` rows 42/42
- PASS `q13 topn=0` rows 42/42 0.67s
- PASS `q14 topn=0 = flight_c` rows 1/1
- PASS `q14 topn=0` rows 1/1 0.51s
- PASS `q15 topn=0 = flight_c` rows 1/1
- PASS `q15 topn=0` rows 1/1 0.78s
- PASS `q16 topn=0 = flight_c` rows 18314/18314
- PASS `q16 topn=0` rows 18314/18314 0.26s
- PASS `q17 topn=0 = flight_c` rows 1/1
- PASS `q17 topn=0` rows 1/1 1.08s
- PASS `q18 topn=0 = flight_c` rows 57/57
- PASS `q18 topn=0` rows 57/57 1.62s
- PASS `q19 topn=0 = flight_c` rows 1/1
- PASS `q19 topn=0` rows 1/1 0.58s
- PASS `q20 topn=0 = flight_c` rows 186/186
- PASS `q20 topn=0` rows 186/186 0.71s
- PASS `q21 topn=0 = flight_c` rows 100/100
- PASS `q21 topn=0` rows 100/100 2.03s
- PASS `q22 topn=0 = flight_c` rows 7/7
- PASS `q22 topn=0` rows 7/7 0.41s
- note: timings flight (s): q01/default=1.65, q02/default=0.62, q03/default=1.12, q04/default=0.73, q05/default=1.33, q06/default=0.32, q07/default=1.03, q08/default=1.62, q09/default=2.58, q10/default=0.98, q11/default=0.40, q12/default=0.61, q13/default=0.65, q14/default=0.51, q15/default=0.66, q16/default=0.32, q17/default=0.73, q18/default=1.55, q19/default=1.07, q20/default=0.81, q21/default=2.07, q22/default=0.39, q01/0=1.45, q02/0=0.30, q03/0=1.04, q04/0=0.62, q05/0=1.45, q06/0=0.37, q07/0=1.09, q08/0=1.47, q09/0=1.93, q10/0=0.93, q11/0=0.33, q12/0=0.78, q13/0=0.67, q14/0=0.51, q15/0=0.78, q16/0=0.26, q17/0=1.08, q18/0=1.62, q19/0=0.58, q20/0=0.71, q21/0=2.03, q22/0=0.41
- note: timings flight_c (s): q01/default=1.53, q02/default=0.47, q03/default=1.08, q04/default=0.63, q05/default=1.13, q06/default=0.30, q07/default=0.90, q08/default=1.62, q09/default=2.36, q10/default=0.92, q11/default=0.31, q12/default=0.56, q13/default=0.73, q14/default=0.57, q15/default=0.94, q16/default=0.24, q17/default=0.82, q18/default=1.39, q19/default=0.60, q20/default=0.74, q21/default=1.84, q22/default=0.29, q01/0=1.43, q02/0=0.36, q03/0=1.00, q04/0=0.51, q05/0=1.27, q06/0=0.40, q07/0=1.37, q08/0=1.51, q09/0=1.61, q10/0=0.99, q11/0=0.37, q12/0=0.66, q13/0=0.58, q14/0=0.40, q15/0=0.62, q16/0=0.24, q17/0=0.84, q18/0=1.53, q19/0=0.61, q20/0=0.61, q21/0=2.06, q22/0=0.37
- note: total (s): flight 42.2, flight_c 39.3

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
