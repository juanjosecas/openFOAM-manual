#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "$0")" && pwd -P)"
exec bash "$HERE/../../scripts/run_docker.sh" "$HERE" "$@"
