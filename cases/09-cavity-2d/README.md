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

## Cómo leer la configuración

Los archivos incluyen comentarios breves junto a las entradas y comandos.
En los diccionarios, `clave valor;` define una entrada, `{ ... }` agrupa un
subdiccionario y `( ... )` delimita listas o vectores. `$nombre` reutiliza una
entrada definida en el diccionario. `//` comenta una línea y `/* ... */` un
bloque: los ejemplos comentados no se ejecutan. En los scripts Bash, `#`
introduce un comentario.

| Archivo | Función |
| --- | --- |
| `0/U` | Velocidad inicial y condiciones de la tapa, paredes y caras 2D. |
| `0/p` | Presión cinemática inicial y sus condiciones de contorno. |
| `constant/transportProperties` | Viscosidad cinemática del fluido. |
| `system/blockMeshDict` | Vértices, subdivisiones, bloque y patches de la malla. |
| `system/controlDict` | Solver, tiempos físicos, escrituras y diagnósticos. |
| `system/fvSchemes` | Aproximaciones numéricas de derivadas e interpolaciones. |
| `system/fvSolution` | Solvers lineales, acoplamiento PISO y referencia de presión. |
| `system/decomposeParDict` | Partición opcional para una ejecución paralela. |
| `system/sampleDict` | Definición de perfiles; necesita invocación de muestreo. |
| `Allmesh` | Generar y comprobar la malla sin ejecutar el solver. |
| `Allrun` | Preparar o reutilizar la malla, verificarla y ejecutar el solver. |
| `Allclean` | Mostrar candidatos de limpieza; borrar solo con `--yes`. |

Con los valores activos, la tapa se mueve a 1 m/s, la longitud de la cavidad
es 1 m y `nu=0.0001 m²/s`: `Re=U L/nu=10000`. La malla contiene 20 × 20 × 1
celdas. Estos datos describen el caso; no demuestran resolución suficiente ni
validación física. En `icoFoam`, `deltaT=0.01` y `endTime=50` son segundos de
tiempo simulado, mientras que las tolerancias de `fvSolution` son controles
numéricos de los sistemas lineales.

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
