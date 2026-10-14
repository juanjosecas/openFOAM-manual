# Tutorial 12 · Goldschmidt · nube de partículas

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U.air`
- `0/p`
- `constant/g`
- `constant/kinematicCloudProperties`
- `constant/momentumTransport.air`
- `constant/transportProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/fvSolution`
- `system/mapFieldsDict`

**Advertencia:** requiere comprobar migración desde versiones anteriores y cualquier preprocesamiento adicional antes de ejecutar.

## Ejecución

Este caso no dispone todavía de un lanzador verificado. Consultar los pasos de preparación del tutorial.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/12-goldschmidt-particulas
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
# DETENIDO: es necesaria una migración o archivo de configuración pendiente
```

**Estado:** No ejecutar todavía: es necesario migrar los diccionarios lagrangianos de Foundation 8. No hay un `Allrun` verificado para este caso.

## Variaciones pequeñas

Tras migrar el caso: reducir deltaT, variar writeInterval o perturbar ligeramente un parámetro de inyección previamente identificado.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/12-goldschmidt-particulas/log.NOMBRE_SOLVER --output plots/12-goldschmidt-particulas
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.
