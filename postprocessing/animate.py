"""Animar campos escalares o vectoriales de un caso OpenFOAM con PyVista."""
import argparse
from pathlib import Path

import numpy as np
import pyvista as pv

from fields import open_reader, internal_mesh, scalar_field


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", type=Path)
    p.add_argument("--field", default="U")
    p.add_argument("--component", type=int, choices=(0, 1, 2))
    p.add_argument("--normal", choices=("x", "y", "z"), default="z")
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--max-frames", type=int)
    p.add_argument("--start-time", type=float)
    p.add_argument("--end-time", type=float)
    p.add_argument("--origin", nargs=3, type=float)
    p.add_argument("--fps", type=int, default=15)
    p.add_argument("--clim", nargs=2, type=float)
    p.add_argument("--cmap", default="viridis")
    p.add_argument("--output", type=Path, default=Path("plots/field.gif"))
    a = p.parse_args()
    if min(a.stride, a.fps) < 1:
        p.error("stride y fps deben ser positivos")
    reader = open_reader(a.case)
    times = [t for t in sorted(reader.time_values)
             if (a.start_time is None or t >= a.start_time)
             and (a.end_time is None or t <= a.end_time)][::a.stride]
    if a.max_frames is not None:
        if a.max_frames < 2:
            p.error("--max-frames debe ser >= 2")
        times = times[:a.max_frames]
    if len(times) < 2:
        p.error("Se requieren dos estados")
    def frame(t):
        reader.set_active_time_value(t)
        grid = internal_mesh(reader.read())
        section = scalar_field(grid, a.field, a.component).slice(normal=a.normal, origin=a.origin)
        if not section.n_points:
            raise ValueError(f"Corte vacío en t={t:g}")
        return section
    if a.clim is None:
        lo, hi = np.inf, -np.inf
        for t in times:
            v = np.asarray(frame(t).point_data["display"])
            v = v[np.isfinite(v)]
            if not v.size:
                raise ValueError(f"Campo sin datos finitos en t={t:g}")
            lo, hi = min(lo, v.min()), max(hi, v.max())
        if lo == hi:
            hi = lo + max(abs(lo)*1e-9, 1e-12)
        clim = (lo, hi)
    else:
        clim = tuple(a.clim)
        if not np.isfinite(clim).all() or clim[0] >= clim[1]:
            p.error("--clim requiere un mínimo menor al máximo")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    pl = pv.Plotter(off_screen=True, window_size=(1280, 720))
    if a.output.suffix.lower() == ".gif":
        pl.open_gif(str(a.output), fps=a.fps)
    elif a.output.suffix.lower() == ".mp4":
        pl.open_movie(str(a.output), framerate=a.fps)
    else:
        p.error("Usar .gif o .mp4")
    for i, t in enumerate(times):
        pl.add_mesh(frame(t), name="field", scalars="display", clim=clim,
                    cmap=a.cmap, reset_camera=False)
        pl.add_text(f"{a.field} | t/iter = {t:g}", name="time", font_size=12)
        if i == 0:
            {"x": pl.view_yz, "y": pl.view_xz, "z": pl.view_xy}[a.normal]()
            pl.enable_parallel_projection()
            pl.reset_camera()
        pl.write_frame()
    pl.close()


if __name__ == "__main__":
    main()
