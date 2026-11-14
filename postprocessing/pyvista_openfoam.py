#!/usr/bin/env python3
"""Visualizar resultados OpenFOAM (.foam) con PyVista sin ejecutar el solver."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
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


def render_frame(plotter, grid, normal, time_value, clim):
    section = grid.slice(normal=normal)
    if section.n_points == 0:
        raise RuntimeError(f"El corte no contiene puntos para el estado {time_value:g}.")
    plotter.clear()
    plotter.set_background("#101522")
    plotter.add_mesh(
        section,
        scalars="U_magnitude",
        clim=clim,
        cmap="magma",
        smooth_shading=True,
        show_edges=False,
        scalar_bar_args={
            "title": "Velocidad |U|",
            "color": "#f4f6fb",
            "label_font_size": 12,
            "title_font_size": 14,
            "n_labels": 5,
            "fmt": "%.2e",
            "vertical": True,
            "position_x": 0.88,
            "position_y": 0.18,
            "height": 0.66,
            "width": 0.06,
        },
    )
    contours = section.contour(isosurfaces=10, scalars="U_magnitude")
    if contours.n_cells:
        plotter.add_mesh(contours, color="#fff2cc", opacity=0.3, line_width=1)
    plotter.add_text(
        f"CAMPO DE VELOCIDAD   ·   tiempo/iteración = {time_value:g}",
        position="upper_left",
        font_size=15,
        color="#f4f6fb",
        shadow=True,
    )
    plotter.add_axes(line_width=2, color="#f4f6fb")
    plotter.view_xy() if normal == "z" else plotter.view_xz()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("foam", type=Path, help="Archivo .foam en la raíz del caso")
    ap.add_argument("--output", type=Path, default=Path("plots/pyvista"))
    ap.add_argument("--time-index", type=int, default=-1)
    ap.add_argument("--gif", action="store_true", help="Animar los estados disponibles")
    ap.add_argument("--mp4", action="store_true", help="Exportar video MP4 con ffmpeg")
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
    if args.gif or args.mp4:
        if len(times) < 2:
            raise SystemExit("Se necesitan al menos dos tiempos/iteraciones para animar.")
        vmax = 0.0
        for time_value in times:
            reader.set_active_time_value(time_value)
            current = prepare(internal_grid(reader))
            vmax = max(vmax, float(np.nanmax(current.point_data["U_magnitude"])))
        clim = (0.0, max(vmax, 1e-12))
    else:
        clim = (0.0, max(float(np.nanmax(grid.point_data["U_magnitude"])), 1e-12))

    plotter = pv.Plotter(off_screen=True, window_size=(1600, 900))
    render_frame(plotter, grid, normal, times[args.time_index], clim)
    plotter.screenshot(str(args.output / "velocidad.png"))
    plotter.close()
    print(args.output / "velocidad.png")

    if args.gif or args.mp4:
        plotter = pv.Plotter(off_screen=True, window_size=(1600, 900))
        if args.gif:
            gif = args.output / "velocidad.gif"
            plotter.open_gif(str(gif), fps=args.fps)
        ffmpeg = None
        if args.mp4:
            ffmpeg = shutil.which("ffmpeg")
            if ffmpeg is None:
                raise SystemExit("No se encontró ffmpeg; instálalo para exportar MP4.")
        with tempfile.TemporaryDirectory(prefix="openfoam-frames-") as temp_dir:
            frame_dir = Path(temp_dir)
            for index, time_value in enumerate(times):
                reader.set_active_time_value(time_value)
                current = prepare(internal_grid(reader))
                render_frame(plotter, current, normal, time_value, clim)
                if args.gif:
                    plotter.write_frame()
                if args.mp4:
                    plotter.screenshot(str(frame_dir / f"frame-{index:06d}.png"))
            plotter.close()
            if args.mp4:
                mp4 = args.output / "velocidad.mp4"
                subprocess.run(
                    [
                        ffmpeg,
                        "-y",
                        "-framerate",
                        str(args.fps),
                        "-i",
                        str(frame_dir / "frame-%06d.png"),
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-movflags",
                        "+faststart",
                        str(mp4),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
        if args.gif:
            print(gif)
        if args.mp4:
            print(mp4)


if __name__ == "__main__":
    main()
