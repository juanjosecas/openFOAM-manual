# Tutorial 03 — Estenosis capilar 2D

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Microfluídica

Estenosis del 50 %

Fluido pseudoplástico


```cpp
simpleFoam
```

Vamos a construir un microcanal que reproduce el estrechamiento localizado de un capilar. Conservamos el enfoque 2D, el modelo de viscosidad dependiente de la tasa de corte y el solver estacionario de los tutoriales anteriores.

La diferencia principal es geométrica: en lugar de colocar un obstáculo dentro del canal, modificaremos la posición de sus paredes para generar una estenosis simétrica.


### 1. Geometría

Representación esquemática del dominio. El estrechamiento se genera desplazando las paredes superior e inferior hacia el centro.

Precisión fisiológica: una estenosis real en un capilar de 10 µm no se representa adecuadamente mediante un fluido homogéneo. Los eritrocitos tienen dimensiones próximas al diámetro capilar, sufren deformaciones y pueden circular individualmente. El efecto Fåhræus–Lindqvist también altera la viscosidad aparente con el diámetro. Nuestro modelo es una aproximación continua para estudiar campos hidrodinámicos, no una predicción cuantitativa del tránsito eritrocitario.


### 2. Nuevo concepto: paredes que cambian de posición

En los tutoriales anteriores las paredes eran horizontales. Ahora construiremos seis bloques consecutivos con diferentes coordenadas verticales.

Seis bloques hexaédricos conectados. Cada sección transversal puede tener una abertura distinta. Coordenadas en µm.

Las coordenadas de cada sección serán:

La línea central permanece en , mientras la distancia entre las paredes disminuye hasta 5 µm.

Usaremos blockMesh y no necesitaremos STL ni snappyHexMesh. Inicialmente las paredes estrechadas serán poligonales. Después podremos reemplazarlas por una curva suave.


### 3. Crear los archivos

Dentro de tu contenedor Docker:


```bash
mkdir -p estenosisCapilar2D/{0,constant,system}
cd estenosisCapilar2D
```


#### 3.1. system/blockMeshDict

La geometría se construye con 28 vértices: 14 en z=0 y otros 14 en z=1 µm.

Cada bloque tiene 40 divisiones transversales. El número de divisiones longitudinales depende de la longitud de cada segmento.


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
    // Plano z = 0
    (0        0        0)  // 0
    (0        10e-6    0)  // 1
    (30e-6    0        0)  // 2
    (30e-6    10e-6    0)  // 3
    (40e-6    1.25e-6  0)  // 4
    (40e-6    8.75e-6  0)  // 5
    (50e-6    2.5e-6   0)  // 6
    (50e-6    7.5e-6   0)  // 7
    (60e-6    1.25e-6  0)  // 8
    (60e-6    8.75e-6  0)  // 9
    (70e-6    0        0)  // 10
    (70e-6    10e-6    0)  // 11
    (100e-6   0        0)  // 12
    (100e-6   10e-6    0)  // 13

    // Plano z = 1 micrometro
    (0        0        1e-6)  // 14
    (0        10e-6    1e-6)  // 15
    (30e-6    0        1e-6)  // 16
    (30e-6    10e-6    1e-6)  // 17
    (40e-6    1.25e-6  1e-6)  // 18
    (40e-6    8.75e-6  1e-6)  // 19
    (50e-6    2.5e-6   1e-6)  // 20
    (50e-6    7.5e-6   1e-6)  // 21
    (60e-6    1.25e-6  1e-6)  // 22
    (60e-6    8.75e-6  1e-6)  // 23
    (70e-6    0        1e-6)  // 24
    (70e-6    10e-6    1e-6)  // 25
    (100e-6   0        1e-6)  // 26
    (100e-6   10e-6    1e-6)  // 27
);

blocks
(
    hex (0 2 3 1 14 16 17 15)
        (30 40 1) simpleGrading (1 1 1)
    hex (2 4 5 3 16 18 19 17)
        (10 40 1) simpleGrading (1 1 1)
    hex (4 6 7 5 18 20 21 19)
        (10 40 1) simpleGrading (1 1 1)
    hex (6 8 9 7 20 22 23 21)
        (10 40 1) simpleGrading (1 1 1)
    hex (8 10 11 9 22 24 25 23)
        (10 40 1) simpleGrading (1 1 1)
    hex (10 12 13 11 24 26 27 25)
        (30 40 1) simpleGrading (1 1 1)
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
            (0 14 15 1)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (12 13 27 26)
        );
    }
    lowerWall
    {
        type wall;
        faces
        (
            (0 2 16 14)
            (2 4 18 16)
            (4 6 20 18)
            (6 8 22 20)
            (8 10 24 22)
            (10 12 26 24)
        );
    }
    upperWall
    {
        type wall;
        faces
        (
            (1 15 17 3)
            (3 17 19 5)
            (5 19 21 7)
            (7 21 23 9)
            (9 23 25 11)
            (11 25 27 13)
        );
    }
);

mergePatchPairs
(
);
```

La malla tendrá 4000 celdas, repartidas en seis bloques. Los límites entre bloques son interfaces internas, no paredes. Las únicas paredes físicas son lowerWall y upperWall.

Al modificar las coordenadas de los vértices de las secciones centrales, podemos cambiar la severidad y asimetría de la estenosis.


#### 3.2. constant/transportProperties

Usamos el mismo esquema de viscosidad cinemática de referencia que en los tutoriales anteriores.


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


#### 3.3. constant/turbulenceProperties

El modelo continúa siendo generalizedNewtonian con ley de potencia.


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
    model generalizedNewtonian;
    viscosityModel powerLaw;
    nuMin 1e-6;
    nuMax 1e-4;
    k 1e-4;
    n 0.5;
}
```

Este modelo permite que la viscosidad disminuya en regiones de elevada tasa de corte. Su configuración coincide con la sintaxis publicada para OpenFOAM.com.

OpenFOAM

Los parámetros no constituyen un ajuste experimental de sangre capilar. Se utilizan para estudiar una respuesta pseudoplástica genérica.


#### 3.4. 0/U


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

internalField uniform (0.0005 0 0);

boundaryField
{
    inlet
    {
        type fixedValue;
        value uniform (0.0005 0 0);
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

    frontAndBack
    {
        type empty;
    }
}
```

La velocidad de entrada es , equivalente a 0.5 mm/s.


#### 3.5. 0/p


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

    frontAndBack
    {
        type empty;
    }
}
```


#### 3.6. system/fvSchemes


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


#### 3.7. system/fvSolution


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
        tolerance 1e-9;
        relTol 0.01;
        smoother GaussSeidel;
    }

    U
    {
        solver smoothSolver;
        smoother symGaussSeidel;
        tolerance 1e-9;
        relTol 0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;

    consistent no;

    residualControl
    {
        p 1e-7;
        U 1e-8;
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
Utilizamos un corrector de no ortogonalidad porque la malla contiene celdas deformadas en la región de estenosis.
```


#### 3.8. system/controlDict


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
endTime 2000;

deltaT 1;

writeControl timeStep;
writeInterval 100;

purgeWrite 0;

writeFormat ascii;
writePrecision 10;
writeCompression off;

timeFormat general;
timePrecision 6;

runTimeModifiable true;
Las 2000 unidades corresponden al límite máximo de iteraciones del solver estacionario, no a 2000 segundos físicos.
```


### 4. Ejecutar la simulación

Primero generamos la malla y comprobamos su calidad:


```bash
blockMesh 2>&1 | tee log.blockMesh
checkMesh -allGeometry -allTopology 2>&1 | tee log.checkMesh
```

Deberían aparecer 4000 celdas hexaédricas y los cinco patches: inlet, outlet, lowerWall, upperWall y frontAndBack.

En particular, revisar en checkMesh la no ortogonalidad máxima, el skewness, la existencia de volúmenes negativos y el estado final de la verificación. Las esquinas entre tramos inclinados y horizontales son las regiones que merecen mayor atención.

Una vez aceptada la malla:


```cpp
simpleFoam 2>&1 | tee log.simpleFoam
```

Podemos inspeccionar la convergencia con:


```cpp
grep -E "Solving for|continuity errors" log.simpleFoam | tail -n 50
```

Estado de verificación: la sintaxis del modelo reológico y del solver está respaldada por la documentación de OpenFOAM.com, pero no he ejecutado este caso en tu contenedor v2406. El primer resultado que debemos verificar es checkMesh, antes de interpretar cualquier campo numérico.


### 5. Visualizar la estenosis en ParaView

Crear el archivo de apertura:


```cpp
touch estenosisCapilar2D.foam
```

Abrirlo desde ParaView. Elegir el último estado calculado y colocar la cámara sobre el eje Z.


#### Campo de velocidades

Representar U → Magnitude.

El caudal de un fluido incompresible debe conservarse:

En nuestro canal 2D de espesor constante, el área transversal es proporcional a la abertura.

Por tanto, al reducirse la abertura a la mitad, la velocidad media local debe duplicarse aproximadamente.

Antes de la estenosis

0.5 mm/s

Velocidad media

En la sección mínima

1.0 mm/s

Velocidad media esperada

Esta relación se refiere a velocidades medias transversales, no a las velocidades máximas ni al valor de cada celda. La sección mínima está situada en x=50e-6.


#### Campo de presión

Representar p.

Esperamos un gradiente de presión mayor en la región estrechada y una presión superior aguas arriba para sostener el mismo caudal. La presión local puede recuperarse parcialmente después de la expansión, pero la resistencia viscosa produce una caída global de presión.

Podemos convertir la presión cinemática en presión física con Calculator:

La salida se expresará en pascales, tomando una densidad de referencia de 1050 kg/m³.


#### Campo de tasa de deformación

Una variable muy interesante en este problema es:

donde $\mathbf D$ es el tensor simétrico de gradientes de velocidad.

Para obtener su distribución en OpenFOAM, primero podemos generar el gradiente de velocidad mediante postprocesamiento:


```cpp
simpleFoam -postProcess -func "grad(U)" -latestTime
```

Esto debería crear el campo grad(U) en el último directorio de resultados. Después podemos analizarlo en ParaView, incluyendo el cálculo del tensor simétrico y su norma si queremos representar directamente .

La región estrechada debería presentar gradientes de velocidad elevados, especialmente junto a las paredes. Como el modelo es pseudoplástico, allí esperamos una reducción de la viscosidad aparente.


### 6. Variar la severidad de la estenosis

Esta es la parte más útil para hacer experimentos.

La severidad geométrica se define aquí como:

donde .

Reducción de abertura

50%

Abertura mínima

5.0 µm

Velocidad media en garganta

1.00 mm/s

Coordenadas de los vértices de la sección x = 50 µm, para reemplazar los vértices 6, 7, 20 y 21 de blockMeshDict.


```cpp
(50e-6 2.500e-6 0) // 6
(50e-6 7.500e-6 0) // 7
(50e-6 2.500e-6 1e-6) // 20
(50e-6 7.500e-6 1e-6) // 21
```

Después de modificar blockMeshDict hay que regenerar la malla y comenzar una simulación limpia, evitando que campos de un caso anterior se reutilicen accidentalmente.


### 7. Análisis que podemos realizar

El primer conjunto de experimentos puede mantener constante el caudal y variar exclusivamente la severidad de la estenosis.

Estas velocidades se derivan de conservación de caudal; no son resultados de OpenFOAM.

Con las simulaciones podremos evaluar cómo cambian la caída de presión, las tensiones de corte sobre las paredes, los gradientes de velocidad y el campo de viscosidad aparente. Resulta especialmente interesante identificar si la mayor reducción de viscosidad pseudoplástica compensa parcialmente el aumento de resistencia hidráulica producido por la estenosis.

Para comprobar la conservación de flujo, también podemos utilizar la utilidad postProcess con el objeto funcional flowRatePatch cuando esté disponible en tu instalación, o integrar el campo de flujo phi sobre las superficies de entrada y salida.


### 8. Limitaciones y siguiente refinamiento geométrico

La estenosis construida en este tutorial tiene paredes lineales por tramos y cambios bruscos de pendiente. Estas esquinas pueden concentrar gradientes numéricos y modificar la distribución local de esfuerzos.

El siguiente refinamiento es reemplazar el contorno por una función suave, por ejemplo:

Esta expresión permite controlar independientemente:

: severidad.

: posición del centro.

: extensión longitudinal de la estenosis.

Para construir esa geometría podemos seguir usando blockMesh, pero generando los vértices a partir de la función en Python. Así evitaríamos modificar manualmente cada coordenada.

En términos fisiológicos, una segunda mejora sería pasar a una geometría axisimétrica y, para capilares cuyo lumen es comparable al tamaño eritrocitario, incorporar células deformables o un modelo multifásico. La aproximación homogénea es particularmente limitada en ese régimen.

El experimento inicial recomendado es comparar el canal sin estenosis y el canal con reducción del 50 %, manteniendo idénticos caudal, reología y resolución transversal. Una vez verificada la malla y la convergencia, la diferencia de presión entre entrada y salida y la distribución de esfuerzos de pared serán los observables centrales.

PROTOCOLO RÁPIDO — Prototipo de animación: simular inicialmente 0,5 segundos, registrar cada 0,01 s y observar la caída del chorro. La interfaz de cuatro celdas de ancho sólo permite una visualización preliminar: no interpretar gotas de una o dos celdas como resultados físicos.
