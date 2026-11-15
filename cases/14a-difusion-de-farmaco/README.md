# Difusión 1D desde un reservorio

Difusión de un soluto hipotético hacia un medio inmóvil, desde una fuente de concentración constante. El campo T representa C/C0 (adimensional), no temperatura.

## Configuración base

Solver: `scalarTransportFoam`. Longitud 2 mm, sección 0.1 × 0.1 mm, 200 × 1 × 1 celdas. DT=1e-9 m²/s, U=0, T inicial=0, fuente fija T=1, extremo impermeable. Simulación 200 s, paso 1 s, salida cada 20 s.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 14a-difusion-de-farmaco --output runs/difusion
bash scripts/run_docker.sh runs/difusion
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/T` | `internalField, source/value` | Concentración inicial y de fuente. Probar fuente 0.5; ajustar --source del análisis. |
| `constant/transportProperties` | `DT` | Difusividad. Probar 5e-10 m²/s; ajustar --diffusivity del análisis. |
| `0/U` | `internalField y contornos` | Mantener cero para difusión pura; advección invalida la referencia. |
| `system/blockMeshDict` | `vertices, blocks` | Longitud y resolución. Probar 400 × 1 × 1 celdas sin cambiar L. |
| `system/controlDict` | `deltaT, endTime, writeInterval` | Resolución temporal, duración y frecuencia de salida. Probar deltaT=0.5 s. |
| `system/fvSchemes` | `ddtSchemes, laplacianSchemes` | Discretización temporal y difusión. |

La evolución obedece ∂T/∂t = DT·∂²T/∂x². La escala difusiva L²/DT=4000 s. El análisis usa la solución de dominio finito con extremo de flujo nulo; la aproximación erfc es válida al comienzo. Para concentración real multiplicar T por C0. No implica permeabilidad, disolución ni metabolismo de un fármaco real.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/reference.py diffusion runs/difusion --diffusivity 1e-9 --gif --output plots/difusion
python postprocessing/statistics.py runs/difusion --field T
python postprocessing/plot_solver_log.py runs/difusion/log.scalarTransportFoam
```

Comprobar 0≤T≤1, acumulación monotónica y error del perfil respecto de la solución analítica. Configuración revisada estáticamente, sin nueva corrida.
