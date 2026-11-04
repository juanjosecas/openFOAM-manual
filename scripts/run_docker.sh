#!/usr/bin/env bash
# Ejecuta los scripts Allrun/Allmesh de cases/ dentro de OpenFOAM v2406 en Docker.
# No requiere OpenFOAM instalado en el host. Los resultados quedan en el repo.
set -Eeuo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
CASES_DIR="$REPO_DIR/cases"
IMAGE="${FOAM_IMAGE:-opencfd/openfoam-default:2406}"
MODE=run
DRY_RUN=false
CASE=""

usage() {
    cat <<'HELP'
Uso:
  bash scripts/run_docker.sh <caso> [--mesh] [--dry-run] [--image IMAGEN]
  bash scripts/run_docker.sh --list

Ejemplos:
  bash scripts/run_docker.sh 09-cavidad-con-tapa-movil
  bash scripts/run_docker.sh 27-flujo-estacionario-alrededor-vaca
  bash scripts/run_docker.sh 28-flujo-transitorio-alrededor-vaca
  bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --mesh
  bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --dry-run

Opciones:
  --list          Listar casos y scripts existentes.
  --mesh          Ejecutar Allmesh en lugar de Allrun (solo construir la malla).
  --dry-run       Mostrar el comando Docker sin ejecutarlo.
  --image IMAGEN  Elegir otra imagen compatible (por defecto: OpenFOAM 2406).
  -h, --help      Mostrar esta ayuda.

Los scripts Allrun/Allmesh controlan las etapas específicas de cada caso.
No se limpian mallas ni resultados automáticamente.
HELP
}

list_cases() {
    local d
    for d in "$CASES_DIR"/*/; do
        [[ -d "$d" ]] || continue
        printf '%-38s' "$(basename "$d")"
        [[ -f "$d/Allrun" ]] && printf '  Allrun' || printf '  ------'
        [[ -f "$d/Allmesh" ]] && printf '  Allmesh' || true
        printf '\n'
    done
}

while (($#)); do
    case "$1" in
        --list) list_cases; exit 0 ;;
        --mesh) MODE=mesh; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --image)
            (($# >= 2)) && [[ -n "$2" ]] || { echo 'ERROR: --image necesita un valor.' >&2; exit 2; }
            IMAGE="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "ERROR: opción desconocida: $1" >&2; usage >&2; exit 2 ;;
        *)
            [[ -z "$CASE" ]] || { echo 'ERROR: indicar un solo caso.' >&2; exit 2; }
            CASE="$1"; shift ;;
    esac
done

[[ -n "$CASE" ]] || { usage >&2; exit 2; }
# Se aceptan nombres de carpeta, no rutas arbitrarias fuera de cases/.
[[ "$CASE" =~ ^[[:alnum:]][[:alnum:]_-]*$ ]] || {
    echo "ERROR: nombre de caso inválido: $CASE" >&2; exit 2;
}
[[ -d "$CASES_DIR/$CASE" ]] || {
    echo "ERROR: no existe cases/$CASE. Usar --list para ver los disponibles." >&2; exit 2;
}

SCRIPT=Allrun
[[ "$MODE" == mesh ]] && SCRIPT=Allmesh
[[ -f "$CASES_DIR/$CASE/$SCRIPT" ]] || {
    echo "ERROR: cases/$CASE no contiene $SCRIPT." >&2
    echo 'Usar --list para consultar los scripts disponibles.' >&2
    exit 2
}

# Montamos TODO el repo porque algunos Allrun usan archivos de otras carpetas
# (por ejemplo, 28-flujo-transitorio-alrededor-vaca usa la malla del caso steady).
# --user evita crear resultados como root en el equipo anfitrión.
# --entrypoint anula el entrypoint propio de la imagen y permite cargar bashrc.
# --rm elimina el contenedor al terminar, pero conserva los resultados montados.
DOCKER_CMD=(
    docker run --rm --init
    --user "$(id -u):$(id -g)"
    --env HOME=/tmp
    --mount "type=bind,source=$REPO_DIR,target=/workspace"
    --workdir "/workspace/cases/$CASE"
    --entrypoint /bin/bash
    "$IMAGE"
    -c 'set -e; source /usr/lib/openfoam/openfoam2406/etc/bashrc; exec bash "$1"'
    bash "./$SCRIPT"
)

printf 'Caso:   %s\nAcción: %s\nImagen: %s\n' "$CASE" "$SCRIPT" "$IMAGE"
printf 'Datos:  %s\n' "$CASES_DIR/$CASE"

if [[ "$DRY_RUN" == true ]]; then
    printf '\nComando que se ejecutaría:\n'
    printf '%q ' "${DOCKER_CMD[@]}"
    printf '\n'
    exit 0
fi

command -v docker >/dev/null 2>&1 || { echo 'ERROR: Docker no está instalado o no está en PATH.' >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo 'ERROR: Docker daemon no está disponible o faltan permisos.' >&2; exit 1; }

"${DOCKER_CMD[@]}"
