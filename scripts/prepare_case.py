#!/usr/bin/env python3
"""Preparar una copia independiente de un caso versionado."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def copy_inputs(source, output):
    for raw in git("ls-files", "-z", "--", str(source.relative_to(ROOT))).split(b"\0"):
        if not raw:
            continue
        path = ROOT / raw.decode()
        rel = path.relative_to(source)
        if rel.parts[0] not in {"0", "constant", "system", "geometry", "postprocessing"}:
            continue
        if rel.parts[:2] == ("constant", "polyMesh"):
            continue
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", nargs="?")
    p.add_argument("--list", action="store_true")
    p.add_argument("--variant")
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    catalog = {c["id"]: c for c in json.loads((ROOT / "cases/catalog.json").read_text())}
    if a.list:
        for c in catalog.values():
            print(c["id"], c["group"], ",".join(c["variants"]) or "-")
        return
    if a.case not in catalog:
        p.error("Elegir un caso del catálogo (--list).")
    c = catalog[a.case]
    if c["group"] not in {"essential", "extended", "visual_cases"}:
        p.error("Consultar el README del caso auxiliar, experimental o heredado.")
    if a.variant and a.variant not in c["variants"]:
        p.error("Variante no disponible.")
    source = ROOT / c["path"]
    out = (a.output or ROOT / "runs" / a.case / datetime.now().strftime("%Y%m%d_%H%M%S_%f")).resolve()
    if out.is_relative_to(source.resolve()):
        p.error("La salida debe estar fuera del caso original.")
    out.mkdir(parents=True, exist_ok=False)
    try:
        copy_inputs(source, out)
        if a.variant:
            copy_inputs(source / "variants" / a.variant, out)
        for name in ("controlDict", "fvSchemes", "fvSolution"):
            if not (out / "system" / name).is_file():
                raise FileNotFoundError(out / "system" / name)
        method = "block"
        if a.case.startswith("13b-"):
            method = "snappy"
            subprocess.run([sys.executable, str(ROOT / "scripts/preparar_stl.py"),
                            "--radius", "0.5", "--output",
                            str(out / "constant/triSurface/sphere.stl")], check=True, cwd=out)
        elif a.case == "cow-flow":
            method = "gmsh-cow"
            shutil.copy2(ROOT / "meshes/cow_tunnel.msh", out / "cow_tunnel.msh")
        elif a.case == "kangaroo-flow":
            method = "gmsh-kangaroo"
            subprocess.run([sys.executable, "geometry/build_mesh.py"], check=True, cwd=out)
        shutil.copy2(ROOT / "scripts/run_prepared_case.sh", out / "Allrun")
        (out / "Allrun").chmod(0o755)
        (out / ".mesh_method").write_text(method + "\n")
        (out / "case.json").write_text(json.dumps({
            "case": a.case, "variant": a.variant or "base", "source": c["path"],
            "source_commit": git("rev-parse", "HEAD").decode().strip(),
            "status": "prepared-not-executed"}, indent=2) + "\n")
    except Exception:
        shutil.rmtree(out)
        raise
    print(out)


if __name__ == "__main__":
    main()
