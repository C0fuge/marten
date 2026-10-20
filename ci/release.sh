#!/usr/bin/env bash
# Assemble the release assets from the cached FE and BE build outputs (used by .github/workflows/release.yml).
#
#   ci/release.sh FE_OUT BE_OUT COMMIT_HASH TAG DIST
#
# FE_OUT: fe.yml output (jars + fe-build-info.txt); BE_OUT: be.yml output (starrocks_be.zst + be-build-info.txt).
# Fails unless both were built from exactly this patch series (commit_hash = 4.1.4 base + hash of patches/*).
# Writes into DIST: the assets, SHA256SUMS and release-notes.md.
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
FE_OUT=$1 BE_OUT=$2 COMMIT_HASH=$3 TAG=$4 DIST=$5

field() { sed -n "s/^$2=//p" "$1" | head -1; }
for f in "$FE_OUT/fe-build-info.txt" "$BE_OUT/be-build-info.txt" "$BE_OUT/starrocks_be.zst" "$FE_OUT/starrocks-fe.jar"; do
    [ -s "$f" ] || { echo "missing $f" >&2; exit 1; }
done
fe_ch=$(field "$FE_OUT/fe-build-info.txt" commit_hash)
be_ch=$(field "$BE_OUT/be-build-info.txt" commit_hash)
if [ "$fe_ch" != "$COMMIT_HASH" ] || [ "$be_ch" != "$COMMIT_HASH" ]; then
    echo "build outputs are not from this patch series: fe=$fe_ch be=$be_ch expected=$COMMIT_HASH" >&2
    echo "rebuild the stale one with ci/dispatch.txt 'fe force=true' or 'be force=true'" >&2
    exit 1
fi
# The jars must still match the checksums recorded at build time.
(cd "$FE_OUT" && grep -E '^[0-9a-f]{64}  ' fe-build-info.txt | sha256sum -c --quiet -)

mkdir -p "$DIST"
name=starrocks-flight-$TAG
tar -C "$FE_OUT" -cf "$DIST/$name-fe-jars.tar" --sort=name --owner=0 --group=0 --numeric-owner \
    $(cd "$FE_OUT" && ls *.jar) fe-build-info.txt
cp "$BE_OUT/starrocks_be.zst" "$DIST/$name-starrocks_be.zst"
tar -C "$REPO_ROOT" -czf "$DIST/$name-patches.tar.gz" --sort=name --owner=0 --group=0 --numeric-owner patches
cp "$FE_OUT/fe-build-info.txt" "$BE_OUT/be-build-info.txt" "$REPO_ROOT/docs/INSTALL.md" "$DIST/"
(cd "$DIST" && sha256sum -- * > SHA256SUMS)

be_sha=$(sed -n 's/^starrocks_be sha256: \([0-9a-f]*\).*/\1/p' "$BE_OUT/be-build-info.txt")
{
    echo "StarRocks 4.1.4 with a native Arrow Flight SQL catalog (\`\"type\" = \"flight\"\`)."
    echo
    echo "Version string: \`4.1.4-$COMMIT_HASH\` (base commit + hash of the patch series)."
    echo
    echo "| Asset | Content |"
    echo "|---|---|"
    echo "| \`$name-fe-jars.tar\` | FE jars to copy into \`fe/lib/\` + \`fe-build-info.txt\` |"
    echo "| \`$name-starrocks_be.zst\` | \`be/lib/starrocks_be\` (Release, no debug info; \`unzstd\`, then sha256 \`$be_sha\`) |"
    echo "| \`$name-patches.tar.gz\` | the patch series on tag 4.1.4 (\`git am patches/*.patch\`; 0007 is a BE test only) |"
    echo "| \`INSTALL.md\` | install guide |"
    echo "| \`fe-build-info.txt\`, \`be-build-info.txt\` | build runs, patches, checksums |"
    echo "| \`SHA256SUMS\` | checksums of all assets |"
    echo
    echo "Patches:"
    echo
    for p in "$REPO_ROOT"/patches/*.patch; do echo "- \`$(basename "$p")\`"; done
    echo
    echo "Builds:"
    echo
    echo "- FE: $(field "$FE_OUT/fe-build-info.txt" run) (input hash $(field "$FE_OUT/fe-build-info.txt" hash))"
    echo "- BE: $(field "$BE_OUT/be-build-info.txt" run) (input hash $(field "$BE_OUT/be-build-info.txt" hash))"
} > "$DIST/release-notes.md"
ls -la "$DIST"
