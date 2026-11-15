"""Perfiles adimensionales y presión superficial de una esfera en flujo +x."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv

from fields import open_reader, internal_mesh


def face_data(patch, field):
    if field not in patch.cell_data:
        raise KeyError(f"Falta {field} en las caras del patch")
    values = np.asarray(patch.cell_data[field], dtype=float)
    area = np.asarray(patch.compute_cell_sizes(
        length=False, area=True, volume=False).cell_data["Area"])
    if not np.isfinite(values).all() or not np.isfinite(area).all() or np.any(area <= 0):
        raise ValueError("Datos de superficie inválidos")
    return values, area


def analyze(case, diameter, nu, output, time=None):
    if not np.isfinite([diameter, nu]).all() or min(diameter, nu) <= 0:
        raise ValueError("Diámetro y viscosidad deben ser positivos")
    reader = open_reader(case)
    reader.enable_all_patch_arrays()
    times = [t for t in sorted(reader.time_values) if t > 0]
    if not times:
        raise ValueError("No hay resultados posteriores a 0")
    t = times[-1] if time is None else min(times, key=lambda v: abs(v-time))
    reader.set_active_time_value(t)
    data = reader.read()
    grid = internal_mesh(data)
    boundary = data["boundary"]
    inlet, outlet, solid = (boundary[n] for n in ("inlet", "outlet", "sphere"))
    u, area = face_data(inlet, "U")
    velocity = np.average(u, axis=0, weights=area)
    uinf = velocity[0]
    if uinf <= 0 or not np.allclose(velocity[1:], 0, atol=uinf*1e-6):
        raise ValueError("Se supone entrada paralela a +x")
    p, area = face_data(outlet, "p")
    pref = np.average(p, weights=area)
    radius = diameter/2
    if not np.allclose(solid.center, 0, atol=diameter*0.02):
        raise ValueError("Se supone esfera centrada en (0,0,0)")
    if not np.isclose(np.max(np.linalg.norm(solid.points, axis=1)), radius, rtol=0.05):
        raise ValueError("El diámetro no coincide con el patch sphere")
    for name in ("U", "p"):
        if name not in grid.cell_data or not np.isfinite(grid.cell_data[name]).all():
            raise ValueError(f"Campo {name} ausente o no finito")
    grid = grid.cell_data_to_point_data()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    re = uinf*diameter/nu

    def sample(points):
        result = pv.PolyData(points).sample(grid)
        valid = np.asarray(result["vtkValidPointMask"], bool)
        valid &= np.linalg.norm(points, axis=1) > radius
        ux = np.asarray(result["U"], float)[:, 0].copy()/uinf
        cp = (np.asarray(result["p"], float).copy()-pref)/(0.5*uinf**2)
        ux[~valid], cp[~valid] = np.nan, np.nan
        return ux, cp

    # Perfil axial y perfiles transversales: huecos del sólido quedan como NaN.
    xmin, xmax, ymin, ymax, _, _ = grid.bounds
    x = np.linspace(xmin+1e-6*diameter, xmax-1e-6*diameter, 800)
    ux, cp = sample(np.column_stack((x, np.zeros_like(x), np.zeros_like(x))))
    np.savetxt(output/"axial.csv", np.column_stack((x/diameter, ux, cp)),
               delimiter=",", header="x_D,Ux_Uinf,Cp", comments="")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, values, label in zip(axes, (ux, cp), ("Ux/Uinf", "Cp")):
        ax.plot(x/diameter, values)
        ax.axvspan(-0.5, 0.5, alpha=0.15)
        ax.set(xlabel="x/D", ylabel=label)
    fig.suptitle(f"Re={re:g}, estado {t:g}")
    fig.tight_layout()
    fig.savefig(output/"axial.png", dpi=180)
    plt.close(fig)

    y = np.linspace(ymin+1e-6*diameter, ymax-1e-6*diameter, 500)
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for xd in (-1, -0.65, 0, 0.65, 1, 1.5):
        if not xmin < xd*diameter < xmax:
            continue
        ux, cp = sample(np.column_stack((np.full_like(y, xd*diameter), y, np.zeros_like(y))))
        rows.extend(zip(np.full_like(y, xd), y/diameter, ux, cp))
        for ax, values, label in zip(axes, (ux, cp), ("Ux/Uinf", "Cp")):
            ax.plot(values, y/diameter, label=f"x/D={xd:g}")
            ax.set(xlabel=label, ylabel="y/D")
    for ax in axes:
        ax.legend()
    fig.tight_layout()
    fig.savefig(output/"transverse.png", dpi=180)
    plt.close(fig)
    np.savetxt(output/"transverse.csv", np.asarray(rows).reshape(-1, 4),
               delimiter=",", header="x_D,y_D,Ux_Uinf,Cp", comments="")

    # Cp sobre caras reales, promedio angular ponderado por área.
    p, area = face_data(solid, "p")
    xyz = solid.cell_centers().points
    theta = np.degrees(np.arccos(np.clip(-xyz[:, 0]/np.linalg.norm(xyz, axis=1), -1, 1)))
    cp = (p-pref)/(0.5*uinf**2)
    np.savetxt(output/"surface.csv", np.column_stack((theta, cp, area)),
               delimiter=",", header="theta_deg,Cp,area_m2", comments="")
    centers, means = [], []
    edges = np.linspace(0, 180, 25)
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (theta >= lo) & ((theta <= hi) if hi == 180 else (theta < hi))
        if mask.any():
            centers.append((lo+hi)/2)
            means.append(np.average(cp[mask], weights=area[mask]))
    fig, ax = plt.subplots()
    ax.scatter(theta, cp, s=5, alpha=0.3, label="Caras")
    ax.plot(centers, means, label="Media ponderada por área")
    ax.set(xlabel="Ángulo desde el frente [°]", ylabel="Cp", xlim=(0, 180))
    ax.legend()
    fig.tight_layout()
    fig.savefig(output/"surface.png", dpi=180)
    plt.close(fig)
    np.savetxt(output/"parameters.csv", [[t, re, uinf, pref, diameter, nu]],
               delimiter=",", header="time,Re,Uinf_m_s,pref_m2_s2,D_m,nu_m2_s", comments="")
    print(f"Re={re:g}; estado={t:g}; resultados en {output}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", type=Path)
    p.add_argument("--diameter", type=float, required=True)
    p.add_argument("--nu", type=float, required=True)
    p.add_argument("--time", type=float)
    p.add_argument("--output", type=Path, default=Path("plots/sphere"))
    a = p.parse_args()
    analyze(a.case, a.diameter, a.nu, a.output, a.time)


if __name__ == "__main__":
    main()
