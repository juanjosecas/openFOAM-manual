# Tutorial 11 · Rotura de presa 2D

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/alpha.water`
- `0/p`
- `0/p_rgh`
- `constant/dynamicMeshDict`
- `constant/g`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/fvSolution`
- `system/probesDict`
- `system/setFieldsDict`

**Advertencia:** requiere comprobar migración desde versiones anteriores y cualquier preprocesamiento adicional antes de ejecutar.

## Ejecución

Este caso no dispone todavía de un lanzador verificado. Consultar los pasos de preparación del tutorial.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/11-dambreak-2d
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
setFields 2>&1 | tee log.setFields
foamDictionary system/controlDict -entry application -value
interFoam 2>&1 | tee log.interFoam
```

**Estado:** Caso heredado: revisar compatibilidad con OpenFOAM.com antes de ejecutar. No hay un `Allrun` verificado para este caso.

## Variaciones pequeñas

Reducir maxCo; variar writeInterval; modificar ligeramente la columna inicial en setFieldsDict y volver a ejecutar setFields.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/11-dambreak-2d/log.NOMBRE_SOLVER --output plots/11-dambreak-2d
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.
