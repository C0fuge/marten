# M4 run 39879641829

2026-10-23 00:51 UTC, series `4.1.4-4a9848e-fld145f6`, server `arrow-flight-server-1.0.0-int6.jar`, store `s3://lake/parquet`, checks 1,3

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 5 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | PASS | 21/21 | 13 s |

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

## Check 3: M4-TESTS §1–2 (EXPLAIN + results)

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (0.64s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.06s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.10s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.13s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (1.37s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.08s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.16s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.20s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.08s)
- PASS `2.3 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.35s)
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.32s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.06s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.04s)
- PASS `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_quantity" FROM "tpch"."lineitem" | rows 1 (0.54s)
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.29s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.57s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.05s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.10s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.09s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.22s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.39s)

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
