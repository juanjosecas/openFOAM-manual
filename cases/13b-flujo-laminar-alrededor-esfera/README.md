# Flujo laminar alrededor de una esfera

Flujo estacionario de agua alrededor de una esfera fija, para analizar estela, presión y sensibilidad a confinamiento y malla.

## Configuración base

Solver: `simpleFoam`. Radio 0.5 m, caja de −2 a 2 m en cada eje, 24³ celdas de fondo. Entrada 1e-5 m/s; nu=1e-6 m²/s; Re=10. Esfera noSlip y laterales slip. Superficie analítica searchableSphere.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 13b-flujo-laminar-alrededor-esfera --output runs/esfera
bash scripts/run_docker.sh runs/esfera
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `inlet/value, internalField` | Velocidad; probar 5e-6 o 5e-5 m/s (Re=5 o 50). |
| `constant/transportProperties` | `nu` | Viscosidad cinemática; cambia Re. |
| `system/snappyHexMeshDict` | `geometry/sphere/radius` | Radio; si se cambia actualizar diámetro del análisis. |
| `system/snappyHexMeshDict` | `refinementSurfaces/sphere/level` | Refinamiento local; probar (2 2) en vez de (1 2), revisar maxGlobalCells. |
| `system/blockMeshDict` | `vertices, blocks` | Confinamiento y refinamiento global; comparar caja ±4 m con 48³. |
| `system/snappyHexMeshDict` | `locationInMesh` | Punto dentro del fluido y fuera de la esfera; conservar coherencia al cambiar dominio. |
| `system/controlDict` | `endTime, writeInterval, purgeWrite` | 1500 iteraciones, escritura cada 100, conserva dos estados. |

Más ensayos en [variantes](variants/README.md). El bloqueo transversal es aproximadamente 4.9 % y no hay capas prismáticas. Re=10 está fuera del límite asintótico de Stokes; no usar Cd=24/Re como validación exacta.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/sphere.py runs/esfera --diameter 1 --nu 1e-6
python postprocessing/fields.py runs/esfera --field U --normal z --streamlines
python postprocessing/fields.py runs/esfera --field U --normal z --edges
python postprocessing/plot_solver_log.py runs/esfera/log.simpleFoam
```

Comparar perfiles adimensionales, Cp superficial y convergencia de malla y dominio. La configuración anterior con STL convergió en 171 iteraciones; la geometría analítica actual no fue reejecutada.
