#!/usr/bin/env bash
# FE build, run INSIDE the dev-env container:  /workspace = patched source, /ci = this directory,
# /root/.m2 = persistent Maven repository.
#
# Env: JOBS, STARROCKS_COMMIT_HASH, FE_TESTS (optional: comma-separated fe-core test classes to run after
# the build, e.g. "FlightTypeMapperTest,PushDownTopNToPreAggRuleTest").
set -euo pipefail
. /ci/env.sh
export STARROCKS_VERSION STARROCKS_COMMIT_HASH=${STARROCKS_COMMIT_HASH:-$STARROCKS_BASE_HASH}
JOBS=${JOBS:-$(nproc)}
cd /workspace
git config --global --add safe.directory /workspace 2>/dev/null || true
start=$(date +%s)
./build.sh --fe --disable-java-check-style -j "$JOBS"
echo "FE build took $(( ($(date +%s) - start) / 60 )) min"
if [ -n "${FE_TESTS:-}" ]; then
    cd fe
    mvn --batch-mode -Dcheckstyle.skip=true -Dmaven.clean.skip=true -pl fe-core -am test \
        -Dtest="$FE_TESTS" -DfailIfNoTests=false -Dsurefire.failIfNoSpecifiedTests=false
fi
