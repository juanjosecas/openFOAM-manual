"""Leer, visualizar y exportar campos OpenFOAM sin ParaView."""
import argparse
from pathlib import Path

import numpy as np
import pyvista as pv


def open_reader(case):
    case = Path(case).resolve()
    if case.is_file() and case.suffix == ".foam":
        marker = case
        case = case.parent
    else:
        marker = case / "case.foam"
    if not (case / "system/controlDict").is_file():
        raise ValueError(f"No es un caso OpenFOAM: {case}")
    marker.touch(exist_ok=True)
    reader = pv.OpenFOAMReader(str(marker))
    reader.enable_all_cell_arrays()
    return reader


def internal_mesh(data):
    if isinstance(data, pv.MultiBlock):
        if "internalMesh" in data.keys():
            return internal_mesh(data["internalMesh"])
        for block in data:
            if isinstance(block, pv.MultiBlock):
                try:
                    return internal_mesh(block)
                except ValueError:
                    pass
        raise ValueError("No se encontró internalMesh")
    if isinstance(data, pv.UnstructuredGrid) and data.n_cells:
        return data
    raise ValueError("Malla interna vacía o no reconocida")


def read_case(case, time=None):
    reader = open_reader(case)
    times = sorted(reader.time_values)
    if not times:
        raise ValueError("No hay tiempos disponibles")
    selected = times[-1] if time is None else min(times, key=lambda t: abs(t-time))
    reader.set_active_time_value(selected)
    return internal_mesh(reader.read()), selected


def scalar_field(grid, field, component=None):
    # Vorticidad calculada sobre puntos si no fue guardada por OpenFOAM.
    if field == "vorticity" and field not in grid.cell_data:
        if "U" not in grid.cell_data:
            raise KeyError("Falta U para calcular vorticidad")
        grid = grid.cell_data_to_point_data(pass_cell_data=True)
        grid = grid.compute_derivative(scalars="U", gradient=False,
                                       vorticity="vorticity", preference="point")
        grid = grid.point_data_to_cell_data(pass_point_data=True)
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
    if "display" in grid.point_data:
        del grid.point_data["display"]
    return grid.cell_data_to_point_data(pass_cell_data=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", type=Path)
    p.add_argument("--field", default="U")
    p.add_argument("--component", type=int, choices=(0, 1, 2))
    p.add_argument("--time", type=float)
    p.add_argument("--list", action="store_true", help="Listar campos y tiempos")
    p.add_argument("--clim", nargs=2, type=float)
    p.add_argument("--origin", nargs=3, type=float)
    p.add_argument("--contour", type=float, help="Isosuperficie del campo seleccionado")
    p.add_argument("--normal", choices=("x", "y", "z"))
    p.add_argument("--output", type=Path)
    p.add_argument("--csv", type=Path)
    p.add_argument("--cmap", default="viridis")
    args = p.parse_args()
    grid, time = read_case(args.case, args.time)
    if args.list:
        print("Tiempos:", sorted(open_reader(args.case).time_values))
        print("Campos:", list(grid.cell_data.keys()))
        return
    grid = scalar_field(grid, args.field, args.component)
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(args.csv, np.column_stack((grid.cell_centers().points,
                   grid.cell_data["display"])), delimiter=",",
                   header="x,y,z,value", comments="")
    mesh = grid.slice(normal=args.normal, origin=args.origin) if args.normal else grid
    if args.contour is not None:
        mesh = mesh.contour([args.contour], scalars="display")
    if not mesh.n_points:
        p.error("El corte o contorno está vacío")
    plotter = pv.Plotter(off_screen=args.output is not None)
    plotter.add_mesh(mesh, scalars="display", cmap=args.cmap, clim=args.clim,
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
