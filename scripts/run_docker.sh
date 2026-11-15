#!/usr/bin/env bash
# Único lanzador Docker del repositorio. Compatible con casos originales y runs/.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
die() { echo "ERROR: $*" >&2; exit 1; }
image="${FOAM_IMAGE:-opencfd/openfoam-default:2406}"
foam_rc="${FOAM_BASHRC:-}"
mode=Allrun
dry=false
target=""
args=()
cmd=()
usage() { echo "Uso: $0 CASO|DIRECTORIO [--mesh|--solve-only] [--image IMAGEN] [--dry-run] [-- COMANDO ...]"; }
while (($#)); do
    case "$1" in
        --list)
            for d in "$ROOT"/cases/*/ "$ROOT"/visual_cases/*/ "$ROOT"/experimental_cases/*/ "$ROOT"/examples/*/; do
                [[ -d "$d" && ! -L "${d%/}" && ( -f "$d/Allrun" || -f "$d/Allmesh" ) ]] || continue
                printf '%s\n' "${d#"$ROOT"/}"
            done; exit 0 ;;
        --mesh|--mesh-only) mode=Allmesh; shift ;;
        --solve-only) args+=(--solve-only); shift ;;
        --image|-i) (($# >= 2)) || die "Falta imagen"; image="$2"; shift 2 ;;
        --dry-run) dry=true; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; (($#)) || die "Falta comando tras --"; cmd=("$@"); break ;;
        -*) die "Opción desconocida: $1" ;;
        *) [[ -z "$target" ]] || die "Indicar un directorio"; target="$1"; shift ;;
    esac
done
[[ -n "$target" ]] || { usage; exit 2; }
if [[ -d "$target" ]]; then
    dir="$(cd -- "$target" && pwd -P)"
else
    dir=""
    for group in cases visual_cases experimental_cases examples; do
        if [[ -d "$ROOT/$group/$target" ]]; then dir="$(cd -- "$ROOT/$group/$target" && pwd -P)"; break; fi
    done
    [[ -n "$dir" ]] || die "Caso no encontrado: $target"
fi
if [[ "$mode" == Allmesh && ${#args[@]} != 0 ]]; then die "Modos incompatibles"; fi
if ((${#cmd[@]} == 0)); then
    if [[ "$mode" == Allmesh && ! -f "$dir/Allmesh" && -f "$dir/.mesh_method" ]]; then
        [[ "${#args[@]}" == 0 ]] || die "Modos incompatibles"
        cmd=(bash ./Allrun --mesh-only)
    else
        [[ -f "$dir/$mode" ]] || die "Falta $mode (caso pendiente o solo mallado)"
        cmd=(bash "./$mode" "${args[@]}")
    fi
fi
# Montar raíz para que wrappers de los casos fuente encuentren herramientas compartidas.
if [[ "$dir" == "$ROOT/"* && ! -f "$dir/.mesh_method" ]]; then
    mount="$ROOT"
    work="/workspace/${dir#"$ROOT"/}"
else
    mount="$dir"
    work=/workspace
fi
[[ "$mount" != / && "$mount" != "$HOME" ]] || die "No montar / ni HOME completos"
volume="$mount:/workspace"
if command -v getenforce >/dev/null && [[ "$(getenforce)" != Disabled ]]; then volume="$volume:z"; fi
init='
    if [[ -z "$FOAM_BASHRC" ]]; then
        shopt -s nullglob
        candidates=(/usr/lib/openfoam/openfoam*/etc/bashrc /opt/openfoam*/etc/bashrc /opt/OpenFOAM/OpenFOAM-*/etc/bashrc)
        (( ${#candidates[@]} == 1 )) || { echo "Elegir FOAM_BASHRC: ${candidates[*]}" >&2; exit 2; }
        FOAM_BASHRC="${candidates[0]}"
    fi
    source "$FOAM_BASHRC" "" || exit 1
    exec "$@"
'
docker_cmd=(docker run --rm --init --user "$(id -u):$(id -g)" -e HOME=/tmp
    -e "FOAM_BASHRC=$foam_rc" -v "$volume" -w "$work")
for g in $(id -G); do [[ "$g" == "$(id -g)" ]] || docker_cmd+=(--group-add "$g"); done
if [[ -t 0 && -t 1 ]]; then docker_cmd+=(-it); else docker_cmd+=(-i); fi
docker_cmd+=(--entrypoint /bin/bash "$image" -c "$init" bash "${cmd[@]}")
if "$dry"; then printf '%q ' "${docker_cmd[@]}"; printf '\n'; exit 0; fi
command -v docker >/dev/null || die "Docker no disponible"
exec "${docker_cmd[@]}"
