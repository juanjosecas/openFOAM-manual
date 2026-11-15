#!/usr/bin/env bash
set -Eeuo pipefail
case_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
method=""
die() { echo "ERROR: $*" >&2; exit 1; }
step() {
    local label="$1"; shift
    command -v "$1" >/dev/null || die "Falta $1."
    "$@" 2>&1 | tee "log.$label"
}
verify_mesh() {
    step "$1" checkMesh
    grep -q 'Mesh OK' "log.$1" || die "checkMesh no confirmó Mesh OK."
}

mode=all
end_time=""
while (($#)); do
    case "$1" in
        --case-dir) (($# >= 2)) || die "Falta directorio."; case_dir="$2"; shift 2 ;;
        --method) (($# >= 2)) || die "Falta método."; method="$2"; shift 2 ;;
        --mesh-only) [[ "$mode" != solve ]] || die "Modos incompatibles."; mode=mesh; shift ;;
        --solve-only) [[ "$mode" != mesh ]] || die "Modos incompatibles."; mode=solve; shift ;;
        --end-time) (($# >= 2)) || die "Falta endTime."; end_time="$2"; shift 2 ;;
        *) die "Opción desconocida: $1" ;;
    esac
done
cd -- "$case_dir"
[[ -f system/controlDict && -f system/fvSchemes && -f system/fvSolution ]] || die "Caso incompleto."
if [[ -z "$method" ]]; then
    [[ -f case.json && -f .mesh_method ]] || die "Preparar copia primero."
    method="$(cat .mesh_method)"
fi
[[ "$method" =~ ^(block|snappy|gmsh-cow|gmsh-kangaroo)$ ]] || die "Método no admitido."
if [[ "$mode" == mesh && -n "$end_time" ]]; then die "--end-time requiere solver."; fi
for dir in */; do
    [[ -d "$dir" ]] || continue
    name="${dir%/}"
    if [[ "$name" != 0 && "$name" =~ ^[+]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?$ ]] ||
       [[ "$name" =~ ^processor[0-9]+$ ]]; then
        die "Resultados existentes: $name. Preparar otra copia."
    fi
done
command -v foamDictionary >/dev/null || die "Cargar OpenFOAM."
solver="$(foamDictionary system/controlDict -entry application -value)"
[[ "$solver" =~ ^[A-Za-z][A-Za-z0-9_]*$ ]] || die "Solver inválido."
if [[ "$mode" != mesh ]]; then command -v "$solver" >/dev/null || die "Falta $solver."; fi
if [[ "$mode" != solve ]]; then
    [[ ! -e constant/polyMesh ]] || die "Malla previa; usar --solve-only o una copia nueva."
    case "$method" in
        block) step blockMesh blockMesh ;;
        snappy)
            step surfaceCheck surfaceCheck constant/triSurface/sphere.stl
            grep -q 'Surface is closed.' log.surfaceCheck || die "Superficie no cerrada."
            grep -q 'Surface has no illegal triangles.' log.surfaceCheck || die "Triángulos inválidos."
            step blockMesh blockMesh
            verify_mesh checkMeshBase
            step snappyHexMesh snappyHexMesh -overwrite ;;
        gmsh-cow)
            mesh=cow_tunnel.msh
            [[ -f "$mesh" ]] || mesh=../../meshes/cow_tunnel.msh
            [[ -f "$mesh" ]] || die "Falta malla bovina."
            step gmshToFoam gmshToFoam "$mesh"
            step changeDictionary changeDictionary ;;
        gmsh-kangaroo)
            [[ -f geometry/kangaroo.msh ]] || step geometry python3 geometry/build_mesh.py
            step gmshToFoam gmshToFoam geometry/kangaroo.msh
            step changeDictionary changeDictionary ;;
        *) die "Mallado desconocido." ;;
    esac
fi
[[ -f constant/polyMesh/points || -f constant/polyMesh/points.gz ]] || die "Malla no disponible."
verify_mesh checkMesh
[[ "$mode" != mesh ]] || exit 0
if [[ -n "$end_time" ]]; then
    [[ "$end_time" =~ ^[0-9]+([.][0-9]+)?([eE][+-]?[0-9]+)?$ ]] || die "endTime inválido."
    awk -v n="$end_time" 'BEGIN {exit !(n>0)}' || die "endTime debe ser positivo."
    foamDictionary system/controlDict -entry endTime -set "$end_time"
fi
[[ ! -f system/setFieldsDict ]] || step setFields setFields
if command -v foamVersion >/dev/null; then foamVersion | tee log.foamVersion; fi
step "$solver" "$solver"
touch case.foam
echo "Solver finalizado; revisar residuos y campos."
