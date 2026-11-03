"""Galería de la esfera monofásica: Matplotlib + PyVista, sin render OpenGL.

No ejecuta CFD. Asume la esfera de diámetro D, centro (0,0,0), flujo en +x.
Los campos derivados son aproximaciones posprocesadas; no se calculan fuerzas.
"""
from pathlib import Path
from datetime import datetime
from uuid import uuid4
import html
import json
import re
import warnings

import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle


_STYLE = {
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.labelcolor": "#334155", "text.color": "#0f172a",
    "figure.facecolor": "white", "axes.facecolor": "#f8fafc",
    "savefig.facecolor": "white", "grid.alpha": .18,
}


def _log_solver(case):
    candidates = sorted(case.glob("log.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        if not path.is_file():
            continue
        with path.open(errors="replace") as f:
            header = f.read(8192)
        if re.search(r"Exec\s*:\s*simpleFoam\b", header):
            return path
    return None


def _convergencia(path):
    residuals, continuity = {}, []
    iteration = None
    number = r"([+\-\d.eE]+)"
    with path.open(errors="replace") as source:
        lines = source.read().splitlines()
    for line in lines:
        match = re.match(r"Time\s*=\s*" + number, line)
        if match:
            iteration = float(match[1])
        match = re.search(r"Solving for (\w+), Initial residual = " + number, line)
        if match and iteration is not None:
            # Primera corrección por campo e iteración: evita mezclar las
            # distintas correcciones de presión en una sola curva.
            residuals.setdefault(match[1], {}).setdefault(iteration, float(match[2]))
        match = re.search(r"sum local = " + number + r", global = " + number, line)
        if match and iteration is not None:
            continuity.append((iteration, float(match[1]), float(match[2])))
    return residuals, np.asarray(continuity)


def graficar_esfera(case_dir, *, diametro=1.0, nu=1e-6, rho=1000.0,
                    resolucion=241, dpi=180, mostrar=True, interactivo=True):
    """Exportar figuras PNG/PDF, perfiles CSV, metadatos y galería HTML.

    U_inf y p_ref se obtienen de los patches inlet y outlet. rho se usa solo
    para convertir diferencias de presión cinemática a Pa; nu para Reynolds.
    El muestreo fino suaviza la presentación, no refina la solución CFD.
    """
    for name, value in (("diametro", diametro), ("nu", nu), ("rho", rho)):
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} debe ser positivo y finito")
    if not isinstance(resolucion, int) or not 41 <= resolucion <= 801:
        raise ValueError("resolucion debe ser un entero entre 41 y 801")
    case = Path(case_dir).resolve(strict=True)
    foam = case / "esfera-agua.foam"
    if not foam.is_file():
        raise FileNotFoundError(foam)
    reader = pv.OpenFOAMReader(str(foam))
    reader.enable_all_cell_arrays()
    reader.enable_all_patch_arrays()
    times = reader.time_values
    if not times or times[-1] <= 0:
        raise RuntimeError("Se necesita una solución posterior a la condición inicial")
    reader.set_active_time_value(times[-1])
    data = reader.read()
    raw = data["internalMesh"]
    for field in ("U", "p"):
        if field not in raw.cell_data:
            raise KeyError(f"Falta {field} en la solución")
        if not np.isfinite(raw.cell_data[field]).all():
            raise ValueError(f"{field} contiene valores no finitos")
    if "V" not in raw.cell_data:
        raise RuntimeError(
            "Falta el campo V. Ejecutar antes con foam_run: "
            "['postProcess', '-func', 'writeCellVolumes', '-latestTime']"
        )
    boundary = data["boundary"]
    inlet = boundary["inlet"].cell_data_to_point_data()
    outlet = boundary["outlet"].cell_data_to_point_data()
    solid = boundary["sphere"].cell_data_to_point_data().triangulate()
    u_inf = float(np.linalg.norm(np.mean(inlet.point_data["U"], axis=0)))
    if u_inf <= 0:
        raise ValueError("La velocidad media en inlet debe ser positiva")
    if not np.allclose(np.mean(inlet.point_data["U"], axis=0)[1:], 0, atol=u_inf*1e-6):
        raise ValueError("Esta galería supone flujo de entrada paralelo a +x")
    p_ref = float(np.mean(outlet.point_data["p"]))
    D, R = float(diametro), float(diametro) / 2
    if not np.allclose(solid.center, (0, 0, 0), atol=D*.02):
        raise ValueError("La galería supone una esfera centrada en el origen")
    if not np.isclose(np.max(np.linalg.norm(solid.points, axis=1)), R, rtol=.05):
        raise ValueError("diametro no coincide con el patch sphere")
    grid = raw.cell_data_to_point_data()
    grid.point_data["speed"] = np.linalg.norm(grid.point_data["U"], axis=1)
    grid = grid.compute_derivative(scalars="U", gradient="gradU",
                                   vorticity="omega", divergence="divU",
                                   preference="point")
    grad = np.asarray(grid.point_data["gradU"]).reshape(-1, 3, 3)
    strain = .5 * (grad + grad.transpose(0, 2, 1))
    grid.point_data["strain"] = np.sqrt(2 * np.sum(strain**2, axis=(1, 2)))
    grid.point_data["omega_mag"] = np.linalg.norm(grid.point_data["omega"], axis=1)
    bounds = np.asarray(grid.bounds).reshape(3, 2)
    output = case / "plots" / f"galeria-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:6]}"
    output.mkdir(parents=True)
    files, captions = {}, {}
    print(f"Iteración {times[-1]:g} · {raw.n_cells:,} celdas · Re={u_inf*D/nu:g}")
    print(f"Exportando en: {output}")

    def save(fig, name, caption):
        fig.suptitle(caption, fontsize=17, fontweight="bold")
        for ext in ("png", "pdf"):
            path = output / f"{name}.{ext}"
            fig.savefig(path, dpi=dpi, bbox_inches="tight")
            files[f"{name}_{ext}"] = path
        captions[name] = caption
        if mostrar:
            plt.show()
        plt.close(fig)
        print(f"  ✓ {name}", flush=True)

    def sample_plane(normal_axis):
        axes = [i for i in range(3) if i != normal_axis]
        a, b = axes
        xs = np.linspace(bounds[a, 0] + 1e-7*D, bounds[a, 1] - 1e-7*D, resolucion)
        ys = np.linspace(bounds[b, 0] + 1e-7*D, bounds[b, 1] - 1e-7*D, resolucion)
        X, Y = np.meshgrid(xs, ys)
        pts = np.zeros((X.size, 3)); pts[:, a] = X.ravel(); pts[:, b] = Y.ravel()
        sampled = pv.PolyData(pts).sample(grid)
        valid = np.asarray(sampled["vtkValidPointMask"], bool)
        valid &= np.linalg.norm(pts, axis=1) > R
        values = {}
        for name in ("U", "p", "omega", "omega_mag", "strain", "divU"):
            arr = np.asarray(sampled.point_data[name], dtype=float).copy()
            arr[~valid] = np.nan
            values[name] = arr.reshape((*X.shape, *arr.shape[1:]))
        values["speed"] = np.linalg.norm(values["U"], axis=-1)
        values["Cp"] = (values["p"] - p_ref) / (.5 * u_inf**2)
        values["pressure"] = rho * (values["p"] - p_ref)
        return X/D, Y/D, values, axes

    planes = {axis: sample_plane(axis) for axis in range(3)}
    X, Y, values, axes_xy = planes[2]
    names = ("x", "y", "z")

    def field(ax, plane, array, title, label, cmap="viridis", limits=None):
        x, y, _, axes = plane
        masked = np.ma.masked_invalid(array)
        if masked.count() == 0:
            raise RuntimeError(f"No hay datos válidos para {title}")
        lo, hi = limits if limits else (float(masked.min()), float(masked.max()))
        if hi <= lo:
            hi = lo + max(abs(lo)*1e-6, 1e-12)
        artist = ax.pcolormesh(x, y, masked, shading="auto", cmap=cmap,
                              vmin=lo, vmax=hi, rasterized=True)
        ax.add_patch(Circle((0, 0), .5, fc="#e2e8f0", ec="#334155", lw=1.2, zorder=5))
        ax.set(xlabel=f"{names[axes[0]]}/D", ylabel=f"{names[axes[1]]}/D",
               title=title, aspect="equal")
        ax.set_xlim(x.min(), x.max()); ax.set_ylim(y.min(), y.max())
        ax.figure.colorbar(artist, ax=ax, label=label, shrink=.8, pad=.025)
        return artist

    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(12, 8), layout="constrained")
        field(ax, planes[2], values["speed"]/u_inf, "Corte central z = 0", "|U| / U∞")
        ax.streamplot(X[0], Y[:, 0], np.ma.masked_invalid(values["U"][:, :, 0]/u_inf),
                      np.ma.masked_invalid(values["U"][:, :, 1]/u_inf),
                      color="white", density=1.7, linewidth=.65, arrowsize=.8,
                      broken_streamlines=False)
        save(fig, "01_flujo", "Agua alrededor de una esfera · velocidad y líneas de corriente")

        fig, axs = plt.subplots(1, 3, figsize=(18, 6), layout="constrained")
        vmax = max(np.nanmax(p[2]["speed"]/u_inf) for p in planes.values())
        for ax, axis, title in zip(axs, (2, 1, 0), ("XY · z = 0", "XZ · y = 0", "YZ · x = 0")):
            field(ax, planes[axis], planes[axis][2]["speed"]/u_inf, title,
                  "|U| / U∞", limits=(0, vmax))
        save(fig, "02_cortes", "Tres perspectivas del campo de velocidad · misma escala")

        fig, axs = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
        for ax, key, title, label in zip(axs, ("pressure", "Cp"),
                ("Presión relativa a la salida", "Coeficiente de presión"),
                ("ρ (p − p_salida) [Pa]", "Cp = 2 (p − p_salida) / U∞²")):
            lim = float(np.nanmax(np.abs(values[key])))
            field(ax, planes[2], values[key], title, label, "RdBu_r", (-lim, lim))
        save(fig, "03_presion", "Distribución de presión · corte central")

        fig, axs = plt.subplots(1, 3, figsize=(18, 6), layout="constrained")
        for i, ax in enumerate(axs):
            arr = values["U"][:, :, i]/u_inf
            lim = float(np.nanmax(np.abs(arr)))
            field(ax, planes[2], arr, f"Componente U{names[i]}", f"U{names[i]} / U∞",
                  "RdBu_r", (-lim, lim) if lim else (-1e-8, 1e-8))
        save(fig, "04_componentes", "Componentes del flujo · Uz debería ser pequeño por simetría")

        fig, axs = plt.subplots(1, 3, figsize=(18, 6), layout="constrained")
        for ax, key, title, label in zip(axs, ("omega_mag", "strain", "divU"),
                ("Magnitud de vorticidad", "Tasa de deformación", "Divergencia interpolada"),
                ("|ω| D / U∞", "√(2 S:S) D / U∞", "(∇·U) D / U∞")):
            arr = values[key] * D/u_inf
            lim = float(np.nanmax(np.abs(arr)))
            field(ax, planes[2], arr, title, label,
                  "RdBu_r" if key == "divU" else "magma",
                  (-lim, lim) if key == "divU" else (0, lim))
        save(fig, "05_derivados", "Gradientes posprocesados · sensibles a la resolución de malla")

        # Perfiles: sample() devuelve máscara; jamás convertir el sólido a ceros.
        def profile(points):
            sampled = pv.PolyData(points).sample(grid)
            valid = np.asarray(sampled["vtkValidPointMask"], bool)
            valid &= np.linalg.norm(points, axis=1) > R
            u = np.asarray(sampled["U"], float).copy(); u[~valid] = np.nan
            p = np.asarray(sampled["p"], float).copy(); p[~valid] = np.nan
            return u/u_inf, (p-p_ref)/(.5*u_inf**2)

        fig, axs = plt.subplots(1, 2, figsize=(14, 5), layout="constrained")
        xp = np.linspace(bounds[0, 0]+1e-5*D, bounds[0, 1]-1e-5*D, 800)
        pts = np.column_stack((xp, np.zeros_like(xp), np.zeros_like(xp)))
        up, cp = profile(pts)
        axs[0].plot(xp/D, up[:, 0], color="#0284c7", lw=2.3)
        axs[1].plot(xp/D, cp, color="#be123c", lw=2.3)
        for ax, ylabel in zip(axs, ("Ux / U∞", "Cp")):
            ax.axvspan(-.5, .5, color="#cbd5e1", alpha=.65, label="Interior sólido")
            ax.set(xlabel="x/D", ylabel=ylabel); ax.grid(); ax.legend()
        save(fig, "06_eje", "Perfiles en el eje de simetría · sin datos dentro de la esfera")
        np.savetxt(output/"perfil_axial.csv", np.column_stack((xp/D, up[:, 0], cp)),
                   delimiter=",", header="x_D,Ux_Uinf,Cp", comments="")

        fig, axs = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
        transverse_rows = []
        ys = np.linspace(bounds[1, 0]+1e-5*D, bounds[1, 1]-1e-5*D, 500)
        for x0 in (-1., -.65, 0., .65, 1., 1.5):
            if not bounds[0, 0] < x0*D < bounds[0, 1]:
                continue
            pts = np.column_stack((np.full_like(ys, x0*D), ys, np.zeros_like(ys)))
            u, cp = profile(pts)
            axs[0].plot(u[:, 0], ys/D, lw=1.8, label=f"x/D = {x0:g}")
            axs[1].plot(cp, ys/D, lw=1.8, label=f"x/D = {x0:g}")
            transverse_rows.extend(zip(np.full_like(ys, x0), ys/D, u[:, 0], cp))
        for ax, xlabel in zip(axs, ("Ux / U∞", "Cp")):
            ax.set(xlabel=xlabel, ylabel="y/D"); ax.grid(); ax.legend(fontsize=9)
        save(fig, "07_transversales", "Cómo cambia el flujo antes, alrededor y después de la esfera")
        np.savetxt(output/"perfiles_transversales.csv", transverse_rows, delimiter=",",
                   header="x_D,y_D,Ux_Uinf,Cp", comments="")

        coords = np.asarray(solid.points)
        radius = np.linalg.norm(coords, axis=1)
        theta = np.degrees(np.arccos(np.clip(-coords[:, 0]/radius, -1, 1)))
        cp_wall = (np.asarray(solid.point_data["p"])-p_ref)/(.5*u_inf**2)
        fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
        ax.scatter(theta, cp_wall, s=9, alpha=.25, color="#0284c7", label="Puntos del patch sphere")
        edges = np.linspace(0, 180, 25)
        centers, means = [], []
        for low, high in zip(edges[:-1], edges[1:]):
            sel = (theta >= low) & (theta <= high if high == 180 else theta < high)
            if np.any(sel):
                centers.append(.5*(low+high)); means.append(np.mean(cp_wall[sel]))
        ax.plot(centers, means, color="#be123c", lw=2, label="Media por banda angular (sin ponderar)")
        ax.set(xlabel="Ángulo desde el punto frontal [°]", ylabel="Cp", xlim=(0, 180))
        ax.grid(); ax.legend()
        save(fig, "08_presion_superficie", "Presión sobre la esfera · frontal 0° / posterior 180°")
        np.savetxt(output/"presion_superficie.csv", np.column_stack((theta, cp_wall)),
                   delimiter=",", header="theta_deg,Cp", comments="")

        section = raw.slice(normal="z", origin=(0, 0, 0))
        faces = section.faces; offset = 0; polygons = []
        while offset < len(faces):
            n = int(faces[offset]); ids = faces[offset+1:offset+1+n]
            polygons.append(section.points[ids, :2]/D); offset += n+1
        fig, axs = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
        for ax, zoom in zip(axs, (False, True)):
            ax.add_collection(PolyCollection(polygons, facecolors="#dbeafe", edgecolors="#475569", linewidths=.3))
            ax.add_patch(Circle((0, 0), .5, fc="#e2e8f0", ec="#334155", lw=1))
            ax.set(xlabel="x/D", ylabel="y/D", aspect="equal")
            ax.set_xlim((-.85, .85) if zoom else tuple(bounds[0]/D))
            ax.set_ylim((-.85, .85) if zoom else tuple(bounds[1]/D))
            ax.set_title("Detalle cercano a la pared" if zoom else "Corte completo")
        save(fig, "09_malla", "Malla real · polígonos sin triangulación artificial")

        volumes = np.asarray(raw.cell_data["V"])
        speeds = np.linalg.norm(raw.cell_data["U"], axis=1)/u_inf
        if np.any(volumes <= 0):
            raise RuntimeError("Se encontraron volúmenes de celda no positivos")
        fig, axs = plt.subplots(1, 2, figsize=(14, 5), layout="constrained")
        axs[0].hist(np.log10(volumes/D**3), bins=40, color="#0284c7", edgecolor="white")
        axs[0].set(xlabel="log₁₀(V_celda / D³)", ylabel="Número de celdas", title="Refinamiento volumétrico")
        axs[1].hist(speeds, bins=45, weights=100*volumes/volumes.sum(), color="#0d9488", edgecolor="white")
        axs[1].set(xlabel="|U| / U∞", ylabel="Fracción del volumen [% por intervalo]", title="Distribución de velocidad ponderada por volumen")
        save(fig, "10_distribuciones", "Distribución de tamaños de celda y velocidades del fluido")

        log = _log_solver(case)
        if log:
            residuals, continuity = _convergencia(log)
            fig, axs = plt.subplots(1, 2, figsize=(14, 5), layout="constrained")
            for field_name, observations in residuals.items():
                xx, yy = zip(*sorted(observations.items()))
                axs[0].semilogy(xx, np.maximum(yy, 1e-30), lw=1.6, label=field_name)
            axs[0].set(xlabel="Iteración SIMPLE", ylabel="Residual inicial", title="Primera corrección de cada iteración")
            axs[0].legend(); axs[0].grid()
            if continuity.size:
                axs[1].semilogy(continuity[:, 0], np.maximum(np.abs(continuity[:, 1]), 1e-30), label="Local")
                axs[1].semilogy(continuity[:, 0], np.maximum(np.abs(continuity[:, 2]), 1e-30), label="Global, valor absoluto")
                axs[1].legend()
            axs[1].set(xlabel="Iteración SIMPLE", ylabel="Error reportado por el solver", title="Continuidad · diagnóstico del log")
            axs[1].grid()
            save(fig, "11_convergencia", "Convergencia numérica · no representa una evolución física temporal")
        else:
            warnings.warn("No se encontró un log de simpleFoam; se omite convergencia")

    if interactivo:
        try:
            import plotly.graph_objects as go
        except ImportError:
            warnings.warn("Instalar plotly para exportar las dos vistas 3D interactivas")
        else:
            # Semillas deterministas aguas arriba. No requiere un contexto OpenGL.
            yz = np.linspace(-.9*D, .9*D, 7)
            yy, zz = np.meshgrid(yz, yz)
            seeds = pv.PolyData(np.column_stack((np.full(yy.size, bounds[0, 0]+.05*D), yy.ravel(), zz.ravel())))
            streams = grid.streamlines_from_source(seeds, vectors="U", integration_direction="forward",
                initial_step_length=.1, max_steps=3000, max_length=6*D,
                terminal_speed=u_inf*1e-7, compute_vorticity=False)
            triangles = solid.faces.reshape(-1, 4)[:, 1:]
            xyz = solid.points/D
            scene = dict(aspectmode="data", xaxis_title="x/D", yaxis_title="y/D", zaxis_title="z/D")
            f3 = go.Figure(go.Mesh3d(x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2],
                i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2], color="#94a3b8", name="Esfera"))
            connectivity = streams.lines; offset = 0; counter = 0
            while offset < len(connectivity):
                n = int(connectivity[offset]); ids = connectivity[offset+1:offset+1+n]; offset += n+1
                points = streams.points[ids]/D
                magnitude = np.linalg.norm(streams.point_data["U"][ids], axis=1)/u_inf
                f3.add_trace(go.Scatter3d(x=points[:, 0], y=points[:, 1], z=points[:, 2], mode="lines",
                    line=dict(color=magnitude, colorscale="Viridis", cmin=0, cmax=vmax,
                              width=4, showscale=counter == 0, colorbar=dict(title="|U|/U∞")),
                    showlegend=False, hovertemplate="x/D=%{x:.2f}<br>y/D=%{y:.2f}<br>z/D=%{z:.2f}<extra></extra>"))
                counter += 1
            f3.update_layout(title="Líneas de corriente 3D · solución estacionaria", scene=scene, template="plotly_white")
            path = output/"12_flujo_3d.html"; f3.write_html(path, include_plotlyjs=True)
            files["flujo_3d_html"] = path
            f3 = go.Figure(go.Mesh3d(x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2],
                i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2], intensity=cp_wall,
                colorscale="RdBu_r", colorbar=dict(title="Cp"), flatshading=False))
            f3.update_layout(title="Presión sobre la esfera · arrastrar para rotar", scene=scene, template="plotly_white")
            path = output/"13_presion_3d.html"; f3.write_html(path, include_plotlyjs=True)
            files["presion_3d_html"] = path
            print(f"  ✓ 3D interactivo: {counter} líneas de corriente")

    meta = {"caso": str(case), "iteracion": float(times[-1]), "celdas": raw.n_cells,
            "U_inf_m_s": u_inf, "diametro_m": D, "nu_m2_s": nu, "rho_kg_m3": rho,
            "Re": u_inf*D/nu, "p_ref_m2_s2": p_ref, "resolucion_grafica": resolucion,
            "pyvista": pv.__version__, "numpy": np.__version__,
            "nota": "Derivadas posprocesadas; el muestreo no añade resolución CFD. Sin validación de malla/dominio."}
    (output/"parametros.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    gallery = ['<!doctype html><html lang="es"><meta charset="utf-8"><title>Esfera · galería CFD</title>',
        '<style>body{font:16px system-ui;background:#f1f5f9;color:#0f172a;max-width:1250px;margin:40px auto;padding:20px}section{background:white;padding:24px;margin:24px 0;border-radius:16px}img{width:100%}a{color:#0369a1}</style>',
        f'<h1>Agua alrededor de una esfera</h1><p>Re = {meta["Re"]:g} · iteración {meta["iteracion"]:g} · {raw.n_cells:,} celdas.</p>',
        '<p>Solución estacionaria. Las derivadas son aproximaciones de posprocesado; no se ha establecido independencia de malla o dominio.</p>']
    for name, caption in captions.items():
        gallery.append(f'<section><h2>{html.escape(caption)}</h2><a href="{name}.pdf">PDF</a><img loading="lazy" src="{name}.png" alt="{html.escape(caption)}"></section>')
    for key in ("flujo_3d_html", "presion_3d_html"):
        if key in files:
            gallery.append(f'<p><a href="{files[key].name}">Abrir {html.escape(key)}</a></p>')
    gallery.append('</html>')
    index = output/"index.html"; index.write_text('\n'.join(gallery), encoding="utf-8")
    files["galeria_html"] = index
    files["directorio"] = output
    print(f"Galería: {index}")
    return files
