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
cd cases/24-conduccion-de-calor-1d
foamVersion
command -v laplacianFoam
bash Allmesh
bash Allrun --solve-only
tail -n 40 log.laplacianFoam
foamToVTK
python3 ../../postprocessing/reference.py heat . --left 400 --right 300 --output plots/temperatura
bash Allclean
~~~

El caso incluye 0/T, constant/transportProperties, system/ con cuatro diccionarios, Allmesh, Allrun, Allclean, variants/README.md. El postproceso requiere numpy, matplotlib y pyvista; tras simular produce plots/temperatura.csv y plots/temperatura.png. No hay GIF porque es estacionario. Allclean --yes borra salidas pero preserva 0/.

**Chequeo estático:** variable T en K, DT en m²/s, extremos Dirichlet, laterales empty, malla 1D, referencia lineal. La sintaxis y convergencia no se han probado con el binario.

## Fuentes originales

- [Documentación oficial laplacianFoam](https://doc.openfoam.com/2312/tools/processing/solvers/rtm/basic/laplacianFoam/).
- [Conducción transitoria de pared, OpenFOAM.es](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam) — problema diferente: este caso es **estacionario**.

Geometría y archivos: elaboración didáctica propia.

## Criterio de revisión

DT se expresa con dimensiones explícitas de difusividad [m²/s]. La referencia de aceptación inicial es el error máximo absoluto frente al perfil lineal en centros de celda; una tolerancia propuesta de 0.01 K debe comprobarse con los resultados, no se considera alcanzada. Los dos pasos de solución son iteraciones, no segundos físicos.

## Referencia analítica común

El análisis se trasladó a `postprocessing/reference.py` del repositorio. Desde la raíz:

```bash
python postprocessing/reference.py heat runs/temperatura --left 400 --right 300 --output plots/temperatura
```

Adaptar la ruta y los parámetros físicos a la corrida. La longitud y sección se obtienen de los límites de la malla; se promedian los centros de cada sección por volumen. Esta comparación supone la geometría y condiciones de contorno descritas arriba. Exporta plots/temperatura.csv, un CSV de errores y una figura del último estado seleccionado. Sin ejecución ni validación nueva.
