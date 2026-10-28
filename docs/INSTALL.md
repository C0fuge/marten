# Install

The build replaces only binaries of a stock StarRocks **4.1.4** installation: the FE jars and the BE executable.
Everything else (configuration, metadata, data, the other jars, java-extensions) stays as shipped. FE and BE must
come from the same patch series (they share the thrift definitions); do not mix them with other builds.

## 1. Get the artifacts

From a green CI run (Actions → run → Artifacts), or a GitHub Release:

| Artifact | Content |
|---|---|
| `fe-jars-<hash>` | `starrocks-fe.jar`, `fe-core-4.1.4.jar`, the other `fe-*-4.1.4.jar`, `starrocks-hadoop-ext.jar`, `fe-build-info.txt` |
| `starrocks_be-<hash>` | `starrocks_be.zst` (Release build without debug info), `be-build-info.txt` |

A GitHub Release `<tag>` carries the same files as `starrocks-flight-<tag>-fe-jars.tar` (jars +
`fe-build-info.txt`), `starrocks-flight-<tag>-starrocks_be.zst`, `starrocks-flight-<tag>-patches.tar.gz` (the
series; `0007` is a BE unit test, not needed at runtime), the two build-info files and `SHA256SUMS`
(`sha256sum -c SHA256SUMS`). The release workflow only packs FE and BE built from the identical patch series.

```bash
mkdir fe-jars && tar -xf starrocks-flight-<tag>-fe-jars.tar -C fe-jars
mv starrocks-flight-<tag>-starrocks_be.zst starrocks_be.zst
```

`*-build-info.txt` lists the patches and checksums. Check that both list the same `thrift:` patch.

```bash
unzstd starrocks_be.zst -o starrocks_be && chmod 755 starrocks_be
sha256sum starrocks_be          # compare with be-build-info.txt
```

## 2a. Docker: overlay the official all-in-one image

```dockerfile
FROM starrocks/allin1-ubuntu:4.1.4
# paths of the allin1 image; check with: docker run --rm --entrypoint ls starrocks/allin1-ubuntu:4.1.4 /data/deploy/starrocks
COPY fe-jars/*.jar /data/deploy/starrocks/fe/lib/
COPY starrocks_be  /data/deploy/starrocks/be/lib/starrocks_be
```

```bash
docker build -t starrocks-flight:4.1.4 .
docker run -d --name sr -p 9030:9030 -p 8030:8030 -p 8040:8040 starrocks-flight:4.1.4
```

## 2b. Existing 4.1.4 deployment (tarball or packages)

On every FE (followers and observers), then every BE/CN, one node at a time:

```bash
# FE
$STARROCKS_HOME/fe/bin/stop_fe.sh
cp -a $STARROCKS_HOME/fe/lib $STARROCKS_HOME/fe/lib.orig      # backup
cp fe-jars/*.jar $STARROCKS_HOME/fe/lib/
$STARROCKS_HOME/fe/bin/start_fe.sh --daemon

# BE / CN
$STARROCKS_HOME/be/bin/stop_be.sh                              # stop_cn.sh for CN
cp -a $STARROCKS_HOME/be/lib/starrocks_be $STARROCKS_HOME/be/lib/starrocks_be.orig
cp starrocks_be $STARROCKS_HOME/be/lib/starrocks_be
$STARROCKS_HOME/be/bin/start_be.sh --daemon
```

Rollback: put the `.orig` files back. Before rolling back, drop every `flight` catalog (`DROP CATALOG …`): a stock
FE cannot load catalogs of type `flight` from its metadata.

## 3. Create a catalog

```sql
CREATE EXTERNAL CATALOG flight PROPERTIES (
  "type" = "flight",
  "flight.uri" = "grpc+tls://flight-host:8815",   -- or grpc:// ; several URIs separated by commas
  "flight.token" = "…"                             -- or flight.user / flight.password
);
SHOW DATABASES FROM flight;
SELECT * FROM flight.<schema>.<table> LIMIT 10;
EXPLAIN SELECT count(*) FROM flight.<schema>.<table>;   -- shows the REMOTE SQL sent to the server
```

All catalog properties: `docs/PLAN.md` §2.1. Session switches: `flight_filter_pushdown`, `flight_aggregate_pushdown`
(both default `true`). The token and password are masked in `SHOW CREATE CATALOG`, logs and profiles.

Time travel (tables the server keeps versions of, e.g. Iceberg tables of our server from build 20b887839edf on):
`SELECT … FROM flight.<schema>.<table> FOR VERSION AS OF <snapshot id>` or `… FOR TIMESTAMP AS OF '<datetime>'`
(the datetime is read in the session time zone and sent to the server in UTC); the clause is forwarded after the
table name in the REMOTE SQL. Ranges (`FOR VERSION BETWEEN …`) are refused; a server without time travel answers
with its own error.

Memory: Flight scans are fast, so a join's probe-side rows can arrive long before its build sides are ready. The
local exchange behind each Flight scan is capped at `flight.exchange_buffer_mb` (default 16 MB) per driver instead
of StarRocks' 128 MB. Large joins/aggregations still need memory like on any other catalog: TPC-H SF10 q18 is at the
edge of a BE with `mem_limit = 4G`; give the BE more memory or `SET enable_spill = true` for such queries.

Slow network between BE and Flight servers: `"flight.compression" = "zstd"` (or `"lz4"`; default `none`) asks the
server (build cadd1aca9c23 or later) to compress the scan's result streams (`arrow-compression` call header); the BE
decodes them. It costs CPU on both sides, so turn it on only where the link, not the server, limits scans (M4 check 13
measures both: on a 1 Gbit link with 10 ms delay a wide scan ran ~1.9× faster with `lz4` and ~1.7× with `zstd`, at 48 % /
32 % of the bytes; on a fast local link both were slower than `none`; `lz4` is the cheaper choice, `zstd` saves more bytes). The FE's metadata and statistics calls never ask for it. A server that does not know the header sends
uncompressed streams, which the BE reads as before.
