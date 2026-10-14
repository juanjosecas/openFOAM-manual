#!/usr/bin/env python3
"""Representar columnas numéricas exportadas mediante postProcess o foamToVTK/CSV.

Los CSV de OpenFOAM pueden incluir cabeceras comentadas con '#'.
Para perfiles, elegir x/y; para series temporales elegir time/variable.
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path)
    p.add_argument("--x", required=True, help="Columna del eje horizontal")
    p.add_argument("--y", required=True, nargs="+", help="Columnas de datos")
    p.add_argument("--output", type=Path, default=Path("plots/perfil.png"))
    p.add_argument("--delimiter", default=None, help="Separador; auto por defecto")
    a = p.parse_args()
    if a.delimiter:
        df = pd.read_csv(a.csv, comment="#", sep=a.delimiter)
    else:
        df = pd.read_csv(a.csv, comment="#", sep=None, engine="python")
    df.columns = df.columns.str.strip()
    missing = [c for c in [a.x, *a.y] if c not in df.columns]
    if missing:
        raise SystemExit(f"Columnas ausentes: {missing}. Disponibles: {list(df.columns)}")
    fig, ax = plt.subplots(figsize=(8, 5))
    for col in a.y:
        ax.plot(pd.to_numeric(df[a.x], errors="coerce"),
                pd.to_numeric(df[col], errors="coerce"), label=col)
    ax.set(xlabel=a.x, ylabel=", ".join(a.y), title=a.csv.name)
    ax.grid(True, alpha=0.25)
    ax.legend()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(a.output, dpi=170)
    print(a.output)
if __name__ == "__main__":
    main()
