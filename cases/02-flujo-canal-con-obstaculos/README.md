# Canal con obstáculo rectangular

Flujo no newtoniano alrededor de un obstáculo fijo unido a la pared. Permite estudiar aceleración, recirculación y sensibilidad a la condición superficial.

## Configuración base

Solver: `simpleFoam`. Canal de 200 × 20 mm, obstáculo de 20 × 4 mm (20 % de bloqueo), 7840 celdas, espesor 1 mm. Entrada 0.01 m/s; powerLaw con n=0.5, k=1e-4, nuMin=1e-6 y nuMax=1e-2.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 02-flujo-canal-con-obstaculos --output runs/obstaculo
bash scripts/run_docker.sh runs/obstaculo
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `inlet/value, internalField` | Velocidad de entrada; reducir a 0.008 m/s. |
| `0/U` | `obstacle/type` | noSlip, slip o partialSlip. El patch es independiente de las paredes. |
| `constant/turbulenceProperties` | `n, k, límites de nu` | Controlan la viscosidad efectiva; variar n a 0.7. |
| `constant/transportProperties + turbulenceProperties` | `nu + laminar/model` | Para agua: nu=1e-6 y model Stokes; sustituir el bloque powerLaw. |
| `system/blockMeshDict` | `vertices, blocks` | Cambiar tamaño del objeto o resolución; conservar interfaces entre bloques. |
| `system/controlDict` | `endTime, writeInterval` | 1500 iteraciones, escritura cada 100; variante transient usa tiempo físico. |

Las recetas de [variantes](variants/README.md) cambian deslizamiento, agua o resolución. Para estudiar desprendimiento de vórtices usar `--variant transient` (pimpleFoam). Un patrón estacionario de recirculación no demuestra oscilación temporal. Con agua, Re basado en altura del objeto es 40.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/obstaculo --field U --normal z --streamlines
python postprocessing/fields.py runs/obstaculo --field vorticity --component 2 --normal z
python postprocessing/statistics.py runs/obstaculo --patch inlet outlet
python postprocessing/plot_solver_log.py runs/obstaculo/log.simpleFoam
```

Comparar velocidad axial negativa aguas abajo, presión y flujo normal en obstáculo. Existen corridas históricas del caso base y recetas anteriores; los scripts actuales no se reejecutaron.
