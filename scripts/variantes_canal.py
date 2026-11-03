"""Preparar variantes del canal con obstáculos sin modificar la plantilla."""
from pathlib import Path
from uuid import uuid4
import json
import re
import shutil

from scripts.foam_docker import foam_run


def preparar_canal_obstaculos(repo_dir, variante="base", *,
                              image="opencfd/openfoam-run:2406", verbose=False):
    """Copiar la plantilla y aplicar una receta JSON usando foamDictionary.

    Devuelve el Path del caso listo para mallar. No ejecuta el solver.
    Las recetas son archivos locales de confianza bajo variants/.
    """
    repo = Path(repo_dir).expanduser().resolve(strict=True)
    source = repo / "cases/02-canal-obstaculos"
    if not isinstance(variante, str) or not re.fullmatch(r"[a-z0-9-]+", variante):
        raise ValueError("Nombre de variante inválido")
    recipe_path = source / "variants" / f"{variante}.json"
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    factor = recipe.get("refinamiento", 1)
    if isinstance(factor, bool) or not isinstance(factor, int) or not 1 <= factor <= 4:
        raise ValueError("refinamiento debe ser un entero entre 1 y 4")
    allowed = {
        "0/U", "0/p", "constant/transportProperties",
        "constant/turbulenceProperties", "system/controlDict",
        "system/fvSolution", "system/fvSchemes",
    }
    edits = recipe.get("ajustes", {})
    if not isinstance(edits, dict) or set(edits) - allowed:
        raise ValueError("La receta contiene archivos no admitidos")
    for relative, entries in edits.items():
        if not (source / relative).is_file() or not isinstance(entries, dict):
            raise ValueError(f"Configuración inválida para {relative}")
        if any(not isinstance(key, str) or not isinstance(value, str)
               for key, value in entries.items()):
            raise ValueError("Las entradas y valores OpenFOAM deben ser cadenas")

    case = repo / "runs" / f"canal-{variante}-{uuid4().hex[:12]}"
    case.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, case, ignore=shutil.ignore_patterns(
        "variants", "polyMesh", "processor[0-9]*", "postProcessing",
        "VTK", "log.*", "*.foam"))
    # Registrar la receta también si una edición posterior falla.
    (case / "variante.json").write_text(
        json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if factor != 1:
        path = case / "system/blockMeshDict"
        pattern = r"(?m)^([ \t]*)\((\d+)\s+(\d+)\s+(\d+)\)([ \t]+simpleGrading\b)"

        def refine(match):
            nx, ny, nz = map(int, match.group(2, 3, 4))
            return f"{match[1]}({nx*factor} {ny*factor} {nz}){match[5]}"

        text, count = re.subn(pattern, refine, path.read_text())
        if count != 8:
            raise RuntimeError(f"Se esperaban ocho bloques, se encontraron {count}. Caso: {case}")
        path.write_text(text, encoding="utf-8")
    for relative, entries in edits.items():
        for entry, value in entries.items():
            foam_run(["foamDictionary", relative, "-entry", entry, "-set", value],
                     case_dir=case, repo_dir=repo, image=image,
                     verbose=verbose, timeout=60)
    print(f"Variante: {variante}\n{recipe.get('descripcion', '')}\nCaso: {case}")
    return case
