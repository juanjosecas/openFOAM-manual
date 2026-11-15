#!/usr/bin/env python3
"""Extraer residuos, Courant y continuidad de un log existente."""
import argparse
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NUM = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
TIME = re.compile(r"^\s*Time\s*=\s*(" + NUM + r")\s*$")
SOLVE = re.compile(r"Solving for\s+([\w.]+),\s+Initial residual\s*=\s*(" + NUM +
                   r"),\s+Final residual\s*=\s*(" + NUM + r"),\s+No Iterations\s+(\d+)")
CO = re.compile(r"(Courant Number|Interface Courant Number)\s+mean:\s*(" + NUM +
                r")\s+max:\s*(" + NUM + r")", re.I)
CONT = re.compile(r"sum local\s*=\s*(" + NUM + r"),\s*global\s*=\s*(" + NUM +
                  r"),\s*cumulative\s*=\s*(" + NUM + r")")


def parse_log(path):
    residuals, courant, continuity = [], [], []
    step, time = 0, None
    with path.open(errors="replace") as f:
        for line in f:
            m = TIME.match(line)
            if m:
                step += 1
                time = float(m[1])
            m = SOLVE.search(line)
            if m:
                residuals.append((step, time, m[1], float(m[2]), float(m[3]), int(m[4])))
            m = CO.search(line)
            if m:
                # Courant puede aparecer antes del siguiente encabezado Time.
                courant.append((len(courant)+1, m[1].lower(), float(m[2]), float(m[3])))
            m = CONT.search(line)
            if m:
                continuity.append((step, time, *map(float, m.groups())))
    return (
        pd.DataFrame(residuals, columns=["step", "time", "field", "initial", "final", "iterations"]),
        pd.DataFrame(courant, columns=["record", "kind", "mean", "max"]),
        pd.DataFrame(continuity, columns=["step", "time", "local", "global", "cumulative"]),
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", type=Path)
    p.add_argument("--output", type=Path, default=Path("plots"))
    a = p.parse_args()
    residuals, courant, continuity = parse_log(a.log)
    tables = [(name, df) for name, df in (
        ("residuos", residuals), ("courant", courant), ("continuidad", continuity)) if not df.empty]
    if not tables:
        p.error("No se reconocieron diagnósticos")
    a.output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(tables), 1, figsize=(9, 3.5*len(tables)), squeeze=False)
    for ax, (name, df) in zip(axes[:, 0], tables):
        df.to_csv(a.output / f"{name}.csv", index=False)
        if name == "residuos":
            # Primera corrección de cada campo por paso; CSV conserva todas.
            for field, rows in df.groupby("field"):
                rows = rows.drop_duplicates("step")
                ax.semilogy(rows.step, rows.initial.where(rows.initial > 0), label=field)
            ax.set(xlabel="Paso del log", ylabel="Residuo inicial")
        elif name == "courant":
            for kind, rows in df.groupby("kind"):
                x = range(1, len(rows)+1)
                ax.plot(x, rows["mean"], label=f"{kind}: medio")
                ax.plot(x, rows["max"], label=f"{kind}: máximo")
            ax.set(xlabel="Registro por tipo", ylabel="Courant")
        else:
            for col in ("local", "global", "cumulative"):
                ax.plot(df.step, df[col], label=col)
            ax.set(xlabel="Paso del log", ylabel="Error de continuidad")
        ax.grid(alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(a.output / "resumen.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
