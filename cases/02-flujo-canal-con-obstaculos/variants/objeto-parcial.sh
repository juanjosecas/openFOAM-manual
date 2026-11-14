#!/usr/bin/env bash
set -Eeuo pipefail
# Mismo fluido de la base; objeto con deslizamiento parcial e impermeable.
[[ -f system/controlDict && ! -e constant/polyMesh ]] || { echo "Usar una copia sin malla" >&2; exit 1; }
foamDictionary '0/U' -entry 'boundaryField/obstacle' -set '{ type partialSlip; refValue uniform (0 0 0); valueFraction uniform 0.5; value uniform (0 0 0); }'
foamDictionary 'system/controlDict' -entry 'endTime' -set '5000'
foamDictionary 'system/controlDict' -entry 'purgeWrite' -set '2'
foamDictionary 'system/controlDict' -entry 'writePrecision' -set '12'
