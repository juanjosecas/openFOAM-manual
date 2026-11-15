#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "$0")/.."
{
    printf '# Catálogo de casos\n\nÍndice generado desde las carpetas versionadas. No implica validación.\n\n| Caso | Solver | Docker |\n| --- | --- | --- |\n'
    for d in cases/*/ visual_cases/*/ legacy_cases/*/ experimental_cases/*/ examples/*/; do
        [[ -d "$d" && ! -L "${d%/}" ]] || continue
        solver=—
        if [[ -f "$d/system/controlDict" ]]; then
            value="$(awk '$1=="application" {gsub(/;/,"",$2);print $2;exit}' "$d/system/controlDict")"
            solver="${value:-—}"
        fi
        docker=No; [[ ! -f "$d/run_docker.sh" ]] || docker=Sí
        printf '| [%s](https://github.com/juanjosecas/openFOAM-manual/tree/main/%s) | %s | %s |\n' "$(basename "$d")" "${d%/}" "$solver" "$docker"
    done
} > docs/catalogo-casos.md
