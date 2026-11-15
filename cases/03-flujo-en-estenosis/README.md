# Flujo a través de una estenosis plana

Canal microscópico con estrechamiento simétrico. Se impone el caudal mediante velocidad de entrada y se calcula la presión necesaria para atravesar la garganta.

## Configuración base

Solver: `simpleFoam`. Longitud 100 µm, abertura 10 µm, garganta 5 µm en x=50 µm; espesor 1 µm, 4000 celdas. Entrada 0.5 mm/s, paredes rígidas noSlip; powerLaw con n=0.5 y k=1e-4.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 03-flujo-en-estenosis --output runs/estenosis
bash scripts/run_docker.sh runs/estenosis
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `inlet/value, internalField` | Velocidad inicial y de entrada; probar 0.0004 m/s. |
| `0/p` | `outlet/value` | Referencia de presión cinemática. |
| `constant/turbulenceProperties` | `n, k, nuMin, nuMax` | Reología efectiva; cotas 1e-6 a 1e-4 m²/s. |
| `system/blockMeshDict` | `vertices en x=40, 50, 60 µm` | Controlan forma y profundidad; modificar ambos planos z. En x=50 µm usar y=3 y 7 µm para una garganta de 4 µm. |
| `system/blockMeshDict` | `blocks` | Seis bloques; mantener compatible el número de celdas transversales en interfaces. |
| `system/fvSolution` | `SIMPLE, residualControl` | Criterios de convergencia estacionaria. |

Por continuidad, la velocidad media de garganta es aproximadamente 1 mm/s con la geometría base. La reducción de altura es 50 % en 2D; no representa una oclusión clínica de un vaso 3D. No hay eritrocitos, pared deformable ni calibración de viscosidad sanguínea.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/estenosis --field U --normal z
python postprocessing/fields.py runs/estenosis --field strain --normal z
python postprocessing/profile.py runs/estenosis --field U --component 0 --start 5e-5 2.6e-6 5e-7 --end 5e-5 7.4e-6 5e-7
python postprocessing/plot_solver_log.py runs/estenosis/log.simpleFoam
```

Comparar balance de caudal, velocidad de garganta y caída de presión; convertir p a Pa con una densidad explícita. Configuración revisada estáticamente. Referencia biológica: [Secomb y Pries, 2013](https://doi.org/10.1016/j.crhy.2013.04.002).
