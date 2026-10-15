#!/usr/bin/env python3
"""Rayos 2D/3D y refraccion en interfaz plana z=0; sin solver CFD."""
import argparse
import csv
import math
from io import BytesIO
from pathlib import Path


def trazar(angulo=35.0, azimut=30.0, n1=1.0003, n2=1.333,
           desde="arriba", altura=0.02, longitud=0.03, x0=0.0, y0=0.0):
    """Segmentos (nombre, punto inicial, punto final), con unidades SI."""
    vals = (angulo, azimut, n1, n2, altura, longitud, x0, y0)
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("Los parametros deben ser finitos.")
    if not 0 <= angulo < 89.9:
        raise ValueError("Angulo fuera de [0, 89.9) grados.")
    if min(n1, n2, altura, longitud) <= 0:
        raise ValueError("Indices y longitudes deben ser positivos.")
    if desde not in ("arriba", "abajo"):
        raise ValueError("desde debe ser arriba o abajo.")
    signo = 1 if desde == "arriba" else -1
    theta, phi = math.radians(angulo), math.radians(azimut)
    st, ct = math.sin(theta), math.cos(theta)
    cp, sp = math.cos(phi), math.sin(phi)
    inicio = (x0, y0, signo * altura)
    choque = (x0 + altura * math.tan(theta) * cp,
              y0 + altura * math.tan(theta) * sp, 0.0)
    reflejado = (choque[0] + longitud * st * cp,
                 choque[1] + longitud * st * sp,
                 signo * longitud * ct)
    segmentos = [("incidente", inicio, choque),
                 ("reflejado", choque, reflejado)]
    sen2 = n1 / n2 * st
    rit = sen2 > 1.0 + 1e-12
    theta2 = None
    if not rit:
        sen2 = min(sen2, 1.0)
        theta2 = math.degrees(math.asin(sen2))
        refractado = (choque[0] + longitud * sen2 * cp,
                      choque[1] + longitud * sen2 * sp,
                      -signo * longitud * math.sqrt(max(0, 1 - sen2 * sen2)))
        segmentos.append(("refractado", choque, refractado))
    return dict(segmentos=segmentos, angulo=angulo, azimut=azimut, n1=n1,
                n2=n2, desde=desde, angulo_refractado=theta2, rit=rit)


def s(p, azimut):
    phi = math.radians(azimut)
    return p[0] * math.cos(phi) + p[1] * math.sin(phi)


def guardar_csv(r, ruta, modo, pasos=60):
    if pasos < 2:
        raise ValueError("pasos debe ser >= 2.")
    with Path(ruta).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["modo", "rama", "punto", "x_m", "y_m", "z_m", "s_m",
                    "n1", "n2", "angulo_incidente_deg",
                    "angulo_refractado_deg", "reflexion_interna_total"])
        for nombre, a, b in r["segmentos"]:
            for i in range(pasos + 1):
                t = i / pasos
                p = tuple(u + t * (v - u) for u, v in zip(a, b))
                w.writerow([modo, nombre, i, *p, s(p, r["azimut"]),
                            r["n1"], r["n2"], r["angulo"],
                            r["angulo_refractado"] if not r["rit"] else "",
                            r["rit"]])


def figura(r, modo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(8, 6))
    colores = {"incidente": "darkorange", "reflejado": "gray",
               "refractado": "dodgerblue"}
    puntos = [p for _, a, b in r["segmentos"] for p in (a, b)]
    if modo == "2d":
        ax = fig.add_subplot(111)
        for nombre, a, b in r["segmentos"]:
            ax.plot([s(a, r["azimut"]), s(b, r["azimut"])],
                    [a[2], b[2]], lw=2.7, color=colores[nombre],
                    label=nombre)
        ss = [s(p, r["azimut"]) for p in puntos]
        zz = [p[2] for p in puntos]
        ds = max(max(ss) - min(ss), 0.005)
        dz = max(max(zz) - min(zz), 0.005)
        ax.set_xlim(min(ss) - .15 * ds, max(ss) + .15 * ds)
        ax.set_ylim(min(zz) - .15 * dz, max(zz) + .15 * dz)
        ax.axhline(0, color="black", lw=1)
        ax.axhspan(ax.get_ylim()[0], 0, color="lightskyblue", alpha=.12)
        ax.set_xlabel("s en el plano de incidencia [m]")
        ax.set_ylabel("z [m]")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=.2)
    elif modo == "3d":
        ax = fig.add_subplot(111, projection="3d")
        for nombre, a, b in r["segmentos"]:
            ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]],
                    lw=2.7, color=colores[nombre], label=nombre)
        xs, ys, zs = zip(*puntos)
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        d = max(max(xs) - min(xs), max(ys) - min(ys), .015) * .75
        vertices = [(cx-d, cy-d, 0), (cx+d, cy-d, 0),
                    (cx+d, cy+d, 0), (cx-d, cy+d, 0)]
        ax.add_collection3d(Poly3DCollection([vertices],
                            facecolors="lightskyblue", alpha=.22))
        ax.set_xlim(cx-d, cx+d)
        ax.set_ylim(cy-d, cy+d)
        zmin, zmax = min(zs), max(zs)
        dz = max(zmax - zmin, .01) * .12
        ax.set_zlim(zmin-dz, zmax+dz)
        ax.set_box_aspect((2*d, 2*d, zmax-zmin+2*dz))
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.set_zlabel("z [m]")
        ax.view_init(elev=25, azim=-60)
    else:
        raise ValueError("modo debe ser 2d o 3d")
    salida = ("reflexion interna total" if r["rit"] else
              f"theta2={r['angulo_refractado']:.2f} grados")
    ax.set_title(f"Snell {modo.upper()}: n1={r['n1']}, n2={r['n2']}\n"
                 f"theta1={r['angulo']:.1f} grados, "
                 f"azimut={r['azimut']:.1f} grados; {salida}")
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def gif_barrido(p, modo, ruta, fotogramas):
    """Barrido parametrico de angulo; NO es evolucion en tiempo fisico."""
    if not 2 <= fotogramas <= 120:
        raise ValueError("fotogramas debe estar entre 2 y 120.")
    from PIL import Image
    import matplotlib.pyplot as plt
    frames = []
    for i in range(fotogramas):
        q = dict(p, angulo=75.0 * i / (fotogramas - 1))
        fig = figura(trazar(**q), modo)
        b = BytesIO()
        fig.savefig(b, format="png", dpi=85)
        plt.close(fig)
        b.seek(0)
        with Image.open(b) as img:
            frames.append(img.convert("RGB"))
    frames[0].save(ruta, save_all=True, append_images=frames[1:],
                   duration=160, loop=0)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--modo", choices=("2d", "3d", "ambos"), default="ambos")
    p.add_argument("--angulo", type=float, default=35.0)
    p.add_argument("--azimut", type=float, default=30.0)
    p.add_argument("--n1", type=float, default=1.0003)
    p.add_argument("--n2", type=float, default=1.333)
    p.add_argument("--desde", choices=("arriba", "abajo"), default="arriba")
    p.add_argument("--altura", type=float, default=.02)
    p.add_argument("--longitud", type=float, default=.03)
    p.add_argument("--x0", type=float, default=0.0)
    p.add_argument("--y0", type=float, default=0.0)
    p.add_argument("--pasos", type=int, default=60)
    p.add_argument("--salida", type=Path, default=Path("plots"))
    p.add_argument("--gif", action="store_true")
    p.add_argument("--fotogramas", type=int, default=20)
    a = p.parse_args()
    params = dict(angulo=a.angulo, azimut=a.azimut, n1=a.n1, n2=a.n2,
                  desde=a.desde, altura=a.altura, longitud=a.longitud,
                  x0=a.x0, y0=a.y0)
    try:
        r = trazar(**params)
        a.salida.mkdir(parents=True, exist_ok=True)
        modos = ("2d", "3d") if a.modo == "ambos" else (a.modo,)
        for modo in modos:
            csv_ruta = a.salida / f"trayectoria_{modo}.csv"
            png_ruta = a.salida / f"trayectoria_{modo}.png"
            guardar_csv(r, csv_ruta, modo, a.pasos)
            fig = figura(r, modo)
            fig.savefig(png_ruta, dpi=150)
            import matplotlib.pyplot as plt
            plt.close(fig)
            print(f"{modo}: {csv_ruta} | {png_ruta}")
            if a.gif:
                gif_ruta = a.salida / f"barrido_{modo}.gif"
                gif_barrido(params, modo, gif_ruta, a.fotogramas)
                print(f"Barrido (no tiempo fisico): {gif_ruta}")
        if r["rit"]:
            print("Reflexion interna total: no hay rayo refractado.")
        else:
            print(f"Angulo refractado: {r['angulo_refractado']:.6f} grados")
    except (ValueError, ImportError) as e:
        p.error(str(e))


if __name__ == "__main__":
    main()
