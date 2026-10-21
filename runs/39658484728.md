# M4 run 39658484728

2026-10-21 19:11 UTC, series `4.1.4-4a9848e-fl80f999`, checks 1,2,3,4,5

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | FAIL | 13/15 | 2 s |
| 2 | types tables, every column | FAIL | 37/49 | 8 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | FAIL | 19/21 | 10 s |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | FAIL | 32/44 | 35 s |
| 5 | sr-cases on SF1 | FAIL | 22/26 | 6 s |

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
- **FAIL** `DESC flight.types.alltypes` c_ubigint: UBIGINT -> DECIMAL(20,0)
- **FAIL** `DESC flight.types.alltypes_full` c_ubigint: UBIGINT -> DECIMAL(20,0)
- note: DESC flight.types.alltypes: id INT, c_bool BOOLEAN, c_tinyint TINYINT, c_smallint SMALLINT, c_int INT, c_bigint BIGINT, c_utinyint SMALLINT, c_usmallint INT, c_uinteger BIGINT, c_ubigint DECIMAL(20,0), c_hugeint DOUBLE, c_float FLOAT, c_double DOUBLE, c_dec9_2 DECIMAL(9,2), c_dec18_4 DECIMAL(18,4), c_dec38_10 DECIMAL(38,10), c_varchar VARCHAR(1073741824), c_date DATE, c_ts DATETIME, c_ts_ms DATETIME, c_ts_ns DATETIME, c_tstz DATETIME
- note: DESC flight.types.alltypes_full: id INT, c_bool BOOLEAN, c_tinyint TINYINT, c_smallint SMALLINT, c_int INT, c_bigint BIGINT, c_utinyint SMALLINT, c_usmallint INT, c_uinteger BIGINT, c_ubigint DECIMAL(20,0), c_hugeint DOUBLE, c_float FLOAT, c_double DOUBLE, c_dec9_2 DECIMAL(9,2), c_dec18_4 DECIMAL(18,4), c_dec38_10 DECIMAL(38,10), c_varchar VARCHAR(1073741824), c_blob VARBINARY, c_date DATE, c_ts DATETIME, c_ts_ms DATETIME, c_ts_ns DATETIME, c_tstz DATETIME, c_uuid VARCHAR(1073741824), c_list ARRAY<BIGINT>, c_struct struct<`a` int(11), `b` varchar(1073741824)>, c_map MAP<VARCHAR(1073741824),INT>

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
- **FAIL** `types.alltypes.c_ubigint (UBIGINT)` 2244/5000 differ; e.g. id=2: sr='-1' duck='18446744073709551615'; id=3: sr='-9223372036854775808' duck='9223372036854775808'; id=154: sr='-9206744073709551616' duck='9240000000000000000'
- PASS `types.alltypes.c_hugeint (DOUBLE)` 0/5000 differ
- **FAIL** `types.alltypes.c_float (FLOAT)` 1/5000 differ; e.g. id=6: sr='1e-45' duck='1.4013e-45'
- PASS `types.alltypes.c_double (DOUBLE)` 0/5000 differ
- PASS `types.alltypes.c_dec9_2 (DECIMAL(9,2))` 0/5000 differ
- PASS `types.alltypes.c_dec18_4 (DECIMAL(18,4))` 0/5000 differ
- PASS `types.alltypes.c_dec38_10 (DECIMAL(38,10))` 0/5000 differ
- PASS `types.alltypes.c_varchar (VARCHAR)` 0/5000 differ
- PASS `types.alltypes.c_date (DATE)` 0/5000 differ
- **FAIL** `types.alltypes.c_ts (TIMESTAMP)` 1/5000 differ; e.g. id=2: sr='Y222-05-09 N5:25:11.627775' duck='1969-12-31 23:59:59.999999'
- **FAIL** `types.alltypes.c_ts_ms (TIMESTAMP)` 1/5000 differ; e.g. id=2: sr='Y222-05-09 N5:25:11.626776' duck='1969-12-31 23:59:59.999000'
- PASS `types.alltypes.c_ts_ns (TIMESTAMP_NS)` 0/5000 differ
- **FAIL** `types.alltypes.c_tstz (TIMESTAMP WITH TIME ZONE)` 1/5000 differ; e.g. id=3: sr='Y222-05-09 N5:25:11.627775' duck='1969-12-31 23:59:59.999999'
- PASS `types.alltypes_full SELECT * row count` got 5000 expected 5000
- PASS `types.alltypes_full.c_bool (BOOLEAN)` 0/5000 differ
- PASS `types.alltypes_full.c_tinyint (TINYINT)` 0/5000 differ
- PASS `types.alltypes_full.c_smallint (SMALLINT)` 0/5000 differ
- PASS `types.alltypes_full.c_int (INTEGER)` 0/5000 differ
- PASS `types.alltypes_full.c_bigint (BIGINT)` 0/5000 differ
- PASS `types.alltypes_full.c_utinyint (UTINYINT)` 0/5000 differ
- PASS `types.alltypes_full.c_usmallint (USMALLINT)` 0/5000 differ
- PASS `types.alltypes_full.c_uinteger (UINTEGER)` 0/5000 differ
- **FAIL** `types.alltypes_full.c_ubigint (UBIGINT)` 2244/5000 differ; e.g. id=2: sr='-1' duck='18446744073709551615'; id=3: sr='-9223372036854775808' duck='9223372036854775808'; id=154: sr='-9206744073709551616' duck='9240000000000000000'
- PASS `types.alltypes_full.c_hugeint (DOUBLE)` 0/5000 differ
- **FAIL** `types.alltypes_full.c_float (FLOAT)` 1/5000 differ; e.g. id=6: sr='1e-45' duck='1.4013e-45'
- PASS `types.alltypes_full.c_double (DOUBLE)` 0/5000 differ
- PASS `types.alltypes_full.c_dec9_2 (DECIMAL(9,2))` 0/5000 differ
- PASS `types.alltypes_full.c_dec18_4 (DECIMAL(18,4))` 0/5000 differ
- PASS `types.alltypes_full.c_dec38_10 (DECIMAL(38,10))` 0/5000 differ
- PASS `types.alltypes_full.c_varchar (VARCHAR)` 0/5000 differ
- PASS `types.alltypes_full.c_blob (BLOB)` 0/5000 differ
- PASS `types.alltypes_full.c_date (DATE)` 0/5000 differ
- **FAIL** `types.alltypes_full.c_ts (TIMESTAMP)` 1/5000 differ; e.g. id=2: sr='Y222-05-09 N5:25:11.627775' duck='1969-12-31 23:59:59.999999'
- **FAIL** `types.alltypes_full.c_ts_ms (TIMESTAMP)` 1/5000 differ; e.g. id=2: sr='Y222-05-09 N5:25:11.626776' duck='1969-12-31 23:59:59.999000'
- PASS `types.alltypes_full.c_ts_ns (TIMESTAMP_NS)` 0/5000 differ
- **FAIL** `types.alltypes_full.c_tstz (TIMESTAMP WITH TIME ZONE)` 1/5000 differ; e.g. id=3: sr='Y222-05-09 N5:25:11.627775' duck='1969-12-31 23:59:59.999999'
- **FAIL** `types.alltypes_full.c_uuid (UUID)` 4706/5000 differ; e.g. id=1: sr='00000000-0000-0000-0000-000000000000' duck='00000000000000000000000000000000'; id=2: sr='ffffffff-ffff-ffff-ffff-ffffffffffff' duck='ffffffffffffffffffffffffffffffff'; id=3: sr='7fffffff-ffff-ffff-8000-000000000000' duck='7fffffffffffffff8000000000000000'
- PASS `types.alltypes_full.c_list (BIGINT[])` 0/5000 differ
- **FAIL** `types.alltypes_full.c_struct (STRUCT(a INTEGER, b VARCHAR))` 1/5000 differ; e.g. id=2: sr='{"a":-1,"b":"Ж\\"q\'"}' duck='{"a":-1,"b":"\\u0416\\"q\'"}'
- PASS `types.alltypes_full.c_map (MAP(VARCHAR, INTEGER))` 0/5000 differ
- note: types.alltypes: hidden columns ['c_time']
- note: types.alltypes_full: hidden columns ['c_time', 'c_interval']

## Check 3: M4-TESTS §1–2 (EXPLAIN + results)

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (0.55s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.08s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.07s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.25s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (1.15s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.18s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.11s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.18s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.11s)
- **FAIL** `2.3` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(l_quantity) as decimal(38, 2))" not found in FROM clause!')
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", CAST(sum("l_quantity") AS DECIMAL(38,2)) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.39s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.08s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.07s)
- **FAIL** `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_quantity" FROM "tpch"."lineitem" | rows 1 (0.41s) | result differs: sr=[('25.508',)] duck=[('25.5079671',)]
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.37s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.60s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.08s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.20s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.19s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.01s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.02s)

## Check 4: TPC-H SF1 q01–q22, topn default and 0

- **FAIL** `q01 topn=default` rows 4/4 1.47s | only in sr: [('A', 'F', '37734107', '56586554400.73', '53758257134.87', '55909065222.8277', '25.5220058', '38273.1297', '0.0499853', '1478493'), ('N', 'F', '991417', '1487504710.38', '1413082168.0541', '1469649223.1944', '25.5164719', '38284.4678', '0.05009343', '38854')] | only in ref: [('A', 'F', '37734107', '56586554400.73', '53758257134.87', '55909065222.8277', '25.5220059', '38273.1297', '0.0499852958', '1478493'), ('N', 'F', '991417', '1487504710.38', '1413082168.0541', '1469649223.1944', '25.5164719', '38284.4678', '0.0500934267', '38854')]
- PASS `q02 topn=default` rows 100/100 0.80s
- PASS `q03 topn=default` rows 10/10 1.33s
- PASS `q04 topn=default` rows 5/5 0.70s
- PASS `q05 topn=default` rows 5/5 1.63s
- **FAIL** `q06 topn=default` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum((cast(l_extendedprice as decimal(15, 2)) * cast(l_discount as decimal(15, 2)))) as decimal(38, 4))" not found in FROM clause!')
- PASS `q07 topn=default` rows 4/4 1.21s
- PASS `q08 topn=default` rows 2/2 1.92s
- PASS `q09 topn=default` rows 175/175 1.89s
- PASS `q10 topn=default` rows 20/20 1.09s
- PASS `q11 topn=default` rows 1048/1048 0.43s
- PASS `q12 topn=default` rows 2/2 0.59s
- PASS `q13 topn=default` rows 42/42 0.83s
- PASS `q14 topn=default` rows 1/1 0.51s
- **FAIL** `q15 topn=default` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum((cast(l_extendedprice as decimal(15, 2)) * cast((1 - cast(l_discount as decimal(16, 2))) as decimal(16, 2)))) as decimal(38, 4))" not found in FROM clause!')
- PASS `q16 topn=default` rows 18314/18314 0.32s
- PASS `q17 topn=default` rows 1/1 0.83s
- **FAIL** `q18 topn=default` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(l_quantity) as decimal(38, 2))" not found in FROM clause!')
- PASS `q19 topn=default` rows 1/1 0.58s
- **FAIL** `q20 topn=default` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(l_quantity) as decimal(38, 2))" not found in FROM clause!')
- PASS `q21 topn=default` rows 100/100 1.84s
- **FAIL** `q22 topn=default` ERROR ProgrammingError: (1064, "Getting syntax error at line 7, column 26. Detail message: Unexpected input 'FROM', the most similar input is {',', ')'}.")
- **FAIL** `q01 topn=0` rows 4/4 1.47s | only in sr: [('A', 'F', '37734107', '56586554400.73', '53758257134.87', '55909065222.8277', '25.5220058', '38273.1297', '0.0499853', '1478493'), ('N', 'F', '991417', '1487504710.38', '1413082168.0541', '1469649223.1944', '25.5164719', '38284.4678', '0.05009343', '38854')] | only in ref: [('A', 'F', '37734107', '56586554400.73', '53758257134.87', '55909065222.8277', '25.5220059', '38273.1297', '0.0499852958', '1478493'), ('N', 'F', '991417', '1487504710.38', '1413082168.0541', '1469649223.1944', '25.5164719', '38284.4678', '0.0500934267', '38854')]
- PASS `q02 topn=0` rows 100/100 0.42s
- PASS `q03 topn=0` rows 10/10 1.18s
- PASS `q04 topn=0` rows 5/5 0.57s
- PASS `q05 topn=0` rows 5/5 1.19s
- **FAIL** `q06 topn=0` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum((cast(l_extendedprice as decimal(15, 2)) * cast(l_discount as decimal(15, 2)))) as decimal(38, 4))" not found in FROM clause!')
- PASS `q07 topn=0` rows 4/4 1.04s
- PASS `q08 topn=0` rows 2/2 1.19s
- PASS `q09 topn=0` rows 175/175 1.56s
- PASS `q10 topn=0` rows 20/20 0.98s
- PASS `q11 topn=0` rows 1048/1048 0.31s
- PASS `q12 topn=0` rows 2/2 0.60s
- PASS `q13 topn=0` rows 42/42 0.62s
- PASS `q14 topn=0` rows 1/1 0.49s
- **FAIL** `q15 topn=0` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum((cast(l_extendedprice as decimal(15, 2)) * cast((1 - cast(l_discount as decimal(16, 2))) as decimal(16, 2)))) as decimal(38, 4))" not found in FROM clause!')
- PASS `q16 topn=0` rows 18314/18314 0.28s
- PASS `q17 topn=0` rows 1/1 0.64s
- **FAIL** `q18 topn=0` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(l_quantity) as decimal(38, 2))" not found in FROM clause!')
- PASS `q19 topn=0` rows 1/1 0.50s
- **FAIL** `q20 topn=0` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(l_quantity) as decimal(38, 2))" not found in FROM clause!')
- PASS `q21 topn=0` rows 100/100 2.42s
- **FAIL** `q22 topn=0` ERROR ProgrammingError: (1064, "Getting syntax error at line 7, column 26. Detail message: Unexpected input 'FROM', the most similar input is {',', ')'}.")
- note: timings (s): q01/default=1.47, q02/default=0.80, q03/default=1.33, q04/default=0.70, q05/default=1.63, q07/default=1.21, q08/default=1.92, q09/default=1.89, q10/default=1.09, q11/default=0.43, q12/default=0.59, q13/default=0.83, q14/default=0.51, q16/default=0.32, q17/default=0.83, q19/default=0.58, q21/default=1.84, q01/0=1.47, q02/0=0.42, q03/0=1.18, q04/0=0.57, q05/0=1.19, q07/0=1.04, q08/0=1.19, q09/0=1.56, q10/0=0.98, q11/0=0.31, q12/0=0.60, q13/0=0.62, q14/0=0.49, q16/0=0.28, q17/0=0.64, q19/0=0.50, q21/0=2.42

## Check 5: sr-cases on SF1

- PASS `SELECT count(*), sum(l_extendedprice) FROM flight.tpch.lineitem WHERE l_orderkey IN (SELECT o_orderkey FROM flight.tpch.orders WHERE o_orderdate = DATE '1995-03-15')` rows 1
- **FAIL** `SELECT count(*), sum(o_totalprice) FROM tpch.orders WHERE o_orderdate >= DATE '1998-07-01'` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(o_totalprice) as decimal(38, 2))" not found in FROM clause!')
- **FAIL** `SELECT o_orderpriority, count(*), sum(o_totalprice) FROM tpch.orders WHERE o_orderdate >= DATE '1997-01-01' GROUP BY o_orderpriority` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(o_totalprice) as decimal(38, 2))" not found in FROM clause!')
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
- **FAIL** `SELECT o_orderstatus, count(*), sum(o_totalprice), min(o_orderdate), max(o_orderdate) FROM tpch.orders GROUP BY o_orderstatus ORDER BY o_orderstatus` ERROR ProgrammingError: (1064, 'Flight GetFlightInfo failed: INVALID_ARGUMENT: Binder Error: Referenced column "cast(sum(o_totalprice) as decimal(38, 2))" not found in FROM clause!')
- **FAIL** `SELECT l_returnflag, l_linestatus, count(*), sum(l_quantity), sum(l_extendedprice), min(l_shipdate), max(l_shipdate), avg(l_discount) FROM flight.tpch.lineitem GROUP BY l_returnflag, l_linestatus ORDE` rows 4 | sr=[('A', 'F', '1478493', '37734107', '56586554400.73', '1992-01-02', '1995-06-16', '0.05'), ('N', 'F', '38854', '991417', '1487504710.38', '1995-05-19', '1995-06-17', '0.0501'), ('N', 'O', '3004998', '76633518', '114935210409.19', '1995-06-18', '1998-12-01', '0.05')] duck=[('A', 'F', '1478493', '37734107', '56586554400.73', '1992-01-02', '1995-06-16', '0.0499852958'), ('N', 'F', '38854', '991417', '1487504710.38', '1995-05-19', '1995-06-17', '0.0500934267'), ('N', 'O', '3004998', '76633518', '114935210409.19', '1995-06-18', '1998-12-01', '0.0500002596')]
- PASS `SELECT o_orderkey, o_totalprice, o_orderdate FROM flight.tpch.orders ORDER BY o_totalprice DESC, o_orderkey LIMIT 5` rows 5
- PASS `SELECT l_orderkey, l_linenumber, l_extendedprice FROM flight.tpch.lineitem ORDER BY l_extendedprice DESC, l_orderkey, l_linenumber LIMIT 5` rows 5
- PASS `SELECT n_name, count(*), sum(o_totalprice) FROM flight.tpch.orders JOIN flight.tpch.customer ON o_custkey = c_custkey JOIN flight.tpch.nation ON c_nationkey = n_nationkey WHERE o_orderdate >= DATE '19` rows 5
- PASS `SELECT count(*), sum(l_extendedprice) FROM flight.tpch.lineitem JOIN flight.tpch.orders ON l_orderkey = o_orderkey WHERE o_orderdate = DATE '1995-03-15'` rows 1

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
