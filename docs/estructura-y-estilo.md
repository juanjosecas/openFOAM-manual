# Estructura, redacción y convenciones

## 1. Alcance y edición de OpenFOAM

La referencia operativa del manual es **OpenFOAM.com v2406**. No confundir esta línea con OpenFOAM Foundation: pueden variar solvers, diccionarios y modelos. Para v2412, anotar únicamente diferencias verificadas. La documentación v2606 puede consultarse para conceptos, pero no se copiará sintaxis nueva sin comprobar compatibilidad.

## 2. Directorio de cada caso

```text
cases/01-canal-2d/
├── 0/
│   ├── U
│   └── p
├── constant/
│   ├── transportProperties
│   └── turbulenceProperties
├── system/
│   ├── blockMeshDict
│   ├── controlDict
│   ├── fvSchemes
│   └── fvSolution
├── Allrun
├── Allclean
└── README.md
```

**`0/`** contiene condiciones iniciales y de contorno; **`constant/`** contiene propiedades físicas y, tras mallar, `polyMesh/`; **`system/`** contiene control de ejecución, discretización y solución. El contenido concreto depende del solver y no se deben generar archivos ficticios. Los directorios `0.01/`, `0.02/`, etc. son resultados temporales que, salvo excepción documentada, **no se versionan**.

Mantener archivos auxiliares necesarios en la carpeta del caso (por ejemplo `constant/triSurface/` o `system/setFieldsDict`). Las geometrías paramétricas generadas con Python deben incluir su script fuente.

## 3. Estructura de cada tutorial

1. **Objetivo observable:** qué fenómeno y qué animación se obtendrán.
2. **Física y supuestos:** tipo de fluido, régimen, dimensiones y límites del modelo.
3. **Geometría y malla:** sistema de coordenadas, parámetros y esquema de bloques.
4. **Archivos necesarios:** árbol completo y comandos `mkdir -p` / `touch` sin líneas truncadas.
5. **Archivos de configuración:** contenido completo de cada archivo, incluso cuando sea igual al anterior.
6. **Explicación de parámetros:** unidades, efecto, valores seguros de inicio y consecuencias de cambiarlos.
7. **Ejecución:** `blockMesh` u otro mallador, `checkMesh`, solver leído de `controlDict` y logs.
8. **Visualización y exportación:** ParaView, VTK, CSV, Python y exportación de animaciones cuando aplique.
9. **Comprobaciones físicas y numéricas:** conservación, estabilidad, resolución y contraste analítico si existe.
10. **Experimentos y limitaciones:** qué se puede modificar y qué queda sin validar.

### Ficha mínima

| Campo | Requisito |
|---|---|
| Edición | OpenFOAM.com v2406; otras versiones únicamente si se probaron |
| Solver | Nombre exacto de `application` |
| Régimen | Transitorio por defecto |
| Duración | Tiempo físico y número esperado de estados |
| Malla | Número aproximado de celdas y criterios de calidad |
| Estado | Borrador / revisado / ejecutado / validado |
| Prueba | Versión, fecha, comandos, resultado y limitaciones |

## 4. Comentarios en los diccionarios

En los archivos de OpenFOAM utilizar comentarios **breves, técnicos y en español**. Preferir `//` encima de un grupo lógico y `/* ... */` para notas excepcionales. No interrumpir tokens, claves, vectores o rutas.

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}

// Campo inicial: fluido en reposo.
// Unidades de U: m/s.
dimensions     [0 1 -1 0 0 0 0];
internalField  uniform (0 0 0);

boundaryField
{
    inlet
    {
        // Velocidad impuesta en el eje X.
        type    fixedValue;
        value   uniform (0.01 0 0);
    }

    outlet
    {
        // Gradiente normal nulo; el caudal resulta de la solución.
        type    zeroGradient;
    }

    walls
    {
        // Adherencia sobre una pared rígida estacionaria.
        type    noSlip;
    }
}
```

Los nombres de patches deben coincidir exactamente con los de la malla. Explicar la función de los parámetros en el Markdown; **no transformar cada línea del diccionario en un párrafo**.

## 5. Sintaxis y unidades

- Entrada estándar: `clave valor;`; subdiccionarios: `nombre { ... }`; listas: `( ... )`.
- El encabezado `FoamFile` declara `version`, `format`, `class` y `object`; `location` puede ser relevante en campos.
- Los vectores se escriben con componentes separadas por espacios, por ejemplo `(0.01 0 0)`, sin comas.
- Los campos indican `dimensions`, `internalField` y `boundaryField` cuando corresponda.
- Las dimensiones se expresan en siete exponentes: masa, longitud, tiempo, temperatura, cantidad de sustancia, corriente e intensidad luminosa.
- No confundir presión cinemática `p` de ciertos solvers incompresibles con presión física en pascales.
- Los `#include` y las sustituciones `$variable` son útiles, pero en los primeros tutoriales se priorizan archivos completos y autocontenidos para facilitar el aprendizaje.

## 6. Comandos reproducibles

Los comandos Bash se presentan en bloques `bash` y los diccionarios en bloques `cpp` o `text`. No mezclar comandos `docker exec` del equipo anfitrión con instrucciones de la terminal del contenedor sin indicarlo.

```bash
cd cases/01-canal-2d
foamVersion
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
solver=$(foamDictionary system/controlDict -entry application -value)
"$solver" 2>&1 | tee "log.$solver"
```

No usar `foamRun` como sustituto universal de solvers clásicos. Los scripts `Allrun` deben mostrar versión, caso, solver y fallar si `checkMesh` no termina correctamente. `Allclean` debe advertir antes de borrar resultados y preservar los archivos originales.

## 7. Prototipado transitorio

- Utilizar **`pimpleFoam`** para ejemplos monofásicos transitorios cuando sea pertinente, y otros solvers específicos para superficie libre o partículas.
- Distinguir **`deltaT`** (integración) de **`writeInterval`** (salida); establecer límites de Courant acordes con el modelo.
- Proponer primero mallas pequeñas y simulaciones cortas, típicamente 100–300 estados si el fenómeno lo permite.
- Explicar el **tiempo físico** representado; las iteraciones de `simpleFoam` no son una evolución temporal.
- Mantener estable la escala de colores al exportar una animación, mostrar unidades y especificar FPS y resolución.
- Una simulación atractiva no equivale a solución convergida o validada.

## 8. Política de archivos y Git

Versionar: documentos Markdown, figuras ligeras, todos los archivos de configuración, scripts, instrucciones `Allrun` y `Allclean`, así como los datos mínimos para reproducir el caso.

Excluir normalmente: `constant/polyMesh/` generado, directorios temporales de salida, `processor*/`, logs, `postProcessing/`, exportaciones VTK y videos voluminosos. Si una malla no puede regenerarse, documentar y conservar un artefacto descargable apropiado.

No editar directamente el caso original cuando se diseñen variantes: duplicarlo con nombre descriptivo y dejar un registro de cambios. Los ejemplos heredados deben indicar origen, licencia y adaptación; no llamarlos compatibles sin probarlos.

## 9. Idioma y tono

Español técnico claro, sin antropomorfismos ni frases promocionales. Presentar primero el concepto físico, luego el parámetro concreto y finalmente el efecto esperado. Usar unidades SI, coma decimal en prosa y punto decimal dentro de archivos ejecutables. Definir cada término nuevo una sola vez, antes de su primer uso. No confundir *condición inicial*, *condición de contorno*, *paso temporal*, *intervalo de escritura*, *residuo* y *criterio de convergencia*.

## Fuentes oficiales

- [Código OpenFOAM](https://gitlab.com/openfoam/core/openfoam)
- [Estructura estándar del caso](https://www.openfoam.com/documentation/user-guide/2-openfoam-cases/2.1-file-structure-of-openfoam-cases)
- [Formato de entrada y salida](https://www.openfoam.com/documentation/user-guide/2-openfoam-cases/2-2-basic-inputoutput-file-format)


## 10. Extensiones y archivos opcionales

- `Allmesh`: construye malla mediante `blockMesh` y ejecuta `checkMesh`, **sin solver**. Se detiene si existe una malla anterior.
- `Allclean`: sin opciones, enumera las rutas generadas; con `--yes`, borra solamente mallas, logs, tiempos posteriores a cero y directorios calculados. Conserva `0/`, `system/` y `constant/` (excepto su `polyMesh` generado).
- `variants/README.md`: describe las variaciones pequeñas sobre copias del caso, sin duplicar todos los archivos fuente.
- `postprocessing/probes.function`: fragmento de función opcional. Para activarlo debe integrarse en `functions` de `controlDict`, previa comprobación de versión y de que los puntos están dentro del fluido.
- Las carpetas `plots/`, `postProcessing/` y tiempos calculados se consideran resultados; **no ignorar el directorio inicial `0/`**.
