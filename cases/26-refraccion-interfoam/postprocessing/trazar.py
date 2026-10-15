#!/usr/bin/env python3
"""Lee alpha.water de interFoam y refracta rayos 2D/3D sobre h(x).

h(x) = integral alpha.water(x,z) dz (columna de agua).
Solo vale para superficie z=h(x), sin roturas, gotas ni voladizos.
"""
import argparse
import csv
import math
from io import BytesIO
from pathlib import Path
import numpy as np

NX, NZ = 80, 60
XMIN, XMAX, ZMAX = -.04, .04, .06
DX, DZ = (XMAX-XMIN)/NX, ZMAX/NZ
X = XMIN+(np.arange(NX)+.5)*DX


def altura(centros, alpha):
    if len(centros) != NX*NZ or len(alpha) != NX*NZ:
        raise ValueError("Malla distinta de 80x1x60; adaptar postprocesamiento.")
    ix = np.clip(np.floor((centros[:,0]-XMIN)/DX).astype(int), 0, NX-1)
    if not np.all(np.bincount(ix, minlength=NX) == NZ):
        raise ValueError("Malla no estructurada en columnas.")
    return np.bincount(ix, weights=np.clip(alpha, 0, 1)*DZ, minlength=NX)


def snell(d, n, n1, n2):
    """n apunta desde agua al aire; d incide desde el aire."""
    d, n = np.asarray(d, float), np.asarray(n, float)
    d, n = d/np.linalg.norm(d), n/np.linalg.norm(n)
    c = -np.dot(d, n)
    if c <= 0:
        raise ValueError("Direccion incidente incorrecta.")
    eta = n1/n2
    k = 1-eta**2*(1-c**2)
    reflejado = d+2*c*n
    transmitido = None if k < -1e-12 else eta*d+(eta*c-np.sqrt(max(0,k)))*n
    return reflejado, transmitido


def rayos(h, angulo=25, azimut=35, n1=1.0003, n2=1.333,
          x0=-.025, y0=0, z0=.055, largo=.02):
    if not 0 <= angulo < 89 or min(n1,n2,largo) <= 0:
        raise ValueError("Angulo/indices/longitud fuera de rango.")
    if not X[0] <= x0 <= X[-1] or not 0 < z0 <= ZMAX:
        raise ValueError("Emisor fuera de dominio.")
    suave = np.convolve(np.pad(h, (2,2), mode="edge"),
                        np.ones(5)/5, mode="valid")
    dhdx = np.gradient(suave, DX)
    teta, phi = np.radians([angulo, azimut])
    d = np.array([np.sin(teta)*np.cos(phi),
                  np.sin(teta)*np.sin(phi), -np.cos(teta)])
    origen = np.array([x0, y0, z0])
    def f(t):
        p = origen+t*d
        return None if not X[0] <= p[0] <= X[-1] else p[2]-np.interp(p[0],X,suave)
    previo, fp = 0., f(0.)
    if fp is None or fp <= 0:
        raise ValueError("Emisor debe estar en aire, por encima de la superficie.")
    intervalo = None
    for t in np.linspace(0, .09, 901)[1:]:
        ft = f(t)
        if ft is None:
            break
        if ft <= 0 < fp:
            intervalo = (previo, t)
            break
        previo, fp = t, ft
    if intervalo is None:
        raise ValueError("No hay impacto: cambiar angulo o posicion.")
    a,b = intervalo
    for _ in range(40):
        m=(a+b)/2
        if f(m)>0: a=m
        else: b=m
    impacto=origen+(a+b)/2*d
    pendiente=np.interp(impacto[0],X,dhdx)
    normal=np.array([-pendiente,0,1.])
    normal/=np.linalg.norm(normal)
    refl, trans=snell(d,normal,n1,n2)
    ramas=[("incidente",origen,impacto),
           ("reflejado",impacto,impacto+largo*refl)]
    if trans is not None:
        ramas.append(("refractado",impacto,impacto+largo*trans))
    return ramas,impacto,normal


def leer(reader, tiempo):
    reader.set_active_time_value(float(tiempo))
    data=reader.read()
    try:
        grid=data["internalMesh"]
    except (KeyError,TypeError):
        raise RuntimeError("No se encuentra internalMesh en archivo .foam.")
    if "alpha.water" not in grid.cell_data:
        raise RuntimeError("Falta alpha.water en cell_data.")
    return altura(grid.cell_centers().points,
                  np.asarray(grid.cell_data["alpha.water"]))


def figura(h, ramas, modo, tiempo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig=plt.figure(figsize=(8,5.5))
    colores={"incidente":"darkorange","reflejado":"gray",
             "refractado":"dodgerblue"}
    if modo=="2d":
        ax=fig.add_subplot(111)
        ax.fill_between(X,0,h,color="lightskyblue",alpha=.35)
        ax.plot(X,h,color="navy",lw=2,label="superficie CFD")
        for nombre,a,b in ramas:
            ax.plot([a[0],b[0]],[a[2],b[2]],color=colores[nombre],
                    lw=2.5,label=nombre)
        ax.set_xlim(XMIN,XMAX)
        ax.set_ylim(0,ZMAX)
        ax.set_aspect("equal",adjustable="box")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("z [m]")
    else:
        ax=fig.add_subplot(111,projection="3d")
        xx,yy=np.meshgrid(X,np.linspace(-.025,.025,8))
        ax.plot_surface(xx,yy,np.broadcast_to(h,xx.shape),
                        color="lightskyblue",alpha=.4,shade=False)
        for nombre,a,b in ramas:
            ax.plot([a[0],b[0]],[a[1],b[1]],[a[2],b[2]],
                    color=colores[nombre],lw=2.5,label=nombre)
        ax.set_xlim(XMIN,XMAX)
        ax.set_ylim(-.025,.025)
        ax.set_zlim(0,ZMAX)
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m] (extrusion optica)")
        ax.set_zlabel("z [m]")
        ax.view_init(elev=23,azim=-65)
    ax.set_title(f"interFoam + Snell | t={tiempo:.4g} s | {modo.upper()}")
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def guardar_ramas(ramas,ruta):
    with ruta.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["rama","punto","x_m","y_m","z_m"])
        for nombre,a,b in ramas:
            for i in range(61):
                w.writerow([nombre,i,*(a+(b-a)*i/60)])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--caso",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--tiempo",type=float,default=None)
    p.add_argument("--angulo",type=float,default=25)
    p.add_argument("--azimut",type=float,default=35)
    p.add_argument("--n-aire",type=float,default=1.0003)
    p.add_argument("--n-agua",type=float,default=1.333)
    p.add_argument("--x0",type=float,default=-.025)
    p.add_argument("--y0",type=float,default=0)
    p.add_argument("--z0",type=float,default=.055)
    p.add_argument("--largo",type=float,default=.02)
    p.add_argument("--gif",action="store_true",help="evolucion de tiempos CFD")
    a=p.parse_args()
    try:
        import pyvista as pv
        import matplotlib.pyplot as plt
        from PIL import Image
    except ImportError as e:
        p.error(f"Instalar requirements.txt: {e}")
    caso=a.caso.resolve()
    if not (caso/"constant/polyMesh").is_dir():
        p.error("Falta malla. Ejecutar bash Allrun primero.")
    marcador=caso/"case.foam"
    marcador.touch(exist_ok=True)
    reader=pv.OpenFOAMReader(str(marcador))
    tiempos=sorted(float(t) for t in reader.time_values)
    if not tiempos:
        p.error("No se encontraron tiempos CFD.")
    t=tiempos[-1] if a.tiempo is None else min(tiempos,key=lambda v:abs(v-a.tiempo))
    out=caso/"plots"
    out.mkdir(exist_ok=True)
    def calcular(ti):
        h=leer(reader,ti)
        ramas,impacto,normal=rayos(
            h,a.angulo,a.azimut,a.n_aire,a.n_agua,a.x0,a.y0,a.z0,a.largo)
        return h,ramas,impacto,normal
    try:
        h,ramas,impacto,normal=calcular(t)
        with (out/"superficie.csv").open("w",newline="") as f:
            w=csv.writer(f)
            w.writerow(["x_m","h_agua_m","tiempo_s"])
            w.writerows(zip(X,h,np.full(NX,t)))
        for modo in ("2d","3d"):
            guardar_ramas(ramas,out/f"rayos_{modo}.csv")
            fig=figura(h,ramas,modo,t)
            fig.savefig(out/f"rayos_{modo}.png",dpi=150)
            plt.close(fig)
        print(f"Tiempo: {t:g} s; impacto: {impacto}; normal: {normal}")
        if a.gif:
            cuadros=[]
            for ti in tiempos:
                try:
                    hi,ri,_,_=calcular(ti)
                except ValueError as e:
                    print(f"Tiempo omitido {ti:g}: {e}")
                    continue
                fig=figura(hi,ri,"2d",ti)
                buf=BytesIO()
                fig.savefig(buf,format="png",dpi=85)
                plt.close(fig)
                buf.seek(0)
                with Image.open(buf) as img:
                    cuadros.append(img.convert("RGB"))
            if not cuadros:
                raise ValueError("No hay fotogramas validos.")
            cuadros[0].save(out/"evolucion_2d.gif",save_all=True,
                            append_images=cuadros[1:],duration=200,loop=0)
        print(f"Archivos en: {out}")
    except (ValueError,RuntimeError) as e:
        p.error(str(e))


if __name__=="__main__":
    main()
