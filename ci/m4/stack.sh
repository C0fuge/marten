#!/usr/bin/env bash
# M4 test stack on one GitHub runner (docs/M4-CI.md §2–3): docker network `m4` with MinIO, our Arrow Flight SQL
# server(s) and StarRocks 4.1.4 (allin1 image overlaid with the FE/BE outputs of the current series).
#
#   ci/m4/stack.sh assets  ASSET_DIR                 download + unpack release m4-assets (needs GH_TOKEN)
#   ci/m4/stack.sh minio   ASSET_DIR                 start MinIO, upload tpch (SF1) + types tables to s3://lake/parquet
#   ci/m4/stack.sh flight  ASSET_DIR NAME [HOSTS]    start a Flight server container NAME (port 32010 in the network)
#   ci/m4/stack.sh starrocks FE_OUT BE_OUT           build the overlay image and start container `sr`
#   ci/m4/stack.sh logs    DIR                       copy all container logs into DIR
#
# MinIO credentials are throwaway values generated per job and kept in $M4_STATE (never in the repo).
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
M4_STATE=${M4_STATE:-$HOME/.m4-state}
SR_HOME=/data/deploy/starrocks
SR_IMAGE=docker.io/starrocks/allin1-ubuntu:4.1.4
JDK_IMAGE=docker.io/library/eclipse-temurin:21-jre
MINIO_IMAGE=docker.io/minio/minio:latest
MC_IMAGE=docker.io/minio/mc:latest

net() { docker network inspect m4 >/dev/null 2>&1 || docker network create m4 >/dev/null; }

case "$1" in
assets)
    A=$2; mkdir -p "$A"
    if [ ! -s "$A/SHA256SUMS" ]; then
        # m4-assets is a draft release: the tag endpoint does not see it, so look it up in the release list.
        rel=$(gh api "repos/$GITHUB_REPOSITORY/releases?per_page=100" --jq '.[] | select(.tag_name=="m4-assets") | .id' | head -1)
        [ -n "$rel" ] || { echo "release m4-assets not found" >&2; exit 1; }
        gh api "repos/$GITHUB_REPOSITORY/releases/$rel/assets?per_page=100" --jq '.[] | "\(.id) \(.name)"' |
        while read -r id name; do
            echo "download $name"
            gh api -H "Accept: application/octet-stream" "repos/$GITHUB_REPOSITORY/releases/assets/$id" > "$A/$name"
        done
    fi
    (cd "$A" && sha256sum -c SHA256SUMS)
    mkdir -p "$A/x"
    [ -d "$A/x/libs" ] || tar -C "$A/x" --zstd -xf "$A/flight-server-libs.tar.zst"
    [ -d "$A/x/sf1" ] || tar -C "$A/x" --zstd -xf "$A/tpch-sf1-parquet.tar.zst"
    cp "$A/arrow-flight-server-1.0.0-int1.jar" "$A/x/server.jar"
    if [ ! -s "$A/x/httpfs.duckdb_extension" ]; then
        curl -sSfL http://extensions.duckdb.org/v1.4.1/linux_amd64/httpfs.duckdb_extension.gz | gunzip > "$A/x/httpfs.duckdb_extension"
    fi
    ls -la "$A/x" "$A/x/sf1/tpch"
    ;;
minio)
    A=$2; net; mkdir -p "$M4_STATE"
    if [ ! -s "$M4_STATE/minio.env" ]; then
        printf 'MINIO_ROOT_USER=m4%s\nMINIO_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 6)" "$(openssl rand -hex 16)" > "$M4_STATE/minio.env"
    fi
    . "$M4_STATE/minio.env"
    docker run -d --name minio --network m4 --env-file "$M4_STATE/minio.env" "$MINIO_IMAGE" server /data >/dev/null
    for i in $(seq 60); do docker exec minio mc ready local >/dev/null 2>&1 && break; sleep 1; done
    docker run --rm --network m4 --env-file "$M4_STATE/minio.env" \
        -v "$A/x/sf1/tpch:/up/tpch:ro" -v "$REPO_ROOT/tests/m4/data/types:/up/types:ro" --entrypoint sh "$MC_IMAGE" -c '
        mc alias set m http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null &&
        mc mb -p m/lake && mc mirror -q /up m/lake/parquet && mc du --depth 2 m/lake/parquet'
    ;;
flight)
    A=$2 NAME=$3 HOSTS=${4:-$3}; net
    . "$M4_STATE/minio.env"
    extra_env=()
    for v in $(compgen -e | grep '^FLIGHT_' || true); do extra_env+=(-e "$v"); done
    [ -n "${FLIGHT_AUTH_PROVIDER:-}${FLIGHT_TLS_CERT:-}" ] || extra_env+=(-e FLIGHT_ALLOW_INSECURE=true)
    docker run -d --name "$NAME" --hostname "$NAME" --network m4 --memory 4g -v "$A/x:/srv:ro" -w /srv \
        -e LANG=C.UTF-8 -e MALLOC_ARENA_MAX=4 \
        -e FLIGHT_S3_ACCESS_KEY="$MINIO_ROOT_USER" -e FLIGHT_S3_SECRET_KEY="$MINIO_ROOT_PASSWORD" "${extra_env[@]}" \
        "$JDK_IMAGE" java --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED \
        --add-opens java.base/java.nio=ALL-UNNAMED -Darrow.enable_unsafe_memory_access=true -DmetricsEnabled=false \
        -DdataDir=s3://lake/parquet -Ds3Endpoint=http://minio:9000 -DduckDbHttpfsExtension=/srv/httpfs.duckdb_extension \
        -DioParallelism=4 -DduckDbMemoryLimit=1GB -DduckDbThreads=2 -DflightBackpressureThresholdBytes=16777216 \
        ${FLIGHT_JAVA_OPTS:-} -Xmx2g -XX:MaxDirectMemorySize=1g \
        -cp "/srv/server.jar:/srv/libs/*" pro.surpin.data.arrowflight.server.HadoopArrowFlightServer \
        --localhost "$NAME" --hosts "$HOSTS" >/dev/null
    for i in $(seq 180); do
        log=$(docker logs "$NAME" 2>&1 || true)
        if grep -q "Server Arrow Flight SQL started" <<<"$log"; then echo "$NAME started after ${i}s"; exit 0; fi
        if grep -qE "Error starting|SIGSEGV" <<<"$log" || [ "$(docker inspect -f '{{.State.Running}}' "$NAME")" != true ]; then
            break
        fi
        sleep 1
    done
    docker logs "$NAME" 2>&1 | tail -80; echo "flight server $NAME did not start" >&2; exit 1
    ;;
starrocks)
    FE_OUT=$2 BE_OUT=$3; net
    B=$(mktemp -d); mkdir -p "$B/fe-jars"
    cp "$FE_OUT"/*.jar "$B/fe-jars/"
    zstd -q -d "$BE_OUT/starrocks_be.zst" -o "$B/starrocks_be" && chmod 755 "$B/starrocks_be"
    cp "$REPO_ROOT/tests/m4/starrocks/fe.conf" "$REPO_ROOT/tests/m4/starrocks/be.conf" "$B/"
    docker pull -q "$SR_IMAGE"
    # The paths of the allin1 image are assumed by docs/INSTALL.md §2a; fail loudly if they moved.
    docker run --rm --entrypoint sh "$SR_IMAGE" -c "ls $SR_HOME/fe/lib/starrocks-fe.jar $SR_HOME/be/lib/starrocks_be $SR_HOME/fe/conf/fe.conf $SR_HOME/be/conf/be.conf"
    cat > "$B/Dockerfile" <<EOF
FROM $SR_IMAGE
COPY fe-jars/ $SR_HOME/fe/lib/
COPY starrocks_be $SR_HOME/be/lib/starrocks_be
COPY fe.conf $SR_HOME/fe/conf/fe.conf
COPY be.conf $SR_HOME/be/conf/be.conf
EOF
    docker build -q -t starrocks-m4 "$B"
    rm -rf "$B"
    docker run -d --name sr --network m4 -p 9030:9030 -p 8030:8030 -p 8040:8040 starrocks-m4 >/dev/null
    docker exec sr $SR_HOME/be/lib/starrocks_be --version || true
    for i in $(seq 120); do
        if python3 - <<'EOF' 2>/dev/null; then echo "StarRocks ready after $((i * 5))s"; exit 0; fi
import pymysql
c = pymysql.connect(host="127.0.0.1", port=9030, user="root", connect_timeout=3)
cur = c.cursor(); cur.execute("SHOW BACKENDS"); cols = [d[0] for d in cur.description]
rows = cur.fetchall(); assert rows and all(r[cols.index("Alive")] == "true" for r in rows)
print(rows[0][cols.index("Version")] if "Version" in cols else rows[0])
EOF
        sleep 5
    done
    docker logs sr 2>&1 | tail -80; echo "StarRocks did not come up" >&2; exit 1
    ;;
logs)
    D=$2; mkdir -p "$D"
    for c in $(docker ps -a --format '{{.Names}}'); do docker logs "$c" > "$D/$c.docker.log" 2>&1 || true; done
    docker cp sr:$SR_HOME/fe/log "$D/fe-log" 2>/dev/null || true
    docker cp sr:$SR_HOME/be/log "$D/be-log" 2>/dev/null || true
    ;;
*) echo "usage: see header" >&2; exit 2 ;;
esac
