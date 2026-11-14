#!/usr/bin/env bash
set -Eeuo pipefail
# Fluido newtoniano nu=1e-6 m2/s, U=0.01 m/s, objeto noSlip; Re_h=40.
[[ -f system/controlDict && ! -e constant/polyMesh ]] || { echo "Usar una copia sin malla" >&2; exit 1; }
foamDictionary 'constant/transportProperties' -entry 'nu' -set '[0 2 -1 0 0 0 0] 1e-6'
foamDictionary 'constant/turbulenceProperties' -entry 'laminar' -set '{ model Stokes; }'
foamDictionary 'system/controlDict' -entry 'endTime' -set '5000'
foamDictionary 'system/controlDict' -entry 'purgeWrite' -set '2'
foamDictionary 'system/controlDict' -entry 'writePrecision' -set '12'
