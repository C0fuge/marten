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
