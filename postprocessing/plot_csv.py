#!/usr/bin/env python3
"""Graficar uno o varios CSV; las columnas deben tener cabecera."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", nargs="+", type=Path)
    p.add_argument("--x", required=True)
    p.add_argument("--y", required=True, nargs="+")
    p.add_argument("--delimiter", default=None)
    p.add_argument("--output", type=Path, default=Path("plots/perfil.png"))
    a = p.parse_args()
    fig, ax = plt.subplots(figsize=(8, 5))
    for path in a.csv:
        data = pd.read_csv(path, comment="#", sep=a.delimiter, engine="python")
        data.columns = data.columns.str.strip()
        missing = set([a.x, *a.y]) - set(data.columns)
        if missing:
            p.error(f"{path}: faltan {sorted(missing)}; disponibles {list(data.columns)}")
        x = pd.to_numeric(data[a.x], errors="coerce").to_numpy(dtype=float)
        for col in a.y:
            y = pd.to_numeric(data[col], errors="coerce").to_numpy(dtype=float)
            valid = np.isfinite(x) & np.isfinite(y)
            if not valid.any():
                p.error(f"{path}: sin pares numéricos para {a.x}/{col}")
            # Mantener los huecos del perfil, por ejemplo dentro de un sólido.
            label = col if len(a.csv) == 1 else f"{path.parent.name}/{path.stem}: {col}"
            ax.plot(np.where(valid, x, np.nan), np.where(valid, y, np.nan), label=label)
    ax.set(xlabel=a.x, ylabel=", ".join(a.y))
    ax.grid(alpha=0.25)
    ax.legend()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(a.output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
