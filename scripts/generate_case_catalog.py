#!/usr/bin/env python3
"""Genera el índice web de casos a partir de los archivos reales del repositorio.

Solo lee metadatos. No ejecuta OpenFOAM, Docker ni simulaciones.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "cases"
OUTPUT = ROOT / "docs" / "catalogo-casos.md"
BASE = "https://github.com/juanjosecas/openFOAM-manual/tree/main/cases"

def solver_for(case: Path) -> str:
    control = case / "system" / "controlDict"
    if not control.is_file():
        return "—"
    # Eliminar comentarios antes de buscar application.
    raw = control.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    raw = re.sub(r"//[^\n]*", "", raw)
    match = re.search(r"(?m)^\s*application\s+([A-Za-z][A-Za-z0-9_]*)\s*;", raw)
    return match.group(1) if match else "—"

def main() -> None:
    lines = [
        "# Catálogo de casos",
        "",
        "Índice generado automáticamente desde `cases/` durante cada publicación.",
        "La presencia de archivos **no equivale a una simulación probada ni validada**.",
        "",
        "| Caso | Solver declarado | Docker | Archivos |",
        "| --- | --- | --- | --- |",
    ]
    for case in sorted(CASES.iterdir()):
        if not case.is_dir():
            continue
        name = case.name
        url = f"{BASE}/{name}"
        docker = "Sí" if (case / "run_docker.sh").is_file() else "No"
        lines.append(
            f"| [{name}]({url}) | `{solver_for(case)}` | {docker} | "
            f"[Ver en GitHub]({url}) |"
        )
    lines += [
        "",
        "## Ejecución con Docker",
        "",
        "Cuando el caso tiene `run_docker.sh`, puede ejecutarse desde la raíz del repositorio:",
        "",
        "```bash",
        "bash cases/09-cavidad-con-tapa-movil/run_docker.sh --dry-run",
        "bash cases/09-cavidad-con-tapa-movil/run_docker.sh",
        "```",
        "",
        "Consultar también la [guía de Docker por caso](docker-por-caso.md) "
        "y la [guía del lanzador general](ejecutar-con-docker.md).",
        "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generado: {OUTPUT} ({len(lines)} líneas)")

if __name__ == "__main__":
    main()
