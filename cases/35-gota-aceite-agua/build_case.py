#!/usr/bin/env python3
"""Build a separate 2D oil-drop/water/air case from OpenFOAM v2406 damBreak4phase.

Runs inside the OpenFOAM Docker image (source etc/bashrc first).
Never changes the bundled official tutorial.
"""
from pathlib import Path
import re
import shutil
import os
import sys

root = Path(__file__).resolve().parent
tutorials = Path(os.environ["FOAM_TUTORIALS"])
source = tutorials / "multiphase/multiphaseInterFoam/laminar/damBreak4phase"
if not source.is_dir():
    sys.exit(f"No existe {source}; buscar el equivalente v2406 en $FOAM_TUTORIALS.")
target = root / "case"
if target.exists():
    sys.exit(f"{target} ya existe. No se sobreescribe.")
shutil.copytree(source, target)
if not (target / "0").exists() and (target / "0.orig").exists():
    shutil.copytree(target / "0.orig", target / "0")
for name in ("water", "oil", "air"):
    if not (target / "0" / f"alpha.{name}").exists():
        sys.exit(f"Falta 0/alpha.{name} en el caso oficial.")
# Remove mercury as a physical phase, not merely as a field.
props = target / "constant/transportProperties"
data = props.read_text()
phase_block = re.search(r"\bphases\s*\([\s\S]*?\)\s*;", data)
if not phase_block:
    sys.exit("Formato de phases desconocido; revisar transportProperties.")
replacement = """phases
(
    water
    {
        transportModel Newtonian;
        nu [0 2 -1 0 0 0 0] 1.002e-06;
        rho [1 -3 0 0 0 0 0] 998;
    }
    oil
    {
        transportModel Newtonian;
        nu [0 2 -1 0 0 0 0] 5.56e-05;
        rho [1 -3 0 0 0 0 0] 900;
    }
    air
    {
        transportModel Newtonian;
        nu [0 2 -1 0 0 0 0] 1.5e-05;
        rho [1 -3 0 0 0 0 0] 1.2;
    }
);"""
data = data[:phase_block.start()] + replacement + data[phase_block.end():]
sigma_block = re.search(r"\bsigmas\s*\([\s\S]*?\)\s*;", data)
if not sigma_block:
    sys.exit("Formato de sigmas desconocido.")
data = data[:sigma_block.start()] + """sigmas
(
    (air water) 0.072
    (air oil) 0.030
    (water oil) 0.025
);""" + data[sigma_block.end():]
props.write_text(data)
for old in list((target / "0").glob("alpha.mercury")):
    old.unlink()
# Initial alpha fields: start with air everywhere. setFields then fills water and oil.
for phase in ("water", "oil", "air"):
    field = target / "0" / f"alpha.{phase}"
    data = field.read_text()
    data, count = re.subn(r"\binternalField\s+[^;]+;", f"internalField uniform {1 if phase == 'air' else 0};", data, count=1)
    if count != 1:
        sys.exit(f"No se pudo ajustar internalField en {field}")
    field.write_text(data)
# 2D rectangular domain, 30 x 30 mm, one cell thick.
mesh = target / "system/blockMeshDict"
mesh.write_text("""FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object blockMeshDict;
}
convertToMeters 1;
vertices
(
    (0 0 0) (0.03 0 0) (0.03 0.03 0) (0 0.03 0)
    (0 0 0.0002) (0.03 0 0.0002) (0.03 0.03 0.0002) (0 0.03 0.0002)
);
blocks (hex (0 1 2 3 4 5 6 7) (150 150 1) simpleGrading (1 1 1));
edges ();
boundary
(
    walls { type wall; faces ((0 4 5 1) (1 5 6 2) (3 2 6 7)); }
    atmosphere { type patch; faces ((0 3 7 4)); }
    frontAndBack { type empty; faces ((0 1 2 3) (4 7 6 5)); }
);
mergePatchPairs ();
""")
# Keep original alpha BC semantics but rename patch entries when necessary.
# A case with incompatible boundary names must fail at checkMesh/solver; never silently accept it.
setfields = target / "system/setFieldsDict"
setfields.write_text("""FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object setFieldsDict;
}
defaultFieldValues
(
    volScalarFieldValue alpha.water 0
    volScalarFieldValue alpha.oil 0
    volScalarFieldValue alpha.air 1
);
regions
(
    boxToCell
    {
        box (0 0 0) (0.03 0.015 0.0002);
        fieldValues
        (
            volScalarFieldValue alpha.water 1
            volScalarFieldValue alpha.oil 0
            volScalarFieldValue alpha.air 0
        );
    }
    sphereToCell
    {
        centre (0.015 0.020 0.0001);
        radius 0.002;
        fieldValues
        (
            volScalarFieldValue alpha.water 0
            volScalarFieldValue alpha.oil 1
            volScalarFieldValue alpha.air 0
        );
    }
);
""")
ctrl = target / "system/controlDict"
data = ctrl.read_text()
for key, value in {
    "application": "multiphaseInterFoam",
    "startFrom": "startTime",
    "startTime": "0",
    "endTime": "0.15",
    "deltaT": "1e-6",
    "writeControl": "adjustableRunTime",
    "writeInterval": "0.002",
    "adjustTimeStep": "yes",
    "maxCo": "0.2",
    "maxAlphaCo": "0.2",
    "maxDeltaT": "1e-4",
}.items():
    pattern = rf"(?m)^\s*{key}\s+[^;]+;"
    if re.search(pattern, data):
        data = re.sub(pattern, f"{key} {value};", data, count=1)
    else:
        data += f"\n{key} {value};\n"
ctrl.write_text(data)

# Replace boundaryField consistently for the new mesh patches.
# Keep the original field header, dimensions and initial values.
def replace_boundary(text, replacement):
    start = re.search(r"\bboundaryField\s*\{", text)
    if not start:
        raise RuntimeError("Falta boundaryField en campo de origen.")
    opening = text.index("{", start.start())
    depth = 0
    end = None
    for i in range(opening, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError("boundaryField sin cierre.")
    return text[:start.start()] + "boundaryField\n{\n" + replacement + "\n}\n" + text[end:]

for field in (target / "0").iterdir():
    if not field.is_file():
        continue
    if field.name == "U":
        patches = """
    walls { type noSlip; }
    atmosphere { type pressureInletOutletVelocity; value uniform (0 0 0); }
    frontAndBack { type empty; }
"""
    elif field.name == "p_rgh":
        patches = """
    walls { type fixedFluxPressure; value uniform 0; }
    atmosphere { type totalPressure; p0 uniform 0; U U; phi phi; rho rho; psi none; gamma 1; value uniform 0; }
    frontAndBack { type empty; }
"""
    elif field.name.startswith("alpha."):
        patches = """
    walls { type zeroGradient; }
    atmosphere { type inletOutlet; inletValue uniform 0; value uniform 0; }
    frontAndBack { type empty; }
"""
        if field.name == "alpha.air":
            patches = patches.replace("inletValue uniform 0", "inletValue uniform 1")
    elif field.name == "p":
        patches = """
    walls { type zeroGradient; }
    atmosphere { type fixedValue; value uniform 0; }
    frontAndBack { type empty; }
"""
    else:
        continue
    field.write_text(replace_boundary(field.read_text(), patches))

print(f"Preparado: {target}. Revisar condiciones de contorno antes de ejecutar.")
