"""Comparar difusión, conducción y flexión con referencias analíticas.

Solo lee resultados guardados. Ejecutar --help y el --help de cada modelo.
"""
import argparse
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fields import open_reader, internal_mesh


def diffusion(x, length, time, diffusivity, source, initial):
    """Barra finita: concentración fija en x=0 y flujo nulo en x=L."""
    tau = diffusivity * time / length**2
    if time <= 0:
        return np.full_like(x, initial)
    # Para tiempos muy cortos el extremo cerrado no altera la solución
    # dentro de la precisión de punto flotante.
    if tau < 1e-5:
        c = np.array([math.erfc(v / (2 * math.sqrt(diffusivity*time)))
                      for v in x])
    else:
        # 1 - sum[4/((2n+1) pi) sin(k_n*x) exp(-D*k_n²*t)]
        # Corte según el decaimiento exponencial, no un N fijo.
        count = max(1, math.ceil(math.sqrt(35/tau)/math.pi + 0.5))
        c = np.ones_like(x, dtype=float)
        for n in range(count):
            k = (n + 0.5) * math.pi
            c -= (2/k) * np.sin(k*x/length) * math.exp(-k*k*tau)
    return initial + (source - initial)*c


def profile(grid, field, component=None):
    if field not in grid.cell_data:
        raise KeyError(f"No existe {field}: {list(grid.cell_data.keys())}")
    values = np.asarray(grid.cell_data[field], dtype=float)
    if component is not None:
        values = values[:, component]
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("Se necesita un campo escalar finito")
    xmin, xmax, ymin, ymax, zmin, zmax = grid.bounds
    x = grid.cell_centers().points[:, 0] - xmin
    # Promedio de sección ponderado por volumen para una malla extruida.
    volumes = np.asarray(grid.compute_cell_sizes(
        length=False, area=False, volume=True).cell_data["Volume"])
    if not np.isfinite(volumes).all() or np.any(volumes <= 0):
        raise ValueError("Volúmenes de celda inválidos")
    xs, index = np.unique(np.round(x, 12), return_inverse=True)
    weight = np.bincount(index, weights=volumes)
    mean = np.bincount(index, weights=values*volumes) / weight
    return xs, mean, (xmax-xmin, ymax-ymin, zmax-zmin)


def draw(x, values, ref, label, title):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x*1000, values, "o", ms=3, label="OpenFOAM")
    ax.plot(x*1000, ref, "-", label="Referencia analítica")
    ax.set(xlabel="x [mm]", ylabel=label, title=title)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def main():
    p = argparse.ArgumentParser(description=__doc__)
    models = p.add_subparsers(dest="model", required=True)
    d = models.add_parser("diffusion", help="Difusión 1D, extremo cerrado")
    d.add_argument("--diffusivity", type=float, required=True, help="D [m²/s]")
    d.add_argument("--source", type=float, default=1.0)
    d.add_argument("--initial", type=float, default=0.0)
    d.add_argument("--gif", action="store_true")
    h = models.add_parser("heat", help="Conducción estacionaria 1D")
    h.add_argument("--left", type=float, required=True, help="T en x mínimo [K]")
    h.add_argument("--right", type=float, required=True, help="T en x máximo [K]")
    b = models.add_parser("beam", help="Viga rectangular empotrada en x mínimo")
    b.add_argument("--young", type=float, required=True, help="E [Pa]")
    b.add_argument("--traction-z", type=float, required=True, help="Tracción terminal [Pa]")
    for model in (d, h, b):
        model.add_argument("case", type=Path)
        model.add_argument("--output", type=Path, default=Path("plots/reference"))
        model.add_argument("--time", type=float, help="Estado guardado más cercano")
    a = p.parse_args()
    if a.model == "diffusion" and (not np.isfinite(a.diffusivity) or a.diffusivity <= 0):
        p.error("D debe ser positivo y finito")
    if a.model == "beam" and (not np.isfinite(a.young) or a.young <= 0):
        p.error("E debe ser positivo y finito")
    reader = open_reader(a.case)
    times = [t for t in sorted(reader.time_values) if t > 0]
    if not times:
        p.error("No hay resultados posteriores a 0")
    if a.time is not None:
        times = [min(times, key=lambda t: abs(t-a.time))]
    elif a.model != "diffusion":
        times = [times[-1]]
    if getattr(a, "gif", False) and len(times) < 2:
        p.error("El GIF necesita al menos dos estados")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    gif = None
    if getattr(a, "gif", False):
        import imageio.v2 as imageio
        gif = imageio.get_writer(a.output.with_suffix(".gif"), fps=4, loop=0)
    try:
        with a.output.with_suffix(".csv").open("w", newline="") as f, \
             a.output.with_name(a.output.name+"_errors").with_suffix(".csv").open("w", newline="") as e:
            rows, errors = csv.writer(f), csv.writer(e)
            rows.writerow(["time", "x_m", "value", "reference", "error"])
            errors.writerow(["time", "MAE", "RMSE", "max_abs_error"])
            for time in times:
                reader.set_active_time_value(time)
                grid = internal_mesh(reader.read())
                x, values, (L, width, height) = profile(
                    grid, "D" if a.model == "beam" else "T",
                    2 if a.model == "beam" else None)
                if min(L, width, height) <= 0:
                    raise ValueError("Dominio sin espesor físico")
                if a.model == "diffusion":
                    ref = diffusion(x, L, time, a.diffusivity, a.source, a.initial)
                    label = "Concentración"
                elif a.model == "heat":
                    ref = a.left + (a.right-a.left)*x/L
                    label = "T [K]"
                else:
                    force = a.traction_z*width*height
                    inertia = width*height**3/12
                    ref = force*x*x*(3*L-x)/(6*a.young*inertia)
                    label = "Dz [m]"
                    print("Flecha terminal teórica [m]:", force*L**3/(3*a.young*inertia))
                if not np.isfinite(ref).all():
                    raise ValueError("Referencia no finita")
                err = values-ref
                rows.writerows(zip(np.full_like(x, time), x, values, ref, err))
                errors.writerow([time, np.mean(abs(err)), np.sqrt(np.mean(err**2)),
                                 np.max(abs(err))])
                fig = draw(x, values, ref, label, f"t/iter = {time:g}")
                if gif is not None:
                    fig.canvas.draw()
                    gif.append_data(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
                if time == times[-1]:
                    fig.savefig(a.output.with_suffix(".png"), dpi=180)
                plt.close(fig)
    finally:
        if gif is not None:
            gif.close()


if __name__ == "__main__":
    main()
