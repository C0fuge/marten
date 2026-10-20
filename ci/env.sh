# Shared build settings (sourced by the CI scripts and by local builds). Part of the input hash.
# Official builder for tag 4.1.4 (build-in-docker.sh uses starrocks/dev-env-ubuntu:<tag>); pinned to the
# linux/amd64 manifest digest so a re-pushed tag cannot change the toolchain or thirdparty libraries.
DEV_IMAGE=docker.io/starrocks/dev-env-ubuntu:4.1.4@sha256:4a9ccbf65df99d908605d7cfafaa918dd08a95bcf2fdc592300d85a2ec20facd
STARROCKS_VERSION=4.1.4
STARROCKS_BASE_HASH=4a9848e
