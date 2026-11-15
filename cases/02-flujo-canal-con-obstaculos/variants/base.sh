#!/usr/bin/env bash
set -Eeuo pipefail
# Referencia original: powerLaw, objeto y paredes noSlip.
[[ -f system/controlDict && ! -e constant/polyMesh ]] || { echo "Usar una copia sin malla" >&2; exit 1; }
