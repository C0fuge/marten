#!/usr/bin/env bash
# Regenerate patches/ from branch `flight` of a source tree prepared by prepare-source.sh.
#
#   scripts/export-patches.sh [SRC_DIR]          default SRC_DIR=./src
#
# --zero-commit and --no-signature keep unchanged patches byte-identical across machines, so a push only
# touches the patches that really changed and only the matching CI workflow (fe / be) starts.
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC=${1:-$REPO_ROOT/src}
TAG=${STARROCKS_TAG:-4.1.4}
rm -f "$REPO_ROOT"/patches/*.patch
git -C "$SRC" format-patch --quiet --zero-commit --no-signature --no-numbered "$TAG..flight" -o "$REPO_ROOT/patches"
ls "$REPO_ROOT/patches"
