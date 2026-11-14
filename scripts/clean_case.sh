#!/usr/bin/env bash
# Limpieza explícita; sin tocar las condiciones iniciales ni archivos versionados.
set -Eeuo pipefail
dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
yes=false
while (($#)); do
    case "$1" in
        --case-dir) (($# >= 2)) || exit 2; dir="$2"; shift 2 ;;
        --yes) yes=true; shift ;;
        *) echo "Uso: Allclean [--yes]" >&2; exit 2 ;;
    esac
done
cd -- "$dir"
[[ -f system/controlDict ]] || { echo "No es un caso CFD." >&2; exit 1; }
if [[ ! -f .mesh_method ]] && ! { command -v git >/dev/null && git rev-parse --is-inside-work-tree >/dev/null 2>&1; }; then
    echo "Limpiar casos fuente desde el host con Git, o usar una copia preparada." >&2; exit 1
fi
shopt -s nullglob
paths=()
for p in * constant/polyMesh; do
    [[ -e "$p" || -L "$p" ]] || continue
    if [[ "$p" == constant/polyMesh || "$p" == postProcessing || "$p" == VTK ||
          "$p" == log.* || "$p" =~ ^processor[0-9]+$ ||
          ( "$p" != 0 && "$p" =~ ^[+]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?$ ) ]]; then
        # No eliminar ningún directorio o archivo con contenido registrado en Git.
        if command -v git >/dev/null && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
            tracked="$(git ls-files -- "$p")"
            [[ -z "$tracked" ]] || { printf 'Conservado (versionado): %s\n' "$p"; continue; }
        fi
        paths+=("$p")
    fi
done
if (("${#paths[@]}" == 0)); then echo "No hay resultados para limpiar."; exit 0; fi
printf '%s\n' "${paths[@]}"
if "$yes"; then
    rm -rf -- "${paths[@]}"
    echo "Limpieza realizada. No restaura campos 0/ modificados por setFields."
else
    echo "Previsualización. Usar --yes para borrar."
fi
