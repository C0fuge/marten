# M4 run 39663221891

2026-10-21 19:44 UTC, series `4.1.4-4a9848e-fla2cd40`, checks 1,2,6

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 15/15 | 3 s |
| 2 | types tables, every column | FAIL | 47/49 | 12 s |
| 6 | failover (2 servers) | PASS | 4/4 | 69 s |

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
- PASS `types.alltypes_full.c_ts_ns (TIMESTAMP_NS)` 0/5000 differ
- PASS `types.alltypes_full.c_tstz (TIMESTAMP WITH TIME ZONE)` 0/5000 differ
- PASS `types.alltypes_full.c_uuid (UUID)` 0/5000 differ
- PASS `types.alltypes_full.c_list (BIGINT[])` 0/5000 differ
- PASS `types.alltypes_full.c_struct (STRUCT(a INTEGER, b VARCHAR))` 0/5000 differ
- PASS `types.alltypes_full.c_map (MAP(VARCHAR, INTEGER))` 0/5000 differ
- note: server direct (ADBC, headers {}): SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: decimal128(20, 0); rows [{'id': 2, 'c_ubigint': Decimal('18446744073709551615')}, {'id': 3, 'c_ubigint': Decimal('9223372036854775808')}]
- note: server direct (ADBC, headers {'x-flight-result-mode': 'partial'}): SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: uint64; rows [{'id': 2, 'c_ubigint': 18446744073709551615}, {'id': 3, 'c_ubigint': 9223372036854775808}]
- note: server direct (ADBC, headers {'x-flight-result-mode': 'complete'}): SELECT id, c_ubigint FROM types.alltypes_full WHERE id IN (2, 3) ORDER BY id -> schema id: int32; c_ubigint: decimal128(20, 0); rows [{'id': 2, 'c_ubigint': Decimal('18446744073709551615')}, {'id': 3, 'c_ubigint': Decimal('9223372036854775808')}]
- note: StarRocks, result_mode=complete: c_ubigint id 2,3 = [(2, Decimal('18446744073709551615')), (3, Decimal('9223372036854775808'))]
- note: types.alltypes: hidden columns ['c_time']
- note: types.alltypes_full: hidden columns ['c_time', 'c_interval']

## Check 6: failover (2 servers)

- PASS `both servers up: full scan correct` 6.4s got=[('6001215', '153078795', '158997209')] exp=[('6001215', '153078795', '158997209')]
- PASS `flight2 stopped before the query: succeeds via backup locations` 11.7s got=[('6001215', '153078795', '158997209')]
- PASS `flight2 killed during the read: no wrong/duplicate rows` query succeeded in 2.8s got=[('6001215', '153078795', '158997209')] exp=[('6001215', '153078795', '158997209')]
- PASS `BE alive after failover tests` 
- note: plan of the failover scan mentions 'flight' 0x

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
