# Tutorial 09 · Cavidad 2D con tapa móvil

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/p`
- `constant/transportProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/fvSolution`
- `system/sampleDict`

## Ejecución

Desde esta carpeta y con OpenFOAM cargado: `./Allrun`. Conserva logs y no elimina resultados previos.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/09-cavity-2d
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
foamDictionary system/controlDict -entry application -value
icoFoam 2>&1 | tee log.icoFoam
```

**Estado:** Caso heredado: revisar compatibilidad con OpenFOAM.com antes de ejecutar. Alternativamente, ejecutar `bash Allrun` desde la carpeta del caso; no combinar los dos procedimientos.

## Variaciones pequeñas

Reducir velocidad de tapa 20%; reducir deltaT a la mitad; refinar malla sin alterar dimensiones.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/09-cavity-2d/log.NOMBRE_SOLVER --output plots/09-cavity-2d
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.
