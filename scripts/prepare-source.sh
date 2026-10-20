#!/usr/bin/env bash
# Clone StarRocks at tag 4.1.4 (shallow) and apply the patch series in patches/*.patch (sorted by name).
#
#   scripts/prepare-source.sh [SRC_DIR]          default SRC_DIR=./src
#
# Re-running on an existing SRC_DIR resets it to the tag first (local changes in SRC_DIR are discarded).
# After applying, every patch is one commit on branch `flight`, so `git log 4.1.4..flight` lists the series.
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC=${1:-$REPO_ROOT/src}
TAG=${STARROCKS_TAG:-4.1.4}
TAG_COMMIT=${STARROCKS_TAG_COMMIT:-4a9848edf03f5c936dac664b2d52527f48e72eb0}
UPSTREAM=${STARROCKS_UPSTREAM:-https://github.com/StarRocks/starrocks.git}

if [ ! -d "$SRC/.git" ]; then
    git clone --quiet --depth 1 --branch "$TAG" --single-branch "$UPSTREAM" "$SRC"
fi
cd "$SRC"
actual=$(git rev-parse "refs/tags/$TAG^{commit}")
if [ "$actual" != "$TAG_COMMIT" ]; then
    echo "tag $TAG points to $actual, expected $TAG_COMMIT" >&2
    exit 1
fi
git -c advice.detachedHead=false checkout --quiet --force -B flight "$TAG"
git clean -fdq -e /be/build_Release -e /output

shopt -s nullglob
patches=("$REPO_ROOT"/patches/*.patch)
if [ ${#patches[@]} -gt 0 ]; then
    git -c user.name=starrocks-flight -c user.email=starrocks-flight@localhost \
        am --quiet --keep-cr --whitespace=nowarn --committer-date-is-author-date "${patches[@]}"
fi
echo "source: $SRC  tag: $TAG  patches applied: ${#patches[@]}  head: $(git rev-parse --short=12 HEAD)"
