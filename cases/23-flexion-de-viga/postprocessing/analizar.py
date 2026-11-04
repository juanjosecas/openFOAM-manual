#!/usr/bin/env python3
"""Extrae campo interno de ultimo tiempo; no ejecuta OpenFOAM."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyvista as pv
case = Path(__file__).resolve().parents[1]
marker = case / "case.foam"
marker.touch(exist_ok=True)
reader = pv.OpenFOAMReader(str(marker))
reader.set_active_time_value(max(reader.time_values))
mesh = reader.read()
def internal_mesh(obj, name=""):
    if isinstance(obj, pv.MultiBlock):
        for key in obj.keys():
            found = internal_mesh(obj[key], str(key))
            if found is not None: return found
        return None
    if obj is not None and "internal" in name.lower(): return obj
    return None
mesh = internal_mesh(mesh)
if mesh is None: raise RuntimeError("No se encontro internalMesh; revisar el lector OpenFOAM.")
x = mesh.cell_centers().points[:, 0]
out = case / "plots"
out.mkdir(exist_ok=True)

if "D" not in mesh.cell_data: raise RuntimeError("Falta campo D en cell_data")
dz = np.asarray(mesh.cell_data["D"])[:, 2]
xb = np.round(x, 10)
xs = np.unique(xb)
zs = np.array([np.mean(dz[xb == v]) for v in xs])
L, b, h, E, F = .1, .01, .01, 2e9, -1.
I = b*h**3/12
ref = F*xs**2*(3*L-xs)/(6*E*I)
with (out/"desplazamiento.csv").open("w",newline="") as f:
    w = csv.writer(f); w.writerow(["x_m","Dz_m","EulerBernoulli_m","diferencia_m"])
    w.writerows(zip(xs,zs,ref,zs-ref))
plt.plot(xs,zs*1000,"o",label="OpenFOAM promedio seccion")
plt.plot(xs,ref*1000,"-",label="Euler-Bernoulli")
plt.xlabel("x [m]"); plt.ylabel("Dz [mm]"); plt.grid(True); plt.legend()
plt.tight_layout(); plt.savefig(out/"flexion.png",dpi=150)
print("Punta teorica [m]:",F*L**3/(3*E*I))
