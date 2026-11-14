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

BG = "#0b1020"
PANEL = "#111a2e"
TEXT = "#e7edf8"
MUTED = "#96a3b8"
ACCENT = "#49dcb1"
BLUE = "#62b5ff"


def style_axis(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color("#26344c")
    ax.grid(True, color="#8290a8", alpha=0.16, linewidth=0.8)


def save_figure(fig, path):
    fig.savefig(path, dpi=220, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


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
        fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
        style_axis(ax)
        for name, (idx, vals) in sorted(residuals.items()):
            ax.semilogy(idx, vals, label=name, linewidth=1.7, alpha=0.9)
        ax.set(xlabel="Índice de escritura de tiempo/iteración en el log",
               ylabel="Residuo inicial", title="Convergencia del solver")
        ax.legend(frameon=False, labelcolor=TEXT, ncols=2)
        fig.tight_layout()
        save_figure(fig, a.output / "residuos.png")
    courant = [(float(m.group(1)), float(m.group(2))) for m in COURANT.finditer(raw)]
    if courant:
        fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
        style_axis(ax)
        ax.plot([x[0] for x in courant], label="Co medio", color=ACCENT, linewidth=1.8)
        ax.plot([x[1] for x in courant], label="Co máximo", color=BLUE, linewidth=1.8)
        ax.set(xlabel="Registro de Courant", ylabel="Número de Courant",
               title="Estabilidad temporal")
        ax.legend(frameon=False, labelcolor=TEXT)
        fig.tight_layout()
        save_figure(fig, a.output / "courant.png")
    if not residuals and not courant:
        raise SystemExit("No se reconocieron residuos ni Courant. Revisar el formato del log.")
    fig, axes = plt.subplots(
        2, 1, figsize=(13, 8), facecolor=BG,
        gridspec_kw={"height_ratios": [1.35, 1]},
    )
    for ax in axes:
        style_axis(ax)
    if residuals:
        for name, (idx, vals) in sorted(residuals.items()):
            axes[0].semilogy(idx, vals, label=name, linewidth=1.6, alpha=0.9)
        axes[0].set_ylabel("Residuo inicial")
        axes[0].legend(frameon=False, labelcolor=TEXT, ncols=3, fontsize=8)
    else:
        axes[0].set_visible(False)
    if courant:
        axes[1].plot([x[0] for x in courant], label="Co medio", color=ACCENT, linewidth=1.8)
        axes[1].plot([x[1] for x in courant], label="Co máximo", color=BLUE, linewidth=1.8)
        axes[1].set(xlabel="Registro de Courant", ylabel="Número de Courant")
        axes[1].legend(frameon=False, labelcolor=TEXT)
    else:
        axes[1].set_visible(False)
    fig.suptitle(a.log.name, color=TEXT, fontsize=16, fontweight="bold", x=0.08, ha="left")
    fig.text(0.08, 0.94, "DIAGNÓSTICO NUMÉRICO  /  OpenFOAM", color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0.04, 0.03, 0.98, 0.91))
    save_figure(fig, a.output / "resumen.png")
    print("Gráficos disponibles en:", a.output)
if __name__ == "__main__":
    main()
