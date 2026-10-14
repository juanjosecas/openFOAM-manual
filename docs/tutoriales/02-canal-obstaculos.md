# Tutorial 02 — Flujo no newtoniano en un canal con obstáculos

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Vamos a continuar con el fluido pseudoplástico del tutorial anterior, pero ahora introduciendo obstáculos sólidos dentro del canal.

El objetivo principal es aprender a definir la posición, las dimensiones y las superficies de un obstáculo, y posteriormente agregar otros sin alterar las condiciones físicas del problema.

Haremos dos variantes: primero un obstáculo rectangular centrado y después dos obstáculos que puedan colocarse en distintas posiciones.


### 1. Geometría que vamos a construir

Esquema del canal con un obstáculo sólido rectangular. El flujo avanza de izquierda a derecha.

El obstáculo ocupa la región:


#### Nuevo concepto: construir un obstáculo como un vacío de la malla

blockMesh trabaja con bloques hexaédricos. Para representar un obstáculo interno rectangular podemos construir varios bloques alrededor y dejar sin mallar el volumen ocupado por el sólido.


```cpp
Descomposición del canal en ocho bloques de fluido. El rectángulo central se omite.
```

Este procedimiento tiene una ventaja didáctica: nos obliga a entender las coordenadas y las conexiones entre bloques. También permite controlar explícitamente la resolución espacial.

Su limitación es que la malla debe adaptarse a la geometría. Para muchos obstáculos, superficies curvas o cuerpos de formas arbitrarias, más adelante utilizaremos snappyHexMesh.

La documentación de blockMesh confirma que la geometría puede definirse mediante múltiples bloques, vértices compartidos y caras asignadas a diferentes patches.


### 2. Crear el caso


```bash
mkdir -p canalObstaculo2D/{0,constant,system}

cd canalObstaculo2D
Los archivos serán:


canalObstaculo2D/
├── 0/
│   ├── U
│   └── p
├── constant/
│   ├── transportProperties
│   └── turbulenceProperties
└── system/
    ├── blockMeshDict
    ├── controlDict
    ├── fvSchemes
    └── fvSolution

canalObstaculo2D/
├── 0/
│   ├── U
│   └── p
├── constant/
│   ├── transportProperties
│   └── turbulenceProperties
└── system/
    ├── blockMeshDict
    ├── controlDict
    ├── fvSchemes
    └── fvSolution

mkdir -p canalObstaculo2D/0 canalObstaculo2D/constant canalObstaculo2D/system
touch canalObstaculo2D/0/U canalObstaculo2D/0/p
touch canalObstaculo2D/constant/transportProperties canalObstaculo2D/constant/turbulenceProperties
```

touch canalObstaculo2D/system/blockMeshDict canalObstaculo2D/system/controlDict canalObstaculo2D/system/fvSchemes canalObstaculo2D/system/fvSolution


### 3. Definir la geometría

En el sistema XY necesitamos cuatro coordenadas longitudinales y cuatro verticales.

Se construyen dos planos idénticos, uno en z=0 y otro en z=0.001. Cada plano contiene 16 vértices.

La numeración será:

En el plano z = 0 los vértices van de 0 a 15. En z = 0.001 se repite la geometría sumando 16 a cada identificador.


#### Archivo system/blockMeshDict


```bash
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object blockMeshDict;
}

scale 1;

vertices
(
    // z = 0
    (0     0      0)      // 0
    (0.08  0      0)      // 1
    (0.10  0      0)      // 2
    (0.20  0      0)      // 3

    (0     0.008  0)      // 4
    (0.08  0.008  0)      // 5
    (0.10  0.008  0)      // 6
    (0.20  0.008  0)      // 7

    (0     0.012  0)      // 8
    (0.08  0.012  0)      // 9
    (0.10  0.012  0)      // 10
    (0.20  0.012  0)      // 11

    (0     0.020  0)      // 12
    (0.08  0.020  0)      // 13
    (0.10  0.020  0)      // 14
    (0.20  0.020  0)      // 15

    // z = 0.001
    (0     0      0.001)  // 16
    (0.08  0      0.001)  // 17
    (0.10  0      0.001)  // 18
    (0.20  0      0.001)  // 19

    (0     0.008  0.001)  // 20
    (0.08  0.008  0.001)  // 21
    (0.10  0.008  0.001)  // 22
    (0.20  0.008  0.001)  // 23

    (0     0.012  0.001)  // 24
    (0.08  0.012  0.001)  // 25
    (0.10  0.012  0.001)  // 26
    (0.20  0.012  0.001)  // 27

    (0     0.020  0.001)  // 28
    (0.08  0.020  0.001)  // 29
    (0.10  0.020  0.001)  // 30
    (0.20  0.020  0.001)  // 31
);

blocks
(
    // Fila inferior
    hex (0 1 5 4 16 17 21 20)
        (80 16 1) simpleGrading (1 1 1)

    hex (1 2 6 5 17 18 22 21)
        (20 16 1) simpleGrading (1 1 1)

    hex (2 3 7 6 18 19 23 22)
        (100 16 1) simpleGrading (1 1 1)

    // Fila central: no hay bloque en el obstáculo
    hex (4 5 9 8 20 21 25 24)
        (80 8 1) simpleGrading (1 1 1)

    hex (6 7 11 10 22 23 27 26)
        (100 8 1) simpleGrading (1 1 1)

    // Fila superior
    hex (8 9 13 12 24 25 29 28)
        (80 16 1) simpleGrading (1 1 1)

    hex (9 10 14 13 25 26 30 29)
        (20 16 1) simpleGrading (1 1 1)

    hex (10 11 15 14 26 27 31 30)
        (100 16 1) simpleGrading (1 1 1)
);

edges
(
);

defaultPatch
{
    name frontAndBack;
    type empty;
}

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 16 20 4)
            (4 20 24 8)
            (8 24 28 12)
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (3 7 23 19)
            (7 11 27 23)
            (11 15 31 27)
        );
    }

    lowerWall
    {
        type wall;
        faces
        (
            (0 1 17 16)
            (1 2 18 17)
            (2 3 19 18)
        );
    }

    upperWall
    {
        type wall;
        faces
        (
            (12 28 29 13)
            (13 29 30 14)
            (14 30 31 15)
        );
    }

    obstacle
    {
        type wall;
        faces
        (
            (5 21 25 9)
            (6 10 26 22)
            (5 6 22 21)
            (9 25 26 10)
        );
    }
);

mergePatchPairs
(
);
```


#### Qué es nuevo

El obstáculo queda definido implícitamente por la ausencia del bloque central. Sus superficies aparecen en la sección:


```cpp
obstacle
{
    type wall;
    faces
    (
        (5 21 25 9)
        (6 10 26 22)
        (5 6 22 21)
        (9 25 26 10)
    );
}
```

Cada grupo de cuatro números es una cara cuadrilateral.

La malla tiene una sola capa de celdas en Z. Usamos defaultPatch de tipo empty para asignar las caras delantera y trasera que no tienen otro patch explícito. Esto es válido porque todas las demás caras exteriores se asignaron individualmente.

El número de celdas será:

Es decir, retiramos 160 celdas correspondientes al volumen ocupado por el obstáculo.


#### Comprobar la geometría antes de simular


```bash
blockMesh | tee log.blockMesh

checkMesh | tee log.checkMesh
```

Hay que verificar que checkMesh termine satisfactoriamente y que aparezcan los patches inlet, outlet, lowerWall, upperWall, obstacle y frontAndBack.

Si la malla es válida, podemos configurar la física.


### 4. Archivos físicos y numéricos

Los siete archivos restantes mantienen la física del tutorial anterior. La diferencia importante es que U debe incorporar la condición noSlip para el nuevo patch obstacle.


#### constant/transportProperties


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object transportProperties;
}

transportModel Newtonian;

nu [0 2 -1 0 0 0 0] 1e-4;
```


#### constant/turbulenceProperties


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object turbulenceProperties;
}

simulationType laminar;

laminar
{
    model           generalizedNewtonian;
    viscosityModel  powerLaw;

    nuMin 1e-6;
    nuMax 1e-2;

    k 1e-4;
    n 0.5;
}
```

La configuración generalizedNewtonian con powerLaw corresponde al marco de modelos laminares de OpenFOAM.com.


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class volVectorField;
    location "0";
    object U;
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

    lowerWall
    {
        type noSlip;
    }

    upperWall
    {
        type noSlip;
    }

    obstacle
    {
        type noSlip;
    }

    frontAndBack
    {
        type empty;
    }
}
```

Con esto, las cuatro superficies del obstáculo tienen velocidad nula. En particular, el fluido no puede atravesar el sólido.


#### 0/p


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class volScalarField;
    location "0";
    object p;
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

    lowerWall
    {
        type zeroGradient;
    }

    upperWall
    {
        type zeroGradient;
    }

    obstacle
    {
        type zeroGradient;
    }

    frontAndBack
    {
        type empty;
    }
}
```


#### system/fvSchemes


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object fvSchemes;
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


#### system/fvSolution


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object fvSolution;
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
    nNonOrthogonalCorrectors 0;

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


#### system/controlDict


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object controlDict;
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

Aumentamos el límite de iteraciones a 1500. La presencia del obstáculo puede dificultar la convergencia respecto del canal vacío.


### 5. Ejecutar y visualizar


```bash
blockMesh | tee log.blockMesh
checkMesh | tee log.checkMesh
simpleFoam 2>&1 | tee log.simpleFoam
```

Para abrir el caso en ParaView:


```cpp
touch canalObstaculo2D.foam
```

En ParaView, representá U → Magnitude en el plano XY.

Deberíamos observar aceleración del fluido en los espacios libres entre el obstáculo y las paredes, regiones de velocidad reducida junto a las superficies sólidas y una alteración del campo de presión.

uclalemur.com

Ejemplo visual orientativo de flujo alrededor de un obstáculo. No representa una solución obtenida con los parámetros de este tutorial.

Una advertencia física: con la viscosidad y velocidad elegidas, no necesariamente aparecerá una estela recirculante intensa. La geometría por sí sola no garantiza separación ni generación de vórtices. El resultado depende del balance entre inercia y esfuerzos viscosos.

Para una estela periódica de desprendimiento de vórtices necesitaríamos además utilizar un solver transitorio, como pimpleFoam, y condiciones de flujo apropiadas.


## 6. Cómo colocar dos obstáculos

Ahora vamos a construir una segunda variante con dos obstáculos rectangulares. Ambos estarán dentro del mismo dominio de fluido.

Los dos obstáculos tendrán las mismas dimensiones, pero posiciones diferentes:

Esto nos permitirá observar la interacción hidrodinámica entre obstáculos.

Para agregar el segundo ya no alcanza con declarar una nueva superficie wall: debemos modificar la geometría de los bloques y retirar el segundo volumen sólido.

Con varios obstáculos, escribir manualmente todas las coordenadas de cada vértice se vuelve innecesariamente propenso a errores. Podemos conservar blockMesh y generar su diccionario de manera determinista mediante un pequeño script Python.

El script utiliza únicamente la biblioteca estándar de Python y escribe un system/blockMeshDict completo. Además, permite cambiar las posiciones desde una lista, sin renumerar manualmente decenas de vértices.


### 7. Generar la geometría para varios obstáculos

Creá un segundo caso:


```bash
cd ..
mkdir -p canalDosObstaculos2D/{0,constant,system}

cp canalObstaculo2D/0/{U,p} canalDosObstaculos2D/0/
cp canalObstaculo2D/constant/{transportProperties,turbulenceProperties} canalDosObstaculos2D/constant/
cp canalObstaculo2D/system/{controlDict,fvSchemes,fvSolution} canalDosObstaculos2D/system/

cd canalDosObstaculos2D
```

Los siete archivos son exactamente los que acabamos de escribir. Mantendremos obstacle como un único patch de paredes, aunque contenga superficies de varios objetos.


#### Archivo make_mesh.py

Este archivo genera el diccionario system/blockMeshDict a partir de los límites del canal y de una lista de obstáculos. No hay que instalar NumPy, gmsh ni ningún paquete adicional.


```python
from pathlib import Path
# Dimensiones del canal (m)
L = 0.20
H = 0.020
thickness = 0.001
# Resolución espacial (m)
dx = 0.001
dy = 0.0005
# Obstáculos:
# (centro_x, centro_y, ancho, altura)
obstacles = [
    (0.09, 0.010, 0.020, 0.004),
    (0.15, 0.010, 0.020, 0.004),
]
# Límites de los obstáculos
rectangles = []
for cx, cy, w, h in obstacles:
    xmin = round(cx - w / 2, 10)
    xmax = round(cx + w / 2, 10)
    ymin = round(cy - h / 2, 10)
    ymax = round(cy + h / 2, 10)
    assert 0 < xmin < xmax < L
    assert 0 < ymin < ymax < H
    rectangles.append((xmin, xmax, ymin, ymax))
# No permitir obstáculos superpuestos
for i, a in enumerate(rectangles):
    for b in rectangles[i + 1:]:
        overlap_x = a[0] < b[1] and b[0] < a[1]
```

Ejecutar:


```bash
python3 make_mesh.py
blockMesh
checkMesh
```

Con las coordenadas del ejemplo, esperamos 48 vértices y 13 bloques de fluido, con un total de 7680 celdas: 8000 originales menos 160 correspondientes a cada obstáculo.

Después:


```cpp
simpleFoam 2>&1 | tee log.simpleFoam
touch canalDosObstaculos2D.foam
```

No es necesario modificar los otros archivos porque todas las superficies sólidas de ambos obstáculos se agrupan en el patch obstacle.


### 8. Modificar la posición de los obstáculos

A partir de ahora, la parte que realmente nos interesa es esta:


```cpp
obstacles = [
    (0.09, 0.010, 0.020, 0.004),
    (0.15, 0.010, 0.020, 0.004),
]
```

El formato es:

Podemos probar otras geometrías sin cambiar manualmente los vértices.


#### Diseñador de obstáculos

Modificá las posiciones y dimensiones. El esquema muestra el espacio ocupado por los obstáculos dentro del canal.

Obstáculo A

Centro X (m)

0.090

Centro Y (m)

0.010

Ancho (m)

0.020

Altura (m)

0.004

Obstáculo B

Activado

Centro X (m)

0.150

Centro Y (m)

0.010

Ancho (m)

0.020

Altura (m)

0.004

Copiar configuración Python

El diseñador permite generar coordenadas para sustituir directamente la lista obstacles de make_mesh.py. Después hay que volver a ejecutar el script, blockMesh y checkMesh.

Una limitación: el script está diseñado para obstáculos rectangulares internos que no se superponen ni tocan las paredes exteriores. Tampoco controla automáticamente la calidad de las celdas que puedan resultar de separaciones extremadamente pequeñas; por eso checkMesh sigue siendo obligatorio.


### 9. Qué conviene comparar

Con un obstáculo podemos estudiar la perturbación individual que introduce en el campo de velocidades. Con dos aparecen interacciones entre sus regiones de influencia.

Especialmente interesantes son tres configuraciones.

Obstáculos alineados

Uno detrás del otro. Permite evaluar cómo el primero altera el flujo que alcanza al segundo.

Obstáculos escalonados

Desplazados también en Y. Permite estudiar la redistribución transversal del flujo y la asimetría del campo de presión.

Obstáculos enfrentados

Ubicados a la misma coordenada X, dejando un paso central estrecho. Permite estudiar aceleración local y pérdida de carga por constricción.

Para cada variante, compararíamos las velocidades máximas, las diferencias de presión entrada-salida, la distribución de viscosidad aparente y los errores de conservación de masa.

Importante: este caso sigue siendo laminar y estacionario. Si aparecen oscilaciones persistentes o el solver no converge a un estado estacionario, no debemos interpretar automáticamente ese resultado como una estela física; puede requerir un análisis transitorio o una revisión de malla y discretización.

La siguiente extensión natural del ejercicio será utilizar obstáculos circulares, donde tendremos que introducir aristas curvas con blockMesh o pasar a snappyHexMesh.
