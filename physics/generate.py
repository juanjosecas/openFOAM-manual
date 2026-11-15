#!/usr/bin/env python3
"""Crear un caso laminar newtoniano o pseudoplástico a partir de una malla del generador 2D.

Solo biblioteca estándar. No requiere Gmsh, Docker ni OpenFOAM para escribir
los diccionarios. La importación y resolución son pasos independientes.
"""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import tomllib


def number(value, label, positive=False):
    value = float(value)
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError(f"Valor inválido: {label}")
    return value


def vec(value, label):
    if len(value) != 3:
        raise ValueError(f"{label}: se necesitan tres componentes")
    v = [number(x, label) for x in value]
    if v[2] != 0:
        raise ValueError(f"{label}: la componente z debe ser cero en 2D")
    return v


def fmt(value):
    return format(value, ".12g")


def vector(v):
    return "(" + " ".join(map(fmt, v)) + ")"


def header(name, kind="dictionary"):
    return f"FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {kind};\n    object {name};\n}}\n\n"


def field(name, kind, dimensions, initial, boundaries):
    result = header(name, kind)
    result += f"dimensions {dimensions};\ninternalField uniform {initial};\n\nboundaryField\n{{\n"
    for patch, entries in boundaries.items():
        result += f"    {patch}\n    {{\n"
        result += "".join(f"        {entry};\n" for entry in entries)
        result += "    }\n"
    return result + "}\n"


def boundaries(metadata, config):
    patches = metadata["patches"]
    ports = {p["name"]: p for p in metadata["ports"]}
    settings = config.get("boundaries", {})
    if set(settings) - set(patches):
        raise ValueError(f"Patches inexistentes: {sorted(set(settings)-set(patches))}")
    if patches.get("frontAndBack") != "empty":
        raise ValueError("Se necesita frontAndBack de tipo empty")
    u, p = {}, {}
    pressure_reference = False
    inward = {"left": (1, 0, 0), "right": (-1, 0, 0),
              "top": (0, -1, 0), "bottom": (0, 1, 0)}
    for name, mesh_type in patches.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
            raise ValueError(f"Nombre de patch inválido: {name}")
        spec = settings.get(name, {})
        if mesh_type == "empty":
            if spec:
                raise ValueError(f"{name} es empty; no admite una condición física")
            u[name] = p[name] = ["type empty"]
        elif mesh_type == "wall":
            kind = spec.get("type", "noSlip")
            if kind not in ("noSlip", "slip"):
                raise ValueError(f"{name}: pared debe usar noSlip o slip")
            if set(spec) - {"type"}:
                raise ValueError(f"{name}: parámetros de pared no admitidos")
            u[name] = [f"type {kind}"]
            p[name] = ["type zeroGradient"]
        elif mesh_type == "patch":
            if name not in ports:
                raise ValueError(f"Puerto no identificado: {name}")
            if "type" not in spec:
                raise ValueError(f"Definir [boundaries.{name}] en physics.toml")
            kind = spec["type"]
            if kind == "velocity":
                if set(spec) - {"type", "speed", "velocity"}:
                    raise ValueError(f"{name}: parámetros de entrada no admitidos")
                if ("speed" in spec) == ("velocity" in spec):
                    raise ValueError(f"{name}: usar speed o velocity, exclusivamente")
                normal = inward[ports[name]["side"]]
                if "speed" in spec:
                    speed = number(spec["speed"], name+".speed", True)
                    v = [speed*x for x in normal]
                else:
                    v = vec(spec["velocity"], name+".velocity")
                    if sum(a*b for a,b in zip(v, normal)) <= 0:
                        raise ValueError(f"{name}: la velocidad debe apuntar hacia el dominio")
                u[name] = ["type fixedValue", f"value uniform {vector(v)}"]
                p[name] = ["type zeroGradient"]
            elif kind == "flow_rate":
                if set(spec) - {"type", "volumetric_flow_rate", "mass_flow_rate"}:
                    raise ValueError(f"{name}: parámetros de caudal no admitidos")
                if ("volumetric_flow_rate" in spec) == ("mass_flow_rate" in spec):
                    raise ValueError(f"{name}: elegir caudal volumétrico o másico")
                if "volumetric_flow_rate" in spec:
                    q = number(spec["volumetric_flow_rate"], name+".Q", True)
                else:
                    q = number(spec["mass_flow_rate"], name+".mass", True)/number(
                        config["fluid"]["rho"], "rho", True)
                u[name] = ["type flowRateInletVelocity",
                           f"volumetricFlowRate {fmt(q)}",
                           "extrapolateProfile false", "value uniform (0 0 0)"]
                p[name] = ["type zeroGradient"]
            elif kind == "velocity_table":
                if set(spec) - {"type", "table"}:
                    raise ValueError(f"{name}: parámetros de tabla no admitidos")
                if config["simulation"]["mode"] != "transient":
                    raise ValueError(f"{name}: la tabla requiere transient")
                normal = inward[ports[name]["side"]]
                rows = []
                for time, speed in spec["table"]:
                    t = number(time, name+".time")
                    speed = number(speed, name+".speed")
                    if t < 0 or speed < 0 or (rows and t <= rows[-1][0]):
                        raise ValueError(f"{name}: tiempos crecientes y velocidades no negativas")
                    rows.append((t, [speed*x for x in normal]))
                if len(rows) < 2 or rows[0][0] != 0 or rows[-1][0] < config["simulation"]["end"]:
                    raise ValueError(f"{name}: la tabla debe cubrir todo el intervalo desde t=0")
                table = "table (\n" + "".join(
                    f"            ({fmt(t)} {vector(v)})\n" for t, v in rows) + "        )"
                u[name] = ["type uniformFixedValue", "uniformValue " + table,
                           f"value uniform {vector(rows[0][1])}"]
                p[name] = ["type zeroGradient"]
            elif kind == "pressure":
                if set(spec) - {"type", "pressure_pa"}:
                    raise ValueError(f"{name}: parámetros de presión no admitidos")
                rho = number(config["fluid"]["rho"], "rho", True)
                value = number(spec["pressure_pa"], name+".pressure_pa")/rho
                u[name] = ["type pressureInletOutletVelocity", "value uniform (0 0 0)"]
                p[name] = ["type fixedValue", f"value uniform {fmt(value)}"]
                pressure_reference = True
            else:
                raise ValueError(f"{name}: usar velocity, velocity_table, flow_rate o pressure")
        else:
            raise ValueError(f"Tipo de patch no admitido: {mesh_type}")
    if not pressure_reference:
        raise ValueError("Definir al menos un puerto con presión fija")
    return u, p


def dictionaries(metadata, config):
    fluid = config["fluid"]
    rho = number(fluid["rho"], "rho [kg/m3]", True)
    if ("nu" in fluid) == ("mu" in fluid):
        raise ValueError("Definir nu [m2/s] o mu [Pa s], exclusivamente")
    nu = (number(fluid["nu"], "nu", True) if "nu" in fluid else
          number(fluid["mu"], "mu", True)/rho)
    model = fluid.get("model", "newtonian")
    if model == "newtonian":
        if "power_law" in fluid:
            raise ValueError("power_law requiere fluid.model = power_law")
        laminar = "laminar { model Stokes; }\n"
    elif model == "power_law":
        law = fluid["power_law"]
        k = number(law["k"], "k", True)
        n = number(law["n"], "n", True)
        low = number(law["nu_min"], "nu_min", True)
        high = number(law["nu_max"], "nu_max", True)
        if low > high:
            raise ValueError("nu_min no puede superar nu_max")
        laminar = f"""laminar
{{
    model generalizedNewtonian;
    viscosityModel powerLaw;
    k {fmt(k)};
    n {fmt(n)};
    nuMin {fmt(low)};
    nuMax {fmt(high)};
}}
"""
    else:
        raise ValueError("fluid.model debe ser newtonian o power_law")
    run = config["simulation"]
    mode = run["mode"]
    if mode not in ("steady", "transient"):
        raise ValueError("simulation.mode debe ser steady o transient")
    steady = mode == "steady"
    solver = "simpleFoam" if steady else "pimpleFoam"
    end = number(run["end"], "simulation.end", True)
    interval = number(run["write_interval"], "write_interval", True)
    if steady and (not end.is_integer() or not interval.is_integer()):
        raise ValueError("En steady, end y write_interval son números enteros de iteraciones")
    dt = 1 if steady else number(run["delta_t"], "delta_t", True)
    max_co = None if steady else number(run.get("max_co", 0.5), "max_co", True)
    max_dt = None if steady else number(run.get("max_delta_t", dt), "max_delta_t", True)
    if not steady and dt > max_dt:
        raise ValueError("delta_t no puede superar max_delta_t")
    initial = config.get("initial", {})
    velocity = vec(initial.get("velocity", [0, 0, 0]), "initial.velocity")
    pressure = number(initial.get("pressure_pa", 0), "initial.pressure_pa")/rho
    u, p = boundaries(metadata, config)
    files = {
        "0/U": field("U", "volVectorField", "[0 1 -1 0 0 0 0]", vector(velocity), u),
        "0/p": field("p", "volScalarField", "[0 2 -2 0 0 0 0]", fmt(pressure), p),
        "constant/transportProperties": header("transportProperties") +
            f"transportModel Newtonian;\nnu [0 2 -1 0 0 0 0] {fmt(nu)};\n",
        "constant/turbulenceProperties": header("turbulenceProperties") +
            "simulationType laminar;\n" + laminar,
    }
    control = header("controlDict") + f"""application {solver};
startFrom startTime;
startTime 0;
stopAt endTime;
endTime {fmt(end)};
deltaT {fmt(dt)};
writeControl {"timeStep" if steady else "adjustableRunTime"};
writeInterval {fmt(interval)};
purgeWrite 0;
writeFormat ascii;
writePrecision 10;
writeCompression off;
timeFormat general;
timePrecision 10;
runTimeModifiable true;
"""
    if not steady:
        control += f"adjustTimeStep yes;\nmaxCo {fmt(max_co)};\nmaxDeltaT {fmt(max_dt)};\n"
    files["system/controlDict"] = control
    files["system/fvSchemes"] = header("fvSchemes") + f"""
ddtSchemes {{ default {"steadyState" if steady else "Euler"}; }}
gradSchemes {{ default Gauss linear; }}
divSchemes
{{
    default none;
    div(phi,U) Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}}
laplacianSchemes {{ default Gauss linear corrected; }}
interpolationSchemes {{ default linear; }}
snGradSchemes {{ default corrected; }}
wallDist {{ method meshWave; }}
"""
    solution = header("fvSolution") + """
solvers
{
    p
    {
        solver GAMG;
        tolerance 1e-8;
        relTol 0.01;
        smoother GaussSeidel;
    }
    U
    {
        solver smoothSolver;
        smoother symGaussSeidel;
        tolerance 1e-8;
        relTol 0.1;
    }
    pFinal { $p; relTol 0; }
    UFinal { $U; relTol 0; }
}
"""
    if steady:
        solution += """
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl { p 1e-6; U 1e-7; }
}
relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; }
}
"""
    else:
        solution += """
PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors 2;
    nNonOrthogonalCorrectors 1;
}
"""
    files["system/fvSolution"] = solution
    return files, solver, rho, nu


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("config", type=Path)
    p.add_argument("--geometry", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error("La salida ya existe; utilizar una carpeta nueva")
    geometry = a.geometry.resolve()
    config = tomllib.loads(a.config.read_text())
    metadata = json.loads((geometry/"patches.json").read_text())
    for name in ("channel.msh", "changeDictionaryDict", "geometry.toml"):
        if not (geometry/name).is_file():
            p.error(f"Falta {geometry/name}")
    files, solver, rho, nu = dictionaries(metadata, config)
    a.output.mkdir(parents=True)
    for name, contents in files.items():
        path = a.output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    shutil.copyfile(geometry/"channel.msh", a.output/"channel.msh")
    shutil.copyfile(geometry/"changeDictionaryDict", a.output/"system/changeDictionaryDict")
    for name in ("geometry.toml", "patches.json"):
        shutil.copyfile(geometry/name, a.output/name)
    shutil.copyfile(a.config, a.output/"physics.toml")
    # Reutilizar el lanzador compartido; no añadir otra capa de ejecución.
    scripts = Path(__file__).resolve().parents[1]/"scripts"
    shutil.copyfile(scripts/"run_prepared_case.sh", a.output/"Allrun")
    shutil.copyfile(scripts/"clean_case.sh", a.output/"Allclean")
    for name in ("Allrun", "Allclean"):
        (a.output/name).chmod(0o755)
    (a.output/".mesh_method").write_text("gmsh-channel\n")
    (a.output/"case.json").write_text(json.dumps({
        "solver": solver, "rho_kg_m3": rho, "nu_m2_s": nu,
        "fluid_model": config["fluid"].get("model", "newtonian"),
        "nu_is_base_value": config["fluid"].get("model") == "power_law",
        "status": "prepared-not-executed"}, indent=2)+"\n")
    print(f"Caso preparado: {a.output} ({solver}, nu={nu:g} m2/s)")


if __name__ == "__main__":
    main()
