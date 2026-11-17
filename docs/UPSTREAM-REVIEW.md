# Upstream connector changes 10.11–15.11 (review, 2026-11-15)

Maintainer item of 2026-11-16 01:45 MSK (`docs/STATUS.md`, Next steps). Upstream: the public server repository
`VadimSurpin/arrow-flight-server`, branch `feat/starrocks-native-integration` at `28d6ea713b8e` (read only; its
StarRocks fork lives there as `starrocks-fork/flight-connector.patch`, 40 patches on `branch-4.0`). Only ideas are
taken over; no upstream code is copied into this repository (CLAUDE.md).

## What upstream changed and what it means for ours

| Upstream change | Commits | What it does | Ours |
|---|---|---|---|
| Runtime filters on the ticket (server side) | `75f2d0c`, `794ae7c` (2026-10-21), `ea2f83f` | The server reads protobuf field 15 of a DoGet ticket (an `Any`; field unused there) as a little-endian block: `ARF1` = IN-filters (column name + int64 keys), `ARF2` = IN-filters + split-block bloom filters with witness keys. It wraps the endpoint's DuckDB query in `SELECT * FROM (…) WHERE col IN (…)`. Since `ea2f83f` a set > 4096 keys goes in as `BETWEEN min AND max` (DuckDB needed 6–14 s to plan a 204 000-literal IN list). Unknown columns or bad blocks are ignored. | **Taken over on the BE side (series after `fl1eb792`, opt-in)**: patch 0003 sends `ARF1`, see below. Bloom filters (`ARF2`) not taken over: the witness protocol depends on the server reproducing StarRocks' bloom hash; upstream itself found them not selective for its cases (findings 24). |
| Bitset runtime filters sent as IN-filters, flags on by default, final-group aggregate | `0ecca4f` | The fork's BE turns StarRocks `BITSET_FILTER`s (broadcast join over a dense integer key) and broadcast-join IN-sets into IN-filters on the ticket. | Same idea in our 0003 (`_ticket_with_runtime_filters`): join IN-sets (`VectorizedInConstPredicate`, `is_join_runtime_filter`, not NOT IN / null-aware / array form) and bitsets on TINYINT…BIGINT keys. Not sent for scans with a pushed aggregation (the server would filter partial aggregates). Default **off** until a server that reads the block is the m4 default. |
| Flight scans wait 500 ms for runtime filters | `384df38` (benchmark client only) | Sets the session `runtime_filter_scan_wait_time = 500` for Flight runs: the dimension scans' filters reach a fact scan 50–200 ms after it opens; at the default 20 ms the scans start without them (TPC-DS q29 9.7 s → 4.4 s; no loss on 9 other queries). | Per scan, not per session: `flight.runtime_filters.wait_ms` (default 500) raises the scan's wait while filters are sent (`ConnectorScanNode::init`); a longer session value wins. |
| Scan sharing of repeated Flight scans / join branches | `3dc2712`, `59dc4b2`, `0217443`, `6a8da6b`, `c80a87a`, `cfaa929`, `0701b6f`, `fc63272` | Optimizer rule (`enable_scan_sharing`, on in their benchmark client): scalar aggregates over the same table that a query cross joins (scalar subqueries, TPC-DS q09/q28/q88), later also joined aggregate branches, become one aggregate over one scan with `CASE WHEN p_i` per aggregate and the OR of the predicates in the scan. | **Not started.** Targets TPC-DS shapes; TPC-H has none of the cross-joined scalar-aggregate shape (q15's view is joined, not cross joined; q22 has one scalar subquery). Expected TPC-H effect ≈ 0, so it does not pay for a large FE rule in 0004 now; candidate if TPC-DS becomes a target (Open questions). |
| Findings 12–26 | `22874f9` … `46d565e` | q09: S3 read throughput (httpfs connection caching closes the gap, server setting); q88: runtime IN-filter pushdown; q29: bitset filters + wait; parallel footer reads; warm-up of a restarted pod. | Server-side items (httpfs caching, footers) are for the kestrel server, not this repo. The **IN-list planning cliff** also explains our SF1 q16 item (Open questions 2026-11-06: ~30 000 part keys pushed as an IN list by the FE join-key rule cost more than they save) — a tighter key cap (e.g. 4096 like upstream's server) is the obvious fix. |

## Our implementation (patches 0002/0003/0004/0006/0007)

- Catalog properties: `flight.runtime_filters.max_keys` (default 4096 since series `fl234f9b`, 2026-11-17; was 0; 0 = off; max 1 000 000), `flight.runtime_filters.wait_ms`
  (default 500, 0–60 000). The FE passes both as `TFlightScanNode.options` (`runtime_filter_max_keys`,
  `runtime_filter_wait_ms`) only for scans without a pushed aggregation. No thrift change.
- BE: at the first DoGet of a range the data source collects the filters that are ready (at most 16, ≤ max_keys keys
  each, ≤ 2 000 000 in all), names each by the remote output column of its slot (`field_names`), and appends field 15
  to the ticket. The same ticket is reused after a location failover. Profile counters `RuntimeFiltersSent`,
  `RuntimeFilterKeysSent`. The BE still evaluates every filter itself, so a server that ignores the block returns
  more rows but the same answer.
- Tests: be-ut `FlightRuntimeFilterTest.EncodesBlockAndAppendsField15`, `FlightConnectorTest.SendsJoinInFilterWithTicket`
  (the in-process server records the block); FE `FlightPropertiesTest.testRuntimeFilters`,
  `FlightScanPlanTest.testNoRuntimeFilterOptionsByDefault`.

## Measurement plan (TPC-H SF1/SF10, before/after)

Server: kestrel pre-release `server-1.0.0-2c169a53db3b` — **not in the `m4-assets` release yet** (2026-11-15 22:40 UTC;
newest jar there is deafc861cce3, which has no runtime-filter classes). When it is uploaded:

1. Pin it as the m4 server (asset digests, deepscan; check its jar for `RuntimeFilters` / `RuntimeInFilters` — without
   them the ticket block is ignored and the "after" pass measures only the wait).
2. `compare sf=1 paths=ours profiles=default,speed` and `sf=10` twice: catalog default (before) and with
   `flight.runtime_filters.max_keys=4096` (after; compare.py needs a catalog-property input for this).
3. m4 S3 1–9 with the option on (answers must not change).
4. If it helps, make it the default and record the numbers in `docs/CONNECTOR-COMPARE.md`.

## Server `server-1.0.0-d2e27119fda4` (asset check 2026-11-16 05:15 UTC)

The maintainer replaced 2c169a53db3b by d2e27119fda4 (2c169a53db3b + kestrel items 49/50), uploaded to `m4-assets`
05:09–05:12 UTC. Check against deafc861cce3 (the m4 default):

- The four SHA256SUMS lines (jar, flight-plugins, flight-server-libs, flight-auth) verify; every inner SHA256SUMS of the
  three tars verifies; no links, setuid/setgid bits, special files or path escapes. Plugins, runtime libs (DuckDB 1.5.6)
  and LDAP/JWT/ranger jars are **content-identical** to deafc861cce3 (only tar metadata differs).
- Server jar: every third-party entry identical; 49 new, 72 changed, 1 removed entries, all in
  `pro.surpin.data.arrowflight.server` (+ `arrowflight.properties`: allocator cap now 75 % of direct memory, HDFS
  metadata-cache notes). New: `HdfsSaslDataTransfer`, `FileStatsPruner`, `FooterStubCache`, `ParquetFooterReads`,
  `PeerStreamAdmission`, `StopGate`, `IoPool`, `AccessRecheck`, `DescribeKey`, … No credentials or new URLs; the only
  new process start is `klist -s` in `HdfsTicketCache` (Kerberos ticket check).
- **No runtime-filter reader**: no class or string for `RuntimeFilter`/`RuntimeInFilter`, `ARF1`/`ARF2`, bloom
  filters, and the same classes as in deafc861cce3 touch protobuf `Any` tickets. So this build, like deafc861cce3,
  ignores field 15: the `ours_rf` pass measures only the 500 ms runtime-filter wait plus the BE-side filtering that
  StarRocks does anyway, not server-side filtering.

## Server `server-1.0.0-6f0aa5a026fa` (kestrel ITEM 51; asset check 2026-11-16 15:50 UTC)

Uploaded to `m4-assets` 2026-11-16 15:38 UTC (jar, flight-plugins, flight-server-libs, flight-auth, new SHA256SUMS).
Check against d2e27119fda4 (the m4 default):

- The four SHA256SUMS lines verify. Plugins, runtime libs and flight-auth are **content-identical** to d2e27119fda4
  (8 / 125 / 64 files, same SHA-256 per file); no links, setuid/setgid bits, special files or path escapes.
- Server jar: every third-party entry identical; 2 new, 9 changed, 0 removed entries, all in
  `pro.surpin.data.arrowflight.server` (`adapters/FlightSqlProducer`, `services/ExecutionService`,
  `services/ParquetQueryParser` and inner classes; new `services/RuntimeFilters` + `$InFilter`). No new process start,
  socket or URL string in the changed classes.
- **Runtime-filter reader present**: `RuntimeFilters.decode` reads ticket field 15 (`TICKET_FIELD = 15`) as a
  little-endian block: int32 magic `0x41524631` ("ARF1"; `0x41524632` "ARF2" = with bloom filters, which it skips),
  int32 filter count (0..16), per filter int32 name length (1..256) + UTF-8 name, int32 value count, values as int64;
  ≤ 2 000 000 values in total, nothing after the block. That is exactly what our `encode_flight_runtime_filters`
  (patch 0003) writes. Server limits: `MAX_IN_VALUES = 4096` (matches ours_rf's `max_keys=4096`). Log lines:
  `runtimeFilters={} keys={} applied={}`, `runtimeFilters=ignored reason=notPlainScan`, `runtimeFilters=refused`.
- Measurement: `compare sf=10 paths=ours,ours_rf profiles=default` and the reversed order, server
  `arrow-flight-server-1.0.0-6f0aa5a026fa-linux.jar` (results in `docs/CONNECTOR-COMPARE.md` / STATUS Log).
