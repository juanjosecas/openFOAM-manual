#!/usr/bin/env bash
# Caso: 07-svg-gmsh. Ejecución autónoma con Docker y OpenFOAM.com v2406.
# No invoca Allrun ni Allmesh. Resultados y logs quedan en este directorio.
set -Eeuo pipefail
CASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_DIR="$(cd -- "$CASE_DIR/../.." && pwd -P)"
IMAGE="${FOAM_IMAGE:-opencfd/openfoam-default:2406}"
if [[ "${1:-}" == --help ]]; then
    echo "Uso: bash run_docker.sh [--dry-run]"; exit 0
fi
[[ "$#" -eq 0 || ( "$#" -eq 1 && "$1" == --dry-run ) ]] || {
    echo "Uso: bash run_docker.sh [--dry-run]" >&2; exit 2;
}
# Montar todo el repo: algunas geometrías y mallas se comparten entre casos.
# Ejecutar con el UID/GID local para evitar archivos propiedad de root.
# El contenedor es efímero; los datos persisten en el bind mount.
cmd=(docker run --rm --init --user "$(id -u):$(id -g)" --env HOME=/tmp
    --mount "type=bind,source=$REPO_DIR,target=/workspace"
    --workdir "/workspace/cases/07-svg-gmsh"
    --entrypoint /bin/bash "$IMAGE" -c
    'set -Eeuo pipefail
     source /usr/lib/openfoam/openfoam2406/etc/bashrc
     export CASE_DIR="$PWD"
     bash -s' )
if [[ "${1:-}" == --dry-run ]]; then
    printf '%q ' "${cmd[@]}"; printf ' < etapas_del_caso\n'; exit 0
fi
command -v docker >/dev/null || { echo "ERROR: Docker no instalado." >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "ERROR: Docker daemon inaccesible." >&2; exit 1; }
# El bloque siguiente se entrega a Bash dentro del contenedor por stdin.
"${cmd[@]}" <<'OPENFOAM_STAGES'
set -Eeuo pipefail
trap 'printf "ERROR en línea %s (código %s)\\n" "$LINENO" "$?" >&2' ERR
cd "$CASE_DIR"

die() { echo "ERROR: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Comando no disponible en imagen: $1"; }
run_step() {
    local label="$1"; shift
    need "$1"
    echo "==> $label: $*"
    "$@" > "log.$label" 2>&1 || { tail -n 70 "log.$label" >&2; die "Falló $label (ver log.$label)"; }
}
verify_mesh() {
    local policy="${1:-strict}"
    run_step checkMesh checkMesh || return 1
    if [[ "$policy" == cow ]]; then
        grep -Eq 'Mesh OK|Failed 1 mesh checks' log.checkMesh || die "Calidad de malla no aceptada (ver log.checkMesh)"
    else
        grep -q 'Mesh OK' log.checkMesh || die "checkMesh no confirmó Mesh OK"
    fi
}
mesh_block() {
    if [[ ! -f constant/polyMesh/points ]]; then
        [[ -f system/blockMeshDict ]] || die "Falta system/blockMeshDict"
        run_step blockMesh blockMesh
    else
        echo "Malla existente: se reutiliza sin regenerarla."
    fi
    verify_mesh
}
run_solver() {
    [[ -f system/controlDict ]] || die "Falta system/controlDict"
    need foamDictionary
    local configured solver
    configured="$(foamDictionary system/controlDict -entry application -value)"
    solver="${1:-$configured}"
    [[ "$solver" =~ ^[A-Za-z][A-Za-z0-9_]*$ ]] || die "Nombre de solver inválido: $solver"
    [[ "$configured" == "$solver" ]] || die "controlDict declara $configured, pero el script requiere $solver"
    need "$solver"
    # No sobrescribir resultados numéricos: crear una copia limpia para repetir.
    if find . -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex './[1-9][0-9]*(\.[0-9]+)?' | grep -q .; then
        die "Ya existen tiempos calculados; ejecutar en una copia limpia del caso."
    fi
    echo "==> Solver: $solver"
    "$solver" 2>&1 | tee "log.$solver"
}

# Etapas específicas del caso; cada comando se registra en log.<etapa>.
[[ ! -f constant/polyMesh/points ]] || die "La malla ya existe; usar una copia limpia."
run_step generar_geometria python3 ../../scripts/generar_canal_gmsh.py
run_step gmshToFoam gmshToFoam geometry/canal.msh
run_step ajustar_patches python3 ../../scripts/ajustar_patches_gmsh.py
verify_mesh
run_solver simpleFoam
OPENFOAM_STAGES
