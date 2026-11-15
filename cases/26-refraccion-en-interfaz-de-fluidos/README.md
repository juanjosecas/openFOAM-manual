# Refracción óptica sobre una interfaz móvil

El flujo agua–aire modifica la superficie de una cubeta. Un postprocesamiento independiente aplica la ley de Snell a la superficie estimada para dibujar rayos reflejados y transmitidos.

## Configuración base

Solver: `interFoam`. Cubeta 80 × 60 mm en x–z, espesor 1 mm en y, malla 80 × 1 × 60. Altura inicial de agua 40 mm a izquierda y 22 mm a derecha; gravedad (0 0 -9.81) m/s². Duración 0.15 s, salida 0.015 s.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 26-refraccion-en-interfaz-de-fluidos --output runs/refraccion
bash scripts/run_docker.sh runs/refraccion
```

Para modificar el modelo, editar la copia antes de ejecutar. Si cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado se puede usar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `system/setFieldsDict` | `regions/boxToCell/box` | Alturas de agua iniciales; probar 35 y 27 mm para reducir desnivel. |
| `constant/g` | `value` | Gravedad en z. |
| `constant/transportProperties` | `rho, nu, sigma` | Propiedades hidrodinámicas; no son índices de refracción. |
| `system/controlDict` | `endTime, writeInterval` | Duración y frecuencia de estados para el trazado. |
| `system/blockMeshDict` | `vertices, blocks` | Geometría y resolución. Si cambia, actualizar XMIN, XMAX, ZMAX, NX, NZ del trazador. |
| `postprocessing/trazar.py` | `--angulo, --azimut, --n-agua, --n-aire` | Parámetros ópticos sin recalcular el CFD. |
| `postprocessing/trazar.py` | `--x0, --y0, --z0, --tiempo` | Origen del rayo en metros y tiempo CFD seleccionado. |

La altura se estima como h(x,t)=∫alpha.water dz; la normal se obtiene a partir del gradiente de h. Snell: n₁ sin θ₁=n₂ sin θ₂. La aproximación supone interfaz univaluada, sin gotas o burbujas; el gráfico 3D extruye el CFD 2D y no resuelve electromagnetismo ni intensidades Fresnel.

## Resultados

Desde la raíz del repositorio, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python -m pip install -r cases/26-refraccion-en-interfaz-de-fluidos/postprocessing/requirements.txt
python cases/26-refraccion-en-interfaz-de-fluidos/postprocessing/trazar.py --caso runs/refraccion --gif
python cases/26-refraccion-en-interfaz-de-fluidos/postprocessing/trazar.py --caso runs/refraccion --angulo 35 --azimut 65 --n-agua 1.40
python postprocessing/fields.py runs/refraccion --field alpha.water --normal y --contour 0.5
python postprocessing/plot_solver_log.py runs/refraccion/log.interFoam
```

El trazador exporta CSV y PNG de superficie y rayos, además de GIF opcional. Comparar volumen inicial (2.48 mL), altura integrada e isosuperficie. El trazador y CFD no se han ejecutado.
