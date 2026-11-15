# Conducción térmica estacionaria 1D

Barra ideal con temperaturas fijas en los extremos y sin variación transversal, fuentes ni convección. El perfil estacionario es lineal.

## Configuración base

Solver: `laplacianFoam`. Longitud 0.02 m, 40 × 1 × 1 celdas. Extremo caliente 400 K, frío 300 K; DT=1e-5 m²/s. Esquema steadyState.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 24-conduccion-de-calor-1d --output runs/calor
bash scripts/run_docker.sh runs/calor
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/T` | `caliente/value, frio/value` | Temperaturas en K; probar caliente=350 K. |
| `constant/transportProperties` | `DT` | Difusividad térmica, m²/s. Cambiar a 2e-5 no altera la solución estacionaria homogénea. |
| `system/blockMeshDict` | `vertices, blocks` | Longitud y resolución; probar 80 × 1 × 1. |
| `system/fvSchemes` | `ddtSchemes` | steadyState elimina derivada temporal; para transitorio revisar también controlDict e inicialización. |
| `system/fvSolution` | `T, tolerancia` | Precisión del sistema lineal. |

La referencia es T(x)=400−100x/0.02 K. DT no es conductividad térmica: se necesita k en W/(m·K) para calcular flujo térmico en W/m². Los directorios numéricos son iteraciones.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/reference.py heat runs/calor --left 400 --right 300 --output plots/temperatura
python postprocessing/fields.py runs/calor --field T
python postprocessing/plot_solver_log.py runs/calor/log.laplacianFoam
```

Comparar error máximo absoluto en centros de celda. Como objetivo inicial puede usarse 0.01 K, no demostrado. Configuración revisada estáticamente.
