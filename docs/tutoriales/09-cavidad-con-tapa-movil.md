# Tutorial 09 · Cavidad 2D con tapa móvil

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Flujo transitorio impulsado por el movimiento de una pared. Permite visualizar la generación de un vórtice principal y estructuras secundarias en una cavidad cerrada.


### Procedencia y compatibilidad

• Fuente: tutorial original de OpenFOAM Foundation 4.x, que usa icoFoam y esquema temporal backward.

• icoFoam existe en OpenFOAM.com v2406; los diccionarios antiguos no se consideran probados.

• Para prototipado: comenzar con Re≈100, mantener malla 2D y reducir duración respecto de los 50 s originales; verificar si 2 s bastan para visualizar el arranque.

• Adaptación recomendada: conservar icoFoam y las condiciones originales; no reemplazar sin necesidad por pimpleFoam.


### Versión rápida: parámetros de animación

Configuración inicial propuesta: duración física 2 s, intervalo de escritura 0.01 s. Estos valores son de prototipado; verificar el CFL y el fenómeno antes de utilizarlos como resultados científicos.

Se conserva a continuación el texto íntegro de los diccionarios suministrados, para que pueda compararse la configuración original con los cambios necesarios. Los bloques originales no se presentan como migrados ni validados en v2406.


### Estructura y creación de archivos

Desde el directorio de trabajo:


```bash
mkdir -p Cavidad_2D_con_tapa_móvil/{0,constant,system}
touch Cavidad_2D_con_tapa_móvil/0/U Cavidad_2D_con_tapa_móvil/0/p
touch Cavidad_2D_con_tapa_móvil/constant/transportProperties
touch Cavidad_2D_con_tapa_móvil/system/blockMeshDict Cavidad_2D_con_tapa_móvil/system/controlDict Cavidad_2D_con_tapa_móvil/system/decomposeParDict Cavidad_2D_con_tapa_móvil/system/fvSchemes Cavidad_2D_con_tapa_móvil/system/fvSolution Cavidad_2D_con_tapa_móvil/system/sampleDict
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
    movingWall
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }

    fixedWalls
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }

    frontAndBack
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
    movingWall
    {
        type            zeroGradient;
    }

    fixedWalls
    {
        type            zeroGradient;
    }

    frontAndBack
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

nu              nu [ 0 2 -1 0 0 0 0 ] 0.01;	//Re 100
//nu              nu [ 0 2 -1 0 0 0 0 ] 0.001;	//Re 1000

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

convertToMeters 1;	//This is an scaling operation. Done at the end.

xmin 0;
xmax 1;
ymin 0;
ymax 1;
zmin 0;
zmax 1;

xcells 20;
ycells 20;
zcells 1;

//deltax 0.00775;	//As in Ghia et al 129 x 129 cells
//deltax 0.05;
//lx #calc "$xmax-$xmin";
//xcells #calc "round($lx/$deltax)";

//ycells $xcells;

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

/*
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 1 0.1)
    (0 1 0.1)
*/
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ($xcells $ycells $zcells) simpleGrading (1 1 1)
);

edges
(
    //arc 0 1 (0.5 -0.1 0)
    //arc 4 5 (0.5 -0.1 1)
);

boundary
(
    movingWall
    {
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }
    fixedWalls
    {
        type wall;
        faces
        (
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
        );
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);

mergePatchPairs
(
    //(interface1 interface2)
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

endTime         50;

deltaT          0.01;

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
/*
residuals
{
	functionObjectLibs ("libutilityFunctionObjects.so");

	type residuals;

	enabled true; 

	writeControl timeStep;
	writeInterval 1;

	fields (p U);
}
*/
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
    default         backward;
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
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0;

/*
        solver           GAMG;
        tolerance        1e-6;
        relTol           0.0;
        smoother         GaussSeidel;
        nPreSweeps       0;
        nPostSweeps      2;
        cacheAgglomeration on;
        agglomerator     faceAreaPair;
        nCellsInCoarsestLevel 100;
        mergeLevels      1;
*/
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
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
);

sets
(

    l1
    {
        type            midPointAndFace;
        //type            midPoint;
        //type            face;

        //type            uniform;
	//nPoints 	  100;

        axis            x;
        start           ( -1  0.5 0);
        end             ( 2  0.5 0);
    }

    l2
    {
        type            midPointAndFace;
        //type            midPoint;
        //type            face;

        axis            y;
        start           (0.5 -1 0);
        end             (0.5 2 0);
    }

);

// *********************************************************************** //
```

Fin de la transcripción de los archivos del paquete.
