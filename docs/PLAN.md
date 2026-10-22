# StarRocks 4.1.4 + native Arrow Flight SQL catalog (variant B): design and build plan

Status: see `docs/STATUS.md` (this file is the design; it was written before the build phase).
Source: tag 4.1.4 (commit 4a9848edf03f, the same build as the bench image `allin1-ubuntu:latest`, which
reports `4.1.4-4a9848e`). Shallow clone of the tag: about 816 MB (`scripts/prepare-source.sh`).
Research notes: `docs/RESEARCH.md`. Current state and next steps: `docs/STATUS.md`.
Paths below are relative to the source root. `FE/` means `fe/fe-core/src/main/java/com/starrocks/`.

The JDBC route (`~/Projects/starrocks-flight-bridge`) stays. This catalog is added beside it.

---

## 1. What StarRocks 4.1.4 already has (research results)

### 1.1 FE connector framework
- **No connector SPI.** `fe/connector/` contains only a README and `fe/fe-spi` contains only auth classes. Every
  connector is compiled into fe-core, so a Flight catalog has to be a patch to fe-core.
- **Registration.**
  - `FE/connector/ConnectorType.java`: one enum entry `X("x", XConnector.class, configClass)` plus an entry in
    `SUPPORT_TYPE_SET`.
  - `FE/sql/analyzer/CatalogAnalyzer.java:72` checks `ConnectorType.isSupport(type)`.
  - `FE/server/CatalogMgr.createCatalog`, then `ConnectorMgr`, then `ConnectorFactory.createRealConnector`, which
    reflects on a `public XConnector(ConnectorContext)` constructor.
  - `LazyConnector` creates the connector on first use and attaches the per-catalog access control
    (native / ranger / allowall).
  - On edit-log replay, unknown types are skipped with only an error log. A catalog created on the patched FE
    therefore does not break an unpatched FE; it is just dropped.
- **Metadata.** `FE/connector/ConnectorMetadata.java` has only default methods. A read-only catalog needs
  `getTableType`, `listDbNames`, `listTableNames`, `getDb`, `getTable`, `tableExists`, `getTableStatistics`,
  `getRemoteFiles(Table, GetRemoteFilesParams)` and `refreshTable`. `GetRemoteFilesParams` carries
  `predicate` (ScalarOperator), `fieldNames` and `limit`, which is exactly what scan planning needs.
- **Models.**
  - JDBC (`FE/connector/jdbc/*`): row-count cache (Caffeine async, never blocks planning), heuristic NDV
    (`connector/statistics/ConnectorNdvEstimator`), decimal mapping through `TypeFactory.createUnifiedDecimalType`
    (DECIMAL32/64/128, 256 up to p=76).
  - Kudu (`KuduMetadata.getRemoteFiles` returns scan tokens, and `KuduScanNode` assigns them round-robin over
    `getAllAvailableBackendOrComputeIds()`, warehouse-aware).
  - ES (`EsScanNode`: its own `TEsScanRange`, `ES_HTTP_SCAN_NODE`, and a dedicated BE connector `es`). **ES and
    Kudu together are the model for variant B.**
- **Secrets** are masked in three separate places, and new keys must be added to all of them:
  - `FE/common/util/PrintableMap.SENSITIVE_KEY` (SHOW CREATE / AST printing);
  - `FE/credential/CredentialUtil.maskCredential` (SHOW CREATE CATALOG);
  - `FE/common/util/SqlCredentialRedactor.CREDENTIAL_KEYS` (audit log of CREATE CATALOG).

  `FE/server/CatalogMgr.java:200,373` logs catalog properties without masking. That is a pre-existing leak and
  we patch it.
- **User identity propagation.** The only precedent is Iceberg REST with `iceberg.catalog.security=JWT`
  (`IcebergRESTCatalog.buildContext`, which forwards `ConnectContext.getAuthToken()`). JDBC and ODPS use fixed
  catalog credentials. JDBC even sends the password in plaintext inside `TJDBCTable` to the BE.
- **Arrow and Flight Java in the FE.**
  - fe-core already depends on arrow-vector, arrow-memory-netty, **flight-core 18.0.0 and flight-sql 18.0.0**,
    with grpc 1.63.0, netty 4.1.136 and protobuf 3.25.5 (`fe/pom.xml:71-79`).
  - The FE runs its own Flight SQL server (`FE/service/arrow/flight/sql/`), so a `FlightSqlClient` needs no new
    dependency.
  - The FE is Java **17**.

### 1.2 FE optimizer → plan (what a new scan type touches)
Here is the full checklist, using JDBC, ODPS and Kudu as references (file:line at tag 4.1.4):
- Operator types: `FE/sql/optimizer/operator/OperatorType.java` (LOGICAL_* around :36-43, PHYSICAL_* around :89-96).
- New classes:
  - `LogicalFlightScanOperator`, which must include a nested `Builder`. `OperatorBuilderFactory` finds it by
    reflection, so a missing Builder only fails at runtime.
  - `PhysicalFlightScanOperator`;
  - `FlightScanImplementationRule`;
  - `RuleType.IMP_FLIGHT_LSCAN_TO_PSCAN`, registered in `RuleSet.java:207-215`.
- `FE/sql/optimizer/transformer/RelationTransformer.java:717-765`: map TableType to the logical scan. Without
  this you get "Not support table type".
- Visitors:
  - `OperatorVisitor.java:191,362`;
  - `OptExpressionVisitor.java:193`;
  - `PlanFragmentBuilder.java` (JDBC :2080, ODPS :1467, Kudu :1516);
  - `StatisticsCalculator.java` (Kudu :791-815; without it the scan has no statistics);
  - `Explain.java:344`, `LogicalPlanPrinter.java:464`, `DebugOperatorTracer.java:212,453`.
- Rules that list scan types:
  - `PruneScanColumnRule.java:43-51`;
  - `PushDownPredicateScanRule.java:44-62` (generic: everything goes into the scan predicate and the BE
    evaluates it);
  - `PushDownPredicateToExternalTableScanRule.java:50-52` (JDBC: only translatable conjuncts, the rest stay in a
    Filter);
  - `MergeLimitDirectRule.java:38-58`;
  - `MultiOpPattern.java:25-40` (`ALL_SCAN_TYPES`).
- Catalog and analyzer:
  - `FE/catalog/Table.java:84` TableType (plus `isSupported()` must return true; it is checked at
    `QueryAnalyzer.java:744`);
  - `FE/sql/analyzer/Authorizer.java:203,209`. **This is required**; otherwise the default branch throws
    AccessDenied.
  - `AstToStringBuilder.java:140,347`, `DesensitizedSQLBuilder.java:122,505`, `StmtExecutor.java:725-755`
    (catalog type for metrics and `TConnectorScanNode.catalog_type`).
  - `ConnectorPartitionTraits.java:75-77`. Only add an entry if MV support is wanted; we do not want it, so FLIGHT
    is also left out of `MaterializedViewAnalyzer.SUPPORTED_TABLE_TYPE`.
- Scheduling:
  - A scan node that is not a "connector scan node" (`ScanNode.isConnectorScanNode()`, :254) goes through
    `NormalBackendSelector`, which honours the `backend_id` we put into each `TScanRangeLocation` (the Kudu
    pattern).
  - If FLIGHT were added to `isConnectorScanNode()`, `HDFSBackendSelector.java:135` would also need a branch,
    because it has `checkState(false)` for unknown nodes. **We do not add it.**
- Runtime filters reach any scan node and are evaluated in the BE on chunks. `canUseRuntimeAdaptiveDop()`
  defaults to false; JDBC, ODPS and Kudu return true.
- **TOP-N bug.** The likely cause of the wrong answers we hit through the JDBC bridge is
  `FE/sql/optimizer/rule/transformation/PushDownTopNToPreAggRule.java`:
  - Its validity check (:129-131) only requires `orderBy ⊆ groupingKeys`, not that the order-by columns determine
    the group.
  - With `GROUP BY a,b ORDER BY a LIMIT n`, each pipeline keeps an arbitrary n of the groups tied on `a`, so the
    global aggregation merges incomplete partial groups.
  - `isSupportedTopN` (:183-209) enables the more aggressive FINAL-TopN path whenever any non-OLAP scan is in the
    subtree, so **a new FLIGHT scan inherits the bug.**
  - It is gated by `cbo_push_down_topn_limit` (and the invisible `topn_push_down_agg_mode = -1`).
  - This analysis has not yet been confirmed by running a query; that is the M4 test.

### 1.3 Thrift (gensrc/thrift)
- `TPlanNodeType` (`PlanNodes.thrift:47-92`) uses implicit values, so a new value is appended:
  `FLIGHT_SCAN_NODE` after `LAKE_CACHE_STATS_SCAN_NODE`.
- `TPlanNode` (:1450): the highest field is 85 (`cache_stats_scan_node`), so **86 is free**.
- `TScanRange` (:488): fields 4, 5, 6, 7, 20 and 30 are used, so **31 is free**.
- `THdfsScanRange`: ids up to 38. `TTableDescriptor` (`Descriptors.thrift:710`): up to 36, so **37 is free**.
- `TTableType` (`Types.thrift:416`): append `FLIGHT_TABLE`.
- Models: `TJDBCScanNode{tuple_id, table_name, columns, filters, limit}` (:683) and `TEsScanRange` (:332).

### 1.4 BE connector framework
- Interfaces in `be/src/connector/connector.h`:
  - `Connector::create_data_source_provider(ConnectorScanNode*, const TPlanNode&)` and `connector_type()`.
    Append `FLIGHT` to the enum.
  - `DataSourceProvider::create_data_source(const TScanRange&)`, `tuple_descriptor()`,
    `insert_local_exchange_operator()`, `accept_empty_scan_ranges()`, `default_data_source_mem_bytes()`.
  - `DataSource::open / get_next(ChunkPtr*) / close`, plus `raw_rows_read`, `num_rows_read`, `num_bytes_read`,
    `cpu_time_spent`, and optionally `estimated_mem_usage`.
  - **The data source evaluates `_conjunct_ctxs` itself** (ES: `ExecNode::eval_conjuncts`). They include the
    runtime IN filters, and `_read_limit` is set by the framework.
- Registry: `be/src/connector/connector.cpp` (`ConnectorManagerInit`, `cm->put(Connector::JDBC, …)`).
- Dispatch:
  - `be/src/exec/exec_node.cpp:515-545` maps `TPlanNodeType` to a connector name through
    `make_connector_scan_node`.
  - `be/src/runtime/descriptors.cpp:745-812` handles `TTableType`; unknown types fall into the `default:` branch.
- Threading:
  - `get_next` and `open` run on the connector-scan IO pool (`connector_scan_executor`, 8 threads per CPU).
    Blocking network reads are normal there; JDBC, ES and HDFS all block.
  - Up to `connector_io_tasks_per_scan_operator` (16) chunk sources run in parallel, which means several
    endpoints are read concurrently on one BE.
  - Returning `Status::TimedOut` from `get_next` yields the task without failing it.
- Memory:
  - Allocations are charged to `query_ctx()->connector_scan_mem_tracker()` through the hooked malloc. Arrow is
    built with `-DARROW_JEMALLOC=OFF`, so Arrow buffers are counted when they are allocated on the IO thread.
  - The scan memory share is `connector_scan_use_query_mem_ratio` (0.3), and the chunk buffer is sized from it.
- **Cancellation is cooperative only.**
  - `ConnectorChunkSource::_read_chunk` checks `state->is_cancelled()` between chunks.
  - `close()` is never called while `get_next()` is blocked in the same source.
  - JDBC cannot interrupt a JNI read either.
  - For Flight, `FlightStreamReader::Cancel()` (gRPC `TryCancel`) can be called from another thread. That is
    what we will use.

### 1.5 Arrow C++ in the BE
- `thirdparty/vars.sh:250`: **Arrow 19.0.1** (the same major version as our server), built static with
  **`-DARROW_FLIGHT=ON -DARROW_FLIGHT_SQL=ON`** (`build-thirdparty.sh:924-925`).
- Other thirdparty versions: gRPC 1.43.0 (`gRPC_SSL_PROVIDER=package`, so TLS is built in), protobuf 3.14.0,
  OpenSSL 1.1.1m.
- `be/CMakeLists.txt:499-503` links `arrow arrow_flight arrow_flight_sql gRPC::grpc++`. **No thirdparty rebuild
  is needed.**
- Existing Flight code in the BE:
  - BE Flight SQL server `be/src/service/service_be/arrow_flight_sql_service.*` (no TLS, port
    `arrow_flight_port`);
  - **Flight client** in `be/src/udf/python/callstub.cpp` (Python UDF over `DoExchange`), including
    `RETURN_IF_ARROW_ERROR`/`to_status` helpers from `be/src/util/arrow/utils.h`.
- **Arrow → Column conversion already exists and is tested.**
  - `be/src/exec/arrow_to_starrocks_converter.{h,cpp}`: `get_arrow_converter(ArrowTypeId, LogicalType,
    nullable, strict)` and `ConvertFuncTree`.
  - The driver functions are public statics of `ParquetScanner` (`be/src/exec/file_scanner/parquet_scanner.h:52-62`):
    `new_column`, `build_dest` and `convert_array_to_column`.
  - The matrix covers BOOL, INT/UINT 8-64, FLOAT/DOUBLE, STRING/LARGE_STRING, BINARY, DATE32/64, TIMESTAMP
    (all units, tz → session tz), DECIMAL128, LIST/MAP/STRUCT (to ARRAY/MAP/STRUCT or JSON), DICTIONARY (decoded)
    and NA.
  - **Not covered:** DECIMAL256, TIME32/64, DURATION, INTERVAL, the *View types (Utf8View…) and UNION.
    Same-width UINT→INT is a memcpy that wraps, so unsigned types must map to a wider StarRocks type.
- Variant A for comparison (ODPS/Paimon/Kudu JNI): Java fills a custom off-heap table, value by value, and the
  call cannot be interrupted. Variant B avoids the JVM entirely.

### 1.6 Upstream `flight-starrocks/` (arrow-flight-server upstream-main dbacd8d), and what is reusable
| Component | As-is? | Use |
|---|---|---|
| `FlightCatalog.java` (GetCatalogs, GetDbSchemas, GetTables, GetExecuteSchema, planScan = execute) | **No.** Package `pro.surpin…`, built for Java 21 (`List.getFirst()`), Arrow 19 API; StarRocks FE is Java 17 / Arrow 18 | Port its logic (`readRows` over every endpoint, the filters) into `FE/connector/flight/FlightSqlMetadataClient`. Apache-2.0, so attribution goes in the header |
| `ScanSql.java` | **No.** ASCII identifiers only, no quoting, no filters | Replaced by `FlightSqlRenderer` (quoted identifiers, filters, limit) |
| `flight_scan_reader.{h,cc}` (Connect(location, bearer), ScanTicket → callback, EndpointLocation) | **No.** Callback (push) model, first location only, no TLS options, no timeouts, no failover, no cancel, `arrow::Status` | Reuse the ideas (EndpointLocation's reuse-connection rule, the DoGet loop) in a pull-based `FlightStreamSource` inside the BE |
| `docs/integrations/starrocks.md` | n/a | Its requirements list (catalog type, scan plan, auth propagation, tests) is covered by this plan |

Lessons from the Trino plugin v10 (`~/Projects/trino-arrow-flight-connector` 6ee7b0e) and the JDBC bridge:
- **Failover:** try the endpoint's locations in order, and move to the next one only if nothing has been delivered
  yet and the error means the server could not be reached (UNAVAILABLE, connection refused, connect timeout,
  unknown host). Server errors are never failed over.
- **Headers:** `x-flight-result-mode: partial` and `x-flight-location-failover: 1`.
- **Timeouts:** connect timeout 5 s, keepalive 10 s.
- **Statistics:** `count(*)`, and optionally min/max, come cheaply from the server's Parquet footers.
- **From the JDBC bridge:**
  - exact decimals (not doubles) in pushed predicates;
  - standard `''` string escapes;
  - dates read as dates;
  - BOOLEAN, TINYINT and FLOAT handled natively;
  - nested types hidden (here they become optional, because the BE converter supports them);
  - `cbo_push_down_topn_limit` (fixed here, see 2.6).

---

## 2. Design (variant B: native C++ scan in the BE/CN)

### 2.1 Catalog properties (`CREATE EXTERNAL CATALOG f PROPERTIES ("type"="flight", …)`)
| Property | Default | Meaning |
|---|---|---|
| `flight.uri` | required | `grpc://host:port` or `grpc+tls://host:port`; a comma-separated list gives FE metadata failover |
| `flight.token` | — | bearer token (**sensitive**) |
| `flight.user` / `flight.password` | — | Basic handshake that returns a bearer token (password **sensitive**) |
| `flight.tls.verify` | true | false sets `disable_server_verification` |
| `flight.tls.ca_file` / `flight.tls.override_hostname` | — | PEM root certs, path read on FE and BE (or inline PEM) |
| `flight.result_mode` | `partial` | header `x-flight-result-mode` |
| `flight.location_failover` | true | header `x-flight-location-failover: 1`, plus BE failover over the endpoint locations |
| `flight.header.<name>` | — | extra call headers |
| `flight.connect_timeout_ms` / `flight.keepalive_ms` / `flight.rpc_timeout_ms` | 5000 / 10000 / 0 | gRPC channel args and per-call deadline (0 = none for streams) |
| `flight.catalog` | — | Flight SQL catalog to expose (default: all; db = `db_schema_name`) |
| `flight.nested_types` | `hide` | `hide` / `native` (ARRAY/MAP/STRUCT) / `json` |
| `flight.converted_types` | `convert` | `convert`: TIME, DURATION, INTERVAL, DECIMAL256, *View columns exposed converted (table below, added 2026-10-22, STATUS P1); `hide`: hidden as before |
| `flight.pushdown.filter` / `.limit` / `.count` | true | per-feature kill switches (also session variables, see 2.6) |
| `flight.metadata_cache_ttl_s` / `flight.stats_cache_ttl_s` | 60 / 600 | table-list and schema cache; row-count and column min/max cache |
| `flight.exchange_buffer_mb` | 16 | memory per driver of the BE local exchange behind a Flight scan (StarRocks default 128 MB per driver; 0 keeps it). A fast endpoint stream otherwise fills dop × 128 MB while the join build sides are not ready (TPC-H q18 SF10 at BE 4G, STATUS A-4; added 2026-10-22) |
| `flight.column_stats` | `true` | per-table `SELECT min(c), max(c), …` (numeric/date columns that are filterable, ≤ 100 per table; answered from Parquet footers by our servers) gives the CBO column min/max and a range NDV; loaded in the background like row counts (added 2026-10-22, STATUS P2) |

### 2.2 FE files (new package `FE/connector/flight/`)
- `FlightConnector implements Connector`:
  - `public FlightConnector(ConnectorContext)`;
  - validates properties (the `OdpsProperties`-style helper `FlightProperties`);
  - owns one `FlightSqlMetadataClient`.
- `FlightSqlMetadataClient`:
  - holds a `RootAllocator` with a limit and one `FlightClient`/`FlightSqlClient` per URI;
  - auth through a bearer `CallOption`, or Basic handshake then bearer;
  - methods: `getDbSchemas`, `getTables(includeSchema=true)` (our server supports include_schema in
    `MetadataService`), with a fallback to `getExecuteSchema("SELECT * FROM t")`;
  - `execute(sql)` returns a `FlightInfo` with the headers from 2.1.
  - Logic ported from the upstream `FlightCatalog`.
- `FlightMetadata implements ConnectorMetadata`:
  - `listDbNames`, `listTableNames`, `getDb`, `getTable` and `tableExists` are served from Caffeine caches
    (same shape as `JDBCMetaCache`);
  - `getTableStatistics` (2.5);
  - `getRemoteFiles(table, params)`: renders the SQL (2.4), calls `execute`, and returns a
    `FlightRemoteFileDesc` (endpoints);
  - `refreshTable` invalidates the caches.
- `FlightTypeMapper` maps Arrow types to StarRocks types:

  | Arrow | StarRocks |
  |---|---|
  | Bool | BOOLEAN |
  | Int8 / 16 / 32 / 64 | TINYINT / SMALLINT / INT / BIGINT |
  | UInt8 / 16 / 32 | SMALLINT / INT / BIGINT |
  | **UInt64** | **LARGEINT** (avoids the same-width memcpy wrap; no DECIMAL(20,0) needed) |
  | Float16 / 32 | FLOAT |
  | Float64 | DOUBLE |
  | Decimal128(p,s) | `createUnifiedDecimalType(p,s)` |
  | Decimal256 | converted: DECIMAL(p,s) if p ≤ 38 (BE narrows to Decimal128), otherwise VARCHAR (plain decimal text) |
  | Utf8 / LargeUtf8 | VARCHAR (default catalog length) |
  | Binary / LargeBinary / FixedSizeBinary | VARBINARY |
  | Date32 / 64 | DATE |
  | Timestamp(unit, no tz) | DATETIME (wall clock preserved, ns truncated to µs) |
  | Timestamp(unit, tz) | DATETIME in the session time zone (the BE converter re-zones it) |
  | Time32/64 | converted: VARCHAR `HH:MM:SS[.f]`, 3/6/9 fraction digits for ms/us/ns |
  | Duration | converted: BIGINT, count in the Arrow unit (column comment names it) |
  | Interval (all units) | converted: VARCHAR ISO-8601, a sign per component (`P1Y2M3DT4H5M6.5S`, `PT-0.5S`, `PT0S`) |
  | Utf8View / BinaryView / ListView / LargeListView | VARCHAR / VARBINARY / ARRAY (BE rewrites to the non-view arrays) |
  | Union / Null / RunEndEncoded / extension | hidden (logged once per table) |

  "Converted" columns exist only at the top level (inside nested types only exact mappings), with
  `flight.converted_types=convert`, and never take part in pushed filters or aggregations (*View columns do).
  | List / Map / Struct | hidden, or ARRAY / MAP / STRUCT / JSON per `flight.nested_types` |
  | Dictionary | its value type |

  Hidden columns are not exposed at all: `DESC` does not show them and `SELECT *` does not request them.
- `FE/catalog/FlightTable extends Table`:
  - `TableType.FLIGHT`, `isSupported()=true`;
  - keeps catalog/db/remote names plus the Arrow field name and type per column;
  - `toThrift` builds `TTableDescriptor(FLIGHT_TABLE)` with `TFlightTable{catalog, schema, table}`.
    **There are no secrets in the descriptor.**
- `FE/planner/FlightScanNode extends ScanNode` (ES/Kudu pattern):
  - `setupScanRangeLocations()` calls `MetadataMgr.getRemoteFiles(…)`. That runs **one GetFlightInfo per scan**
    on the FE, returning N endpoints.
  - It builds one `TScanRangeLocations` per endpoint with `TScanRange.flight_scan_range` and assigns backend ids
    round-robin over `getAllAvailableBackendOrComputeIds()` (warehouse-aware, as Kudu does).
  - `toThrift` produces `FLIGHT_SCAN_NODE` + `TFlightScanNode`.
  - `canUseRuntimeAdaptiveDop()=true`.
  - Explain shows the remote SQL, the endpoint count and the result mode, **never the tokens or tickets**.
  - Not added to `isConnectorScanNode()`, so it uses `NormalBackendSelector`.
- Optimizer plumbing: the checklist in 1.2, with logical and physical operators, the implementation rule, the
  visitors, `PruneScanColumnRule`, `PushDownPredicateScanRule`, `MergeLimitDirectRule`, `MultiOpPattern` and
  `StatisticsCalculator.computeFlightScanNode`.
- Masking:
  - `flight.token`, `flight.password` → `PrintableMap.SENSITIVE_KEY`, `CredentialUtil.maskCredential`,
    `SqlCredentialRedactor.CREDENTIAL_KEYS`;
  - mask the two `CatalogMgr` log lines.
- Not in scope: writes/sinks, MVs over Flight tables, partitions (the table is unpartitioned to StarRocks).

### 2.3 Thrift (one batch, done once)
```thrift
// Types.thrift
enum TTableType { … , FLIGHT_TABLE }
// Descriptors.thrift
struct TFlightTable { 1: optional string catalog_name; 2: optional string schema_name; 3: optional string table_name }
struct TTableDescriptor { … 37: optional TFlightTable flightTable }
// PlanNodes.thrift
enum TPlanNodeType { … , FLIGHT_SCAN_NODE }
struct TFlightCredential { 1: optional string bearer_token; 2: optional string user; 3: optional string password }
struct TFlightScanNode {
  1: optional Types.TTupleId tuple_id
  2: optional list<string> field_names        // Arrow field i -> tuple slot i (positional, name checked)
  3: optional string default_location         // catalog URI, used for "reuse connection" endpoints
  4: optional TFlightCredential credential    // never logged; see 2.7
  5: optional bool tls_verify; 6: optional string tls_root_certs; 7: optional string tls_override_hostname
  8: optional map<string,string> call_headers // x-flight-result-mode, x-flight-location-failover, custom
  9: optional i32 connect_timeout_ms; 10: optional i32 keepalive_ms; 11: optional i64 rpc_timeout_ms
  12: optional string remote_sql             // for profile/explain only
  13: optional bool location_failover
}
struct TFlightScanRange {
  1: optional binary ticket
  2: optional list<string> locations          // primary first, then backups; empty -> default_location
  3: optional i64 estimated_rows; 4: optional i32 endpoint_index
}
struct TScanRange { … 31: optional TFlightScanRange flight_scan_range }
struct TPlanNode { … 86: optional TFlightScanNode flight_scan_node }
```
Every Thrift change regenerates headers that are included almost everywhere (`PlanNodes_types.h`), which makes
the BE rebuild nearly in full. So **all Thrift changes land in one commit at the start of M2**.

### 2.4 Planning and pushdown (FE)
- **SQL rendering** (`FlightSqlRenderer`, DuckDB dialect):
  - Form: `SELECT "c1","c2" FROM "schema"."table" [WHERE …] [LIMIT n]`.
  - Identifiers are double-quoted, with `"` doubled.
  - Strings are `'…'` with `'` doubled; there are no backslash escapes.
  - Exact numeric literals (BigDecimal plain string, never `E0` doubles). Dates are `DATE 'yyyy-mm-dd'` and
    datetimes are `TIMESTAMP '…'`.
- **Projection.** `PruneScanColumnRule` gives the needed columns. With no columns (for example `count(*)` before
  P3), the smallest column is chosen; the rule already does this.
- **Filters.**
  - FLIGHT joins `PushDownPredicateScanRule` (the Kudu/ODPS pattern): every conjunct goes into the scan predicate.
  - `FlightPredicateConverter` renders only the translatable subset into `WHERE`. Translatable means:
    - comparisons, IN, BETWEEN, IS [NOT] NULL, AND/OR/NOT;
    - LIKE with a constant pattern;
    - casts between compatible numeric types;
    - only over columns of exactly mapped types.
  - **All conjuncts are still evaluated in the BE**, unlike JDBC, which drops them. The cost is small, and it
    removes any risk from semantic differences (collation, NaN, time zones).
  - Session variable `flight_filter_pushdown` (default true).
- **LIMIT.** `MergeLimitDirectRule` places the limit in the scan node, and it is rendered as `LIMIT n`. With N
  endpoints each endpoint returns at most n rows; StarRocks still applies the global limit above the exchange,
  and the BE `_read_limit` stops reading early.
- **TOP-N is not pushed into SQL.** StarRocks does not do that for JDBC either, and it would need ORDER BY
  semantics on each endpoint.
- **count(\*) (P3).** New rule `RewriteSimpleAggToFlightScanRule`, modelled on `RewriteSimpleAggToHDFSScanRule`.
  - It matches `count(*)`/`count(const)`/`count(col)` with no GROUP BY over a FLIGHT scan with no limit.
  - It renders `SELECT count(*) AS "___count___" FROM … [WHERE …]` (the WHERE only if every conjunct was
    rendered), and the plan becomes `sum(___count___)` over the scan.
  - The server answers from Parquet footers. Measured with the Trino plugin, that takes milliseconds, compared
    with 12 s for 60M rows through JDBC.
- **More aggregate pushdown later (P4, optional).** GROUP BY with sum/count/min/max, using the same pattern with
  a rewritten "remote aggregate" scan. Effort is large (a new rule plus partial/final aggregation semantics); it
  is a later decision.
- **Endpoints and scan ranges.**
  - Each endpoint becomes one scan range: ticket bytes plus its locations in order.
  - Our failover build lists up to 2 backup locations per partial endpoint.
  - An empty location list, or the reuse-connection URI, means the catalog URI.
  - Assignment is round-robin over alive BEs/CNs.
  - In complete mode there is one endpoint, read by one stream; partial mode is the default.
- **Planning cost.** There is one GetFlightInfo per scan per query, run while `PlanFragmentBuilder` builds the
  plan, so EXPLAIN also triggers it (the same as Kudu tokens).
  - Timeout: `flight.rpc_timeout_ms` for unary calls, 30 s by default.
  - A Flight error becomes a `StarRocksConnectorException` with the server message; the token is never included.

### 2.5 Statistics for the CBO
- Row count comes from an async Caffeine cache (the JDBC pattern), filled with
  `SELECT count(*) FROM t`, which our server answers from footers. The load starts when the table is resolved
  (`getTable`); the first caller of a cold load waits for it at most 250 ms, later callers never wait (M4 fix 2026-10-22; a 1 s wait
  repeated per statistics call broke the 3 s memo budget), otherwise the plan
  uses `Config.default_statistics_output_row_count`; a known value is tagged `TABLE_METADATA`.
  `FlightMetadata.clear()` is a no-op: MetadataMgr calls it at the end of every query (query-level metadata), and
  clearing there emptied the row-count cache before every plan (local final check A-1).
- Per-column NDV uses `ConnectorNdvEstimator` (heuristic, by type). Option for later: `approx_count_distinct`
  or min/max queries for join ordering.
- Without row counts, TPC-H join order is poor. The JDBC catalog has the same limitation, and that is the
  baseline we compare against.

### 2.6 TOP-N fix (separate patch)
- Patch `PushDownTopNToPreAggRule.check()`: require the order-by columns to cover all grouping keys, in addition
  to the existing `orderBy ⊆ groupingKeys`. Otherwise do not apply the rule.
- Add a unit test for `GROUP BY a,b ORDER BY a LIMIT n`.
- Until the M4 test confirms the fix, keep `cbo_push_down_topn_limit = 0` in the bench scripts for both the
  JDBC and Flight catalogs.

### 2.7 BE files (new `be/src/connector/flight/`, registered as connector `"flight"`)
- `flight_connector.{h,cpp}`:
  - `FlightConnector` with `connector_type() FLIGHT` and `create_data_source_provider`;
  - registered in `be/src/connector/connector.cpp`;
  - mapped in `be/src/exec/exec_node.cpp` (`FLIGHT_SCAN_NODE → make_connector_scan_node("flight")`);
  - `FLIGHT_TABLE` added to `be/src/runtime/descriptors.{h,cpp}` (a `FlightTableDescriptor` holding names only).
- `FlightDataSourceProvider`:
  - holds the `TFlightScanNode` and builds the `arrow::flight::FlightClientOptions` once (TLS root certs,
    override hostname, `disable_server_verification`, plus `generic_options` for keepalive and reconnect
    backoff);
  - `insert_local_exchange_operator()=true` (helps complete mode);
  - `accept_empty_scan_ranges()=false`.
- `FlightClientCache` (process-wide): pools `FlightClient`s by (location URI, TLS options) and drops a client
  after an UNAVAILABLE error. This is the equivalent of the plugin's per-location pool.
- `FlightDataSource` (one per scan range, i.e. per endpoint):
  - **`open()`:**
    - Resolve the location list.
    - Build `FlightCallOptions`: headers `authorization: Bearer <token>`, or Basic handshake then bearer, plus
      the call headers.
    - Call `DoGet(ticket)` on the first location.
    - Read the schema and build a positional slot mapping, checking each field name against
      `field_names[i]`.
    - Build one `ConvertFuncTree` plus a cast expression per slot with `ParquetScanner::build_dest/new_column`.
      These are strict (non-strict) like broker load, with an `ArrowConvertContext{state, current_slot}`.
  - **`get_next()`:**
    - Take the next RecordBatch; a large batch is sliced into `chunk_size` pieces.
    - Convert with `ParquetScanner::convert_array_to_column` per column, then run the cast exprs.
    - `ExecNode::eval_conjuncts(_conjunct_ctxs, chunk)`.
    - Respect `_read_limit`, update counters, and return `EndOfFile` at the end.
  - **Failover (matches plugin v10):**
    - While no batch has been returned (`delivered == false`), an error with Flight status `Unavailable`, an
      `IOError` from gRPC UNAVAILABLE / connect failure / DNS failure, or a connect deadline moves the source to
      the next location with the same ticket. Each move is logged as WARN (location, error, next).
    - After the first batch, and for every other status (INVALID_ARGUMENT, INTERNAL, UNAUTHENTICATED…), the
      error is final: no resume and no duplicate rows.
  - **Timeouts:**
    - Connect timeout comes from the gRPC arg `grpc.min_reconnect_backoff_ms` / the initial connect deadline. To
      be validated on 1.43; the fallback is a short unary `DoAction("ping")`/ListActions probe with a 5 s
      deadline before DoGet.
    - Keepalive uses `grpc.keepalive_time_ms=10000` and `grpc.keepalive_timeout_ms=max(20000, keepalive_ms)`
      (was 5000: killed healthy streams on a loaded host, local final check 2026-10-22), only when
      `location_failover` is on, because our server accepts pings every 5 s.
  - **Cancellation:**
    - The source registers its `FlightStreamReader` with a BE-wide `FlightCancelWatcher`, one thread that wakes
      every 200 ms and calls `reader->Cancel()` (gRPC `TryCancel`, thread-safe) for readers whose `RuntimeState`
      is cancelled or whose fragment is finishing (limit reached).
    - `get_next` also checks `state->is_cancelled()` between batches.
    - `close()` cancels and unregisters the reader and releases the client lease.
  - **Memory:**
    - Batches are converted immediately and released, so at most one RecordBatch is held per source.
    - `estimated_mem_usage()` reports the last batch size so the scan arbitrator can size IO tasks.
    - gRPC receive buffers (max message size of 64 MB) are allocated on gRPC threads and **not charged** to the
      query tracker. This is a known gap (risk R5), bounded by the number of concurrent sources × one message.
  - **Profile:** `FlightConnectTime`, `FlightReadTime(*)`, `ConvertTime`, `BatchesRead`, `RowsRead`, `BytesRead`,
    `FailoverCount`, and `Location` as an info string. The token, ticket and headers never appear.
- **Credential handling:**
  - The token is sent FE→BE only in `TFlightScanNode.credential`, inside the plan RPC, which is the same exposure
    as the JDBC password in `TJDBCTable` today.
  - It must never reach a log line. The patch adds no `ThriftDebugString`/`apache::thrift::to_string` of
    TPlanNode/TFlightScanNode on the BE.
  - The `TFlightScanRange` ticket is not a secret on its own, but it is also never logged; only its length is
    logged.
  - Phase 2 option: per-user identity. Forward `ConnectContext.getAuthToken()` (JWT logins, as in Iceberg REST)
    when `flight.auth=jwt_passthrough`, so the Ranger rules on the server apply per user.

### 2.8 Pushdown phases (deliverables)
| Phase | What | Where |
|---|---|---|
| P0 | full scan, projection (column pruning comes free), BE conjuncts | M2 |
| P1 | LIMIT | M3 |
| P2 | filter rendering (whitelist), session switch | M3 |
| P3 | `count(*)` rewrite + row-count statistics | M3 |
| P4 | GROUP BY aggregate pushdown | M3 (decided: in scope) |

---


## 3. Build

Builds run only in GitHub Actions (`.github/workflows/fe.yml`, `be.yml`, `be-part.yml`) in the official image
`docker.io/starrocks/dev-env-ubuntu:4.1.4` (thirdparty prebuilt, incl. Arrow 19.0.1 with Flight + Flight SQL).
BE without debug info via the ccache launcher wrapper `ci/ccache-g0.sh`. See STATUS.md › CI.

## 4. Steps, effort, milestones
Effort is in agent working days. Wall-clock time is dominated by BE builds, so builds are batched.
| M | Content | Effort | Exit criterion |
|---|---|---|---|
| M0 | Build **unmodified** 4.1.4 FE+BE (no `-g`, no java-ext); overlay image; smoke on bench against the official image (same `SELECT` on the JDBC catalog) | 0.5–1 d (+ 3–6 h build) | identical results; disk, RAM and time recorded in STATUS.md |
| M1 | FE: `ConnectorType.FLIGHT`, FlightConnector/Metadata/Client/TypeMapper, FlightTable, masking, Authorizer, caches; FE unit tests for type mapping and masking | 2–3 d | `CREATE CATALOG`, `SHOW DATABASES/TABLES`, `DESC` on the bench types table; SHOW CREATE CATALOG masks the token |
| M2 | Thrift batch; FE optimizer plumbing + FlightScanNode (endpoints become scan ranges); BE flight connector (DoGet, converters, conjuncts, limit, profile, TLS, token, failover, cancel watcher) | 5–7 d | `SELECT *` and projections over every type equal the JDBC bridge / truth data; partial mode spreads N endpoints across IO tasks; KILL QUERY stops a running stream within 1 s |
| M3 | P1 LIMIT, P2 filter renderer, P3 count(*) rule + row-count stats; TOP-N rule fix + unit test | 3–5 d | EXPLAIN shows the remote SQL; `count(*)` on 60M rows takes well under 1 s (JDBC: 12 s); TOP-N repro correct with `cbo_push_down_topn_limit` at its default |
| M4 | Bench: types table, TPC-H SF10 22 queries (checksums against truth and JDBC catalog), timings Flight-native vs JDBC vs Trino plugin; failover (kill a node before and during reads), TLS + token on, wrong token, memory (big scan under a query mem limit) | 2–3 d | 22/22 PASS, 0 WRONG; failover behaves as plugin v10; no token in fe.log/be.INFO/profile |
| M5 | Packaging: `git format-patch` series on tag 4.1.4 (1 thrift, 2 FE connector, 3 FE optimizer/planner, 4 BE connector, 5 TOP-N fix, 6 tests), `build.sh`, Containerfile for the overlay image, README (properties, limits), offline bundle | 1–2 d | the series applies cleanly to a fresh 4.1.4 checkout and rebuilds to the same image |

Total: about **14–21 agent-days**; builds run in GitHub Actions.

## 5. Risks
- **R3, gRPC 1.43 connect timeout.** There may be no clean way to set a connect timeout; the fallback is a probe
  RPC with a deadline. The keepalive arguments must match the server's ping policy, otherwise the server answers
  with GOAWAY "too_many_pings".
- **R4, converter gaps.**
  - Utf8View, Decimal256, TIME and INTERVAL have no BE converter, so those columns are hidden (or need a new
    converter).
  - UINT64→LARGEINT must be verified to be a widening conversion and not a memcpy.
  - The tz-timestamp converter overwrites the Arrow type's time zone in place (a const-cast hack in StarRocks), so
    each batch must not be shared.
- **R5, memory accounting.** gRPC receive buffers are not charged to the query tracker. Bounded by max message
  size × concurrent sources.
- **R6, credentials.** The token travels in the plan RPC (the same exposure as JDBC passwords today). A future
  StarRocks debug log of TPlanNode would leak it. A per-user identity needs JWT logins on StarRocks.
- **R7, planning latency.** GetFlightInfo runs inside planning (and inside EXPLAIN). During server membership
  changes our server can stall planning for up to about 11 s (as measured with fo1).
- **R8, statistics.** Only row counts are real, and NDV is heuristic, so join order on TPC-H may differ from
  Trino's. That is the same as the JDBC catalog; P4 or min/max stats would help.
- **R9, maintenance.** About 35 fe-core files are touched across the optimizer, so moving to 4.1.6 or later means
  rebasing the patch series. A no-SPI design has no way around this. The upstream feature request (StarRocks
  issue 69868, ADBC catalog) could later replace it.
- **R10, the TOP-N fix is a guess until reproduced.** If the cause is elsewhere, the session-variable workaround
  remains.

## 6. Decisions (made by the user, 2026-10-20)
1. StarRocks **4.1.4**, variant **B** (native C++ BE scan). Builds only in GitHub Actions.
2. BE without debug info (`-g0` through the ccache launcher).
3. Auth v1: catalog-level token (or user/password), forwarded to the BE in the plan, as JDBC does.
4. Defaults: result mode `partial`, location failover on.
5. Nested types (ARRAY/MAP/STRUCT) exposed natively; catalog option `flight.nested_types=hide|json` to change.
6. **Full scope:** projection, filters (BE re-check), LIMIT, `count(*)` **and** GROUP BY aggregate pushdown (P4 is in).
7. TOP-N rule fix as a separate patch (confirm the cause by a reproduction first).
8. Deliver as ONE package: patch series on tag 4.1.4 + build artifacts + install guide.
9. M4 (bench tests) runs on the maintainer's local stand, not in the cloud.
