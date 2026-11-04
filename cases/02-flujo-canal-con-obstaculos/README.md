# Tutorial 02 — Flujo no newtoniano en un canal con obstáculos

**Estado:** caso base ejecutado con OpenFOAM.com v2406; comentarios y variantes documentados. La convergencia numérica no equivale a validación física.

## Archivos presentes

- `0/U`
- `0/p`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/fvSchemes`
- `system/fvSolution`

## Configuración comentada e interacción con el objeto

La plantilla conserva todos sus valores físicos y numéricos originales. Los
diccionarios explican unidades, función de las entradas y simplificaciones. Los
scripts también están comentados. El canal mide 200 x 20 mm y contiene un
obstáculo rectangular de 20 x 4 mm; la malla planar tiene 7840 celdas y una
celda en z. El espesor de 1 mm no convierte el objeto en una esfera o un cilindro.

El patch `obstacle` es independiente de `lowerWall` y `upperWall`. Puede tener
`slip` o `partialSlip` mientras ambas paredes siguen `noSlip`, manteniendo
inalterados geometría y patches de presión. Las [recetas preparadas](variants/README.md)
permiten comparar esos comportamientos, agua newtoniana y una malla más fina.
Se aplican solo en copias nuevas de `runs/` y dejan la plantilla intacta.

Las configuraciones de transporte base y `generalizedNewtonian/powerLaw` actúan
en distintos niveles. Cambiar solo `nu` no convierte esta base en agua de
viscosidad constante; las recetas `agua-*` modifican ambos archivos de forma
coordinada. La presión es cinemática, no Pa; requiere una densidad para convertir
diferencias. Los diagnósticos opcionales permanecen inactivos.

## Ejecución

Desde esta carpeta y con OpenFOAM cargado: `./Allrun`. Registra logs y no elimina directorios de resultados previos; los logs con el mismo nombre pueden sobrescribirse.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/02-flujo-canal-con-obstaculos
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
foamDictionary system/controlDict -entry application -value
simpleFoam 2>&1 | tee log.simpleFoam
```

**Verificación:** mallado y solver base comprobados en Docker v2406. Alternativamente, ejecutar `bash Allrun` desde la carpeta del caso; no combinar los dos procedimientos.

## Variaciones pequeñas

Reducir la velocidad de entrada 20%; variar n de 0.5 a 0.7; refinar bloques próximos al obstáculo conservando interfaces.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/02-flujo-canal-con-obstaculos/log.NOMBRE_SOLVER --output plots/02-flujo-canal-con-obstaculos
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.


## Ampliación transitoria

Este caso utiliza `simpleFoam` estacionario. Si interesa estudiar arranques, pulsaciones o fluctuaciones físicas, consultar la [guía de conversión a `pimpleFoam`](../../docs/simplefoam-a-transitorio.md). La transición requiere una **copia independiente** y revisar esquemas, algoritmo, compatibilidad de modelos y condiciones de contorno; no cambiar únicamente `application`.
