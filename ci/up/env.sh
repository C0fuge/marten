# Connector comparison (docs/CONNECTOR-COMPARE.md): build settings of the UPSTREAM native Flight connector
# (fork VadimSurpin/starrocks, branch feat/flight-connector on branch-4.0) and of the upstream JDBC adapter
# (VadimSurpin/arrow-flight-server, module flight-starrocks). Mounted over /ci/env.sh in the up-* builds, so
# ci/build-be.sh / build-fe.sh run unchanged. Nothing here is part of this repo's own patch series.
UP_REPO=https://github.com/VadimSurpin/starrocks.git
UP_COMMIT=4b3497def80e6258e9736ecbcdcca450bdd066de   # feat/flight-connector, 2026-10-23
UP_BASE=1c10db3edc7794126ab7a8d00b21898e77ef6b72     # branch-4.0, 2026-10-17 (between 4.0.16 and 4.0.17)
AFS_REPO=https://github.com/VadimSurpin/arrow-flight-server.git
AFS_COMMIT=6e264c10f4031edcc7c021cd86dc807c8fff9bc6  # feat/starrocks-native-integration
# Builder and runtime of the 4.0 line (linux/amd64 manifest digests of tag 4.0.17, the first 4.0 release after UP_BASE)
DEV_IMAGE=docker.io/starrocks/dev-env-ubuntu:4.0.17@sha256:39a9f9b6945ce576199c6cc691c727ddb1a0d3a124386eafcd323e2054f89f52
UP_SR_IMAGE=docker.io/starrocks/allin1-ubuntu:4.0.17@sha256:339e26a8878e9aa326260affe19ebe449d7aaf1435740aab3843196042dfb91c
STARROCKS_VERSION=4.0-flight-up
STARROCKS_BASE_HASH=4b3497d
