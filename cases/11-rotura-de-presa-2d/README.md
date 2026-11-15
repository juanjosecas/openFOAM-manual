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

Se proporciona Allrun mediante el runner compartido. Pendiente de ejecución.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/11-rotura-de-presa-2d
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
setFields 2>&1 | tee log.setFields
foamDictionary system/controlDict -entry application -value
interFoam 2>&1 | tee log.interFoam
```

**Estado:** Caso heredado: revisar compatibilidad con OpenFOAM.com antes de ejecutar. El nuevo `Allrun` no se ha ejecutado.

## Variaciones pequeñas

Reducir maxCo; variar writeInterval; modificar ligeramente la columna inicial en setFieldsDict y volver a ejecutar setFields.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/11-rotura-de-presa-2d/log.NOMBRE_SOLVER --output plots/11-rotura-de-presa-2d
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.

## Revisión estática v2406

Se reemplazó la lista inicial de 2268 fracciones de fase por alpha.water uniforme 0; setFields define la columna después del mallado. El dominio y obstáculo se conservan. La columna nominal mide 0.1461 × 0.292 m, con espesor 0.0146 m (volumen geométrico ≈ 0.000623 m³; el volumen discretizado depende de los centros de celda seleccionados). Se declara defaultFaces empty explícitamente, se actualizan las bibliotecas de los function objects, se elimina el tipo duplicado cellSource y se usa regionType all. Se utiliza interfaceCompression y un límite máximo de paso 0.005 s con Co y alphaCo máximos de 0.5 en base y animación. Estos son cambios numéricos conservadores propuestos, no estabilidad demostrada. Las sondas se desplazaron al interior del fluido; probesDict no se ejecuta automáticamente. Se conservan 0/p y demás archivos heredados mientras se verifica compatibilidad.

Preparar una copia limpia y ejecutar:

```bash
bash scripts/prepare_case.sh 11-rotura-de-presa-2d --output runs/dambreak
bash scripts/run_docker.sh runs/dambreak
```

Verificar balance de agua mediante integral de alpha.water, límites de fracción de fase, Courant y posición del frente. Considerar cualquier flujo de agua por la atmósfera al evaluar conservación. No se ha ejecutado.
