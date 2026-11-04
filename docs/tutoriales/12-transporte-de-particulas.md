# Tutorial 12 · Goldschmidt · nube de partículas

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Caso lagrangiano con partículas sólidas en un fluido portador. No equivale a una esfera rígida resuelta con malla overset ni a un problema VOF.


### Procedencia y compatibilidad

• Fuente original: OpenFOAM Foundation 8.

• Solver declarado DPMFoam; su familia está presente en v2406, pero los modelos de nube y campos con sufijo .air requieren migración específica.

• El archivo 0/U.air no equivale al campo 0/U; es necesario verificar los nombres que realmente solicita el solver.

• No se afirma compatibilidad ejecutable. Es un caso de referencia para migración antes de producir animaciones.


### Versión rápida: parámetros de animación

Configuración inicial propuesta: duración física 0.5 s, intervalo de escritura 0.005 s. Estos valores son de prototipado; verificar el CFL y el fenómeno antes de utilizarlos como resultados científicos.

Se conserva a continuación el texto íntegro de los diccionarios suministrados, para que pueda compararse la configuración original con los cambios necesarios. Los bloques originales no se presentan como migrados ni validados en v2406.


### Estructura y creación de archivos

Desde el directorio de trabajo:


```bash
mkdir -p Goldschmidt_·_nube_de_partículas/{0,constant,system}
touch Goldschmidt_·_nube_de_partículas/0/U.air Goldschmidt_·_nube_de_partículas/0/p
touch Goldschmidt_·_nube_de_partículas/constant/g Goldschmidt_·_nube_de_partículas/constant/kinematicCloudProperties Goldschmidt_·_nube_de_partículas/constant/momentumTransport.air Goldschmidt_·_nube_de_partículas/constant/transportProperties
touch Goldschmidt_·_nube_de_partículas/system/blockMeshDict Goldschmidt_·_nube_de_partículas/system/controlDict Goldschmidt_·_nube_de_partículas/system/decomposeParDict Goldschmidt_·_nube_de_partículas/system/fvSchemes Goldschmidt_·_nube_de_partículas/system/fvSolution Goldschmidt_·_nube_de_partículas/system/mapFieldsDict
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

application DPMFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime 0.5;
deltaT 0.0005;
adjustTimeStep yes;
maxCo 0.5;
maxDeltaT 0.005;
writeControl adjustableRunTime;
writeInterval 0.005;
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
DPMFoam 2>&1 | tee log.DPMFoam
touch caso.foam
```

En ParaView: abrir caso.foam, mostrar Surface with Edges para revisar la malla, seleccionar el campo principal y usar Snap To TimeSteps. Mantener fija la escala de colores al exportar una animación.


### Archivos originales completos del paquete


#### 0/U.air


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      binary;
    class       volVectorField;
    location    "0";
    object      U.air;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    walls
    {
        type            noSlip;
    }

    top
    {
        type            pressureInletOutletVelocity;
        phi             phi.air;
        inletValue      uniform (0 0 0);
        value           uniform (0 0 0);
    }

    bottom
    {
        type            interstitialInletVelocity;
        inletVelocity   uniform (0 0 1.875);
        value           uniform (0 0 1.875);
        phi             phi.air;
        alpha           alpha.air;
    }

    frontAndBack
    {
        type            symmetry;
    }
}


// ************************************************************************* //
```


#### 0/p


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
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
    walls
    {
        type            fixedFluxPressure;
        phi             phi.air;
        value           $internalField;
    }

    bottom
    {
        type            fixedFluxPressure;
        phi             phi.air;
        value           $internalField;
    }

    top
    {
        type            fixedValue;
        phi             phi.air;
        value           $internalField;
    }

    frontAndBack
    {
        type            symmetry;
    }
}

// ************************************************************************* //
```


#### constant/g


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       uniformDimensionedVectorField;
    location    "constant";
    object      g;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -2 0 0 0 0];
value           (0 0 -9.81);


// ************************************************************************* //
```


#### constant/kinematicCloudProperties


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      particleProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solution
{
    active          true;
    coupled         true;
    transient       yes;
    cellValueSourceCorrection off;

    interpolationSchemes
    {
        rho.air         cell;
        U.air           cellPoint;
        mu.air          cell;
        alpha.air       cell;
    }

    integrationSchemes
    {
        U               Euler;
    }

    sourceTerms
    {
        schemes
        {
            U semiImplicit 1;
        }
    }
}

constantProperties
{
    parcelTypeId 1;

    rhoMin          1e-15;
    minParcelMass   1e-15;

    rho0            2526;
    youngsModulus   1e8;
    poissonsRatio   0.35;

    constantVolume  false;

    alphaMax        0.99;
}

subModels
{
    particleForces
    {
        ErgunWenYuDrag
        {
            alphac alpha.air;
        }
        gravity;
    }

    injectionModels
    {
        model1
        {
            type            manualInjection;
            massTotal       0;
            parcelBasisType fixed;
            nParticle       1;
            SOI             0;
            positionsFile   "kinematicCloudPositions";
            U0              (0 0 0);
            sizeDistribution
            {
                type        fixedValue;
                fixedValueDistribution
                {
                    value   0.0025;
                }
            }
        }
    }

    dispersionModel none;

    patchInteractionModel localInteraction;

    localInteractionCoeffs
    {
        patches
        (
            top
            {
                type rebound;
                e    0.97;
                mu   0.09;
            }
            bottom
            {
                type rebound;
                e    0.97;
                mu   0.09;
            }
            walls
            {
                type rebound;
                e    0.97;
                mu   0.09;
            }
            frontAndBack
            {
                type rebound;
                e    0.97;
                mu   0.09;
            }
        );
    }

    StandardWallInteractionCoeffs
    {
        type rebound;
        e    0.97;
        mu   0.09;
    }

    heatTransferModel none;

    surfaceFilmModel none;

    collisionModel pairCollision;

    pairCollisionCoeffs
    {
        maxInteractionDistance  0.0025;

        writeReferredParticleCloud no;

        pairModel pairSpringSliderDashpot;

        pairSpringSliderDashpotCoeffs
        {
            useEquivalentSize   no;
            alpha               0.02;
            b                   1.5;
            mu                  0.10;
            cohesionEnergyDensity 0;
            collisionResolutionSteps 12;
        };

        wallModel wallSpringSliderDashpot;

        wallSpringSliderDashpotCoeffs
        {
            useEquivalentSize no;
            collisionResolutionSteps 12;
            youngsModulus   1e8;
            poissonsRatio   0.23;
            alpha           0.01;
            b               1.5;
            mu              0.09;
            cohesionEnergyDensity 0;
        };

        U     U.air;
    }

    stochasticCollisionModel none;

    radiation off;
}


cloudFunctions
{}


// ************************************************************************* //
```


#### constant/momentumTransport.air


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties.air;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType  laminar;

// ************************************************************************* //
```


#### constant/transportProperties


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

continuousPhaseName air;

rho.air         1.2;

transportModel  Newtonian;
nu              1e-05;

// ************************************************************************* //
```


#### system/blockMeshDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 0.001;

vertices
(
    (-7.5 -75   0)
    ( 7.5 -75   0)
    ( 7.5  75   0)
    (-7.5  75   0)
    (-7.5 -75 450)
    ( 7.5 -75 450)
    ( 7.5  75 450)
    (-7.5  75 450)
);

blocks
(
    // hex (0 1 2 3 4 5 6 7) (1 15 45) simpleGrading (1 1 1)
    hex (0 1 2 3 4 5 6 7) (2 30 90) simpleGrading (1 1 1)
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
            (4 5 6 7)
        );
    }

    bottom
    {
        type wall;
        faces
        (
            (0 1 2 3)
        );
    }

    walls
    {
        type wall;
        faces
        (
            (0 1 5 4)
            (2 3 7 6)
        );
    }

    frontAndBack
    {
        type symmetry;
        faces
        (
            (1 2 6 5)
            (3 0 4 7)
        );
    }
);

// ************************************************************************* //
```


#### system/controlDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     DPMFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         5;

deltaT          2e-5;

writeControl    runTime;

writeInterval   0.01;

purgeWrite      0;

writeFormat     binary;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable yes;

// ************************************************************************* //
```


#### system/decomposeParDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains 6;

method          simple;

simpleCoeffs
{
    n               (1 6 1);
    delta           0.001;
}

// ************************************************************************* //
```


#### system/fvSchemes


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
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
    default Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;

    div(alphaPhi.air,U.air)    Gauss linearUpwindV unlimited;
    div(((alpha.air*nuEff.air)*dev2(T(grad(U.air))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}


// ************************************************************************* //
```


#### system/fvSolution


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    "(p|kinematicCloud:theta)"
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    "(p|kinematicCloud:theta)Final"
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0;
        smoother        GaussSeidel;
    }

    "(U.air|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    "(U.air|k|omega)Final"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0;
    }
}

PIMPLE
{
    nOuterCorrectors 1;
    nCorrectors     2;
    momentumPredictor yes;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

relaxationFactors
{
}


// ************************************************************************* //
```


#### system/mapFieldsDict


```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      mapFieldsDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// List of pairs of source/target patches for mapping
patchMap
(
);

// List of target patches cutting the source domain (these need to be
// handled specially e.g. interpolated from internal values)
cuttingPatches
(
);

// ************************************************************************* //
```

Fin de la transcripción de los archivos del paquete.
