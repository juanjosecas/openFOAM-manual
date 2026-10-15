# Caso 26 · OpenFOAM: refracción sobre una superficie de agua móvil

**Dos etapas:** (1) OpenFOAM `interFoam` calcula el movimiento del agua y el aire en una cubeta; (2) Python lee el campo CFD `alpha.water`, aproxima la superficie `z=h(x,t)` y aplica la ley de Snell para dibujar un rayo incidente, uno reflejado y otro transmitido en **2D y 3D**.

**Estado:** estructura y fórmulas revisadas estáticamente. **No se ha ejecutado OpenFOAM ni el postprocesamiento**; compatibilidad efectiva con OpenFOAM.com v2406/v2412 pendiente de prueba. El modelo es didáctico, no óptica de precisión.

## Física

**CFD:** flujo incompresible bifásico agua–aire, método VOF; `alpha.water=1` agua y `0` aire. Gravedad $\mathbf g=(0,0,-9.81)$ m/s². La cubeta mide 80 mm de ancho por 60 mm de alto, espesor numérico de 1 mm; la malla es **80×1×60** y `frontAndBack` es `empty`. Al principio hay 40 mm de agua a la izquierda y 22 mm a la derecha, inicializados con `setFields`. Las paredes laterales e inferior son `noSlip`; la superficie superior comunica con la atmósfera.

**Óptica:** en cada columna vertical, la altura efectiva se estima como

$$
h(x,t)\approx\int_0^{0.06\,\mathrm{m}}\alpha_{\mathrm{water}}(x,z,t)\,\mathrm dz.
$$

Es una **aproximación de columna**, no una extracción exacta de la isosuperficie $\alpha=0.5$. Supone una superficie univaluada sin gotas, salpicaduras, burbujas ni olas que vuelquen. Se suavizan cinco columnas para calcular la normal local:

$$
\mathbf n=\frac{(-\partial h/\partial x,\ 0,\ 1)}
{\sqrt{1+(\partial h/\partial x)^2}}.
$$

El rayo incidente viene desde el aire; se busca su primera intersección con `h(x,t)` y se aplica la ley de Snell:

$$
n_{\mathrm{aire}}\sin\theta_{\mathrm{aire}}
=n_{\mathrm{agua}}\sin\theta_{\mathrm{agua}}.
$$

Los índices ilustrativos son $n_{\mathrm{aire}}=1.0003$ y $n_{\mathrm{agua}}=1.333$ (adimensionales). Se calcula la reflexión especular y la dirección refractada mediante Snell vectorial. **No se calculan intensidades de Fresnel, absorción, polarización, dispersión cromática ni ondas electromagnéticas.** El campo óptico no influye sobre el CFD.

**2D/3D:** OpenFOAM resuelve **solo CFD 2D**. El gráfico 3D extruye esa misma superficie en la dirección y y permite un rayo con azimut distinto de cero; **no** es una simulación hidrodinámica 3D.

## Archivos

```text
cases/26-refraccion-interfoam/
├── 0/{U,p_rgh,alpha.water}
├── constant/{g,transportProperties,turbulenceProperties}
├── system/{blockMeshDict,setFieldsDict,controlDict,fvSchemes,fvSolution}
├── Allmesh, Allrun, Allclean
├── postprocessing/{trazar.py,requirements.txt,test_trazar.py}
├── variants/README.md
└── README.md
```

## Comandos exactos

En una terminal con **OpenFOAM.com v2406 o v2412 cargado**:

```bash
cd cases/26-refraccion-interfoam
bash Allmesh       # blockMesh y checkMesh
setFields          # prepara alpha.water en tiempo 0
interFoam | tee log.interFoam
```

O, desde un caso limpio, todo el CFD de una vez:

```bash
bash Allrun        # blockMesh, checkMesh, setFields, interFoam
```

El cálculo termina en 0.15 s de tiempo físico, con estados cada 0.015 s. Si se desea repetir desde cero:

```bash
bash Allclean       # previsualización
bash Allclean --yes # borra resultados y malla; conserva 0/
bash Allrun
```

Para el trazado de rayos y gráficos, en Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r postprocessing/requirements.txt
python3 -m unittest discover -s postprocessing -p 'test_*.py' -v
python3 postprocessing/trazar.py --gif
```

La opción `--gif` genera una **animación basada en los tiempos físicos guardados por OpenFOAM** (no es un barrido artificial de ángulo). Puede omitirse para generar solo los CSV y PNG del último estado.

## Jugar con el rayo

```bash
# Cambiar angulo de incidencia respecto a la vertical (grados)
python3 postprocessing/trazar.py --angulo 10

# Cambiar azimut para mostrar una trayectoria espacial
python3 postprocessing/trazar.py --angulo 35 --azimut 65

# Cambiar el indice de refraccion del agua, sin recalcular CFD
python3 postprocessing/trazar.py --n-agua 1.40

# Elegir el tiempo CFD guardado mas cercano a 0.06 s
python3 postprocessing/trazar.py --tiempo 0.06

# Cambiar el punto emisor [m]
python3 postprocessing/trazar.py --x0 -0.025 --z0 0.055
```

El script busca el primer impacto. Si el emisor está bajo la superficie, el rayo sale del dominio o no intersecta el agua, muestra un error en lugar de inventar un rayo.

## Resultados

`plots/superficie.csv`: `x_m`, `h_agua_m`, `tiempo_s`. `plots/rayos_2d.csv` y `plots/rayos_3d.csv`: puntos de cada rama en metros. `plots/rayos_2d.png` y `plots/rayos_3d.png`: gráficos con interfaz y rayos. `plots/evolucion_2d.gif`: evolución temporal opcional. El CSV se puede abrir en ParaView, pandas, LibreOffice o PyVista; `case.foam` permite inspeccionar los campos CFD en ParaView/PyVista.

## Variantes y comprobación

Consultar [variants/README.md](variants/README.md). `postprocessing/test_trazar.py` contiene comprobaciones matemáticas independientes de OpenFOAM para Snell, reflexión interna total, superficie plana y altura integrada; **no se han ejecutado**. No sustituyen una prueba real de `interFoam`, de PyVista ni de estabilidad numérica. No se realizó análisis de convergencia de malla.

**Advertencia importante:** el cálculo de `h(x)` usa exactamente la malla 80×1×60; si se cambia `blockMeshDict`, adaptar `NX`, `NZ`, `DX`, `DZ` en `postprocessing/trazar.py`. Los índices ópticos son independientes de `transportProperties`: `nu` [m²/s], `rho` [kg/m³] y `sigma` [N/m] son propiedades CFD, no índices de refracción.

## Procedencia y referencias

Caso y trazador originales para el manual, basados en el esquema general de `interFoam` de los casos 04 y 11 del repositorio, **sin copiar código de terceros**. Referencias de consulta:

- Estructura de casos OpenFOAM: https://www.openfoam.com/documentation/user-guide/2-openfoam-cases/2.1-file-structure-of-openfoam-cases
- Solver `interFoam` (documentación): https://www.openfoam.com/documentation/guides/latest/doc/guide-applications-solvers-multiphase-interFoam.html
- PyVista OpenFOAMReader: https://docs.pyvista.org/api/readers/_autosummary/pyvista.OpenFOAMReader.html
- Ley de Snell: https://en.wikipedia.org/wiki/Snell%27s_law
- [Caso 25: óptica geométrica sin CFD](../25-refraccion-luz/README.md)

Las URL no demuestran por sí solas compatibilidad con una versión determinada. No se ha probado el caso en v2406/v2412.
