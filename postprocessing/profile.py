"""Extraer un perfil sobre una línea; exportar CSV y gráfico."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fields import read_case, scalar_field


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", type=Path)
    p.add_argument("--field", default="U")
    p.add_argument("--component", type=int, choices=(0, 1, 2))
    p.add_argument("--time", type=float)
    p.add_argument("--start", nargs=3, type=float, required=True)
    p.add_argument("--end", nargs=3, type=float, required=True)
    p.add_argument("--points", type=int, default=201)
    p.add_argument("--output", type=Path, default=Path("plots/profile"))
    a = p.parse_args()
    if a.points < 2 or a.start == a.end:
        p.error("Se necesitan dos puntos distintos y al menos dos muestras")
    grid, time = read_case(a.case, a.time)
    grid = scalar_field(grid, a.field, a.component)
    line = grid.sample_over_line(a.start, a.end, resolution=a.points-1)
    valid = np.asarray(line["vtkValidPointMask"], dtype=bool)
    if not valid.any():
        raise ValueError("La línea no intersecta el dominio")
    x = np.asarray(line["Distance"])
    y = np.asarray(line["display"], dtype=float).copy()
    y[~valid] = np.nan
    a.output.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(a.output.with_suffix(".csv"),
               np.column_stack((x, line.points, y, valid)), delimiter=",",
               header="distance,x,y,z,value,valid", comments="")
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set(xlabel="Distancia [m]", ylabel=a.field, title=f"t/iter = {time:g}")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(a.output.with_suffix(".png"), dpi=180)


if __name__ == "__main__":
    main()
