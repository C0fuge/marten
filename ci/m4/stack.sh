#!/usr/bin/env bash
# M4 test stack on one GitHub runner (docs/M4-CI.md §2–3): docker network `m4` with MinIO, our Arrow Flight SQL
# server(s) and StarRocks 4.1.4 (allin1 image overlaid with the FE/BE outputs of the current series).
#
#   ci/m4/stack.sh assets  ASSET_DIR                 download + unpack release m4-assets (needs GH_TOKEN)
#   ci/m4/stack.sh minio   ASSET_DIR                 start MinIO, upload tpch (SF1) + types tables to s3://lake/parquet
#   ci/m4/stack.sh flight  ASSET_DIR NAME [HOSTS]    start a Flight server container NAME (port 32010 in the network)
#   ci/m4/stack.sh starrocks FE_OUT BE_OUT           build the overlay image and start container `sr`
#   ci/m4/stack.sh wait    NAME                      wait until the Flight server NAME is started (M4_NO_WAIT=1 skips it in `flight`)
#   ci/m4/stack.sh stop|kill NAME...                 remove (stop) or SIGKILL Flight server containers
#   ci/m4/stack.sh certs   DIR HOST                  self-signed EC cert for HOST (DIR/server.crt, PKCS#8 server.key)
#   ci/m4/stack.sh logs    DIR                       copy all container logs into DIR
#
# `flight` passes every FLIGHT_* variable of the environment to the server (open mode when neither
# FLIGHT_AUTH_PROVIDER nor FLIGHT_TLS_CERT is set) and mounts $M4_CERTS at /certs when set. flight1 is also
# reachable as flight1-alias (TLS host name mismatch test).
#
# MinIO credentials are throwaway values generated per job and kept in $M4_STATE (never in the repo).
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
M4_STATE=${M4_STATE:-$HOME/.m4-state}
SR_HOME=/data/deploy/starrocks
SR_IMAGE=docker.io/starrocks/allin1-ubuntu:4.1.4
JDK_IMAGE=docker.io/library/eclipse-temurin:21-jre
# docker.io/minio/minio no longer exists (2026-10-21: "pull access denied"); first image that pulls wins.
# Format: image|args (args empty = the image's own entrypoint/cmd serves /data, as bitnami does).
MINIO_IMAGES=("quay.io/minio/minio:latest|server /data" "docker.io/bitnamilegacy/minio:latest|"
              "cgr.dev/chainguard/minio:latest|server /data")

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
    started=
    for c in "${MINIO_IMAGES[@]}"; do
        img=${c%%|*} margs=${c#*|}
        docker pull -q "$img" >/dev/null 2>&1 || { echo "cannot pull $img"; continue; }
        # shellcheck disable=SC2086
        docker run -d --name minio --network m4 -p 127.0.0.1:9000:9000 --env-file "$M4_STATE/minio.env" "$img" $margs >/dev/null
        for i in $(seq 60); do
            curl -sf http://127.0.0.1:9000/minio/health/ready >/dev/null && { started=$img; break; }
            sleep 1
        done
        [ -n "$started" ] && break
        docker logs minio 2>&1 | tail -20; docker rm -f minio >/dev/null
    done
    [ -n "$started" ] || { echo "no MinIO image worked" >&2; exit 1; }
    echo "MinIO: $started"
    # upload with boto3 (the mc image is gone as well)
    MINIO_ROOT_USER=$MINIO_ROOT_USER MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD python3 - "$A/x/sf1/tpch" "$REPO_ROOT/tests/m4/data/types" <<'PY'
import os, sys, boto3
from botocore.config import Config
# Single PUTs, no multipart: run 39656873818 failed with "ClientDisconnected" on UploadPart against MinIO.
try:
    cfg = Config(s3={"addressing_style": "path"}, request_checksum_calculation="when_required",
                 response_checksum_validation="when_required")
except TypeError:   # older botocore
    cfg = Config(s3={"addressing_style": "path"})
s3 = boto3.client("s3", endpoint_url="http://127.0.0.1:9000", region_name="us-east-1", config=cfg,
                  aws_access_key_id=os.environ["MINIO_ROOT_USER"], aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"])
s3.create_bucket(Bucket="lake")
n = 0
for src in sys.argv[1:]:
    schema = os.path.basename(src.rstrip("/"))
    for root, _, files in os.walk(src):
        for f in files:
            p = os.path.join(root, f)
            with open(p, "rb") as fh:
                s3.put_object(Bucket="lake", Key=f"parquet/{schema}/{os.path.relpath(p, src)}", Body=fh,
                              ContentLength=os.path.getsize(p))
            n += 1
print(f"uploaded {n} files")
for o in s3.list_objects_v2(Bucket="lake", Prefix="parquet/types/")["Contents"]:
    print(o["Key"], o["Size"])
PY
    ;;
flight)
    A=$2 NAME=$3 HOSTS=${4:-$3}; net
    . "$M4_STATE/minio.env"
    extra_env=()
    [ -z "${M4_CERTS:-}" ] || extra_env+=(-v "$M4_CERTS:/certs:ro")
    # flight1 is also published on the runner (ADBC probes in m4.py; /etc/hosts maps flight1 to 127.0.0.1)
    [ "$NAME" != flight1 ] || extra_env+=(--network-alias flight1-alias -p 127.0.0.1:32010:32010)
    # a stopped container of the same name (logs kept for the artifact) must make room
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    for v in $(compgen -e | grep '^FLIGHT_' || true); do extra_env+=(-e "$v"); done
    [ -n "${FLIGHT_AUTH_PROVIDER:-}${FLIGHT_TLS_CERT:-}" ] || extra_env+=(-e FLIGHT_ALLOW_INSECURE=true)
    docker run -d --name "$NAME" --hostname "$NAME" --network m4 --memory 4g -v "$A/x:/srv:ro" -w /tmp \
        -e LANG=C.UTF-8 -e MALLOC_ARENA_MAX=4 \
        -e FLIGHT_S3_ACCESS_KEY="$MINIO_ROOT_USER" -e FLIGHT_S3_SECRET_KEY="$MINIO_ROOT_PASSWORD" "${extra_env[@]}" \
        "$JDK_IMAGE" java --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED \
        --add-opens java.base/java.nio=ALL-UNNAMED -Darrow.enable_unsafe_memory_access=true -DmetricsEnabled=false \
        -DdataDir=s3://lake/parquet -Ds3Endpoint=http://minio:9000 -DduckDbHttpfsExtension=/srv/httpfs.duckdb_extension \
        -DioParallelism=4 -DduckDbMemoryLimit=1GB -DduckDbThreads=2 -DflightBackpressureThresholdBytes=16777216 \
        ${FLIGHT_JAVA_OPTS:-} -Xmx2g -XX:MaxDirectMemorySize=1g \
        -cp "/srv/server.jar:/srv/libs/*" pro.surpin.data.arrowflight.server.HadoopArrowFlightServer \
        --localhost "$NAME" --hosts "$HOSTS" >/dev/null
    [ -z "${M4_NO_WAIT:-}" ] || exit 0
    exec "$0" wait "$NAME"
    ;;
wait)
    NAME=$2
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
stop)
    shift; for n in "$@"; do
        docker logs "$n" >> "$M4_STATE/$n.previous.log" 2>&1 || true
        docker rm -f "$n" >/dev/null 2>&1 || true
    done
    ;;
kill)
    shift; for n in "$@"; do docker kill "$n" >/dev/null; done
    ;;
certs)
    D=$2 H=$3; mkdir -p "$D"
    openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 2 -subj "/CN=$H" \
        -addext "subjectAltName=DNS:$H" -keyout "$D/key.pem" -out "$D/server.crt" 2>/dev/null
    openssl pkcs8 -topk8 -nocrypt -in "$D/key.pem" -out "$D/server.key"
    chmod 644 "$D/server.key" "$D/server.crt"
    ;;
logs)
    D=$2; mkdir -p "$D"
    for c in $(docker ps -a --format '{{.Names}}'); do docker logs "$c" > "$D/$c.docker.log" 2>&1 || true; done
    docker cp sr:$SR_HOME/fe/log "$D/fe-log" 2>/dev/null || true
    docker cp sr:$SR_HOME/be/log "$D/be-log" 2>/dev/null || true
    cp "$M4_STATE"/*.previous.log "$D/" 2>/dev/null || true
    ;;
*) echo "usage: see header" >&2; exit 2 ;;
esac
