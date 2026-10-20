# Research notes (StarRocks 4.1.4 source survey, 2026-10-20)

Facts gathered before the build phase. Line numbers refer to tag 4.1.4. Design: PLAN.md. State: STATUS.md.

## Inputs
- Bench image `docker.io/starrocks/allin1-ubuntu:latest` (3.17 GB local): BE `--version` prints
  `4.1.4-4a9848e` = commit of tag 4.1.4 (`4a9848edf03f…`). FE lib has Java arrow 18.0.0
  (arrow-vector, flight-core, flight-sql, arrow-jdbc). starrocks_be in the image: 532 MB (debug stripped).
- Source: `git clone --depth 1 --branch 4.1.4 --single-branch` ,
  **816 MB** total (.git 152 MB, 19 590 files). 
- Upstream `flight-starrocks/` (arrow-flight-server upstream-main dbacd8d): FlightCatalog.java (Flight SQL
  GetCatalogs/GetDbSchemas/GetTables/GetExecuteSchema, planScan = execute → FlightInfo), ScanSql.java
  (SELECT cols FROM schema.table, ASCII identifiers only), C++ FlightScanReader (Connect(location, bearer),
  ScanTicket(ticket, consumer), Scan(query)); no StarRocks glue, no chunk conversion, first location only,
  no failover, no cancellation, no TLS options beyond URI scheme.
- Trino plugin v10 (our Trino Arrow Flight connector, commit 6ee7b0e): failover rule to port =
  try endpoint locations in order; skip to the next only if nothing was delivered yet and the error is
  "unreachable" (UNAVAILABLE, connect refused/timeout, unknown host); server errors are never failed over;
  headers `x-flight-result-mode: partial` + `x-flight-location-failover: 1`; connect timeout 5 s,
  keepalive 10 s. Statistics: `SELECT count(*)` (+ min/max) answered by the server from Parquet footers.


## Build system facts

- Arrow C++ in thirdparty: **19.0.1**, static, `-DARROW_FLIGHT=ON -DARROW_FLIGHT_SQL=ON`
  (thirdparty/build-thirdparty.sh:924-925); grpc 1.43.0, protobuf 3.14.0, OpenSSL 1.1.1m.
  be/CMakeLists.txt:499-501 links `arrow arrow_flight arrow_flight_sql` into starrocks_be.
  → Flight client classes are already in the binary; no thirdparty rebuild needed.
- Dev image: Docker Hub `starrocks/dev-env-ubuntu:4.1.4` (also `4.1-latest`), amd64 digest
  sha256:4a9ccbf65df9…, 10 layers, **2.91 GB compressed** (registry API, not pulled). Layers: base 30 MB,
  apt (maven, jdk17, ccache…) 476 MB, gcc-toolset-14 95 MB, cmake 56 MB, **thirdparty 1.76 GB**,
  /root/.m2 117 B (empty), starlet 490 MB. Env: STARROCKS_THIRDPARTY=/var/local/thirdparty,
  STARROCKS_LINKER=lld, JAVA_HOME=/lib/jvm/java-17-openjdk.
  `starrocks/dev-env-centos7:4.1.4` 2.58 GB compressed (alternative).
- build.sh: Release default; BE flags always contain `-g` + `-gdwarf-4` (CXX_GCC_FLAGS / CXX_FLAGS_RELEASE,
  be/CMakeLists.txt:297,338), debug section compressed (`-gz=zlib`, WITH_COMPRESS ON). Release install
  splits debuginfo (`objcopy --only-keep-debug`). CMAKE_CXX_FLAGS are SET (not appended) → no env knob to
  drop -g; `STARROCKS_CXX_COMMON_FLAGS` is prepended (a `-g0` there is overridden). Workable trick: build.sh
  uses `$CCACHE` as CMAKE_CXX_COMPILER_LAUNCHER → set `CCACHE=/workspace/tools/g0.sh` (`exec "$@" -g0`).
- FE: `mvn package -am -pl plugin/hive-udf,fe-testing,plugin/spark-dpp,fe-server -DskipTests`; dev image
  has no pre-filled ~/.m2 → Maven downloads (build-in-docker mounts $HOME/.m2).
- `--without-java-ext` skips java-extensions (BE JNI readers); we can overlay only starrocks-fe.jar +
  starrocks_be onto the allin1 4.1.4 image, which already has every jar.
- Uncompressed size of dev-env-ubuntu:4.1.4 estimated from each layer's gzip ISIZE trailer (4-byte HTTP
  range reads, nothing pulled): base 0.08 + apt 1.26 + gcc 0.27 + cmake 0.16 + thirdparty 1.22+4.29k
  + starlet 1.41 GB. Thirdparty is ISIZE mod 4 GiB → 5.5 GB (k=1, ratio 3.1) most likely, 9.8 GB if k=2.
  **Image on disk ≈ 8.7 GB (worst 13 GB)**; peak during pull ≈ +2.9 GB of compressed blobs.
- BE sources: 1 387 .cpp/.cc files, 425 k lines in be/src; FE 5 807 .java files.

## Source survey

- FE: no connector SPI (fe/connector = README, fe-spi = auth only) → catalog must live in fe-core.
  Registration = ConnectorType enum + SUPPORT_TYPE_SET; reflection ctor `(ConnectorContext)`.
  Models: Kudu (getRemoteFiles → tokens, KuduScanNode round-robin over getAllAvailableBackendOrComputeIds)
  + ES (own TEsScanRange, ES_HTTP_SCAN_NODE, BE connector "es"). FE already ships flight-core/flight-sql
  18.0.0 (grpc 1.63, netty 4.1.136); FE is Java 17 (upstream FlightCatalog needs Java 21 → port, not as-is).
- Secrets masking in 3 places (PrintableMap.SENSITIVE_KEY, CredentialUtil.maskCredential,
  SqlCredentialRedactor.CREDENTIAL_KEYS); CatalogMgr.java:200,373 logs catalog props unmasked (pre-existing).
- Thrift free ids: TPlanNode 86, TScanRange 31, TTableDescriptor 37; TPlanNodeType/TTableType append.
- BE: connector.h DataSource/Provider; registry connector.cpp; exec_node.cpp:515-545 node→connector;
  descriptors.cpp:745-812 table types. DataSource must eval conjuncts itself (ES does). get_next on the
  connector IO pool (blocking OK), up to 16 IO tasks per scan operator. Cancel is cooperative only →
  FlightStreamReader::Cancel() from a watcher thread.
- BE Arrow→Column: arrow_to_starrocks_converter + ParquetScanner::{build_dest,new_column,convert_array_to_column};
  gaps: Decimal256, TIME, INTERVAL, DURATION, *View, UNION; same-width UINT→INT memcpy wraps.
  Existing FlightClient user: be/src/udf/python/callstub.cpp. gRPC built with OpenSSL → grpc+tls works.
- TOP-N: likely culprit PushDownTopNToPreAggRule.check() (only orderBy ⊆ groupingKeys); external scans get the
  aggressive FINAL path (isExternalScanOperator). Not yet reproduced.

