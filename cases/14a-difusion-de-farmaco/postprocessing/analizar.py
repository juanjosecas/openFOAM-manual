#!/usr/bin/env python3
"""CSV, curvas, error analítico y GIF de T=C/C0; ejecutar desde cualquier cwd.

Requiere: pip install pyvista matplotlib numpy imageio
No inicia simulaciones; lee archivos de resultados OpenFOAM existentes.
"""
from pathlib import Path
import csv
import math
import sys
import numpy as np
try:
    import pyvista as pv
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import imageio.v2 as imageio
except ImportError as exc:
    raise SystemExit("Instalar: python -m pip install pyvista matplotlib numpy imageio") from exc

ROOT = Path(__file__).resolve().parents[1]
D = 1e-9  # Actualizar si se cambia DT en constant/transportProperties.
L = 0.002
OUT = ROOT / "plots"
OUT.mkdir(exist_ok=True)
marker = ROOT / "case.foam"
marker.touch(exist_ok=True)
reader = pv.OpenFOAMReader(str(marker))
reader.enable_all_cell_arrays()
times = [float(t) for t in reader.time_values]
if not times:
    raise SystemExit("No se encontraron tiempos de OpenFOAM.")

def internal_mesh(obj):
    if isinstance(obj, pv.MultiBlock):
        for key in obj.keys():
            if key == "internalMesh":
                candidate = obj[key]
                if isinstance(candidate, pv.MultiBlock):
                    return internal_mesh(candidate)
                return candidate
        for item in obj:
            try:
                return internal_mesh(item)
            except LookupError:
                pass
        raise LookupError("No se encontró internalMesh.")
    if "T" in obj.cell_data:
        return obj
    raise LookupError("No se encontró campo T.")

def erfc_reference(x, time):
    if time <= 0:
        return np.zeros_like(x)
    return np.array([math.erfc(float(v)/(2*math.sqrt(D*time))) for v in x])

frames=[]
with (OUT / "perfiles.csv").open("w", newline="") as fh:
    writer=csv.writer(fh)
    writer.writerow(["time_s","x_m","C_over_C0","erfc_semifinita"])
    for time in times:
        if time <= 0:  # Evitar discontinuidad en la frontera en t=0.
            continue
        reader.set_active_time_value(time)
        grid=internal_mesh(reader.read())
        if "T" not in grid.cell_data:
            raise SystemExit("Falta T en los datos de celdas.")
        centers=grid.cell_centers().points[:,0]
        vals=np.asarray(grid.cell_data["T"], dtype=float)
        order=np.argsort(centers)
        x=centers[order]
        c=vals[order]
        ref=erfc_reference(x,time)
        for xx,cc,rr in zip(x,c,ref):
            writer.writerow([time,float(xx),float(cc),float(rr)])
        fig,ax=plt.subplots(figsize=(7,4))
        ax.plot(x*1000,c,label="OpenFOAM")
        ax.plot(x*1000,ref,"--",label="erfc, seminf.")
        ax.set(xlabel="x [mm]",ylabel="C/C0",title=f"t={time:g} s",ylim=(-0.05,1.05),xlim=(0,L*1000))
        ax.legend()
        fig.tight_layout()
        filename=OUT/f"perfil_{time:010.4f}.png"
        fig.savefig(filename,dpi=130)
        fig.canvas.draw()
        rgba=np.asarray(fig.canvas.buffer_rgba()).copy()
        frames.append(rgba[:,:,:3])
        plt.close(fig)
if not frames:
    raise SystemExit("No hay tiempos >0 para graficar.")
imageio.mimsave(OUT/"difusion.gif",frames,duration=0.35,loop=0)
print("Archivos creados en",OUT)
print("Referencia erfc: seminf.; revisar efecto de x=L y valor de DT.")
