#!/usr/bin/env python3
"""Comparar perfiles CSV de variantes con ejes y columnas declarados explícitamente."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", nargs="+", type=Path)
    ap.add_argument("--x", required=True)
    ap.add_argument("--y", required=True)
    ap.add_argument("--output", type=Path, default=Path("plots/comparacion.png"))
    a = ap.parse_args()
    fig, ax = plt.subplots(figsize=(9, 5))
    for path in a.csv:
        if not path.is_file():
            ap.error(f"No existe {path}")
        data = pd.read_csv(path, comment="#", sep=None, engine="python")
        data.columns = data.columns.str.strip()
        if a.x not in data.columns or a.y not in data.columns:
            ap.error(f"{path}: columnas disponibles: {list(data.columns)}")
        clean = data[[a.x, a.y]].apply(pd.to_numeric, errors="coerce").dropna()
        if clean.empty:
            ap.error(f"{path}: no hay datos numéricos para {a.x}/{a.y}")
        ax.plot(clean[a.x], clean[a.y], label=path.stem)
    ax.set(xlabel=a.x, ylabel=a.y, title="Comparación de variantes")
    ax.grid(alpha=0.3)
    ax.legend()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(a.output, dpi=180)
    print(a.output)

if __name__ == "__main__":
    main()
