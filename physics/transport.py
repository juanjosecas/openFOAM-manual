"""Añadir transporte pasivo de solutos a un caso transitorio generado."""
import re

from generate import number, fmt, field


def add_transport(files, metadata, physics, config):
    if physics["simulation"]["mode"] != "transient":
        raise ValueError("El transporte pasivo requiere modo transient")
    solutes = config["solutes"]
    if not solutes:
        raise ValueError("Definir al menos un soluto")
    patches = metadata["patches"]
    flow = physics["boundaries"]
    control, schemes, solution = [], [], []
    names = set()
    for spec in solutes:
        name = spec["name"]
        if not re.fullmatch(r"C_[A-Za-z0-9_]+", name) or name in names:
            raise ValueError("Nombre de soluto inválido o repetido; usar C_nombre")
        names.add(name)
        diffusivity = number(spec["diffusivity"], name+".D", True)
        initial = number(spec.get("initial", 0), name+".initial")
        values = spec.get("inlets", {})
        if initial < 0 or set(values)-set(patches):
            raise ValueError(f"{name}: concentración inicial o patches inválidos")
        boundaries = {}
        for patch, mesh_type in patches.items():
            if mesh_type == "empty":
                entries = ["type empty"]
            elif mesh_type == "wall":
                entries = ["type zeroGradient"]
            elif flow[patch]["type"] == "pressure":
                value = number(values.get(patch, 0), patch)
                if value < 0:
                    raise ValueError("Concentración negativa")
                entries = ["type inletOutlet", f"inletValue uniform {fmt(value)}",
                           f"value uniform {fmt(value)}"]
            else:
                if patch not in values:
                    raise ValueError(f"{name}: falta concentración de entrada {patch}")
                value = number(values[patch], patch)
                if value < 0:
                    raise ValueError("Concentración negativa")
                entries = ["type fixedValue", f"value uniform {fmt(value)}"]
            if patch in values and mesh_type != "patch":
                raise ValueError(f"{name}: {patch} no es un puerto")
            boundaries[patch] = entries
        files["0/"+name] = field(name, "volScalarField", "[0 0 0 0 0 0 0]",
                                  fmt(initial), boundaries)
        control.append(f"""    transport_{name}
    {{
        type scalarTransport;
        libs (solverFunctionObjects);
        field {name};
        phi phi;
        D {fmt(diffusivity)};
        resetOnStartUp false;
        executeControl timeStep;
        executeInterval 1;
        writeControl writeTime;
    }}
""")
        schemes.append(f"    div(phi,{name}) Gauss upwind;\n")
        solution.append(f"""    {name}
    {{
        solver smoothSolver;
        smoother symGaussSeidel;
        tolerance 1e-9;
        relTol 0;
    }}
""")
    files["system/controlDict"] += "\nfunctions\n{\n"+"".join(control)+"}\n"
    files["system/fvSchemes"] = files["system/fvSchemes"].replace(
        "    div(phi,U) Gauss upwind;\n",
        "    div(phi,U) Gauss upwind;\n"+"".join(schemes), 1)
    files["system/fvSolution"] = files["system/fvSolution"].replace(
        'solvers\n{\n', 'solvers\n{\n'+"".join(solution), 1)
