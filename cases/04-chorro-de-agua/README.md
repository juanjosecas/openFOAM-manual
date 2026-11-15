# Chorro de agua en aire

Un chorro horizontal entra en un dominio inicialmente lleno de aire. El método VOF sigue la interfaz entre ambas fases.

## Configuración base

Solver: `interFoam`. Dominio 300 × 200 mm, espesor 1 mm, 9600 celdas. Entrada de altura 10 mm a 1 m/s; agua con nu=1e-6 m²/s, rho=1000 kg/m³; aire con nu=1.5e-5 m²/s, rho=1.2 kg/m³; sigma=0.072 N/m.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 04-chorro-de-agua --output runs/chorro
bash scripts/run_docker.sh runs/chorro
```

Para modificar el modelo, editar la copia antes de ejecutar. Si cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado se puede usar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `waterInlet/value` | Velocidad de entrada: probar (0.8 0 0). |
| `0/alpha.water` | `internalField, waterInlet/value` | 0 es aire y 1 es agua. Mantener dominio inicialmente en aire y entrada en agua; no necesita setFields. |
| `0/p_rgh` | `atmosphere` | Presión modificada por gravedad; mantener salida abierta coherente con U y alpha. |
| `constant/transportProperties` | `water/nu, water/rho, air/nu, air/rho, sigma` | Viscosidades, densidades y tensión superficial; sigma afecta curvatura y fragmentación. |
| `constant/g` | `value` | Dirección y magnitud de gravedad. |
| `system/blockMeshDict` | `vertices, blocks` | Altura de entrada y resolución; conservar patches y una celda de espesor. |
| `system/controlDict` | `deltaT, maxCo, maxAlphaCo, endTime, writeInterval` | Paso inicial 1e-5 s, límites 0.35, duración 20 s, salida cada 0.005 s. Probar endTime=0.5 s antes de una corrida larga. |

La variante animation cambia la escritura a 0.02 s. Prepararla con --variant animation. El Reynolds basado en altura de entrada es 10000; el modelo laminar 2D y cuatro celdas en la entrada no resuelven atomización ni turbulencia tridimensional.

## Resultados

Desde la raíz del repositorio, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/chorro --field alpha.water --normal z --clim 0 1
python postprocessing/animate.py runs/chorro --field alpha.water --clim 0 1 --output plots/chorro.gif
python postprocessing/statistics.py runs/chorro --field alpha.water
python postprocessing/plot_solver_log.py runs/chorro/log.interFoam
```

Revisar Courant, límites de alpha y frente del chorro. El agua puede salir por la atmósfera, por lo que su volumen interno no es constante. Sin ejecución comprobada.
