#!/usr/bin/env bash
# Importar tutorial oficial usando el lanzador Docker personal, sin SDK.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
case "${1:-}" in
    --list) printf '%s\n' 27-cilindro-potencial 28-escalon-turbulento 29-placa-agujero; exit 0 ;;
    27-cilindro-potencial) tutorial=basic/potentialFoam/cylinder ;;
    28-escalon-turbulento) tutorial=incompressible/simpleFoam/pitzDaily ;;
    29-placa-agujero) tutorial=stressAnalysis/solidDisplacementFoam/plateHole ;;
    *) echo "Uso: $0 CASO [--dry-run] | --list" >&2; exit 2 ;;
esac
dest="$ROOT/cases/$1"
[[ ! -e "$dest" ]] || { echo "Destino existente: $dest" >&2; exit 1; }
if [[ "${2:-}" == --dry-run ]]; then printf '%s -> %s\n' "$tutorial" "$dest"; exit 0; fi
[[ $# == 1 ]] || exit 2
command -v openfoam >/dev/null || { echo "Falta el lanzador openfoam" >&2; exit 1; }
tmp="$(mktemp -d "$ROOT/cases/.official-XXXXXX")"
trap 'rm -rf -- "$tmp"' EXIT
openfoam -i "${FOAM_IMAGE:-opencfd/openfoam-default:2406}" -d "$tmp" -- bash -ec '
    src="$FOAM_TUTORIALS/$1"
    test -d "$src"
    cp -a "$src"/. .
' bash "$tutorial"
[[ -f "$tmp/system/controlDict" ]] || exit 1
mv -T -- "$tmp" "$dest"
printf '%s\n' "$dest"
