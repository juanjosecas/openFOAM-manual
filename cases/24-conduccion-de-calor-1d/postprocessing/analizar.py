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

if "T" not in mesh.cell_data: raise RuntimeError("Falta campo T en cell_data")
xs = x[np.argsort(x)]
ts = np.asarray(mesh.cell_data["T"])[np.argsort(x)]
ref = 400-100*xs/.02
with (out/"temperatura.csv").open("w",newline="") as f:
    w = csv.writer(f); w.writerow(["x_m","T_K","T_lineal_K","diferencia_K"])
    w.writerows(zip(xs,ts,ref,ts-ref))
plt.plot(xs,ts,"o",label="OpenFOAM"); plt.plot(xs,ref,"-",label="Referencia lineal")
plt.xlabel("x [m]"); plt.ylabel("T [K]"); plt.grid(True); plt.legend()
plt.tight_layout(); plt.savefig(out/"temperatura.png",dpi=150)
print("Error maximo centros [K]:",np.max(np.abs(ts-ref)))
