# Tutorial 10B · Tubería laminar · case1

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Tres variantes recibidas: condiciones y esquemas diferentes para comparar flujo en conductos y muestreos de perfiles. Se conservan como subcasos porque no son archivos duplicados.


### Procedencia y compatibilidad

• Origen: OpenFOAM Foundation 4.x.

• Solver original: icoFoam (transitorio).

• Para animación, case0/case1 son preferibles por su formulación ya transitoria; case2 requiere migrar fvSchemes/fvSolution y cambiar el solver como un conjunto.

• La transcripción conserva sampleDict, decomposeParDict y otros diccionarios pertinentes.


### Versión rápida: parámetros de animación

Configuración inicial propuesta: duración física 2 s, intervalo de escritura 0.01 s. Estos valores son de prototipado; verificar el CFL y el fenómeno antes de utilizarlos como resultados científicos.

Se conserva a continuación el texto íntegro de los diccionarios suministrados, para que pueda compararse la configuración original con los cambios necesarios. Los bloques originales no se presentan como migrados ni validados en v2406.


### Estructura y creación de archivos

Desde el directorio de trabajo:


```bash
mkdir -p Tubería_laminar_·_case1/{0,constant,system}
touch Tubería_laminar_·_case1/0/U Tubería_laminar_·_case1/0/p
touch Tubería_laminar_·_case1/constant/transportProperties
touch Tubería_laminar_·_case1/system/blockMeshDict Tubería_laminar_·_case1/system/controlDict Tubería_laminar_·_case1/system/decomposeParDict Tubería_laminar_·_case1/system/fvSchemes Tubería_laminar_·_case1/system/fvSolution Tubería_laminar_·_case1/system/sampleDict
```


### Adaptación temporal propuesta (system/controlDict)


```cpp
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object controlDict;
}

application icoFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime 2;
deltaT 0.0005;
adjustTimeStep yes;
maxCo 0.5;
maxDeltaT 0.005;
writeControl adjustableRunTime;
writeInterval 0.01;
purgeWrite 0;
writeFormat binary;
writeCompression off;
timeFormat fixed;
timePrecision 6;
runTimeModifiable true;
```

Este controlDict es una plantilla para el solver indicado; no garantiza compatibilidad con los demás archivos heredados. Para interFoam se necesita también controlar maxAlphaCo; para el caso lagrangiano deben revisarse las opciones temporales soportadas por su solver.


### Ejecutar y visualizar


```bash
# Después de migrar/verificar los demás diccionarios
blockMesh 2>&1 | tee log.blockMesh
checkMesh -allGeometry -allTopology 2>&1 | tee log.checkMesh
# Ejecutar solamente cuando checkMesh sea satisfactorio
icoFoam 2>&1 | tee log.icoFoam
touch caso.foam
```

En ParaView: abrir caso.foam, mostrar Surface with Edges para revisar la malla, seleccionar el campo principal y usar Snap To TimeSteps. Mantener fija la escala de colores al exportar una animación.


### Archivos originales completos del paquete


#### 0/U


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            pressureNormalInletOutletVelocity;
        phi             phi;
        rho             rho;
        value           uniform (0 0 0);
    }

    outlet
    {
	type 		zeroGradient;
    }

    top
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }

    bottom
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }

    front
    {
        type            empty;
    }

    back
    {
        type            empty;
    }
}

// ************************************************************************* //
```


#### 0/p


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1.53103;

/*
        type            totalPressure;
        U               U;
        phi             phi;
        rho             none;
        psi             none;
        gamma           1.4;
        p0              uniform 2.025;
*/
    }

    outlet
    {

        type            fixedValue;
        value           uniform 0;

        //type 		zeroGradient;
    }

    top
    {
	type 		zeroGradient;           
    }

    bottom
    {
	type 		zeroGradient;           
    }

    front
    {
        type            empty;
    }

    back
    {
        type            empty;
    }
}

// ************************************************************************* //
```


#### constant/transportProperties


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

//nu              nu [ 0 2 -1 0 0 0 0 ] 0.05;
nu              nu [ 0 2 -1 0 0 0 0 ] 0.01;
//nu              nu [ 0 2 -1 0 0 0 0 ] 0.000004;

// ************************************************************************* //
```


#### system/blockMeshDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

xmin 0;
xmax 10;
ymin -0.5;
ymax 0.5;
zmin 0;
zmax 0.1;

vertices
(
    ($xmin  $ymin  $zmin)
    ($xmax  $ymin  $zmin)
    ($xmax  $ymax  $zmin)
    ($xmin  $ymax  $zmin)
    ($xmin  $ymin  $zmax)
    ($xmax  $ymin  $zmax)
    ($xmax  $ymax  $zmax)
    ($xmin  $ymax  $zmax)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 10 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    top
    {
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }
    inlet
    {
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (2 6 5 1)
        );
    }
    bottom
    {
        type wall;
        faces
        (
            (1 5 4 0)
        );
    }
    back
    {
        type empty;
        faces
        (
            (0 3 2 1)
        );
    }
    front
    {
        type empty;
        faces
        (
            (4 5 6 7)
        );
    }
);

mergePatchPairs
(
);

// ************************************************************************* //
```


#### system/controlDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     icoFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         20;

deltaT          0.05;

/*
writeControl    timeStep;
writeInterval   100;
*/

writeControl    runTime;
writeInterval   1;

purgeWrite      0;

writeFormat     ascii;

writePrecision  8;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //

functions
{

///////////////////////////////////////////////////////////////////////////

minmaxdomain
{
    type fieldMinMax;

    functionObjectLibs ("libfieldFunctionObjects.so");

    enabled true; //true or false

    mode component;

    writeControl timeStep;
    writeInterval 1;

    log true;

    fields (p U);
}

///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////
inMassFlow
{
    type            surfaceRegion;
    functionObjectLibs ("libfieldFunctionObjects.so");
    enabled         true;

    //writeControl     outputTime;
    writeControl   timeStep;
    writeInterval  1;

    log             true;

    writeFields     false;

    regionType          patch;
    name      inlet;

    operation       sum;

    fields
    (
        phi
    );
}
///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////
outMassFlow
{
    type            surfaceRegion;
    functionObjectLibs ("libfieldFunctionObjects.so");
    enabled         true;

    //writeControl     outputTime;
    writeControl   timeStep;
    writeInterval  1;

    log             true;

    writeFields     false;

    regionType          patch;
    name      outlet;

    operation       sum;

    fields
    (
        phi
    );
}
///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////

inPre
{
    type            surfaceRegion;
    functionObjectLibs ("libfieldFunctionObjects.so");
    enabled         true;

    //writeControl     outputTime;
    writeControl   timeStep;
    writeInterval  1;

    log             true;

    writeFields     false;

    regionType          patch;
    name      inlet;

    operation       weightedAverage;

    fields
    (
        phi
        U
	p
    );
}

/*
CoV
areaAverage
areaIntegrate
areaNormalAverage
areaNormalIntegrate
average
max
min
none
sum
sumDirection
sumDirectionBalance
sumMag
weightedAreaAverage
weightedAverage
*/

///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////

outMax
{
    type            surfaceRegion;
    functionObjectLibs ("libfieldFunctionObjects.so");
    enabled         true;

    //writeControl     outputTime;
    writeControl   timeStep;
    writeInterval  1;

    log             true;

    writeFields     false;

    regionType          patch;
    name      outlet;

    operation       max;

    fields
    (
        U
	p
    );
}

///////////////////////////////////////////////////////////////////////////

};
```


#### system/decomposeParDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains 4;

method          scotch;

// ************************************************************************* //
```


#### system/fvSchemes


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linear;
  //div(phi,U)      Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear orthogonal;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         orthogonal;
}

// ************************************************************************* //
```


#### system/fvSolution


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
/*
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0;
*/
        solver           GAMG;
        tolerance        1e-6;
        relTol           0.01;
        smoother         GaussSeidel;
        nPreSweeps       0;
        nPostSweeps      2;
        cacheAgglomeration on;
        agglomerator     faceAreaPair;
        nCellsInCoarsestLevel 100;
        mergeLevels      1;
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    U
    {
/*
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-08;
        relTol          0;
*/
        solver          PBiCG;
        preconditioner  DILU;
        tolerance       1e-08;
        relTol          0;
    }
}

PISO
{
    nCorrectors     1;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

// ************************************************************************* //
```


#### system/sampleDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.x                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      sampleDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

type sets;

setFormat raw;

//interpolationScheme cell;
//interpolationScheme cellPoint;
interpolationScheme cellPointFace;

// Fields to sample.
fields
(
    U
    p
//    T
//    rho
);

sets
(

    s1
    {
        type            midPointAndFace;
        //type            midPoint;
        //type            face;

        //type            uniform;
	//nPoints 	24;

        axis            x;
        start           ( 0   0 0);
        end             ( 10  0 0);
    }

    s2
    {
        type            midPointAndFace;
        //type            midPoint;
        //type            face;

        //type            uniform;
	//nPoints 	100;

        axis            y;
        start           (9 -1 0);
        end             (9  1 0);
    }

);

// *********************************************************************** //
```

Fin de la transcripción de los archivos del paquete.
