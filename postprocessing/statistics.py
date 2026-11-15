"""Estadísticos, integrales y balances sobre resultados OpenFOAM guardados."""
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv

from fields import open_reader, internal_mesh


def cell_statistics(grid, field, component=None):
    """Promedio ponderado por volumen e integral de un campo escalar."""
    if field not in grid.cell_data:
        raise KeyError(f"Campo {field} ausente: {list(grid.cell_data.keys())}")
    values = np.asarray(grid.cell_data[field], dtype=float)
    if values.ndim == 2:
        values = (np.linalg.norm(values, axis=1) if component is None
                  else values[:, component])
    elif component is not None:
        raise ValueError("El campo es escalar")
    volumes = np.asarray(grid.compute_cell_sizes(
        length=False, area=False, volume=True).cell_data["Volume"])
    if not np.isfinite(values).all() or not np.isfinite(volumes).all():
        raise ValueError("Hay valores no finitos")
    if np.any(volumes <= 0):
        raise ValueError("Hay celdas sin volumen positivo")
    total = volumes.sum()
    integral = np.dot(values, volumes)
    mean = integral / total
    std = np.sqrt(np.dot((values - mean)**2, volumes) / total)
    return dict(min=values.min(), max=values.max(), mean=mean,
                std=std, integral=integral, volume=total)


def patch_flux(data, name, density=None):
    """Caudal exterior aproximado a partir de U en las caras del patch."""
    if name not in data.keys():
        raise KeyError(f"Patch {name} no encontrado")
    patch = data[name]
    if not isinstance(patch, pv.PolyData):
        raise ValueError("El patch debe ser una superficie PolyData")
    if "U" not in patch.cell_data:
        raise KeyError("Falta U de caras; no se usa U de centros internos")
    surface = patch.compute_normals(cell_normals=True, point_normals=False,
                                    consistent_normals=False,
                                    auto_orient_normals=False)
    area = np.asarray(surface.compute_cell_sizes(
        length=False, area=True, volume=False).cell_data["Area"])
    velocity = np.asarray(surface.cell_data["U"])
    normals = np.asarray(surface.cell_data["Normals"])
    flux = np.einsum("ij,ij->i", velocity, normals) * area
    if density is not None:
        flux = flux * density
    if not np.isfinite(flux).all():
        raise ValueError("Flujo no finito")
    return dict(area=area.sum(), net=flux.sum(),
                positive=flux[flux > 0].sum(), negative=flux[flux < 0].sum())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", type=Path)
    p.add_argument("--field", default="U")
    p.add_argument("--component", type=int, choices=(0, 1, 2))
    p.add_argument("--patch", nargs="+",
                   help="Caudal por patch (usar nombres de --list-patches)")
    p.add_argument("--list-patches", action="store_true")
    p.add_argument("--rho", type=float, help="Densidad constante en kg/m³")
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--start-time", type=float)
    p.add_argument("--end-time", type=float)
    p.add_argument("--output", type=Path, default=Path("plots/statistics"))
    a = p.parse_args()
    if a.stride < 1 or (a.rho is not None and
                        (not np.isfinite(a.rho) or a.rho <= 0)):
        p.error("stride y densidad deben ser positivos")
    if a.rho is not None and not a.patch:
        p.error("--rho requiere --patch")
    reader = open_reader(a.case)
    if a.patch or a.list_patches:
        reader.enable_all_patch_arrays()
        reader.enable_all_cell_arrays()
        if a.list_patches:
            print("\n".join(reader.patch_array_names))
            return
    times = [t for t in sorted(reader.time_values)
             if (a.start_time is None or t >= a.start_time)
             and (a.end_time is None or t <= a.end_time)][::a.stride]
    if not times:
        p.error("No hay estados en el intervalo")
    rows = []
    for time in times:
        reader.set_active_time_value(time)
        data = reader.read()
        if a.patch:
            boundary = data["boundary"]
            fluxes = [patch_flux(boundary, name.split("/")[-1],
                                a.rho) for name in a.patch]
            row = {"time": time}
            for name, flux in zip(a.patch, fluxes):
                row.update({f"{name}:{k}": v for k, v in flux.items()})
            row["net_sum"] = sum(f["net"] for f in fluxes)
        else:
            row = {"time": time, **cell_statistics(
                internal_mesh(data), a.field, a.component)}
        rows.append(row)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.with_suffix(".csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fig, ax = plt.subplots()
    columns = ([f"{name}:net" for name in a.patch] + ["net_sum"]
               if a.patch else ["mean", "min", "max"])
    for key in columns:
        ax.plot(times, [r[key] for r in rows], label=key)
    ax.set(xlabel="Tiempo / iteración",
           ylabel=("kg/s" if a.rho is not None else "m³/s") if a.patch else a.field)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(a.output.with_suffix(".png"), dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
