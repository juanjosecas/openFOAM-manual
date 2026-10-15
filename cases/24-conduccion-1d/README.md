# 24 — Conducción de calor estacionaria 1D

**Estado: archivos completos por revisión estática; no ejecutado ni validado.** Solver: laplacianFoam de OpenFOAM.com v2406/v2412 (ejecución por comprobar).

Barra matemática 1D: longitud L=0.02 m, 40×1×1 celdas. Los cuatro laterales usan empty, que elimina variaciones en y y z. Extremo x=0 a 400 K y extremo x=L a 300 K. Difusividad térmica DT=1e-5 m²/s (ilustrativa). Sin fuentes, convección ni radiación.

$$
\frac{\partial T}{\partial t}=D_T\frac{\partial^2 T}{\partial x^2},
\qquad T_{\mathrm{est}}(x)=400-100\frac{x}{0.02}\ \mathrm{K}.
$$

El esquema ddtSchemes=steadyState anula la derivada temporal: endTime no es tiempo físico. **DT no es conductividad térmica**; sin k [W/(m K)] no se calcula flujo térmico en W/m². El perfil lineal es la referencia exacta del problema continuo y puede compararse en centros de celda.

## Ejecución

~~~bash
cd cases/24-conduccion-1d
foamVersion
command -v laplacianFoam
bash Allmesh
bash Allrun
tail -n 40 log.laplacianFoam
foamToVTK
python3 postprocessing/analizar.py
bash Allclean
~~~

El caso incluye 0/T, constant/transportProperties, system/ con cuatro diccionarios, Allmesh, Allrun, Allclean, postprocessing/analizar.py y variants/README.md. El postproceso requiere numpy, matplotlib y pyvista; tras simular produce plots/temperatura.csv y plots/temperatura.png. No hay GIF porque es estacionario. Allclean --yes borra salidas pero preserva 0/.

**Chequeo estático:** variable T en K, DT en m²/s, extremos Dirichlet, laterales empty, malla 1D, referencia lineal. La sintaxis y convergencia no se han probado con el binario.

## Fuentes originales

- [Documentación oficial laplacianFoam](https://doc.openfoam.com/2312/tools/processing/solvers/rtm/basic/laplacianFoam/).
- [Conducción transitoria de pared, OpenFOAM.es](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam) — problema diferente: este caso es **estacionario**.

Geometría y archivos: elaboración didáctica propia.
