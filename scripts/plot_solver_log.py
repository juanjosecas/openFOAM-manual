#!/usr/bin/env python3
"""Graficar diagnósticos de OpenFOAM a partir de logs existentes. No ejecuta CFD."""
import argparse
import re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TIME = re.compile(r"^Time\s*=\s*([+\-0-9.eE]+)", re.M)
SOLVE = re.compile(r"Solving for\s+([\w.]+),\s+Initial residual\s*=\s*([+\-0-9.eE]+)")
COURANT = re.compile(r"Courant Number mean:\s*([+\-0-9.eE]+)\s+max:\s*([+\-0-9.eE]+)")
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", type=Path)
    p.add_argument("--output", type=Path, default=Path("plots"))
    a = p.parse_args()
    raw = a.log.read_text(errors="replace")
    a.output.mkdir(parents=True, exist_ok=True)
    # El índice es la secuencia de solución; no implica segundos ni iteraciones físicas.
    count = 0
    residuals = {}
    for ln in raw.splitlines():
        if TIME.match(ln):
            count += 1
        m = SOLVE.search(ln)
        if m:
            residuals.setdefault(m.group(1), ([], []))
            residuals[m.group(1)][0].append(count)
            residuals[m.group(1)][1].append(float(m.group(2)))
    if residuals:
        fig, ax = plt.subplots(figsize=(9, 5))
        for name, (idx, vals) in sorted(residuals.items()):
            ax.semilogy(idx, vals, label=name, alpha=0.8)
        ax.set(xlabel="Índice de escritura de tiempo/iteración en el log",
               ylabel="Residuo inicial", title="Diagnóstico de convergencia")
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(a.output / "residuos.png", dpi=170)
        plt.close(fig)
    courant = [(float(m.group(1)), float(m.group(2))) for m in COURANT.finditer(raw)]
    if courant:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot([x[0] for x in courant], label="Co medio")
        ax.plot([x[1] for x in courant], label="Co máximo")
        ax.set(xlabel="Registro de Courant", ylabel="Número de Courant",
               title="Estabilidad temporal")
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(a.output / "courant.png", dpi=170)
        plt.close(fig)
    if not residuals and not courant:
        raise SystemExit("No se reconocieron residuos ni Courant. Revisar el formato del log.")
    print("Gráficos disponibles en:", a.output)
if __name__ == "__main__":
    main()
