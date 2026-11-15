#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
case "${1:-}" in
    27-cilindro-potencial|28-escalon-turbulento|29-placa-agujero) ;;
    *) echo "Indicar caso oficial importado" >&2; exit 2 ;;
esac
dir="$ROOT/cases/$1"; shift
[[ -f "$dir/system/controlDict" ]] || { echo "Importar primero el caso" >&2; exit 1; }
args=()
mode=run
for arg in "$@"; do
    case "$arg" in --dry-run) args+=(--dry-run);; --mesh-only) mode=mesh;; *) exit 2;; esac
done
if [[ "$mode" == mesh ]]; then
    cmd=(bash -ec 'blockMesh && checkMesh')
elif [[ -f "$dir/Allrun" ]]; then
    cmd=(bash Allrun)
else
    cmd=(bash -ec 'blockMesh && checkMesh && solver=$(foamDictionary system/controlDict -entry application -value) && "$solver"')
fi
exec bash "$ROOT/scripts/run_docker.sh" "$dir" --image "${FOAM_IMAGE:-opencfd/openfoam-default:2406}" "${args[@]}" -- "${cmd[@]}"
