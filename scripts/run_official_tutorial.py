#!/usr/bin/env python3
"""Run imported official OpenFOAM v2406 cases in Docker without sudo.

Requires access to Docker daemon. Results remain in cases/<name>.
"""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOLVERS = {
    "27-cilindro-potencial": "potentialFoam",
    "28-escalon-turbulento": "simpleFoam",
    "29-placa-agujero": "solidDisplacementFoam",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=SOLVERS)
    parser.add_argument("--mesh-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    case = ROOT / "cases" / args.case
    if not (case / "system" / "controlDict").is_file():
        parser.error(f"Falta el caso importado: {case}. Ejecutar import_official_tutorial.py.")
    if not shutil.which("docker"):
        parser.error("No se encontró docker.")
    # Use the original official Allrun if provided, preserving its setup steps.
    allrun = case / "Allrun"
    if args.mesh_only:
        cmd = "blockMesh > log.blockMesh 2>&1; checkMesh > log.checkMesh 2>&1"
    elif allrun.is_file():
        cmd = "bash ./Allrun > log.Allrun 2>&1"
    else:
        solver = SOLVERS[args.case]
        cmd = f"blockMesh > log.blockMesh 2>&1; checkMesh > log.checkMesh 2>&1; {solver} > log.{solver} 2>&1"
    # Do not hide failure of an intermediate stage.
    command = [
        "docker", "run", "--rm", "--init",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-e", "HOME=/tmp",
        "--mount", f"type=bind,source={ROOT},target=/workspace",
        "-w", f"/workspace/cases/{args.case}",
        "--entrypoint", "/bin/bash",
        os.environ.get("FOAM_IMAGE", "opencfd/openfoam-default:2406"),
        "-ec", "source /usr/lib/openfoam/openfoam2406/etc/bashrc; " + cmd,
    ]
    if args.dry_run:
        print(" ".join(command))
        return
    subprocess.run(command, check=True)
    print(f"Finalizado. Resultados: {case}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
