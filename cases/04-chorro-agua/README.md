# OpenFOAM v2406 — Tutorial 04

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/alpha.water`
- `0/p_rgh`
- `constant/g`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `system/blockMeshDict`
- `system/fvSchemes`
- `system/fvSolution`

**Caso incompleto:** no se recuperó `system/controlDict`; no ejecutar hasta reconstruirlo desde una fuente comprobada.

## Ejecución

Este caso no dispone todavía de un lanzador verificado. Consultar los pasos de preparación del tutorial.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/04-chorro-agua
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
# DETENIDO: es necesaria una migración o archivo de configuración pendiente
```

**Estado:** No ejecutar todavía: falta system/controlDict. No hay un `Allrun` verificado para este caso.

## Variaciones pequeñas

Reducir la velocidad de entrada 20%; reducir maxCo; aumentar la frecuencia de escritura una vez recuperado controlDict.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/04-chorro-agua/log.NOMBRE_SOLVER --output plots/04-chorro-agua
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.


## Actualización de configuración

Se añadió `system/controlDict`, `Allrun`, `Allmesh` y `Allclean` para el modelo `interFoam` con fase inicial de aire (`alpha.water=0`) y entrada de agua (`alpha.water=1`). No se requiere `setFields` para esta condición inicial. Ver [explicación y parámetros](COMPLETADO.md). Las advertencias históricas anteriores sobre la ausencia de `controlDict` han quedado obsoletas; la compatibilidad física y funcional sigue sin comprobarse.
