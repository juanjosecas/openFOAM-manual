#!/usr/bin/env bash
# Preparación de casos sin Python ni Docker SDK. Bash + Git.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
die() { echo "ERROR: $*" >&2; exit 1; }
list_cases() {
    local d
    for d in "$ROOT"/cases/*/ "$ROOT"/visual_cases/*/; do
        [[ -d "$d" && ! -L "${d%/}" && -f "$d/system/controlDict" ]] || continue
        printf '%s\n' "$(basename "$d")"
    done
}
case_id="" variant="" output=""
while (($#)); do
    case "$1" in
        --list) list_cases; exit 0 ;;
        --variant) (($# >= 2)) || die "Falta variante"; variant="$2"; shift 2 ;;
        --output) (($# >= 2)) || die "Falta salida"; output="$2"; shift 2 ;;
        -h|--help) echo "Uso: $0 CASO [--variant NOMBRE] [--output RUTA] | --list"; exit 0 ;;
        -*) die "Opción desconocida: $1" ;;
        *) [[ -z "$case_id" ]] || die "Indicar un solo caso"; case_id="$1"; shift ;;
    esac
done
[[ "$case_id" =~ ^[a-zA-Z0-9_-]+$ ]] || die "Indicar caso válido"
source_dir="$ROOT/cases/$case_id"
[[ -d "$source_dir" && ! -L "$source_dir" ]] || source_dir="$ROOT/visual_cases/$case_id"
[[ -f "$source_dir/system/controlDict" ]] || die "Caso no disponible"
overlay=""
if [[ -n "$variant" ]]; then
    [[ "$variant" =~ ^[a-zA-Z0-9_-]+$ ]] || die "Variante inválida"
    overlay="$source_dir/variants/$variant"
    [[ -d "$overlay" ]] || die "Variante no disponible"
fi
output="${output:-$ROOT/runs/$case_id/$(date +%Y%m%d_%H%M%S_%N)}"
output="$(realpath -m -- "$output")"
case "$output/" in
    "$ROOT/cases/"*|"$ROOT/visual_cases/"*|"$ROOT/legacy_cases/"*|"$ROOT/experimental_cases/"*|"$ROOT/examples/"*) die "Salida dentro de biblioteca de casos" ;;
esac
[[ ! -e "$output" && ! -L "$output" ]] || die "Destino existente"
mkdir -p -- "$(dirname -- "$output")"
mkdir -- "$output"
trap 'echo "Preparación incompleta: $output" >&2' ERR
copy_inputs() {
    local src="$1" path rel
    local manifest
    manifest="$(mktemp)"
    git -C "$ROOT" ls-files -z -- "${src#"$ROOT"/}/" > "$manifest"
    while IFS= read -r -d '' path; do
        rel="${path#${src#"$ROOT"/}/}"
        case "$rel" in
            constant/polyMesh/*) continue ;;
            0/*|constant/*|system/*|geometry/*|postprocessing/*) ;;
            *) continue ;;
        esac
        [[ -f "$ROOT/$path" ]] || die "Falta $path"
        mkdir -p -- "$(dirname -- "$output/$rel")"
        cp -- "$ROOT/$path" "$output/$rel"
    done < "$manifest"
    rm -- "$manifest"
}
copy_inputs "$source_dir"
[[ -z "$overlay" ]] || copy_inputs "$overlay"
for f in controlDict fvSchemes fvSolution; do
    [[ -f "$output/system/$f" ]] || die "Falta system/$f"
done
method=block
case "$case_id" in
    13b-*)
        method=snappy
        # Generación geométrica, no ejecución del solver.
        python3 "$ROOT/scripts/preparar_stl.py" --radius 0.5 --output "$output/constant/triSurface/sphere.stl" >&2 ;;
    cow-flow)
        method=gmsh-cow
        cp -- "$ROOT/meshes/cow_tunnel.msh" "$output/cow_tunnel.msh" ;;
    kangaroo-flow)
        method=gmsh-kangaroo
        (cd "$output" && python3 geometry/build_mesh.py) >&2 ;;
esac
cp -- "$ROOT/scripts/run_prepared_case.sh" "$output/Allrun"
cp -- "$ROOT/scripts/clean_case.sh" "$output/Allclean"
chmod +x "$output/Allrun" "$output/Allclean"
printf '%s\n' "$method" > "$output/.mesh_method"
printf '{"case":"%s","variant":"%s","source_commit":"%s","status":"prepared-not-executed"}\n' \
    "$case_id" "${variant:-base}" "$(git -C "$ROOT" rev-parse HEAD)" > "$output/case.json"
printf '%s\n' "$output"
