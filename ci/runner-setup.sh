#!/usr/bin/env bash
# GitHub-hosted runner preparation: report resources, free disk space, pick a work directory.
# Writes WORK=<dir> to $GITHUB_ENV.  Usage: ci/runner-setup.sh [light]
set -euo pipefail
echo "::group::resources before"
nproc; free -g; df -h / /mnt 2>/dev/null || df -h /
echo "::endgroup::"

# Preinstalled toolchains we never use (several GB each). Removal runs in parallel.
sudo rm -rf /usr/share/dotnet /usr/local/lib/android /opt/ghc /usr/local/.ghcup &
sudo rm -rf /opt/hostedtoolcache/CodeQL /usr/local/share/boost /usr/share/swift &
if [ "${1:-}" != light ]; then
    sudo rm -rf /usr/local/julia* /opt/az /usr/local/share/powershell /usr/local/share/chromium \
        /opt/microsoft /opt/google /usr/lib/firefox /opt/hostedtoolcache/go /opt/hostedtoolcache/PyPy &
    sudo docker image prune --all --force >/dev/null &
fi
wait
sudo swapoff -a 2>/dev/null || true
sudo rm -f /mnt/swapfile /swapfile

# Work directory on whichever filesystem has more free space (/mnt is a separate disk on most runners).
root_free=$(df --output=avail -k / | tail -1)
mnt_free=$(df --output=avail -k /mnt 2>/dev/null | tail -1 || echo 0)
if [ "${mnt_free:-0}" -gt "$root_free" ]; then WORK=/mnt/work; else WORK=$HOME/work; fi
sudo mkdir -p "$WORK"
sudo chown "$(id -u):$(id -g)" "$WORK"
# Swap on the work disk: gcc peaks at 3-5 GB on the heaviest BE translation units.
if [ "${1:-}" != light ]; then
    swf=$(dirname "$WORK")/swapfile.sr
    { sudo fallocate -l 8G "$swf" && sudo chmod 600 "$swf" && sudo mkswap "$swf" >/dev/null && sudo swapon "$swf"; } || true
fi
echo "WORK=$WORK" >> "$GITHUB_ENV"
echo "::group::resources after"
free -g; df -h / /mnt 2>/dev/null || df -h /
echo "::endgroup::"
