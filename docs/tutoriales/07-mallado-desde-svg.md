# Tutorial 07 — Geometrías SVG y Gmsh

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Herramientas: SVG + Python + Gmsh + gmshToFoam + simpleFoam + ParaView.

Vamos a construir un flujo de trabajo que permita dibujar una geometría en SVG, convertirla en una malla compatible con OpenFOAM y ejecutar una simulación de fluidos.

El ejemplo será un canal bidimensional con un obstáculo circular. Después podremos modificar el SVG para incorporar otros obstáculos, estrechamientos o geometrías irregulares.


#### 1. Qué vamos a construir

Geometría objetivo. El disco representa una región sólida excluida de la malla.

La geometría se representará mediante dos contornos cerrados: uno exterior, que delimita el canal, y otro interior, que delimita el sólido.


### 2. Elegir el procedimiento de conversión

Elegimos Python para leer el SVG y controlar Gmsh. Es un procedimiento más reproducible que la conversión manual SVG → DXF → STEP, especialmente cuando queremos repetir simulaciones con variaciones geométricas.

La API de Gmsh permite construir superficies, extruirlas, crear grupos físicos y generar mallas tridimensionales. Los grupos físicos se utilizan para identificar las regiones y los contornos durante la conversión a OpenFOAM.

GitHub

+1


#### Correcciones al procedimiento original

Hay cuatro detalles importantes:

Merge "geometria.step" no garantiza que la superficie importada tenga identificador 1. Los identificadores deben obtenerse de la geometría real.

Recombine no produce automáticamente hexaedros en cualquier geometría. Una superficie triangular extrusionada una capa genera normalmente prismas, perfectamente utilizables en OpenFOAM.


```cpp
gmshToFoam no asigna necesariamente empty a las superficies frontales. Hay que configurar los patches importados.
```

extrudeMesh no es una herramienta que simplemente colapse una malla 3D arbitraria a 2D. Extruye superficies o patches según un modelo geométrico y requiere una configuración específica. No lo necesitaremos en este caso.
 
GitHub
+1


### 3. Instalar las herramientas

Dentro de tu entorno Linux, comprobar:


```cpp
foamVersion
which gmsh
which gmshToFoam
python3 --version
```

El comando gmshToFoam corresponde a OpenFOAM. Gmsh es una aplicación independiente.

Para este tutorial utilizaremos la API Python de Gmsh y svgpathtools.

La instalación se puede hacer dentro del mismo contenedor, en un entorno virtual:


```cpp
python3 -m venv ~/svgmesh-env

source ~/svgmesh-env/bin/activate

python -m pip install --upgrade pip

python -m pip install gmsh svgpathtools
```

Comprobar:


```python
python -c "import gmsh, svgpathtools; print('Bibliotecas disponibles')"
```

Dependiendo de la imagen Docker, Gmsh puede necesitar bibliotecas del sistema como libGLU. Si aparecen errores de carga de bibliotecas compartidas, habrá que instalarlas mediante el gestor de paquetes correspondiente al sistema base del contenedor.

Una vez instalado, Gmsh puede utilizarse sin interfaz gráfica.


### 4. Crear la estructura completa

Crearemos un nuevo caso:


```bash
mkdir -p svgCanal2D/0
mkdir -p svgCanal2D/constant
mkdir -p svgCanal2D/system
mkdir -p svgCanal2D/geometry

touch svgCanal2D/geometry/canal.svg
touch svgCanal2D/geometry/svg_to_gmsh.py
touch svgCanal2D/geometry/ajustar_patches.py

touch svgCanal2D/0/U
touch svgCanal2D/0/p

touch svgCanal2D/constant/transportProperties
touch svgCanal2D/constant/turbulenceProperties

touch svgCanal2D/system/controlDict
touch svgCanal2D/system/fvSchemes
touch svgCanal2D/system/fvSolution

cd svgCanal2D
```

La estructura será:

svgCanal2D/

├── geometry/

│   ├── canal.svg

│   ├── svg_to_gmsh.py

│   └── ajustar_patches.py

├── 0/

│   ├── U

│   └── p

├── constant/

│   ├── transportProperties

│   └── turbulenceProperties

└── system/

├── controlDict

├── fvSchemes

└── fvSolution

No utilizamos blockMeshDict. La malla será generada mediante Gmsh.


### 5. Crear la geometría SVG


#### Archivo geometry/canal.svg

El SVG contiene dos elementos <path>.

domain define el contorno exterior y obstacle define la región que queremos excluir del fluido.

El círculo está definido mediante dos arcos SVG de radio 8, centrados aproximadamente en (80,20) dentro del sistema de coordenadas SVG.


#### Coordenadas y unidades

En este SVG:

200 unidades horizontales corresponden a 200 mm.

40 unidades verticales corresponden a 40 mm.

Una unidad del viewBox corresponde a 0,001 m.

También debemos tener en cuenta que en SVG el eje Y generalmente crece hacia abajo, mientras que en nuestra geometría OpenFOAM crecerá hacia arriba.

La conversión será:

$$ x_{\mathrm m}=0,001x_{\mathrm{SVG}} $$

$$ y_{\mathrm m}=0,001(40-y_{\mathrm{SVG}}) $$

Este cambio invierte el eje vertical.

Importante: el factor de escala se define explícitamente en el script. No vamos a depender de cómo Inkscape, FreeCAD o Gmsh interpreten las unidades del documento.


### 6. Convertir el SVG en una malla con Python y Gmsh

Vamos a implementar tres operaciones:

Leer los trazados SVG y convertir sus curvas en puntos.

Construir una superficie plana con el obstáculo como agujero.

Extruir esa superficie una sola capa y etiquetar sus caras.

Usaremos svgpathtools para interpretar las curvas SVG y la API oficial de Gmsh para generar la malla.


#### Archivo geometry/svg_to_gmsh.py

from pathlib import Pathfrom math import ceilimport gmshfrom svgpathtools import svg2paths2# --------------------------------------------------# CONFIGURACIÓN# --------------------------------------------------SVG_FILE = Path("geometry/canal.svg")OUTPUT_MESH = "dominio.msh"SCALE = 0.001         # SVG -> metrosSVG_HEIGHT = 40.0     # Altura del viewBoxTHICKNESS = 0.001     # Espesor en Z (m)MESH_SIZE = 0.002     # Tamaño objetivo de malla (m)CURVE_STEP = 0.001    # Discretización de curvas (m)# --------------------------------------------------# CONVERSIÓN DE COORDENADAS# --------------------------------------------------def svg_to_xyz(point):    x = point.real * SCALE    y = (SVG_HEIGHT - point.imag) * SCALE    return x, y, 0.0def signed_area(points):    area = 0.0

Este script está pensado para el SVG específico del tutorial, que contiene exactamente dos contornos identificados como domain y obstacle.

En los próximos casos podremos generalizar la lista de obstáculos. Para geometrías con múltiples agujeros o entradas laterales más complejas habrá que modificar la identificación de regiones.


#### Cómo funciona la discretización de curvas

Gmsh no resuelve directamente las instrucciones SVG. Primero convertimos las curvas Bézier o arcos del SVG en una sucesión de segmentos.

Por ejemplo, una circunferencia puede convertirse en una polilínea de decenas de lados.

Cuanto menor sea CURVE_STEP, más fiel será la aproximación geométrica. Sin embargo, un mayor número de segmentos también introduce más entidades geométricas y puede aumentar el costo de mallado.

En este caso usamos:

CURVE_STEP = 0.001

Es decir, aproximadamente 1 mm de longitud por segmento curvo.


#### Ejecutar la conversión

Desde la raíz de svgCanal2D:


```cpp
python geometry/svg_to_gmsh.py
```

El resultado será:

dominio.msh

Esta malla tiene una capa de elementos prismáticos en Z, generada por la extrusión de una malla triangular bidimensional.


#### Visualizar antes de convertir

Si disponés de la interfaz gráfica de Gmsh en Fedora:


```cpp
gmsh dominio.msh
```

Si estás trabajando exclusivamente en Docker sin servidor gráfico, podés copiar dominio.msh al host o abrirlo desde un volumen compartido.


### 7. Convertir la malla a OpenFOAM

En el directorio del caso:


```cpp
gmshToFoam dominio.msh 2>&1 | tee log.gmshToFoam
```

Esto creará:

constant/polyMesh/

├── boundary

├── faces

├── neighbour

├── owner

└── points

Inspeccionar las superficies importadas:


```cpp
cat constant/polyMesh/boundary
```

Deberíamos encontrar patches con nombres equivalentes a:

inlet

outlet

walls

frontAndBack

También puede aparecer algún patch adicional si Gmsh u OpenFOAM detectan caras no asignadas correctamente. En ese caso debemos revisar la clasificación geométrica antes de simular.


#### Corregir el tipo de frontAndBack

Gmsh identifica las caras delantera y posterior, pero gmshToFoam puede importarlas como patches convencionales.

Para que OpenFOAM resuelva el problema en 2D, ambas deben ser de tipo empty.

No modificaremos manualmente los contadores nFaces ni startFace, porque los genera OpenFOAM.


#### Archivo geometry/ajustar_patches.py

from pathlib import Pathimport reboundary_file = Path(    "constant/polyMesh/boundary")text = boundary_file.read_text()pattern = (    r"(^\s*frontAndBack\s*\{\s*"    r"type\s+)\w+")text, replacements = re.subn(    pattern,    r"\g<1>empty",    text,    count=1,    flags=re.MULTILINE)if replacements != 1:    raise RuntimeError(        "No se encontró el patch frontAndBack"    )boundary_file.write_text(text)print("frontAndBack configurado como empty")

Ejecutar:


```cpp
python geometry/ajustar_patches.py
```

Comprobar el resultado:


```cpp
grep -A 7 frontAndBack constant/polyMesh/boundary
```

Debería aparecer:

frontAndBack

{

type empty;

// Otros atributos generados por OpenFOAM

}

Es importante que la geometría tenga una sola capa de celdas en Z y que todas las caras normales a esa dirección estén incluidas en frontAndBack.

Advertencia: este script modifica únicamente el tipo del patch. Si la extrusión o la conversión produjo una topología incorrecta, cambiar el nombre del tipo no la repara. La prueba decisiva será checkMesh.


### 8. Configurar el fluido y las condiciones de contorno

Ahora tenemos que definir los campos físicos. Utilizaremos un fluido newtoniano incompresible con viscosidad cinemática de .

En este tutorial nos concentraremos en la conversión de geometrías. Una vez validada la malla, podremos utilizar modelos no newtonianos como en los casos anteriores.


#### Archivo constant/transportProperties


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

transportModel Newtonian;

nu [0 2 -1 0 0 0 0] 1e-5;
```


#### Archivo constant/turbulenceProperties


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType laminar;
```


#### Archivo 0/U


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}

dimensions [0 1 -1 0 0 0 0];

internalField uniform (0.01 0 0);

boundaryField
{
    inlet
    {
        type fixedValue;
        value uniform (0.01 0 0);
    }

    outlet
    {
        type zeroGradient;
    }

    walls
    {
        type noSlip;
    }

    frontAndBack
    {
        type empty;
    }
}
```

El patch walls incluye tanto las paredes exteriores del canal como la superficie del obstáculo.

Esto es suficiente si todas esas superficies comparten la misma condición noSlip.

Si quisiéramos medir por separado las fuerzas sobre el obstáculo, sería conveniente definir un patch exclusivo llamado obstacle, en lugar de incluirlo en walls.


#### Archivo 0/p


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}

dimensions [0 2 -2 0 0 0 0];

internalField uniform 0;

boundaryField
{
    inlet
    {
        type zeroGradient;
    }

    outlet
    {
        type fixedValue;
        value uniform 0;
    }

    walls
    {
        type zeroGradient;
    }

    frontAndBack
    {
        type empty;
    }
}
```

La presión de salida se establece como referencia cero.


### 9. Métodos numéricos


#### Archivo system/fvSchemes


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default steadyState;
}

gradSchemes
{
    default Gauss linear;
}

divSchemes
{
    default none;

    div(phi,U) bounded Gauss upwind;

    div((nuEff*dev2(T(grad(U)))))
        Gauss linear;
}

laplacianSchemes
{
    default Gauss linear corrected;
}

interpolationSchemes
{
    default linear;
}

snGradSchemes
{
    default corrected;
}

wallDist
{
    method meshWave;
}
```

Como utilizamos una malla de prismas con geometría curva aproximada mediante segmentos, los esquemas corrected serán útiles si aparecen celdas no ortogonales.


#### Archivo system/fvSolution


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    p
    {
        solver GAMG;
        tolerance 1e-8;
        relTol 0.01;
        smoother GaussSeidel;
    }

    U
    {
        solver smoothSolver;
        smoother symGaussSeidel;
        tolerance 1e-8;
        relTol 0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;

    consistent no;

    residualControl
    {
        p 1e-6;
        U 1e-7;
    }
}

relaxationFactors
{
    fields
    {
        p 0.3;
    }

    equations
    {
        U 0.7;
    }
}
```


#### Archivo system/controlDict


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application simpleFoam;

startFrom startTime;
startTime 0;

stopAt endTime;
endTime 1500;

deltaT 1;

writeControl timeStep;
writeInterval 100;

purgeWrite 0;

writeFormat ascii;
writePrecision 8;
writeCompression off;

timeFormat general;
timePrecision 6;

runTimeModifiable true;
```

La simulación utiliza simpleFoam y busca una solución estacionaria.

Como la malla es externa a blockMesh, los archivos de geometría permanecen en geometry/ y dominio.msh. No necesitamos system/blockMeshDict.


### 10. Ejecutar el caso completo

Una vez completados todos los archivos, podemos realizar la secuencia completa.

Desde la raíz de svgCanal2D:


```cpp
# 1. Convertir SVG en malla Gmsh
python geometry/svg_to_gmsh.py

# 2. Importar la malla a OpenFOAM
gmshToFoam dominio.msh 2>&1 | tee log.gmshToFoam

# 3. Configurar las caras 2D
python geometry/ajustar_patches.py

# 4. Verificar la malla
checkMesh -allGeometry -allTopology 2>&1 | tee log.checkMesh

# 5. Ejecutar la simulación
simpleFoam 2>&1 | tee log.simpleFoam

# 6. Preparar visualización
touch svgCanal2D.foam
```

No conviene ejecutar simpleFoam si checkMesh ha identificado errores.

Podés comprobar rápidamente la ejecución mediante:


```cpp
tail -n 40 log.checkMesh

tail -n 40 log.simpleFoam
```


#### Qué revisar en checkMesh

Los criterios fundamentales son:

También debemos verificar que el agujero circular esté realmente excluido de la región de fluido.

Si aparecen celdas dentro del obstáculo, el problema está en la construcción de la superficie con agujero, no en las condiciones de contorno.


### 11. Visualizar en ParaView


```cpp
Abrir svgCanal2D.foam.
```

Primero conviene observar la malla sin resultados:

Seleccionar Mesh Regions y los patches relevantes.

Cambiar la representación a Surface With Edges.

Orientar la cámara al eje Z.

Comprobar que el obstáculo circular esté vacío.

Después representar U → Magnitude.

El campo de velocidades debería mostrar:

Velocidad prácticamente nula en las paredes.

Aceleración en los espacios entre el obstáculo y las paredes del canal.

Alteración del perfil de velocidad aguas abajo.

Recuperación progresiva del perfil en dirección a la salida.

También podemos representar el campo p y estudiar las diferencias de presión generadas por la presencia del obstáculo.

Como se trata de una simulación estacionaria, los diferentes directorios temporales representan iteraciones de convergencia, no una evolución física temporal.


### 12. Ajuste de tolerancia para Gmsh

En geometry/svg_to_gmsh.py, utilizá:

TOL = 1e-6

en lugar de 1e-8.

Gmsh puede ampliar ligeramente las cajas delimitadoras (bounding boxes) de sus entidades geométricas. Una tolerancia excesivamente estricta podría impedir que el script reconozca las superficies situadas en x=0 y x=0.20.

Para comprobar qué superficies está clasificando, podés agregar dentro del bucle:

print(    f"Superficie {surface}: "    f"xmin={xmin:.8f}, xmax={xmax:.8f}, "    f"ymin={ymin:.8f}, ymax={ymax:.8f}")

Esto también sirve para entender cómo Gmsh organiza las caras tridimensionales resultantes de la extrusión.


### 13. Adaptar el tutorial a otras geometrías SVG

La ventaja del procedimiento es que la geometría ahora es independiente de OpenFOAM.

Podemos dibujar un nuevo contorno en Inkscape, modificar el SVG y generar otra malla.

Sin embargo, el script actual está restringido a un dominio exterior y un obstáculo interior. No es todavía un conversor SVG universal.


#### Geometrías que podemos implementar

Varios obstáculos

Extender el script para reconocer todos los paths cuyo identificador comience con obstacle. Cada uno se convertirá en un agujero independiente de la superficie fluida.

Estenosis y conductos irregulares

Dibujar el canal con paredes curvas y definir directamente la superficie fluida. La geometría puede aproximarse mediante segmentos o reconstruirse con curvas de Gmsh.

Canales ramificados

Crear una geometría con varias entradas y salidas. Requiere identificar cada sección del contorno y asignarle un grupo físico diferente.


#### Una mejora importante: preservar curvas reales

Nuestro script aproxima los arcos y las curvas Bézier mediante segmentos rectos. Funciona para aprender y generar geometrías sencillas, pero no aprovecha completamente las capacidades geométricas de Gmsh.

En una implementación más avanzada podemos convertir las curvas del SVG en splines u otras entidades curvas de Gmsh. Esto permite mejorar la representación de contornos suaves sin introducir necesariamente tantos segmentos geométricos.

También conviene separar los patches de paredes exteriores y obstáculos, para poder imponer distintas condiciones físicas o calcular fuerzas hidrodinámicas individuales.


### 14. Comparación de los tres procedimientos

Para nuestra colección de tutoriales, SVG + Python + Gmsh ofrece una combinación útil de control geométrico y reproducibilidad.

Permite separar la definición visual de la geometría de las propiedades físicas y los métodos numéricos de OpenFOAM.


#### Limitaciones del caso entregado

El tutorial contiene el SVG, los scripts de conversión y los siete diccionarios físicos y numéricos necesarios. El flujo de conversión se ha fundamentado en la API de Gmsh y la utilidad gmshToFoam, pero no se ha ejecutado en tu contenedor.

Antes de utilizar una geometría arbitraria, habrá que verificar que los contornos estén cerrados, que los agujeros se encuentren completamente dentro del dominio y que la clasificación de las superficies corresponda a sus condiciones físicas.

Referencias técnicas:

Gmsh — Manual y API oficial

svgpathtools — Procesamiento de geometrías SVG

OpenFOAM.com — Documentación

gmshToFoam — Conversión de mallas Gmsh

El resultado buscado es un flujo reproducible:


```cpp
SVG → Python → Gmsh → OpenFOAM → ParaView
```

A partir de él podremos utilizar geometrías dibujadas en Inkscape para simular flujo laminar, fluidos no newtonianos, estenosis, redes microfluídicas y obstáculos de formas arbitrarias.
