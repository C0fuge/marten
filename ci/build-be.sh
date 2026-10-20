#!/usr/bin/env bash
# BE build, run INSIDE the dev-env container:  /workspace = patched source, /ci = this directory,
# /ccache = persistent ccache directory.
#
# Env: JOBS (parallel jobs), BUDGET_SEC (0 = no limit), STARROCKS_COMMIT_HASH.
# Exit: 0 = starrocks_be built and installed into /workspace/output/be;
#       124 = time budget reached (the build was stopped; everything compiled so far is in ccache);
#       other = build error.
set -uo pipefail
. /ci/env.sh
export STARROCKS_VERSION STARROCKS_COMMIT_HASH=${STARROCKS_COMMIT_HASH:-$STARROCKS_BASE_HASH}
export BUILD_TYPE=Release
export CCACHE=/ci/ccache-g0.sh
export CCACHE_DIR=/ccache
export CCACHE_MAXSIZE=${CCACHE_MAXSIZE:-9G}
export CCACHE_BASEDIR=/workspace
export CCACHE_COMPILERCHECK=content
export CCACHE_SLOPPINESS=pch_defines,include_file_mtime,include_file_ctime,time_macros
# build.sh only honours an explicit CPU feature set by switching features OFF; pin the official defaults.
export USE_AVX2=ON USE_AVX512=OFF USE_SSE4_2=ON USE_BMI_2=ON
JOBS=${JOBS:-$(nproc)}
BUDGET_SEC=${BUDGET_SEC:-0}

cd /workspace
git config --global --add safe.directory /workspace 2>/dev/null || true
ccache --version | head -1
ccache --zero-stats >/dev/null

start=$(date +%s)
if [ "$BUDGET_SEC" -gt 0 ]; then
    echo "BE build with a budget of $((BUDGET_SEC / 60)) min, -j$JOBS"
    timeout --signal=TERM --kill-after=120 "$BUDGET_SEC" ./build.sh --be --without-java-ext -j "$JOBS"
    rc=$?
else
    ./build.sh --be --without-java-ext -j "$JOBS"
    rc=$?
fi
# timeout returns 124 (TERM) or 137 (KILL after --kill-after)
[ $rc -eq 137 ] && rc=124
echo "build.sh exit code $rc after $(( ($(date +%s) - start) / 60 )) min"
ccache --show-stats || true
if [ $rc -eq 0 ]; then
    # Drop cache entries that this (complete) build did not use, so the saved cache stays one build big.
    ccache --evict-older-than "$(( $(date +%s) - start + 600 ))s" || true
    ccache --show-stats | grep -iE 'cache size|files' || true
fi
exit $rc
