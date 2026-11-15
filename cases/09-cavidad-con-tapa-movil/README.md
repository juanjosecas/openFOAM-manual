# Cavidad cuadrada con tapa móvil

Fluido inicialmente en reposo dentro de una cavidad cerrada. La tapa superior se desplaza en x y genera circulación interna.

## Configuración base

Solver: `icoFoam`. Cavidad 1 × 1 m, 20 × 20 × 1 celdas, tapa a 1 m/s, nu=1e-4 m²/s; Re=10000. deltaT=0.01 s y endTime=120 s. El caso base es demasiado grueso para un benchmark cuantitativo.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 09-cavidad-con-tapa-movil --output runs/cavidad
bash scripts/run_docker.sh runs/cavidad
```

Para modificar el modelo, editar los archivos de la copia **antes de ejecutar**. Si se cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado también se puede ejecutar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `movingWall/value` | Velocidad de tapa; probar (0.8 0 0). |
| `constant/transportProperties` | `nu` | Re=UL/nu. Subir nu a 0.01 reduce Re a 100. |
| `system/blockMeshDict` | `xmin, xmax, ymin, ymax` | Dimensiones de cavidad; mantenerla cuadrada para comparar benchmarks. |
| `system/blockMeshDict` | `xcells, ycells, zcells` | Refinar x e y; zcells=1 con empty. |
| `system/controlDict` | `deltaT, endTime` | Paso y duración físicos. Al refinar, revisar Courant y reducir deltaT. |
| `system/fvSolution` | `PISO, pRefCell, pRefValue` | Acoplamiento y referencia de presión de la cavidad cerrada. |
| `system/sampleDict` | `sets` | Líneas centrales de muestreo; actualizar si se modifica tamaño. |

La variante preparada `--variant re100` usa nu=0.01, 64 × 64 × 1 celdas, deltaT=0.005 s y endTime=40 s. Es mejor punto de partida para comparar perfiles centrales con [Ghia et al. (1982)](https://doi.org/10.1016/0021-9991(82)90058-4).

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento; no confundir tolerancia numérica con precisión física.

## Resultados

Desde la raíz, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/cavidad --field U --normal z --streamlines
python postprocessing/profile.py runs/cavidad --field U --component 0 --start 0.5 0.0001 0.5 --end 0.5 0.9999 0.5
python postprocessing/animate.py runs/cavidad --field U --normal z --output plots/cavidad.gif
python postprocessing/plot_solver_log.py runs/cavidad/log.icoFoam
```

Comparar perfiles Ux(y) y Uy(x), posición del vórtice y sensibilidad temporal y espacial. Configuraciones revisadas estáticamente, sin validación nueva.
