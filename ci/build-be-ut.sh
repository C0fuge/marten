#!/usr/bin/env bash
# BE unit test of the Flight connector, run INSIDE the dev-env container (same mounts as build-be.sh).
#
# The upstream UT build (run-be-ut.sh: MAKE_TEST=ON, BE_TEST defines, ASAN) shares nothing with our Release
# ccache and would be a full rebuild. Instead the test is added to the Release tree (CI only, appended to
# be/CMakeLists.txt here) and linked like starrocks_be; only the test and the changed sources compile, the rest
# comes from ccache.
#
# Env: JOBS, GTEST_FILTER (default *). Exit: 0 = tests passed; 3 = test binary not built; other = test failure.
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
export USE_AVX2=ON USE_AVX512=OFF USE_SSE4_2=ON USE_BMI_2=ON
JOBS=${JOBS:-$(nproc)}
TEST=flight_connector_test

cd /workspace
git config --global --add safe.directory /workspace 2>/dev/null || true
cat >> be/CMakeLists.txt <<CMAKE

# CI only (ci/build-be-ut.sh): $TEST in the Release tree, linked like starrocks_be
add_executable($TEST \${CMAKE_CURRENT_SOURCE_DIR}/test/connector/$TEST.cpp)
target_link_libraries($TEST \${TEST_LINK_LIBS})
# same compile flag as upstream ADD_BE_TEST
set_target_properties($TEST PROPERTIES COMPILE_FLAGS "-fno-access-control" RUNTIME_OUTPUT_DIRECTORY \${CMAKE_BINARY_DIR}/ut)
CMAKE
ccache --zero-stats >/dev/null
start=$(date +%s)
# A full Release build (the test target is part of "all"); build.sh --module cannot be used: its getopt spec
# declares "module" without an argument.
./build.sh --be --without-java-ext -j "$JOBS"
echo "build.sh exit code $? after $(( ($(date +%s) - start) / 60 )) min"
ccache --show-stats || true
bin=be/build_Release/ut/$TEST
if [ ! -x "$bin" ]; then
    echo "::error::$TEST was not built"
    exit 3
fi
ls -la "$bin"
mkdir -p /workspace/ut-report
# starrocks_be links some libraries dynamically (libjvm.so, libjemalloc.so.2, ...); start_backend.sh puts
# their directories on the library path. Do the same for whatever ldd cannot resolve.
search=(/workspace/output/be/lib /workspace/be/output/lib "${STARROCKS_THIRDPARTY:-/var/local/thirdparty}"
        "${JAVA_HOME:-/usr/lib/jvm}/" /usr/lib/jvm/)
for lib in $(ldd "$bin" | awk '/not found/ {print $1}' | sort -u); do
    f=$(find "${search[@]}" -name "$lib" 2>/dev/null | head -1)
    if [ -n "$f" ]; then
        echo "$lib from $(dirname "$f")"
        export LD_LIBRARY_PATH="$(dirname "$f"):${LD_LIBRARY_PATH:-}"
    else
        echo "::warning::$lib not found"
    fi
done
ldd "$bin" | grep 'not found' || true
"$bin" --gtest_filter="${GTEST_FILTER:-*}" --gtest_output=xml:/workspace/ut-report/$TEST.xml 2>&1 |
    tee /workspace/ut-report/$TEST.log
exit "${PIPESTATUS[0]}"
