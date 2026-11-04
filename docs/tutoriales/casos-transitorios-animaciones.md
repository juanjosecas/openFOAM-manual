# Cinco casos transitorios independientes para animaciones

Estos casos son **copias independientes**: no modifican las carpetas originales ni agregan subdirectorios de variantes dentro de ellas. Se prioriza la evolución temporal y la visualización; **no son modelos validados**.

| Caso nuevo | Origen | Solver | Visualización |
| --- | --- | --- | --- |
| `30-estela-de-vaca-animacion` | `28-flujo-transitorio-alrededor-vaca` | `pimpleFoam` | Estela, velocidad, vorticidad |
| `31-estela-de-canguro-animacion` | `29-estela-transitoria-de-canguro` | `pimpleFoam` | Estela y desprendimiento de vórtices |
| `32-chorro-de-agua-animacion` | `04-chorro-de-agua` | `interFoam` | Interfaz agua-aire |
| `33-rotura-de-presa-animacion` | `11-rotura-de-presa-2d` | `interFoam` | Propagación de agua |
| `34-flujo-transitorio-canal-obstaculos` | `02-flujo-canal-con-obstaculos` | `pimpleFoam` | Recirculación y vorticidad |

Cada caso tiene su propio `0/`, `constant/`, `system/`, `Allrun`, `Allmesh`, `Allclean`, `run_docker.sh` y `README.md`. La vaca incluye su archivo `cow_tunnel.msh`; el canguro incluye los archivos de geometría necesarios para construir la malla.

## Ejecución con Docker

Desde la raíz del repositorio:

```bash
bash scripts/run_docker.sh 30-estela-de-vaca-animacion
bash scripts/run_docker.sh 32-chorro-de-agua-animacion
bash scripts/run_docker.sh 33-rotura-de-presa-animacion
bash scripts/run_docker.sh 34-flujo-transitorio-canal-obstaculos
```

Para el canguro, el mallado requiere `gmsh` con bindings Python **en el host**. Primero:

```bash
python3 cases/31-estela-de-canguro-animacion/geometry/build_mesh.py
bash scripts/run_docker.sh 31-estela-de-canguro-animacion
```

Alternativamente, desde el propio caso `bash run_docker.sh` prepara la geometría en el host si falta. No se asume que la imagen Docker de OpenFOAM tenga el módulo Python `gmsh`.

**No ejecutar dos variantes a la vez en la misma carpeta**: los archivos temporales y los resultados se escriben en el directorio del caso. Para volver a cero, `bash Allclean --yes` elimina resultados y mallas (revisar el contenido antes de ejecutar).

## Visualización con ParaView

Los resultados se guardan en carpetas temporales numeradas dentro del caso. Para abrirlos:

```bash
touch cases/32-chorro-de-agua-animacion/case.foam
paraview cases/32-chorro-de-agua-animacion/case.foam
```

Para animaciones, el repositorio incluye un script opcional que necesita `pvpython` (ParaView instalado en el host):

```bash
pvpython scripts/render_transient.py cases/30-estela-de-vaca-animacion --field U --output plots/vaca.avi
pvpython scripts/render_transient.py cases/34-flujo-transitorio-canal-obstaculos --field U --output plots/canal.avi
```

El script utiliza el campo `U`, su magnitud, una escala de colores fijada durante la animación y los tiempos de salida disponibles. Es un renderizador **básico**: para interfaces agua-aire es preferible crear una isosuperficie de `alpha.water = 0.5` en ParaView y animar esa superficie. El soporte para AVI/MP4 depende de cómo esté compilado ParaView; si falla, usar exportación de secuencia de imágenes desde su interfaz.

## Ajustes numéricos

- Los casos existentes `pimpleFoam` e `interFoam` conservan su modelo físico y cambian la frecuencia de escritura para facilitar animaciones.
- El canal con obstáculos se convierte a `pimpleFoam` con `ddtSchemes: Euler`, `PIMPLE` en `fvSolution`, `maxCo = 0.5`, `deltaT = 0.001` y escritura cada 0.05 s. **Esto es una configuración inicial, no un cálculo validado.**
- Los casos 2D pueden mostrar recirculación sin desprendimiento periódico de vórtices. Para obtener estelas oscilantes quizá haya que ajustar Reynolds, geometría, tiempo de simulación y malla.
- La escala de colores fija permite comparar fotogramas. Evitar autoescalado por frame, que exagera variaciones pequeñas.

**Estado:** archivos revisados estáticamente; no se ejecutó OpenFOAM v2406 ni se comprobaron animaciones o estabilidad. Antes de publicar resultados, revisar `log.checkMesh`, logs del solver y número de Courant.
