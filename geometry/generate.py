#!/usr/bin/env python3
"""Canal plano con obstáculos internos y fronteras configurables."""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import tomllib

import gmsh


def positive(value, name):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} debe ser positivo y finito")
    return value


def name_of(value):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        raise ValueError(f"Nombre de patch inválido: {value}")
    return value


def make_geometry(config):
    """Construir la cara plana y guardar la clasificación de sus aristas."""
    domain = config["domain"]
    L, H, T = (positive(domain[k], k) for k in ("length", "height", "thickness"))
    size = positive(config["mesh"]["size"], "mesh.size")
    tol = max(L, H, T)*1e-7
    if min(L, H, T) <= 100*tol:
        raise ValueError("Dimensiones demasiado dispares para esta tolerancia geométrica")
    occ = gmsh.model.occ
    sides = {"bottom": L, "right": H, "top": L, "left": H}
    # Coordenada de un segmento: x en top/bottom; y en left/right.
    segments = {side: [] for side in sides}
    patches = {"walls": "wall", "frontAndBack": "empty"}
    for port in config.get("ports", []):
        name = name_of(port["name"])
        side = port["side"]
        if side not in sides or name in patches:
            raise ValueError(f"Puerto inválido o repetido: {name}")
        kind = port["kind"]
        if kind not in ("inlet", "outlet", "opening"):
            raise ValueError(f"Tipo de puerto inválido: {kind}")
        start, end = float(port.get("start", 0)), float(port.get("end", sides[side]))
        if not (0 <= start < end <= sides[side]) or end-start <= 100*tol:
            raise ValueError(f"Intervalo inválido de {name}: {start}, {end}")
        segments[side].append((start, end, name))
        patches[name] = "patch"
    for side, intervals in segments.items():
        intervals.sort()
        for a, b in zip(intervals, intervals[1:]):
            if a[1] > b[0]:
                raise ValueError(f"Puertos superpuestos en {side}")
    if not any(p["kind"] == "inlet" for p in config.get("ports", [])):
        raise ValueError("Definir al menos una entrada")
    if not any(p["kind"] in ("outlet", "opening") for p in config["ports"]):
        raise ValueError("Definir al menos una salida o abertura")

    def xy(side, s):
        return {"bottom": (s, 0), "top": (s, H),
                "left": (0, s), "right": (L, s)}[side]

    # Segmentar primero el perímetro: así los puertos son aristas CAD reales.
    outer = []
    for side, limit in sides.items():
        cuts = sorted({0., limit, *(v for a, b, _ in segments[side] for v in (a, b))})
        if min(b-a for a, b in zip(cuts, cuts[1:])) <= 100*tol:
            raise ValueError(f"Segmentos demasiado pequeños en {side}")
        if side in ("top", "left"):
            cuts.reverse()
        outer.extend(xy(side, s) for s in cuts[:-1])
    points = [occ.addPoint(x, y, 0) for x, y in outer]
    edges = [occ.addLine(p, points[(i+1) % len(points)]) for i, p in enumerate(points)]
    surface = occ.addPlaneSurface([occ.addCurveLoop(edges)])

    # Obstáculos estrictamente interiores y separados en esta primera versión.
    objects = []
    for obj in config.get("obstacles", []):
        name = name_of(obj["name"])
        if name in patches:
            raise ValueError(f"Nombre repetido: {name}")
        x, y = map(float, obj["center"])
        angle = math.radians(float(obj.get("rotation", 0)))
        if not all(map(math.isfinite, (x, y, angle))):
            raise ValueError(f"Posición o rotación inválida: {name}")
        shape = obj["shape"]
        if shape == "circle":
            r = positive(obj["radius"], name)
            tag = occ.addDisk(x, y, 0, r, r)
        elif shape == "ellipse":
            rx = positive(obj["radius_x"], name)
            ry = positive(obj["radius_y"], name)
            # OCC exige el semieje mayor primero.
            tag = occ.addDisk(x, y, 0, max(rx, ry), min(rx, ry))
            if ry > rx:
                angle += math.pi/2
        elif shape == "rectangle":
            w = positive(obj["width"], name)
            h = positive(obj["height"], name)
            tag = occ.addRectangle(x-w/2, y-h/2, 0, w, h)
        else:
            raise ValueError(f"Forma no admitida: {shape}")
        if angle:
            occ.rotate([(2, tag)], x, y, 0, 0, 0, 1, angle)
        occ.synchronize()
        xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(2, tag)
        if not (xmin > 100*tol and ymin > 100*tol and xmax < L-100*tol and ymax < H-100*tol):
            raise ValueError(f"{name} debe quedar completamente dentro del canal")
        area = occ.getMass(2, tag)
        for other in objects:
            if occ.getDistance(2, tag, 2, other["tag"])[0] <= 100*tol:
                raise ValueError(f"Obstáculos superpuestos o en contacto: {name}, {other['name']}")
        refinement = obj.get("refinement", {})
        local = positive(refinement.get("size", size), name+".size")
        distance = positive(refinement.get("distance", 3*size), name+".distance")
        if local > size:
            raise ValueError(f"Refinamiento de {name} debe ser <= mesh.size")
        objects.append(dict(name=name, tag=tag, area=area, size=local, distance=distance))
        patches[name] = "wall"

    # Identificar las aristas del obstáculo por la distancia a su superficie CAD,
    # guardando los sólidos originales hasta después de clasificar el corte.
    if objects:
        result, _ = occ.cut([(2, surface)], [(2, o["tag"]) for o in objects],
                            removeObject=True, removeTool=False)
        if len(result) != 1 or result[0][0] != 2:
            raise ValueError("El dominio fluido debe ser una única región")
        surface = result[0][1]
    occ.synchronize()
    expected = L*H-sum(o["area"] for o in objects)
    if not math.isclose(occ.getMass(2, surface), expected, rel_tol=1e-7, abs_tol=tol**2):
        raise ValueError("El área del corte no coincide con el dominio esperado")

    groups = {name: [] for name in patches if name != "frontAndBack"}
    for _, edge in gmsh.model.getBoundary([(2, surface)], oriented=False):
        x0, y0, _, x1, y1, _ = gmsh.model.getBoundingBox(1, edge)
        x, y, _ = occ.getCenterOfMass(1, edge)
        side = next((s for s, hit in (
            ("bottom", max(abs(y0), abs(y1)) < 100*tol),
            ("top", max(abs(y0-H), abs(y1-H)) < 100*tol),
            ("left", max(abs(x0), abs(x1)) < 100*tol),
            ("right", max(abs(x0-L), abs(x1-L)) < 100*tol)) if hit), None)
        if side:
            coord = x if side in ("bottom", "top") else y
            lo, hi = (x0, x1) if side in ("bottom", "top") else (y0, y1)
            matches = [n for a, b, n in segments[side] if a < coord < b]
            name = matches[0] if matches else "walls"
            if matches:
                a, b, _ = next(v for v in segments[side] if v[2] == name)
                if lo < a-100*tol or hi > b+100*tol:
                    raise ValueError(f"El corte CAD no preservó el segmento de {name}")
            elif any(min(hi,b)-max(lo,a) > 100*tol for a,b,_ in segments[side]):
                raise ValueError("El perímetro no conservó los segmentos de los puertos")
        else:
            matches = [o["name"] for o in objects
                       if occ.getDistance(1, edge, 2, o["tag"])[0] < 100*tol]
            if len(matches) != 1:
                raise ValueError("No se pudo asignar una arista a un obstáculo")
            name = matches[0]
        groups[name].append(edge)

    for name, curves in groups.items():
        if not curves and name != "walls":
            raise ValueError(f"Patch sin aristas: {name}")
    for side, intervals in segments.items():
        for a, b, name in intervals:
            if not math.isclose(sum(occ.getMass(1, edge) for edge in groups[name]),
                                b-a, rel_tol=1e-6, abs_tol=100*tol):
                raise ValueError(f"Longitud incorrecta del puerto {name}")
    # Retirar únicamente las entidades auxiliares no compartidas con el fluido.
    if objects:
        occ.remove([(2, o["tag"]) for o in objects], recursive=True)
        occ.synchronize()

    # Extrusión de una capa: prismas, no tetraedros, para frontAndBack empty.
    out = occ.extrude([(2, surface)], 0, 0, T, numElements=[1], recombine=True)
    occ.synchronize()
    volumes = [tag for dim, tag in out if dim == 3]
    if len(volumes) != 1:
        raise ValueError("La extrusión no produjo un volumen único")
    faces = [tag for dim, tag in gmsh.model.getBoundary([(3, volumes[0])], oriented=False)]
    physical = {name: [] for name in patches}
    edge_patch = {edge: name for name, curves in groups.items() for edge in curves}
    for face in faces:
        if face == surface:
            physical["frontAndBack"].append(face)
            continue
        boundary = [tag for dim, tag in gmsh.model.getBoundary([(2, face)], oriented=False)]
        names = {edge_patch[e] for e in boundary if e in edge_patch}
        if not names:
            _, _, z0, _, _, z1 = gmsh.model.getBoundingBox(2, face)
            if max(abs(z0-T), abs(z1-T)) < 100*tol:
                physical["frontAndBack"].append(face)
                continue
        if len(names) != 1:
            raise ValueError(f"Cara lateral sin patch inequívoco: {face}")
        physical[names.pop()].append(face)
    if len(physical["frontAndBack"]) != 2:
        raise ValueError("Se esperaban dos caras planas frontAndBack")
    for name, faces in physical.items():
        if not faces:
            if name == "walls":
                continue
            raise ValueError(f"Patch sin caras: {name}")
        gmsh.model.addPhysicalGroup(2, faces, name=name)
    gmsh.model.addPhysicalGroup(3, volumes, name="fluid")

    gmsh.option.setNumber("Mesh.MeshSizeMax", size)
    gmsh.option.setNumber("Mesh.MeshSizeMin", min([size]+[o["size"] for o in objects]))
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    fields = gmsh.model.mesh.field
    thresholds = []
    for obj in objects:
        if obj["size"] == size:
            continue
        d = fields.add("Distance")
        fields.setNumbers(d, "CurvesList", groups[obj["name"]])
        fields.setNumber(d, "Sampling", 200)
        threshold = fields.add("Threshold")
        for key, value in (("InField", d), ("SizeMin", obj["size"]),
                           ("SizeMax", size), ("DistMin", 0), ("DistMax", obj["distance"])):
            fields.setNumber(threshold, key, value)
        thresholds.append(threshold)
    if thresholds:
        field = fields.add("Min")
        fields.setNumbers(field, "FieldsList", thresholds)
        fields.setAsBackgroundMesh(field)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.option.setNumber("Mesh.Binary", 0)
    gmsh.option.setNumber("Mesh.ElementOrder", 1)
    return {name: patches[name] for name, faces in physical.items() if faces}


def write_patch_dictionary(output, patches):
    lines = ["FoamFile", "{", "    version 2.0;", "    format ascii;",
             "    class dictionary;", "    object changeDictionaryDict;", "}",
             "dictionaryReplacement", "{", "    boundary", "    {"]
    for name, kind in patches.items():
        lines.append(f"        {name} {{ type {kind}; }}")
    lines.extend(["    }", "}", ""])
    (output/"changeDictionaryDict").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--show", action="store_true", help="Abrir la malla en Gmsh")
    args = parser.parse_args()
    config = tomllib.loads(args.config.read_text())
    if args.output.exists():
        parser.error("El directorio de salida ya existe")
    gmsh.initialize()
    try:
        gmsh.model.add("channel")
        patches = make_geometry(config)
        gmsh.model.mesh.generate(3)
        # Solo prismas o hexaedros lineales, una capa de extrusión.
        types, tags, _ = gmsh.model.mesh.getElements(3)
        if not len(types) or set(types)-{5, 6}:
            raise ValueError(f"Elementos de volumen no admitidos: {list(types)}")
        args.output.mkdir(parents=True)
        gmsh.write(str(args.output/"channel.msh"))
        write_patch_dictionary(args.output, patches)
        shutil.copyfile(args.config, args.output/"geometry.toml")
        (args.output/"patches.json").write_text(json.dumps({
            "patches": patches, "ports": config["ports"],
            "cells": sum(len(t) for t in tags)}, indent=2)+"\n")
        print(f"Malla: {args.output/'channel.msh'}")
        if args.show:
            gmsh.fltk.run()
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    main()
