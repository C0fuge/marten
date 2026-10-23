# M4 run 39984497103

2026-10-23 16:28 UTC, series `4.1.4-4a9848e-fl4bda75`, server `arrow-flight-server-1.0.0-int7.jar`, store `iceberg: s3://lake/parquet`, checks 1,11

| # | Check | Result | Items | Time |
|---|---|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS | 25/25 | 12 s |
| 11 | Iceberg: REST catalog tables, deletes, rename, appends | PASS | 22/22 | 51 s |

## Check 1: catalog, SHOW, DESC, masking

- PASS `create catalog` 
- PASS `SHOW CREATE CATALOG masks the token` flight CREATE EXTERNAL CATALOG `flight` PROPERTIES ("type"  =  "flight", "flight.token"  =  "******", "flight.uri"  =  "grpc://flight1:32010" )
- PASS `SHOW DATABASES has tpch and types` got ['_iceberg', 'ice', 'information_schema', 'tpch', 'types']
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

## Check 11: Iceberg: REST catalog tables, deletes, rename, appends

- PASS `SHOW DATABASES has tpch and ice` got ['_iceberg', 'ice', 'information_schema', 'tpch', 'types']
- PASS `SHOW TABLES FROM flight.ice` got ['del', 'lineitem', 'orders', 'ren', 't']
- PASS `DESC flight.ice.lineitem = DESC flight.tpch.lineitem` [('l_orderkey', 'BIGINT'), ('l_partkey', 'BIGINT'), ('l_suppkey', 'BIGINT'), ('l_linenumber', 'BIGINT')] vs [('l_orderkey', 'BIGINT'), ('l_partkey', 'BIGINT'), ('l_suppkey', 'BIGINT'), ('l_linenumber', 'BIGINT')]
- PASS `DESC flight.ice.orders = DESC flight.tpch.orders` [('o_orderkey', 'BIGINT'), ('o_custkey', 'BIGINT'), ('o_orderstatus', 'VARCHAR(1073741824)'), ('o_totalprice', 'DECIMAL(15,2)')] vs [('o_orderkey', 'BIGINT'), ('o_custkey', 'BIGINT'), ('o_orderstatus', 'VARCHAR(1073741824)'), ('o_totalprice', 'DECIMAL(15,2)')]
- PASS `flight.ice.lineitem aggregates = parquet` [('6001215', '153078795', '229577310901.2', '1998-12-01', '1500000')] vs [('6001215', '153078795', '229577310901.2', '1998-12-01', '1500000')]
- PASS `flight.ice.orders aggregates = parquet` [('1500000', '226829306447.46', '1992-01-01', '99996')] vs [('1500000', '226829306447.46', '1992-01-01', '99996')]
- PASS `q01 on flight.ice = reference` rows 4/4 2.05s
- PASS `q04 on flight.ice = reference` rows 5/5 0.90s
- PASS `q12 on flight.ice = reference` rows 2/2 0.92s
- PASS `flight.ice.del: position deletes applied` got (900, 450000), deleted ids visible 0
- PASS `flight.ice.ren: column renamed after the first append` got [(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd'), (5, 'e')], filter [(2,)]
- PASS `flight_c.ice.lineitem aggregates = parquet` [('6001215', '153078795', '229577310901.2', '1998-12-01', '1500000')] vs [('6001215', '153078795', '229577310901.2', '1998-12-01', '1500000')]
- PASS `flight_c.ice.orders aggregates = parquet` [('1500000', '226829306447.46', '1992-01-01', '99996')] vs [('1500000', '226829306447.46', '1992-01-01', '99996')]
- PASS `q01 on flight_c.ice = reference` rows 4/4 2.03s
- PASS `q04 on flight_c.ice = reference` rows 5/5 0.96s
- PASS `q12 on flight_c.ice = reference` rows 2/2 0.90s
- PASS `flight_c.ice.del: position deletes applied` got (900, 450000), deleted ids visible 0
- PASS `flight_c.ice.ren: column renamed after the first append` got [(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd'), (5, 'e')], filter [(2,)]
- PASS `ice.t before the append` got (1, 1)
- PASS `an append (one snapshot, 1 file) is seen by later queries` got (3, 6) after 5.3 s, snapshot 6883362861087496536
- PASS `no query saw a state other than before/after` seen [(1, 1), (3, 6)]
- PASS `complete mode sees the append (views refresh every 60 s)` [(3, 6)] after 20.7 s
- note: ice.del snapshot summary: {'spark.app.id': 'local-1792772700903', 'added-position-delete-files': '2', 'added-delete-files': '2', 'added-files-size': '3319', 'added-position-deletes': '100', 'changed-partition-count': '1', 'total-records': '1000', 'total-files-size': '6578', 'total-data-files': '2', 'total-delete-files': '2', 'total-position-deletes': '100', 'total-equality-deletes': '0', 'engine-version': '3.5.6', 'app-id': 'local-1792772700903', 'engine-name': 'spark', 'iceberg-version': 'Apache Iceberg 1.9.2 (commit 071d5606bc6199a0be9b3f274ec7fbf111d88821)', 'operation': 'delete'}
- note: the dataDir listing also shows the warehouse directory as schema _iceberg: tables ['ice']
- note: REMOTE SQL of count(*) on ice.del: SELECT count(*) AS "__flight_agg_0" FROM "ice"."del"

## Log masking

- PASS catalog token in no log (fe.log, be.INFO/WARNING, container logs)
