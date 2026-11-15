# Flexión de una viga empotrada

Una viga rectangular, fija por un extremo, se deforma bajo una tracción transversal aplicada en la cara opuesta. El campo D es desplazamiento en metros.

## Configuración base

Solver: `solidDisplacementFoam`. Longitud 100 mm, sección 10 × 10 mm, 40 × 4 × 4 celdas. E=2 GPa, coeficiente de Poisson 0.3, rho=1200 kg/m³; tracción terminal −10000 Pa en z, fuerza total −1 N.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 23-flexion-de-viga --output runs/viga
bash scripts/run_docker.sh runs/viga
```

Para modificar el modelo, editar la copia antes de ejecutar. Si cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado se puede usar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/D` | `extremoCargado/traction` | Carga superficial en Pa; probar (0 0 -5000), que reduce la fuerza a la mitad. |
| `0/D` | `empotramiento/value` | Desplazamiento fijo; conservar cero para una viga empotrada. |
| `constant/mechanicalProperties` | `E/value, nu/value, rho/value` | Rigidez, Poisson y densidad; aumentar E reduce flexión. nu aquí es adimensional, no viscosidad. |
| `constant/thermalProperties` | `thermalStress` | Acoplamiento térmico; desactivado en este caso. |
| `system/blockMeshDict` | `vertices, blocks` | Longitud y sección; refinar de (40 4 4) a (80 8 8). |
| `system/controlDict, system/fvSolution` | `endTime, tolerancias` | Iteraciones pseudo-temporales y convergencia; no segundos físicos. |

Para una sección rectangular, I=b·h³/12 y la flecha terminal de Euler–Bernoulli es F·L³/(3·E·I), aproximadamente −0.2 mm. La referencia supone viga esbelta y fuerza terminal equivalente; los centros de celda no coinciden con la cara terminal.

## Resultados

Desde la raíz del repositorio, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/reference.py beam runs/viga --young 2e9 --traction-z -10000 --output plots/flexion
python postprocessing/fields.py runs/viga --field D --component 2
python postprocessing/plot_solver_log.py runs/viga/log.solidDisplacementFoam
```

Comparar el perfil de desplazamiento, error y sensibilidad a resolución transversal. Ajustar parámetros de referencia si cambia material o carga. Sin ejecución comprobada.
