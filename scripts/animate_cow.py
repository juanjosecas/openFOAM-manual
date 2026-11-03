#!/usr/bin/env python3
"""Renderiza PNG estacionario o GIF transitorio del caso cow con PyVista."""
from pathlib import Path
import argparse
import imageio.v2 as imageio
import numpy as np
import pyvista as pv


def internal_mesh(block):
    if isinstance(block, pv.MultiBlock):
        if "internalMesh" in block.keys():
            return block["internalMesh"]
        for value in block:
            try:
                return internal_mesh(value)
            except (KeyError, TypeError):
                continue
        raise KeyError("internalMesh no encontrado")
    if isinstance(block, pv.UnstructuredGrid):
        return block
    raise KeyError("No se encontró el volumen")


def prepare(mesh, field):
    source = "p" if field == "pressure" else "U"
    if source not in mesh.point_data and source not in mesh.cell_data:
        raise KeyError(f"Falta el campo {source}: {mesh.array_names}")

    # Campo escalar o vectorial sobre puntos para el cálculo de curl.
    if field == "pressure":
        return mesh, "p"
    if "U" in mesh.cell_data:
        mesh = mesh.cell_data_to_point_data()
    if field == "speed":
        mesh.point_data["speed"] = np.linalg.norm(np.asarray(mesh.point_data["U"]), axis=1)
        return mesh, "speed"
    mesh = mesh.compute_derivative(scalars="U", vorticity=True)
    mesh.point_data["omega_z"] = np.asarray(mesh.point_data["Vorticity"])[:, 2]
    return mesh, "omega_z"


def frame(reader, t, field, clim):
    reader.set_active_time_value(float(t))
    mesh, scalar = prepare(internal_mesh(reader.read()).copy(deep=True), field)
    z_mid = 0.5 * (mesh.bounds[4] + mesh.bounds[5])
    planar = mesh.slice(normal=(0, 0, 1), origin=(0, 0, z_mid))
    pl = pv.Plotter(off_screen=True, window_size=(1400, 650))
    pl.set_background("#111820")
    pl.add_mesh(planar, scalars=scalar, cmap="coolwarm" if field == "vorticity" else "inferno",
                clim=clim, scalar_bar_args={"title":scalar})
    pl.view_xy()
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = 5.6
    pl.add_text(f"Cow CFD  |  {field}  |  index = {t:.5g}", position="upper_left", font_size=12)
    rgb = pl.screenshot(return_img=True)[:, :, :3].copy()
    pl.close()
    return rgb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case", type=Path)
    ap.add_argument("--field", choices=("speed", "vorticity", "pressure"), default="speed")
    ap.add_argument("--still", action="store_true")
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--max-frames", type=int, default=200)
    args = ap.parse_args()
    if min(args.fps, args.stride, args.max_frames) <= 0:
        ap.error("fps, stride, max-frames deben ser positivos")
    case = args.case.resolve()
    foam = case / "cow.foam"
    foam.touch(exist_ok=True)
    reader = pv.OpenFOAMReader(str(foam))
    reader.skip_zero_time = True
    reader.enable_all_cell_arrays()
    times = list(reader.time_values)
    if not times:
        raise RuntimeError("No hay estados guardados para renderizar")
    if args.still:
        times = [times[-1]]
    else:
        times = times[::args.stride][:args.max_frames]
    clim = {"speed":(0,16), "pressure":(-200,200), "vorticity":(-100,100)}[args.field]
    output = case / "postprocessing" / "animations"
    output.mkdir(parents=True, exist_ok=True)
    if args.still:
        dest = output / f"{args.field}_steady.png"
        imageio.imwrite(dest, frame(reader, times[-1], args.field, clim))
    else:
        dest = output / f"{args.field}_transient.gif"
        with imageio.get_writer(dest, mode="I", duration=1/args.fps, loop=0) as writer:
            for t in times:
                writer.append_data(frame(reader, t, args.field, clim))
    print(dest)


if __name__ == "__main__":
    main()
