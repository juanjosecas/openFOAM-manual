"""Leer, visualizar y exportar campos OpenFOAM sin ParaView."""
import argparse
from pathlib import Path

import numpy as np
import pyvista as pv


def read_case(case, time=None):
    case = Path(case).resolve()
    if not (case / "system/controlDict").is_file():
        raise ValueError(f"No es un caso OpenFOAM: {case}")
    marker = case / "case.foam"
    marker.touch(exist_ok=True)
    reader = pv.OpenFOAMReader(str(marker))
    reader.enable_all_cell_arrays()
    times = list(reader.time_values)
    if not times:
        raise ValueError("No hay tiempos disponibles")
    selected = times[-1] if time is None else min(times, key=lambda t: abs(t-time))
    reader.set_active_time_value(selected)
    data = reader.read()
    grid = data["internalMesh"] if isinstance(data, pv.MultiBlock) else data
    if grid is None or not grid.n_cells:
        raise ValueError("internalMesh vacío")
    return grid, selected


def scalar_field(grid, field, component=None):
    if field not in grid.cell_data:
        raise KeyError(f"Campos disponibles: {list(grid.cell_data.keys())}")
    values = np.asarray(grid.cell_data[field])
    if values.ndim == 2:
        if component is None:
            values = np.linalg.norm(values, axis=1)
        else:
            values = values[:, component]
    elif component is not None:
        raise ValueError("El campo es escalar")
    grid.cell_data["display"] = values
    return grid.cell_data_to_point_data(pass_cell_data=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", type=Path)
    p.add_argument("--field", default="U")
    p.add_argument("--component", type=int, choices=(0, 1, 2))
    p.add_argument("--time", type=float)
    p.add_argument("--normal", choices=("x", "y", "z"))
    p.add_argument("--output", type=Path)
    p.add_argument("--csv", type=Path)
    p.add_argument("--cmap", default="viridis")
    args = p.parse_args()
    grid, time = read_case(args.case, args.time)
    grid = scalar_field(grid, args.field, args.component)
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(args.csv, np.column_stack((grid.cell_centers().points,
                   grid.cell_data["display"])), delimiter=",",
                   header="x,y,z,value", comments="")
    mesh = grid.slice(normal=args.normal) if args.normal else grid
    plotter = pv.Plotter(off_screen=args.output is not None)
    plotter.add_mesh(mesh, scalars="display", cmap=args.cmap,
                     scalar_bar_args={"title": args.field})
    plotter.add_text(f"{args.field} | t/iter = {time:g}", font_size=12)
    if args.normal:
        {"x": plotter.view_yz, "y": plotter.view_xz, "z": plotter.view_xy}[args.normal]()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        plotter.show(screenshot=str(args.output))
    else:
        plotter.show()


if __name__ == "__main__":
    main()
