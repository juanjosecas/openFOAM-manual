# Flujo pulsátil en una tubería 3D

Una tubería rígida recibe un flujo laminar cuya velocidad de entrada cambia con el tiempo. Interesa estudiar la respuesta del perfil radial y la presión a la pulsación.

## Configuración base

Solver: `pimpleFoam`. Longitud 0.12 m, radio 0.01 m, nu=1e-4 m²/s, 12288 celdas en cinco bloques. Velocidad máxima 0.02 m/s (Re=4), duración 2 s.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 08-flujo-en-tuberia-3d --output runs/tuberia
bash scripts/run_docker.sh runs/tuberia
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `inlet/uniformValue table` | Pares tiempo (s), vector velocidad (m/s); cambiar máximos 0.020 a 0.015 o modificar los instantes. |
| `constant/transportProperties` | `nu` | Controla difusión viscosa y Reynolds. |
| `system/blockMeshDict` | `vertices, arcs, blocks` | Longitud, radio y resolución de la sección circular; conservar arcos e interfaces. |
| `system/controlDict` | `deltaT, maxCo, maxDeltaT` | Paso inicial 0.001 s, Co máximo 0.5 y techo 0.005 s; reducir maxCo a 0.25. |
| `system/controlDict` | `endTime, writeInterval` | 2 s y salida cada 0.01 s; duplicar intervalo reduce archivos, no aumenta paso de cálculo. |
| `system/fvSolution` | `PIMPLE` | Correcciones de presión y velocidad por paso. |

La tabla prescribe velocidad uniforme en la sección de entrada, no un perfil parabólico. Hagen–Poiseuille no es una solución exacta para todo el arranque pulsátil. Al extender endTime, extender también la tabla si se quiere mantener la pulsación.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/tuberia --field U --normal z
python postprocessing/animate.py runs/tuberia --field U --normal z --output plots/tuberia.gif
python postprocessing/statistics.py runs/tuberia --patch inlet outlet
python postprocessing/plot_solver_log.py runs/tuberia/log.pimpleFoam
```

Comparar caudal, perfil radial, desfase temporal y Courant. Configuración revisada estáticamente, sin nueva corrida.
