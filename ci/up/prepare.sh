#!/usr/bin/env bash
# Fetch the upstream sources of the connector comparison at the commits pinned in ci/up/env.sh.
#   ci/up/prepare.sh sr  DIR     VadimSurpin/starrocks @ UP_COMMIT (depth 1)
#   ci/up/prepare.sh afs DIR     VadimSurpin/arrow-flight-server @ AFS_COMMIT (depth 1)
set -euo pipefail
. "$(dirname "$0")/env.sh"
case "$1" in
    sr) url=$UP_REPO c=$UP_COMMIT ;;
    afs) url=$AFS_REPO c=$AFS_COMMIT ;;
    *) echo "usage: $0 sr|afs DIR" >&2; exit 2 ;;
esac
D=$2
if [ ! -d "$D/.git" ]; then git init -q "$D"; git -C "$D" remote add origin "$url"; fi
for i in 1 2 3 4; do git -C "$D" fetch -q --depth 1 origin "$c" && break; sleep $((2 ** i)); done
git -C "$D" -c advice.detachedHead=false checkout -q --force "$c"
git -C "$D" clean -fdq -e /be/build_Release -e /output
echo "$1: $(git -C "$D" log -1 --format='%H %cI %s')"
