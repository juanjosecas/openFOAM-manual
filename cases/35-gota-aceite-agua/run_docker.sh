#!/usr/bin/env bash
# Ejecutar desde la raíz del repositorio: bash cases/35-gota-aceite-agua/run_docker.sh
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
docker run --rm --init --user "$(id -u):$(id -g)" -e HOME=/tmp \
  --mount "type=bind,source=$ROOT,target=/workspace" \
  -w /workspace/cases/35-gota-aceite-agua \
  --entrypoint /bin/bash "${FOAM_IMAGE:-opencfd/openfoam-default:2406}" -ec '
    source /usr/lib/openfoam/openfoam2406/etc/bashrc
    command -v multiphaseInterFoam >/dev/null || { echo "multiphaseInterFoam no disponible en esta imagen" >&2; exit 3; }
    if [[ ! -d case ]]; then python3 build_case.py; fi
    cd case
    if [[ ! -f constant/polyMesh/points ]]; then
      blockMesh > log.blockMesh 2>&1
      checkMesh > log.checkMesh 2>&1
      setFields > log.setFields 2>&1
    fi
    multiphaseInterFoam 2>&1 | tee log.multiphaseInterFoam
  '
