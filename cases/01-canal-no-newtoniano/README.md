# Tutorial 01 — Flujo no newtoniano en un canal 2D

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/p`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/fvSchemes`
- `system/fvSolution`

## Ejecución

Desde esta carpeta y con OpenFOAM cargado: `./Allrun`. Conserva logs y no elimina resultados previos.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/01-canal-no-newtoniano
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
foamDictionary system/controlDict -entry application -value
simpleFoam 2>&1 | tee log.simpleFoam
```

**Estado:** Comandos documentados, no comprobados mediante ejecución. Alternativamente, ejecutar `bash Allrun` desde la carpeta del caso; no combinar los dos procedimientos.

## Variaciones pequeñas

Reducir velocidad de entrada a la mitad; variar n de 0.5 a 0.7; bajar resolución de 200×40×1 a 100×20×1.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/01-canal-no-newtoniano/log.NOMBRE_SOLVER --output plots/01-canal-no-newtoniano
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.
