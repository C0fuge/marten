#!/usr/bin/env bash
# Print a content hash of everything that determines the FE or BE build output.
#
#   scripts/input-hash.sh SRC_DIR be|fe
#
# Uses git tree ids of the patched source (so it is cheap and independent of file mtimes) plus the
# CI scripts of this repo. Equal hash => identical build inputs => the cached artifact can be reused.
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC=$1
WHAT=$2
case "$WHAT" in
    be) paths=(be gensrc build-support build.sh env.sh); own=(ci/env.sh ci/build-be.sh ci/ccache-g0.sh) ;;
    fe) paths=(fe gensrc build-support build.sh env.sh java-extensions/hadoop-ext java-extensions/pom.xml); own=(ci/env.sh ci/build-fe.sh) ;;
    *) echo "usage: $0 SRC be|fe" >&2; exit 2 ;;
esac
{
    for p in "${paths[@]}"; do
        echo "$p $(git -C "$SRC" rev-parse "HEAD:$p")"
    done
    for f in "${own[@]}"; do
        echo "$f $(sha256sum < "$REPO_ROOT/$f" | cut -c1-64)"
    done
} | sha256sum | cut -c1-16
