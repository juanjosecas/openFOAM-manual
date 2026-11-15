#!/usr/bin/env bash
set -Eeuo pipefail
# Comparación con agua-estela: mismo fluido y velocidad, solo el objeto cambia a slip.
[[ -f system/controlDict && ! -e constant/polyMesh ]] || { echo "Usar una copia sin malla" >&2; exit 1; }
foamDictionary '0/U' -entry 'boundaryField/obstacle' -set '{ type slip; }'
foamDictionary 'constant/transportProperties' -entry 'nu' -set '[0 2 -1 0 0 0 0] 1e-6'
foamDictionary 'constant/turbulenceProperties' -entry 'laminar' -set '{ model Stokes; }'
foamDictionary 'system/controlDict' -entry 'endTime' -set '5000'
foamDictionary 'system/controlDict' -entry 'purgeWrite' -set '2'
foamDictionary 'system/controlDict' -entry 'writePrecision' -set '12'
