#!/usr/bin/env python3
"""Visualizar resultados OpenFOAM (.foam) con PyVista sin ejecutar el solver."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pyvista as pv

def internal_grid(reader):
    data = reader.read()
    if not isinstance(data, pv.MultiBlock):
        return data
    # vtkOpenFOAMReader normalmente expone internalMesh como bloque nombrado.
    def find(obj):
        if not isinstance(obj, pv.MultiBlock):
            return obj if obj is not None and obj.n_cells > 0 else None
        for name in obj.keys():
            child = obj[name]
            if name == "internalMesh" and child is not None:
                return child
            found = find(child)
            if found is not None and not isinstance(found, pv.MultiBlock):
                return found
        return None
    if "internalMesh" in data.keys():
        return data["internalMesh"]
    return find(data)

def prepare(grid):
    if grid is None or grid.n_cells == 0:
        raise RuntimeError("No se encontró una malla interna con celdas.")
    if "U" in grid.cell_data:
        grid = grid.cell_data_to_point_data(pass_cell_data=True)
    if "U" not in grid.point_data:
        raise RuntimeError(f"Campo U ausente. Datos disponibles: {list(grid.array_names)}")
    vec = np.asarray(grid.point_data["U"])
    grid.point_data["U_magnitude"] = np.linalg.norm(vec, axis=1)
    return grid

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("foam", type=Path, help="Archivo .foam en la raíz del caso")
    ap.add_argument("--output", type=Path, default=Path("plots/pyvista"))
    ap.add_argument("--time-index", type=int, default=-1)
    ap.add_argument("--gif", action="store_true", help="Animar los estados disponibles")
    ap.add_argument("--fps", type=int, default=15)
    args = ap.parse_args()
    if not args.foam.is_file():
        raise SystemExit(f"No existe {args.foam}. Crear con: touch {args.foam}")
    if args.fps < 1:
        raise SystemExit("--fps debe ser >= 1")
    args.output.mkdir(parents=True, exist_ok=True)
    reader = pv.OpenFOAMReader(str(args.foam.resolve()))
    times = list(reader.time_values)
    if not times:
        raise SystemExit("No se encontraron tiempos/iteraciones en los resultados.")
    if not (-len(times) <= args.time_index < len(times)):
        raise SystemExit(f"Índice de tiempo fuera de rango: 0..{len(times)-1}")
    reader.set_active_time_value(times[args.time_index])
    grid = prepare(internal_grid(reader))
    # Un corte central ofrece una representación útil tanto de dominios 2D como 3D.
    normal = "z" if (grid.bounds[5] - grid.bounds[4]) < (grid.bounds[3] - grid.bounds[2]) else "y"
    sl = grid.slice(normal=normal)
    if sl.n_points == 0:
        raise SystemExit("El corte no contiene puntos; revisar geometría y normal.")
    plotter = pv.Plotter(off_screen=True, window_size=(1280, 720))
    plotter.add_mesh(sl, scalars="U_magnitude", cmap="viridis", show_edges=False)
    plotter.add_axes()
    plotter.view_xy() if normal == "z" else plotter.view_xz()
    plotter.screenshot(str(args.output / "velocidad.png"))
    plotter.close()
    print(args.output / "velocidad.png")

    if args.gif:
        if len(times) < 2:
            raise SystemExit("Se necesitan al menos dos tiempos/iteraciones para un GIF.")
        # Rango fijo para permitir comparación visual; recorre los tiempos disponibles.
        vmax = 0.0
        for t in times:
            reader.set_active_time_value(t)
            g = prepare(internal_grid(reader))
            vmax = max(vmax, float(np.nanmax(g.point_data["U_magnitude"])))
        plotter = pv.Plotter(off_screen=True, window_size=(1280, 720))
        gif = args.output / "velocidad.gif"
        plotter.open_gif(str(gif), fps=args.fps)
        for t in times:
            reader.set_active_time_value(t)
            g = prepare(internal_grid(reader))
            s = g.slice(normal=normal)
            plotter.clear()
            plotter.add_mesh(s, scalars="U_magnitude", clim=(0.0, max(vmax, 1e-12)),
                             cmap="viridis", show_scalar_bar=True)
            plotter.add_text(f"Time/iteration: {t:g}", font_size=11)
            plotter.add_axes()
            plotter.view_xy() if normal == "z" else plotter.view_xz()
            plotter.write_frame()
        plotter.close()
        print(gif)
if __name__ == "__main__":
    main()
