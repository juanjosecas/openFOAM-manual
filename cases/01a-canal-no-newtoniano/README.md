# Canal plano con fluido no newtoniano

Flujo laminar estacionario entre dos paredes paralelas. El fluido adelgaza por cizallamiento; interesa medir cómo cambian el perfil de velocidad y la caída de presión con la reología.

## Configuración base

Solver: `simpleFoam`. Canal de 200 × 20 mm, espesor de representación 1 mm, 200 × 40 × 1 celdas. Entrada uniforme 0.01 m/s; paredes noSlip; salida con presión de referencia. Modelo powerLaw, n=0.5, k=1e-4.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --output runs/canal
bash scripts/run_docker.sh runs/canal
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `internalField, inlet/value` | Velocidad inicial y de entrada (m/s). Probar 0.005 en vez de 0.01. |
| `0/p` | `outlet/value` | Referencia de presión cinemática; cambiarla desplaza el nivel de p. |
| `constant/turbulenceProperties` | `n, k, nuMin, nuMax` | n=0.5: adelgazamiento; probar 0.7. k fija la consistencia; los límites 1e-6 y 1e-2 acotan nu efectiva. |
| `constant/transportProperties` | `nu` | Viscosidad base; no desactiva powerLaw. |
| `system/blockMeshDict` | `vertices, blocks` | Dimensiones y resolución. Probar 100 × 20 × 1 o 400 × 80 × 1; mantener una celda z. |
| `system/controlDict` | `endTime, writeInterval` | Máximo 1000 iteraciones y escritura cada 100; no son segundos. |

Dentro de los límites de viscosidad, nu_eff = k·gammaDot^(n−1). El modelo newtoniano de referencia se obtiene con `--variant newtonian`, que aplica viscosidad constante sin cambiar la geometría. Comparar ambos a igual caudal; el perfil parabólico es la referencia plenamente desarrollada, no la entrada uniforme.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/canal --field U --normal z
python postprocessing/profile.py runs/canal --field U --component 0 --start 0.15 0.0001 0.0005 --end 0.15 0.0199 0.0005
python postprocessing/statistics.py runs/canal --patch inlet outlet
python postprocessing/plot_solver_log.py runs/canal/log.simpleFoam
```

Comparar perfil transversal, diferencia de presión y caudal; p es cinemática (m²/s²). La configuración actual está revisada estáticamente, sin nueva corrida.
