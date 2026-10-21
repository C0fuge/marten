# M4 run 39661743301

2026-10-21 19:35 UTC, series `4.1.4-4a9848e-fla2cd40`, checks 1,2,3,4,5,6,7,8,9

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | FAIL | 13/15 | 2 s |
| 2 | types tables, every column | FAIL | 45/49 | 11 s |
| 3 | M4-TESTS §1–2 (EXPLAIN + results) | PASS | 21/21 | 13 s |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | PASS | 44/44 | 58 s |
| 5 | sr-cases on SF1 | PASS | 26/26 | 9 s |
| 6 | failover (2 servers) | FAIL | 0/1 | 195 s |
| 7 | KILL QUERY during a long scan | PASS | 2/2 | 6 s |
| 8 | token and TLS | PASS | 10/10 | 26 s |
| 9 | memory limit | PASS | 3/3 | 6 s |

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
- PASS `types.alltypes.c_float (FLOAT)` 0/5000 differ
- PASS `types.alltypes.c_double (DOUBLE)` 0/5000 differ
- PASS `types.alltypes.c_dec9_2 (DECIMAL(9,2))` 0/5000 differ
- PASS `types.alltypes.c_dec18_4 (DECIMAL(18,4))` 0/5000 differ
- PASS `types.alltypes.c_dec38_10 (DECIMAL(38,10))` 0/5000 differ
- PASS `types.alltypes.c_varchar (VARCHAR)` 0/5000 differ
- PASS `types.alltypes.c_date (DATE)` 0/5000 differ
- PASS `types.alltypes.c_ts (TIMESTAMP)` 0/5000 differ
- PASS `types.alltypes.c_ts_ms (TIMESTAMP)` 0/5000 differ
- **FAIL** `types.alltypes.c_ts_ns (TIMESTAMP_NS)` 1/5000 differ; e.g. id=2: sr='1969-12-31 23:59:59.999999' duck='1970-01-01 00:00:00'
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
- **FAIL** `types.alltypes_full.c_ubigint (UBIGINT)` 2244/5000 differ; e.g. id=2: sr='-1' duck='18446744073709551615'; id=3: sr='-9223372036854775808' duck='9223372036854775808'; id=154: sr='-9206744073709551616' duck='9240000000000000000'
- PASS `types.alltypes_full.c_hugeint (DOUBLE)` 0/5000 differ
- PASS `types.alltypes_full.c_float (FLOAT)` 0/5000 differ
- PASS `types.alltypes_full.c_double (DOUBLE)` 0/5000 differ
- PASS `types.alltypes_full.c_dec9_2 (DECIMAL(9,2))` 0/5000 differ
- PASS `types.alltypes_full.c_dec18_4 (DECIMAL(18,4))` 0/5000 differ
- PASS `types.alltypes_full.c_dec38_10 (DECIMAL(38,10))` 0/5000 differ
- PASS `types.alltypes_full.c_varchar (VARCHAR)` 0/5000 differ
- PASS `types.alltypes_full.c_blob (BLOB)` 0/5000 differ
- PASS `types.alltypes_full.c_date (DATE)` 0/5000 differ
- PASS `types.alltypes_full.c_ts (TIMESTAMP)` 0/5000 differ
- PASS `types.alltypes_full.c_ts_ms (TIMESTAMP)` 0/5000 differ
- **FAIL** `types.alltypes_full.c_ts_ns (TIMESTAMP_NS)` 1/5000 differ; e.g. id=2: sr='1969-12-31 23:59:59.999999' duck='1970-01-01 00:00:00'
- PASS `types.alltypes_full.c_tstz (TIMESTAMP WITH TIME ZONE)` 0/5000 differ
- PASS `types.alltypes_full.c_uuid (UUID)` 0/5000 differ
- PASS `types.alltypes_full.c_list (BIGINT[])` 0/5000 differ
- PASS `types.alltypes_full.c_struct (STRUCT(a INTEGER, b VARCHAR))` 0/5000 differ
- PASS `types.alltypes_full.c_map (MAP(VARCHAR, INTEGER))` 0/5000 differ
- note: server direct (ADBC): SELECT id, c_ubigint, c_ts, c_uuid FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: decimal128(20, 0); c_ts: timestamp[us]; c_uuid: string; rows [{'id': 2, 'c_ubigint': Decimal('18446744073709551615'), 'c_ts': datetime.datetime(1969, 12, 31, 23, 59, 59, 999999), 'c_uuid': 'ffffffff-ffff-ffff-ffff-ffffffffffff'}, {'id': 3, 'c_ubigint': Decimal('9223372036854775808'), 'c_ts': datetime.datetime(1, 1, 1, 0, 0), 'c_uuid': '7fffffff-ffff-ffff-8000-000000000000'}]
- note: server GetTables schema of types.alltypes_full: id: int32; c_bool: bool; c_tinyint: int8; c_smallint: int16; c_int: int32; c_bigint: int64; c_utinyint: int16; c_usmallint: int32; c_uinteger: int64; c_ubigint: decimal128(20, 0); c_hugeint: double; c_float: float; c_double: double; c_dec9_2: decimal128(9, 2); c_dec18_4: decimal128(18, 4); c_dec38_10: decimal128(38, 10); c_varchar: string; c_blob: binary; c_date: date32[day]; c_time: time64[us]; c_ts: timestamp[us]; c_ts_ms: timestamp[us]; c_ts_ns: timestamp[ns]; c_tstz: timestamp[us, tz=Etc/UTC]; c_uuid: string; c_interval: month_day_nano_interval; c_list: list<l: int64>;   child 0, l: int64; c_struct: struct<a: int32, b: string>;   child 0, a: int32;   child 1, b: string; c_map: map<string, int32>;   child 0, entries: struct<key: string not null, value: int32> not null;       child 0, key: string not null;       child 1, value: int32
- note: types.alltypes: hidden columns ['c_time']
- note: types.alltypes_full: hidden columns ['c_time', 'c_interval']

## Check 3: M4-TESTS §1–2 (EXPLAIN + results)

- PASS `1.1 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" WHERE ("l_shipdate" >= DATE '1998-09-01') AND ("l_returnflag" = 'R') | rows 0 (0.63s)
- PASS `1.2 SELECT * FROM flight.tpch.nation LIMIT 5` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" LIMIT 5 | rows 5 (0.07s)
- PASS `1.3 SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` REMOTE SQL: SELECT "n_nationkey", "n_name", "n_regionkey", "n_comment" FROM "tpch"."nation" WHERE ("n_name" LIKE 'A%') LIMIT 3 | rows 2 (0.13s)
- PASS `1.4 SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` REMOTE SQL: SELECT "c_comment" FROM "tpch"."customer" | rows 1 (0.15s)
- PASS `1.5 SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` REMOTE SQL: SELECT "l_orderkey", "l_quantity", "l_returnflag", "l_shipdate" FROM "tpch"."lineitem" | rows 0 (1.37s)
- PASS `2.1 SELECT count(*) FROM flight.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.15s)
- PASS `2.1 (complete) SELECT count(*) FROM flight_c.tpch.lineitem` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" | rows 1 (0.31s)
- PASS `2.2 SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.17s)
- PASS `2.2 (complete) SELECT count(*) FROM flight_c.tpch.lineitem WHERE l_quantity > 45` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" WHERE ("l_quantity" > 45) | rows 1 (0.16s)
- PASS `2.3 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.80s)
- PASS `2.3 (complete) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_c.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_returnflag", "l_linestatus", sum(CAST("l_quantity" AS DECIMAL(38,2))) AS "__flight_agg_0", min("l_shipdate") AS "__flight_agg_1", max("l_discount") AS "__flight_agg_2", count(*) AS "__flight_agg_3" FROM "tpch"."lineitem" GROUP BY "l_returnflag", "l_linestatus" | rows 4 (0.44s)
- PASS `2.4 SELECT DISTINCT n_regionkey FROM flight.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.08s)
- PASS `2.4 (complete) SELECT DISTINCT n_regionkey FROM flight_c.tpch.nation` REMOTE SQL: SELECT "n_regionkey" FROM "tpch"."nation" GROUP BY "n_regionkey" | rows 5 (0.08s)
- PASS `2.5 SELECT avg(l_quantity) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_quantity" FROM "tpch"."lineitem" | rows 1 (0.49s)
- PASS `2.6 SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` REMOTE SQL: SELECT "l_suppkey" FROM "tpch"."lineitem" | rows 1 (0.40s)
- PASS `2.7 SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` REMOTE SQL: SELECT "o_orderpriority", "o_comment" FROM "tpch"."orders" | rows 0 (0.82s)
- PASS `2.8 SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."nation" WHERE ("n_nationkey" < 0) | rows 1 (0.09s)
- PASS `2.9 SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.26s)
- PASS `2.9 (complete) SELECT l_returnflag, count(*) c FROM flight_c.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` REMOTE SQL: SELECT "l_returnflag", count(*) AS "__flight_agg_0" FROM "tpch"."lineitem" GROUP BY "l_returnflag" | rows 3 (0.21s)
- PASS `2.10 SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.45s)
- PASS `2.11 (flight.pushdown.aggregate=false) SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight_noagg.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` REMOTE SQL: SELECT "l_quantity", "l_discount", "l_returnflag", "l_linestatus", "l_shipdate" FROM "tpch"."lineitem" | rows 4 (1.33s)

## Check 4: TPC-H SF1 q01–q22, topn default and 0

- PASS `q01 topn=default` rows 4/4 2.21s
- PASS `q02 topn=default` rows 100/100 0.91s
- PASS `q03 topn=default` rows 10/10 1.45s
- PASS `q04 topn=default` rows 5/5 0.87s
- PASS `q05 topn=default` rows 5/5 2.08s
- PASS `q06 topn=default` rows 1/1 0.53s
- PASS `q07 topn=default` rows 4/4 1.44s
- PASS `q08 topn=default` rows 2/2 2.17s
- PASS `q09 topn=default` rows 175/175 3.11s
- PASS `q10 topn=default` rows 20/20 1.72s
- PASS `q11 topn=default` rows 1048/1048 0.54s
- PASS `q12 topn=default` rows 2/2 0.77s
- PASS `q13 topn=default` rows 42/42 0.86s
- PASS `q14 topn=default` rows 1/1 0.81s
- PASS `q15 topn=default` rows 1/1 1.14s
- PASS `q16 topn=default` rows 18314/18314 0.58s
- PASS `q17 topn=default` rows 1/1 1.09s
- PASS `q18 topn=default` rows 57/57 1.96s
- PASS `q19 topn=default` rows 1/1 0.73s
- PASS `q20 topn=default` rows 186/186 1.00s
- PASS `q21 topn=default` rows 100/100 2.96s
- PASS `q22 topn=default` rows 7/7 0.72s
- PASS `q01 topn=0` rows 4/4 1.88s
- PASS `q02 topn=0` rows 100/100 0.41s
- PASS `q03 topn=0` rows 10/10 1.35s
- PASS `q04 topn=0` rows 5/5 0.72s
- PASS `q05 topn=0` rows 5/5 3.07s
- PASS `q06 topn=0` rows 1/1 0.43s
- PASS `q07 topn=0` rows 4/4 1.60s
- PASS `q08 topn=0` rows 2/2 1.94s
- PASS `q09 topn=0` rows 175/175 2.37s
- PASS `q10 topn=0` rows 20/20 1.37s
- PASS `q11 topn=0` rows 1048/1048 0.58s
- PASS `q12 topn=0` rows 2/2 1.28s
- PASS `q13 topn=0` rows 42/42 0.79s
- PASS `q14 topn=0` rows 1/1 0.63s
- PASS `q15 topn=0` rows 1/1 1.02s
- PASS `q16 topn=0` rows 18314/18314 0.34s
- PASS `q17 topn=0` rows 1/1 0.96s
- PASS `q18 topn=0` rows 57/57 2.00s
- PASS `q19 topn=0` rows 1/1 0.74s
- PASS `q20 topn=0` rows 186/186 0.85s
- PASS `q21 topn=0` rows 100/100 2.65s
- PASS `q22 topn=0` rows 7/7 0.48s
- note: timings (s): q01/default=2.21, q02/default=0.91, q03/default=1.45, q04/default=0.87, q05/default=2.08, q06/default=0.53, q07/default=1.44, q08/default=2.17, q09/default=3.11, q10/default=1.72, q11/default=0.54, q12/default=0.77, q13/default=0.86, q14/default=0.81, q15/default=1.14, q16/default=0.58, q17/default=1.09, q18/default=1.96, q19/default=0.73, q20/default=1.00, q21/default=2.96, q22/default=0.72, q01/0=1.88, q02/0=0.41, q03/0=1.35, q04/0=0.72, q05/0=3.07, q06/0=0.43, q07/0=1.60, q08/0=1.94, q09/0=2.37, q10/0=1.37, q11/0=0.58, q12/0=1.28, q13/0=0.79, q14/0=0.63, q15/0=1.02, q16/0=0.34, q17/0=0.96, q18/0=2.00, q19/0=0.74, q20/0=0.85, q21/0=2.65, q22/0=0.48

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

- **FAIL** `check aborted` RuntimeError: stack.sh flight /home/runner/m4-assets flight1 flight1,flight2 failed: 7:32:01 PM com.hazelcast.internal.cluster.impl.TcpIpJoiner WARNING: [flight1]:5701 [dev] [5.6.0] Cannot resolve hostname 'flight2'. Please make sure host is valid and reachable. Oct 21, 2026 7:32:01 PM com.hazelcast.internal.cluster.ClusterService INFO: [flight1]:5701 [dev] [5.6.0]   Members {size:1, ver:1} [ 	Member [flight1]:5701 - afd60200-6afa-4758-8058-5609f2e2209f this ]  Oct 21, 2026 7:32:01 PM com.hazelcast.core.LifecycleService INFO: [flight1]:5701 [dev] [5.6.0] [flight1]:5701 is STARTED Oct 21, 2026 7:32:01 PM com.hazelcast.internal.partition.impl.PartitionStateManagerImpl INFO: [flight1]:5701 [dev] [5.6.0] Initializing cluster partition table arrangement... [main] INFO pro.surpin.data.arrowflight.server.HadoopArrowFlightServer - Waiting up to 60s for 2 nodes to connect (hosts: [flight1, flight2]) [main] ERROR pro.surpin.data.arrowflight.server.HadoopArrowFlightServer - Cluster join timeout after 60s: only 1 of 2 nodes connected. Expected hosts: [flight1, flight2]. Exception in thread "main" java.lang.IllegalStateException: Cluster join timeout after 60s: only 1 of 2 nodes connected. Expected hosts: [flight1, flight2]. 	at pro.surpin.data.arrowflight.server.HadoopArrowFlightServer.waitForCluster(HadoopArrowFlightServer.java:305) 	at pro.surpin.data.arrowflight.server.HadoopArrowFlightServer.start(HadoopArrowFlightServer.java:159) 	at pro.surpin.data.arrowflight.server.HadoopArrowFlightServer.main(HadoopArrowFlightServer.java:378) flight server flight1 did not start 

## Check 7: KILL QUERY during a long scan

- PASS `KILL QUERY stops the scan within ~1 s` 0.01s after KILL: OperationalError: (1317, 'killed manually: KILL QUERY 33554442')
- PASS `next query works` [(25,)]
- note: flight1 log lines with 'cancel' after the KILL: 35; [flight-server-default-executor-1] INFO pro.surpin.data.arrowflight.server.adapters.DuckDbAdapter - qid=20ba81ac-2 node=flight1 backpressure=cancelled waited=16.5us / [flight-server-default-executor-1] INFO pro.surpin.data.arrowflight.server.adapters.FlightSqlProducer - qid=20ba81ac-2 node=flight1 thread=flight-server-default-executor-1 execution=failed server=grpc+tcp://flight1:32010 elapsedMs=21

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
- PASS `TLS, trusted CA file` ok [(25,)]
- PASS `TLS, wrong host name fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAVAILABLE: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline$TailContext#0]\nFlightRuntimeException: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline
- PASS `TLS, untrusted certificate fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAVAILABLE: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline$TailContext#0]\nFlightRuntimeException: io exception\nChannel Pipeline: [SslHandler#0, ProtocolNegotiators$ClientTlsHandler#0, WriteBufferingAndExceptionHandler#0, DefaultChannelPipeline
- PASS `TLS, flight.tls.verify=false` ok [(25,)]
- PASS `plain client against the TLS server fails` ProgrammingError: (1064, 'Flight GetDbSchemas failed: UNAVAILABLE: Network closed for unknown reason\nFlightRuntimeException: Network closed for unknown reason')

## Check 9: memory limit

- PASS `big aggregation under query_mem_limit=100MB fails cleanly` 2.5s ProgrammingError: (1064, 'Memory of Query01a15ff6-6351-734a-96e3-c72302e7a089 exceed limit. Pipeline Backend: 127.0.0.1, fragment: 01a15ff6-6351-734a-96e3-c72302e7a08c Used: 105492800, Limit: 104857600. Mem usage has exceed the limit of single query, You can change the limit by set session variable query_mem_limit.: BE:10001')
- PASS `BE alive afterwards` 
- PASS `next query works` [(25,)]

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
