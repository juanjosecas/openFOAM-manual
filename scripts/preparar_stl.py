#!/usr/bin/env python3
"""Crear STL de esfera en metros o reescalar un STL existente (PyVista).

El STL no codifica unidades. La escala se aplica a las coordenadas.
"""
import argparse
from pathlib import Path
import numpy as np
import pyvista as pv

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, help="STL propio de entrada")
parser.add_argument("--output", type=Path, default=Path("constant/triSurface/sphere.stl"))
parser.add_argument("--units", choices=["m", "mm", "cm"], default="m",
                    help="Unidad asumida en las coordenadas del STL de entrada")
parser.add_argument("--radius", type=float, default=0.5,
                    help="Radio de la esfera de demostración en metros")
args = parser.parse_args()
if args.input is None:
    if args.radius <= 0:
        parser.error("--radius debe ser > 0")
    surface = pv.Sphere(radius=args.radius, theta_resolution=48, phi_resolution=48)
else:
    if not args.input.is_file():
        parser.error(f"No existe el STL: {args.input}")
    surface = pv.read(args.input).extract_surface().triangulate()
    factor = {"m": 1.0, "cm": 1e-2, "mm": 1e-3}[args.units]
    surface.points = np.asarray(surface.points) * factor
if surface.n_cells == 0:
    parser.error("La superficie no contiene triángulos")
args.output.parent.mkdir(parents=True, exist_ok=True)
surface.save(args.output, binary=True)
print(f"STL exportado: {args.output}")
print(f"Extensiones en metros: {surface.bounds}")
print(f"Superficie cerrada (sin bordes abiertos): {surface.n_open_edges == 0}")
