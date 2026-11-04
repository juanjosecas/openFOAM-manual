#!/usr/bin/env bash
# Generar malla con Gmsh Python en el host si todavía no existe.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -f constant/polyMesh/points && ! -f geometry/kangaroo.msh ]]; then
  python3 geometry/build_mesh.py
fi
exec bash ../../scripts/run_docker.sh 31-estela-de-canguro-animacion "$@"
