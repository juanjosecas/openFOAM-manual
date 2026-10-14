# Tutorial 08. Flujo transitorio en una tubería cilíndrica 3D

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

OpenFOAM.com v2406 · Geometría nativa blockMesh · Solver pimpleFoam · Animación en ParaView


### Objetivo y configuración inicial

Se construirá una tubería circular verdaderamente tridimensional, sin CAD ni archivos STL. Un líquido viscoso ocupa inicialmente todo el interior. La velocidad de entrada crece desde el reposo y después oscila, lo que permitirá animar perfiles de velocidad y presión. Se prioriza un prototipo de bajo costo, no una malla validada para resultados cuantitativos.


### Cómo se construye el cilindro

blockMesh exige bloques hexaédricos. Para construir un disco sin celdas degeneradas, se utiliza una O-grid: un cuadrado central rodeado por cuatro bloques. Se repite esa sección en x=0 y x=0,12 m. Los puntos exteriores están en (y,z)=(±R/√2,±R/√2). Las aristas exteriores son arcos de circunferencia (palabra clave arc). Las caras laterales forman pipeWall; no se usa empty porque la malla es 3D.


### Crear la estructura y los archivos

Comandos Bash


```bash
mkdir -p tuberiaCilindrica3D/{0,constant,system}
touch tuberiaCilindrica3D/0/{U,p}
touch tuberiaCilindrica3D/constant/{transportProperties,turbulenceProperties}
touch tuberiaCilindrica3D/system/{blockMeshDict,controlDict,fvSchemes,fvSolution}
touch tuberiaCilindrica3D/Allrun
cd tuberiaCilindrica3D
```


### Archivos completos de configuración

system/blockMeshDict


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
    (0 -0.004 -0.004) // 0 núcleo de entrada
    (0  0.004 -0.004) // 1
    (0  0.004  0.004) // 2
    (0 -0.004  0.004) // 3
    (0 -0.007071067812 -0.007071067812) // 4 perímetro
    (0  0.007071067812 -0.007071067812) // 5
    (0  0.007071067812  0.007071067812) // 6
    (0 -0.007071067812  0.007071067812) // 7
    (0.12 -0.004 -0.004) // 8 núcleo de salida
    (0.12  0.004 -0.004) // 9
    (0.12  0.004  0.004) // 10
    (0.12 -0.004  0.004) // 11
    (0.12 -0.007071067812 -0.007071067812) // 12 perímetro
    (0.12  0.007071067812 -0.007071067812) // 13
    (0.12  0.007071067812  0.007071067812) // 14
    (0.12 -0.007071067812  0.007071067812) // 15
);
blocks
(
    hex (0 1 2 3 8 9 10 11) (8 8 48) simpleGrading (1 1 1)
    hex (4 5 1 0 12 13 9 8) (8 6 48) simpleGrading (1 1 1)
    hex (1 5 6 2 9 13 14 10) (6 8 48) simpleGrading (1 1 1)
    hex (3 2 6 7 11 10 14 15) (8 6 48) simpleGrading (1 1 1)
    hex (4 0 3 7 12 8 11 15) (6 8 48) simpleGrading (1 1 1)
);
edges
(
    arc 4 5 (0 0 -0.01)
    arc 5 6 (0 0.01 0)
    arc 6 7 (0 0 0.01)
    arc 7 4 (0 -0.01 0)
    arc 12 13 (0.12 0 -0.01)
    arc 13 14 (0.12 0.01 0)
    arc 14 15 (0.12 0 0.01)
    arc 15 12 (0.12 -0.01 0)
);
boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 3 2 1)
            (4 0 1 5)
            (1 2 6 5)
            (3 7 6 2)
            (4 7 3 0)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (8 9 10 11)
            (12 13 9 8)
            (9 13 14 10)
            (11 10 14 15)
            (12 8 11 15)
        );
    }
    pipeWall
    {
        type wall;
        faces
        (
            (4 5 13 12)
            (5 6 14 13)
            (6 7 15 14)
            (7 4 12 15)
        );
    }
);
mergePatchPairs ();
```

La tripleta de divisiones indica la resolución en las tres direcciones locales del bloque. Todas las interfaces compartidas necesitan discretizaciones compatibles. La expresión arc i j (x y z) define el punto medio geométrico de un arco circular, no una celda adicional.

constant/transportProperties


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

constant/turbulenceProperties


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object turbulenceProperties;
}
simulationType laminar;
```

El solver transitorio no requiere un modelo turbulento: el régimen elegido es laminar. La viscosidad de referencia es deliberadamente superior a la del agua para facilitar la primera animación.

0/U


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
internalField uniform (0 0 0);
boundaryField
{
    inlet
    {
        type uniformFixedValue;
        uniformValue table
        (
            (0.00 (0.000 0 0))
            (0.10 (0.020 0 0))
            (0.50 (0.020 0 0))
            (0.75 (0.005 0 0))
            (1.00 (0.020 0 0))
            (1.25 (0.005 0 0))
            (1.50 (0.020 0 0))
            (1.75 (0.005 0 0))
            (2.00 (0.020 0 0))
        );
        value uniform (0 0 0);
    }
    outlet
    {
        type zeroGradient;
    }
    pipeWall
    {
        type noSlip;
    }
}
```

uniformFixedValue utiliza una tabla de pares (tiempo, vector U); entre tiempos se interpola linealmente. internalField es el estado inicial dentro del volumen. noSlip impone velocidad nula sobre la pared.

0/p


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
    inlet { type zeroGradient; }
    outlet { type fixedValue; value uniform 0; }
    pipeWall { type zeroGradient; }
}
```

p es presión cinemática (m²/s²), no presión en Pa; la salida fija su valor de referencia.

system/fvSchemes


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
    default Euler;
}
gradSchemes
{
    default Gauss linear;
}
divSchemes
{
    default none;
    div(phi,U) Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
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

Euler es una integración temporal implícita de primer orden. Upwind prioriza robustez y puede difuminar gradientes: basta para este prototipo visual, pero no reemplaza un estudio de independencia de malla y paso temporal.

system/fvSolution


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
    pFinal
    {
        $p;
        relTol 0;
    }
    U
    {
        solver smoothSolver;
        smoother symGaussSeidel;
        tolerance 1e-8;
        relTol 0.1;
    }
    UFinal
    {
        $U;
        relTol 0;
    }
}
PIMPLE
{
    momentumPredictor yes;
    nOuterCorrectors 1;
    nCorrectors 2;
    nNonOrthogonalCorrectors 0;
}
```

PIMPLE acopla velocidad y presión por paso temporal. nOuterCorrectors define iteraciones externas, nCorrectors las correcciones internas de presión. Los residuos deben vigilarse durante la primera ejecución.

system/controlDict


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object controlDict;
}
application pimpleFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime 2;
deltaT 0.001;
adjustTimeStep yes;
maxCo 0.5;
maxDeltaT 0.005;
writeControl adjustableRunTime;
writeInterval 0.01;
purgeWrite 0;
writeFormat binary;
writePrecision 8;
writeCompression off;
timeFormat fixed;
timePrecision 5;
runTimeModifiable true;
```

deltaT es el intervalo de integración inicial; writeInterval determina cada cuánto se guardan resultados. adjustableRunTime hace coincidir las escrituras con tiempos físicos, aunque el paso de integración se adapte para respetar maxCo. purgeWrite=0 conserva todos los cuadros.

Allrun


```cpp
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SOLVER=$(foamDictionary system/controlDict -entry application -value)
echo "OpenFOAM $(foamVersion) | Caso: $(pwd) | Solver: $SOLVER"
command -v "$SOLVER" >/dev/null 2>&1 || { echo "Solver ausente"; exit 1; }
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1 || { tail -n 50 log.checkMesh; exit 1; }
grep -q 'Mesh OK' log.checkMesh || { tail -n 50 log.checkMesh; exit 1; }
"$SOLVER" 2>&1 | tee "log.$SOLVER"
```


### Ejecución y controles

Comandos Bash


```cpp
chmod +x Allrun
./Allrun
tail -n 40 log.pimpleFoam
grep 'continuity errors' log.pimpleFoam | tail -n 15
touch tuberiaCilindrica3D.foam
```

Allrun lee application desde controlDict para evitar ejecutar el solver equivocado. Este script vuelve a mallar, pero no elimina resultados previos. Para un nuevo cálculo desde cero, limpiar primero los directorios de tiempo distintos de 0; conservar siempre 0/, constant/ y system/.


### Animación 3D en ParaView

Abrir tuberiaCilindrica3D.foam, habilitar el volumen interno y la pared pipeWall, y aplicar opacidad 0,15–0,30 a la pared. Para observar la distribución de U, usar Slice con plano longitudinal de normal (0,0,1), y fijar el rango de color antes de exportar. Para líneas de corriente instantáneas usar Stream Tracer; para trayectorias materiales, Particle Tracer. Elegir Snap To TimeSteps para reproducir los aproximadamente 200 estados. Exportar la secuencia como PNG de 1920×1080.

Exportar MP4 (si FFmpeg incluye libx264)


```cpp
ffmpeg -framerate 30 -i frame.%04d.png \
    -c:v libx264 -crf 18 -pix_fmt yuv420p tuberia3D.mp4
```


### Interpretación y límites

Se espera que el campo U evolucione debido a la aceleración inicial y a las oscilaciones de la velocidad de entrada. No hay avance de una superficie libre: el tubo está lleno desde t=0. El perfil totalmente desarrollado para flujo laminar newtoniano es parabólico, pero la solución transitoria no tiene por qué coincidir instantáneamente con él. Para comparaciones cuantitativas, verificar conservación de masa y sensibilidad a malla, discretización y paso temporal.


### Cambios geométricos sencillos

Para modificar la longitud se cambian las coordenadas X de los vértices de salida. Para variar el radio hay que escalar todos los puntos perimetrales, ajustar los arcos y, si procede, el cuadrado central. Una estenosis axial requiere agregar secciones transversales y conectarlas con más bloques; es apropiado automatizar la generación de vértices con Python. La geometría de este tutorial permanece fija durante el cálculo.

Referencias: https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.3-mesh-generation-with-the-blockmesh-utility ; https://doc.openfoam.com/2312/tools/processing/boundary-conditions/rtm/derived/general/uniformFixedValue/ ; https://www.openfoam.com/news/main-news/openfoam-v2406/numerics

Estado: caso propuesto para OpenFOAM.com v2406; requiere ejecutar blockMesh/checkMesh y el solver en el contenedor del usuario para confirmar la compatibilidad exacta.
