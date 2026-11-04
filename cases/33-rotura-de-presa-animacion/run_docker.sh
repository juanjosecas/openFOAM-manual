#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
exec bash ../../scripts/run_docker.sh "33-rotura-de-presa-animacion" "$@"
