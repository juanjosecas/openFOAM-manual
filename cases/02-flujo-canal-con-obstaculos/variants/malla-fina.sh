#!/usr/bin/env bash
set -Eeuo pipefail
# Mismo fluido y BC de la base, doble resolución en x e y: 31360 celdas.
[[ -f system/controlDict && ! -e constant/polyMesh ]] || { echo "Usar una copia sin malla" >&2; exit 1; }
awk -v factor=2 ' /^[[:space:]]*\([0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+\)[[:space:]]+simpleGrading/ { split($0,a,"[()]"); split(a[2],n,/[[:space:]]+/); sub(/\([0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+\)/,"(" n[1]*factor " " n[2]*factor " " n[3] ")"); count++ } {print} END {if(count!=8) exit 1}' system/blockMeshDict > system/blockMeshDict.tmp && mv system/blockMeshDict.tmp system/blockMeshDict
foamDictionary 'system/controlDict' -entry 'endTime' -set '8000'
foamDictionary 'system/controlDict' -entry 'purgeWrite' -set '2'
foamDictionary 'system/controlDict' -entry 'writePrecision' -set '12'
