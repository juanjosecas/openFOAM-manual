#!/usr/bin/env python3
"""Import an unmodified official tutorial from the pinned OpenFOAM v2406 image.

The destination is a new cases/<name> directory; existing cases are never overwritten.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "27-cilindro-potencial": "basic/potentialFoam/cylinder",
    "28-escalon-turbulento": "incompressible/simpleFoam/pitzDaily",
    "29-placa-agujero": "stressAnalysis/solidDisplacementFoam/plateHole",
}
IMAGE = os.environ.get("FOAM_IMAGE", "opencfd/openfoam-default:2406")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", choices=CASES)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.list:
        for name, source in CASES.items():
            print(f"{name:29} $FOAM_TUTORIALS/{source}")
        return
    if args.case is None:
        parser.error("Indicar un caso o --list.")
    dest = ROOT / "cases" / args.case
    if dest.exists():
        parser.error(f"El destino ya existe: {dest}. No se sobreescribe.")
    if args.dry_run:
        print(f"Imagen: {IMAGE}\nOrigen: $FOAM_TUTORIALS/{CASES[args.case]}\nDestino: {dest}")
        return
    if not shutil.which("docker"):
        parser.error("No se encontró docker en PATH.")
    # Temp directory is on the same filesystem to allow atomic rename.
    with tempfile.TemporaryDirectory(prefix=".official-", dir=ROOT / "cases") as tmp:
        command = [
            "docker", "run", "--rm", "--init",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-e", "HOME=/tmp",
            "--mount", f"type=bind,source={tmp},target=/export",
            "--entrypoint", "/bin/bash", IMAGE, "-ec",
            'source /usr/lib/openfoam/openfoam2406/etc/bashrc; '
            'src="$FOAM_TUTORIALS/$1"; '
            'test -d "$src" || { echo "No existe $src" >&2; exit 3; }; '
            'cp -a "$src"/. /export/',
            "bash", CASES[args.case],
        ]
        subprocess.run(command, check=True)
        if not (Path(tmp) / "system" / "controlDict").is_file():
            raise RuntimeError("El tutorial importado no contiene system/controlDict.")
        Path(tmp).rename(dest)
    print(f"Importado en {dest}. Inspeccionar y ejecutar según README.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
