# M4 run 40312078753

2026-10-26 11:12 UTC, series `4.1.4-4a9848e-fldb9219`, server `arrow-flight-server-1.0.0-57d252b1437f-linux.jar`, store `s3: s3://lake/parquet`, checks 6

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 4 s |
| 6 | failover (2 servers) | PASS | 6/6 | 64 s |

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

## Check 6: failover (2 servers)

- PASS `both servers up: full scan correct` 3.9s got=[('6001215', '153078795', '158997209')] exp=[('6001215', '153078795', '158997209')]
- PASS `both servers up: 3x lineitem read correct` 2.9s got=[('18003645', '459236385', '476991627')]
- PASS `flight2 stopped before the query: succeeds via backup locations` 16.3s got=[('6001215', '153078795', '158997209')]
- PASS `flight2 killed during the read: no wrong/duplicate rows` query succeeded in 2.7s got=[('18003645', '459236385', '476991627')] exp=[('18003645', '459236385', '476991627')]
- PASS `the kill overlapped the read (query ended after it; error or FailoverCount > 0)` ended 1.4s after the kill, success, FailoverCount=3
- PASS `BE alive after failover tests` 
- note: plan of the failover scan mentions 'flight' 0x
- note: query after the stop ran 11:11:55–11:12:11 UTC; fe.log failover lines: 2026-10-26 11:12:05.903Z WARN (starrocks-mysql-nio-pool-1|166) [FlightSqlMetadataClient.withFailover():258] Flight GetFlightInfo failed on grpc://flight1:32010 (UNAVAILABLE), trying next location / 2026-10-26 11:12:10.912Z WARN (starrocks-mysql-nio-pool-1|166) [FlightSqlMetadataClient.withFailover():238] Flight GetFlightInfo: cannot connect to grpc://flight2:32010 (TIMED_OUT), trying next location
- note: during: read time with both servers 2.9s; flight2 killed 1.3s into the query; query ended 1.4s after the kill

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
