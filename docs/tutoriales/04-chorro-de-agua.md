# OpenFOAM v2406 — Tutorial 04

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.


### Chorro de agua en caída libre, impacto contra un piso y formación de un charco

Objetivo: simular un chorro horizontal de agua que entra en un recinto inicialmente lleno de aire, cae por gravedad, impacta sobre el piso y se extiende formando un charco.

Utilizaremos interFoam, el método VOF (Volume of Fluid) y una simulación transitoria de dos fases inmiscibles. Este es el mismo enfoque físico que emplea el tutorial oficial damBreak de OpenFOAM.


#### 1. Geometría y parámetros

Esquema conceptual. La trayectoria y el charco son ilustrativos, no resultados calculados.

El dominio tendrá un piso inferior, una pared izquierda con una pequeña entrada de agua y superficies abiertas a la atmósfera en la parte superior y derecha.

El agua que alcance el borde derecho podrá salir del dominio. Esto evita que el líquido se acumule indefinidamente en un recipiente cerrado.

Importante: la simulación será estrictamente 2D. Lo que llamamos chorro es, matemáticamente, una lámina de agua con espesor computacional constante. Puede reproducir la trayectoria, el impacto y la extensión del líquido, pero no la fragmentación tridimensional real de un chorro cilíndrico.


### 2. Crear todos los archivos antes de ejecutar

Desde el directorio donde guardás tus simulaciones, ejecutar:


```bash
mkdir -p chorroAgua2D/0 chorroAgua2D/constant chorroAgua2D/system
touch chorroAgua2D/0/U chorroAgua2D/0/p_rgh chorroAgua2D/0/alpha.water
touch chorroAgua2D/constant/g chorroAgua2D/constant/transportProperties chorroAgua2D/constant/turbulenceProperties
```

touch chorroAgua2D/system/blockMeshDict chorroAgua2D/system/controlDict chorroAgua2D/system/fvSchemes chorroAgua2D/system/fvSolution


```cpp
cd chorroAgua2D
Son diez archivos de configuración.
```

La estructura será:


```cpp
chorroAgua2D/
```

├── 0/

│   ├── U

│   ├── p_rgh

│   └── alpha.water

├── constant/

│   ├── g

│   ├── transportProperties

│   └── turbulenceProperties

└── system/

├── blockMeshDict

├── controlDict

├── fvSchemes

└── fvSolution

No necesitamos setFieldsDict en este caso porque el dominio inicialmente contiene solamente aire. El agua ingresará progresivamente a través de la condición de entrada.


### 3. Construir la malla: system/blockMeshDict

Para representar una entrada pequeña en la pared izquierda, dividiremos el dominio en tres bloques horizontales.

División en tres bloques para que la entrada de agua sea un patch independiente del resto de la pared izquierda.

El bloque inferior ocupa y=0 a y=0.145, el central de y=0.145 a y=0.155 y el superior hasta y=0.20.

Usaremos una malla uniforme de 2.5 mm de resolución en X e Y, con una sola celda en Z.

Así tendremos:

Esta resolución sirve para el primer experimento, pero solo deja cuatro celdas a través del espesor del chorro. Para estudiar salpicaduras o tensión superficial con precisión habrá que refinarla.


#### Contenido completo


```bash
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

scale 1;

vertices
(
    // Plano frontal z=0

    (0    0      0)      // 0
    (0.30 0      0)      // 1
    (0    0.145  0)      // 2
    (0.30 0.145  0)      // 3
    (0    0.155  0)      // 4
    (0.30 0.155  0)      // 5
    (0    0.20   0)      // 6
    (0.30 0.20   0)      // 7

    // Plano posterior z=0.001

    (0    0      0.001)  // 8
    (0.30 0      0.001)  // 9
    (0    0.145  0.001)  // 10
    (0.30 0.145  0.001)  // 11
    (0    0.155  0.001)  // 12
    (0.30 0.155  0.001)  // 13
    (0    0.20   0.001)  // 14
    (0.30 0.20   0.001)  // 15
);

blocks
(
    // Bloque inferior
    hex (0 1 3 2 8 9 11 10)
        (120 58 1)
        simpleGrading (1 1 1)

    // Bloque central: altura de la entrada
    hex (2 3 5 4 10 11 13 12)
        (120 4 1)
        simpleGrading (1 1 1)

    // Bloque superior
    hex (4 5 7 6 12 13 15 14)
        (120 18 1)
        simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    waterInlet
    {
        type patch;

        faces
        (
            (2 10 12 4)
        );
    }

    leftWall
    {
        type wall;

        faces
        (
            (0 8 10 2)
            (4 12 14 6)
        );
    }

    floor
    {
        type wall;

        faces
        (
            (0 1 9 8)
        );
    }

    atmosphere
    {
        type patch;

        faces
        (
            (6 14 15 7)

            (1 3 11 9)
            (3 5 13 11)
            (5 7 15 13)
        );
    }

    frontAndBack
    {
        type empty;

        faces
        (
            (0 2 3 1)
            (2 4 5 3)
            (4 6 7 5)

            (8 9 11 10)
            (10 11 13 12)
            (12 13 15 14)
        );
    }
);

mergePatchPairs
(
);
```

A diferencia de los casos anteriores, atmosphere agrupa la cara superior y las tres caras de la derecha. Ambas regiones permitirán la salida del fluido y, donde corresponda, la entrada de aire.


### 4. Definir las fases: constant/transportProperties

Ahora OpenFOAM necesita las propiedades de dos fluidos.

El agua y el aire tienen densidades y viscosidades distintas, y existe una tensión interfacial entre ambos.


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

phases (water air);

water
{
    transportModel Newtonian;

    nu  [0 2 -1 0 0 0 0] 1e-6;

    rho [1 -3 0 0 0 0 0] 1000;
}

air
{
    transportModel Newtonian;

    nu  [0 2 -1 0 0 0 0] 1.5e-5;

    rho [1 -3 0 0 0 0 0] 1.2;
}

sigma [1 0 -2 0 0 0 0] 0.072;
phases (water air) indica los nombres de las dos fases.
sigma representa la tensión superficial entre el agua y el aire, expresada en N/m.
Los parámetros corresponden aproximadamente a agua y aire a temperatura ambiente.
```


### 5. Gravedad: constant/g


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       uniformDimensionedVectorField;
    object      g;
}

dimensions [0 1 -2 0 0 0 0];

value (0 -9.81 0);
```

La aceleración gravitatoria apunta hacia abajo, en dirección Y negativa.

Si cambiaras el vector a (0 0 0), el líquido dejaría de experimentar aceleración gravitatoria. En ese caso, la trayectoria del chorro sería muy diferente.


### 6. Modelo de turbulencia: constant/turbulenceProperties

Para este primer ejemplo utilizaremos un modelo laminar.


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType laminar;
Esto permite estudiar la evolución del líquido sin incorporar todavía un modelo RANS o LES.
```

Conviene aclarar que laminar no impone necesariamente un campo estacionario: el solver puede reproducir estructuras transitorias que la malla y las ecuaciones resueltas permitan representar.


### 7. Fracción de agua: 0/alpha.water

Este es el archivo nuevo más importante del tutorial.

La variable alpha.water representa la fracción volumétrica de agua en cada celda.

Inicialmente todo el dominio contiene aire, por eso definimos:

Sin embargo, en waterInlet imponemos alpha.water=1.


#### Contenido completo


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      alpha.water;
}

dimensions [0 0 0 0 0 0 0];

internalField uniform 0;

boundaryField
{
    waterInlet
    {
        type fixedValue;
        value uniform 1;
    }

    leftWall
    {
        type zeroGradient;
    }

    floor
    {
        type zeroGradient;
    }

    atmosphere
    {
        type inletOutlet;

        inletValue uniform 0;
        value uniform 0;
    }

    frontAndBack
    {
        type empty;
    }
}
```

En atmosphere, inletOutlet permite que entre aire cuando el flujo local apunta hacia el interior. Cuando el flujo apunta hacia afuera, la fracción volumétrica se extrapola desde el interior.

Así el dominio puede intercambiar aire y agua con el exterior.


### 8. Velocidad: 0/U

El dominio comienza en reposo, con velocidad uniforme nula.

El agua entra horizontalmente a 1 m/s.


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

internalField uniform (0 0 0);

boundaryField
{
    waterInlet
    {
        type fixedValue;

        value uniform (1 0 0);
    }

    leftWall
    {
        type noSlip;
    }

    floor
    {
        type noSlip;
    }

    atmosphere
    {
        type pressureInletOutletVelocity;

        value uniform (0 0 0);
    }

    frontAndBack
    {
        type empty;
    }
}
```

La condición pressureInletOutletVelocity está diseñada para fronteras abiertas cuyo comportamiento cambia según la dirección local del flujo. Es compatible con la familia OpenFOAM.com que estás utilizando.

Las paredes tienen noSlip. Por eso, al impactar el chorro contra el piso, el líquido debe desacelerarse y redistribuirse lateralmente.


### 9. Presión: 0/p_rgh


```cpp
interFoam utiliza una variable de presión diferente de la empleada en simpleFoam.
```

Se define:

$$ p_{rgh}=p-\rho(\mathbf g\cdot\mathbf x) $$

Esta transformación facilita el tratamiento de fuerzas hidrostáticas.


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p_rgh;
}

dimensions [1 -1 -2 0 0 0 0];

internalField uniform 0;

boundaryField
{
    waterInlet
    {
        type fixedFluxPressure;
        value uniform 0;
    }

    leftWall
    {
        type fixedFluxPressure;
        value uniform 0;
    }

    floor
    {
        type fixedFluxPressure;
        value uniform 0;
    }

    atmosphere
    {
        type prghTotalPressure;

        p0 uniform 0;
        value uniform 0;
    }

    frontAndBack
    {
        type empty;
    }
}
```

En este caso, la presión tiene dimensiones de pascales.

fixedFluxPressure ajusta el gradiente de presión según el flujo impuesto y las fuerzas volumétricas.

prghTotalPressure establece una condición de presión total en la frontera abierta.

Tomamos la presión atmosférica como referencia manométrica cero.


### 10. Discretización temporal y espacial: system/fvSchemes

Usamos integración temporal de Euler y esquemas de transporte para velocidad y fracción volumétrica.


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
    default Euler;
}

gradSchemes
{
    default Gauss linear;
}

divSchemes
{
    default none;

    div(rhoPhi,U) Gauss linearUpwind grad(U);

    div(phi,alpha) Gauss vanLeer;

    div(phirb,alpha) Gauss interfaceCompression;

    div(((rho*nuEff)*dev2(T(grad(U)))))
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

fluxRequired
{
    default no;

    p_rgh;
    pcorr;
    alpha.water;
}

wallDist
{
    method meshWave;
}
Dos esquemas merecen atención:
div(phi,alpha) Gauss vanLeer transporta la fracción volumétrica de agua.
div(phirb,alpha) Gauss interfaceCompression ayuda a mantener una interfaz relativamente definida entre ambas fases.
Estos términos forman parte del esquema VOF que utiliza interFoam.
```


### 11. Solución numérica: system/fvSolution


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
    "alpha.water.*"
    {
        nAlphaCorr 2;
        nAlphaSubCycles 2;

        cAlpha 1;

        MULESCorr yes;
        nLimiterIter 3;

        solver smoothSolver;
        smoother symGaussSeidel;

        tolerance 1e-8;
        relTol 0;
    }

    "pcorr.*"
    {
        solver PCG;
        preconditioner DIC;

        tolerance 1e-8;
        relTol 0;
    }

    p_rgh
    {
        solver GAMG;
        smoother GaussSeidel;

        tolerance 1e-8;
        relTol 0.05;
    }

    p_rghFinal
    {
        $p_rgh;
        relTol 0;
    }

    U
    {
        solver smoothSolver;
        smoother symGaussSeidel;

        tolerance 1e-7;
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
    momentumPredictor no;

    nOuterCorrectors 1;
    nCorrectors 3;

    nNonOrthogonalCorrectors 0;
}
A diferencia de los casos monofásicos, aparece un bloque para resolver alpha.water.
nAlphaSubCycles 2 permite subdividir el avance de la fracción de fase en pasos internos.
cAlpha 1 establece la intensidad de compresión numérica de la interfaz.
```

La estructura de los controles de fase y PIMPLE sigue la organización de los tutoriales de interFoam.


### 12. Tiempo de simulación: system/controlDict

Vamos a simular dos segundos físicos, guardando un estado cada 0,02 segundos.

Eso permite obtener aproximadamente 100 cuadros para la animación.


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application interFoam;

startFrom startTime;

startTime 0;

stopAt endTime;

endTime 2;

deltaT 0.0001;

adjustTimeStep yes;

maxCo 0.3;
maxAlphaCo 0.3;

maxDeltaT 0.001;

writeControl adjustableRunTime;

writeInterval 0.02;

purgeWrite 0;

writeFormat binary;

writePrecision 8;

writeCompression off;

timeFormat general;

timePrecision 6;

runTimeModifiable true;


FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application interFoam;

startFrom startTime;

startTime 0;

stopAt endTime;

endTime 2;

deltaT 0.0001;

adjustTimeStep yes;

maxCo 0.3;
maxAlphaCo 0.3;

maxDeltaT 0.001;

writeControl adjustableRunTime;

writeInterval 0.02;

purgeWrite 0;

writeFormat binary;

writePrecision 8;

writeCompression off;

timeFormat general;

timePrecision 6;

runTimeModifiable true;
adjustTimeStep yes permite adaptar el paso temporal según el número de Courant.
maxCo 0.3 y maxAlphaCo 0.3 son límites conservadores para comenzar.
```

El paso temporal inicial es  s, aunque el solver puede reducirlo si las condiciones numéricas lo exigen.

La velocidad del chorro es suficientemente elevada como para que el avance temporal y el tamaño de las celdas deban vigilarse especialmente. La resolución espacial también condicionará cuánto detalle de la interfaz puede observarse.


### 13. Ejecutar la simulación

Ahora que todos los archivos están completos, ejecutamos las herramientas en orden.


#### Paso 1. Comprobar la versión


```cpp
foamVersion
which interFoam
```

La versión debe ser 2406 y el comando interFoam debe existir en el entorno del contenedor.


#### Paso 2. Generar la malla


```bash
blockMesh 2>&1 | tee log.blockMesh
Esperamos 9600 celdas y cinco patches:


waterInlet
leftWall
floor
atmosphere
frontAndBack
```


#### Paso 3. Verificar la geometría


```cpp
checkMesh -allGeometry -allTopology 2>&1 | tee log.checkMesh
```

El resultado debería terminar con:


```cpp
Mesh OK.
```

Si aparecen errores de topología, caras sin asignar o volúmenes negativos, hay que resolverlos antes de ejecutar el solver.


#### Paso 4. Ejecutar interFoam


```cpp
interFoam 2>&1 | tee log.interFoam
```

Durante la ejecución deberían aparecer las iteraciones temporales y valores relacionados con el transporte de la fracción volumétrica.

Por ejemplo, se informarán estadísticas de alpha.water, los números de Courant y los residuos de presión y velocidad.

Podés inspeccionarlos con:


```cpp
grep -E "Time =|Courant Number|Phase-1 volume fraction" log.interFoam | tail -n 40
```

Los valores de alpha.water deberían mantenerse próximos al intervalo [0,1]. Pequeños sobrepasamientos numéricos pueden aparecer, pero valores muy alejados de ese intervalo indican un problema.

Compatibilidad: el caso se ha planteado para la rama OpenFOAM.com v2406, contrastando la estructura con los tutoriales y documentación de interFoam. No lo he ejecutado dentro de tu Docker, por lo que su funcionamiento exacto todavía requiere la prueba de ejecución. En particular, si v2406 solicita un esquema de discretización o una entrada adicional, el mensaje FOAM FATAL IO ERROR permitirá identificarla.


### 14. Animación en ParaView

Desde el directorio del caso:


```cpp
touch chorroAgua2D.foam
```

Abrir chorroAgua2D.foam en ParaView.


#### A. Visualizar el agua

Seleccionar alpha.water como variable de color.

Podés utilizar un mapa de colores donde el agua sea azul y el aire aparezca blanco.

Para resaltar únicamente la interfaz:

Aplicar el filtro Contour.

Seleccionar alpha.water.

Establecer el valor de isosuperficie en 0.5.

Pulsar Apply.

En un dominio 2D de una sola celda de espesor, el filtro puede generar una superficie estrecha que se observa mejor desde un ángulo oblicuo. Para ver la distribución completa del agua, también es útil representar directamente alpha.water sobre el plano XY.


#### B. Reproducir la animación

En la barra temporal de ParaView, pulsar Play.

La secuencia debería mostrar cómo:

El agua comienza a ingresar en el dominio.

Se forma un chorro que avanza horizontalmente.

La gravedad curva progresivamente su trayectoria.

El chorro impacta contra el piso.

El agua se extiende lateralmente y comienza a acumularse.

El charco crece mientras continúa la entrada de líquido.

Los resultados concretos dependerán de la solución numérica, especialmente cerca de la interfaz agua-aire y del punto de impacto.


#### C. Exportar un video

En ParaView:


```cpp
File → Save Animation
```

Seleccionar el formato .avi o una secuencia de imágenes .png, según los formatos disponibles en la instalación.

Una secuencia PNG es particularmente útil porque permite posteriormente generar un MP4 con FFmpeg.

Por ejemplo:


```cpp
ffmpeg -framerate 30 \
  -i frame.%04d.png \
  -c:v libx264 \
  -pix_fmt yuv420p \
  animacion.mp4
```

El patrón frame.%04d.png debe coincidir con los nombres que genere ParaView. El comando también requiere que FFmpeg tenga disponible el codificador libx264.


### 15. Qué observar físicamente


#### Trayectoria del chorro

Antes de impactar, si despreciamos la resistencia del aire y consideramos una velocidad horizontal inicial de 1 m/s:

Desde una altura de 0.15 m, el tiempo ideal de caída es aproximadamente:

La distancia horizontal recorrida sería aproximadamente 0.175 m.

Por lo tanto, el chorro debería impactar cerca de x=0.175 m, aunque la interacción aire-agua, la viscosidad, la tensión superficial y el desarrollo del flujo pueden modificar la trayectoria.


#### Formación del charco

El chorro transporta continuamente masa hacia el interior.

El caudal volumétrico impuesto es:

Es decir, 10 mL/s para la lámina tridimensional representada por la malla.

La acumulación de agua depende de la diferencia entre el caudal de entrada y el de salida. Inicialmente esperamos acumulación sobre el piso. Cuando el líquido alcance la frontera derecha, una parte podrá abandonar el dominio.


#### ¿Aparecerán gotas y salpicaduras?

Es posible que aparezcan deformaciones importantes de la interfaz, pequeñas lenguas de líquido y estructuras que visualmente recuerden salpicaduras.

Sin embargo, hay dos limitaciones:

La geometría 2D no puede representar correctamente la ruptura tridimensional de un chorro cilíndrico.

La malla inicial, con cuatro celdas a través del chorro, es demasiado gruesa para resolver fielmente gotas pequeñas y fragmentación de la interfaz.

Por eso, cualquier gota diminuta o estructura de una o dos celdas debe interpretarse con cautela.


### 16. Experimentos posteriores

Una vez comprobado que la simulación funciona, podemos variar parámetros sin modificar la geometría.

Para refinar la malla, en blockMeshDict reemplazá las divisiones de los tres bloques:


```cpp
// Bloque inferior
(240 116 1)

// Bloque central
(240 8 1)

// Bloque superior
(240 36 1)
```

La nueva malla tendrá 38.400 celdas. Esta modificación aumenta el costo de cálculo, pero representa mejor el espesor del chorro y las regiones próximas al impacto.

También conviene reducir los límites de maxCo y maxAlphaCo si se observan inestabilidades.


#### Referencias

La configuración está basada en el método VOF y la estructura de casos multifásicos de OpenFOAM.com:

OpenFOAM — Breaking of a dam

OpenFOAM.es — Dam Break con interFoam

Referencia de interFoam

Este cuarto tutorial introduce tres elementos que no teníamos en los casos anteriores: la interfaz móvil agua-aire, la gravedad como fuerza volumétrica y la acumulación de líquido sobre una superficie sólida. La evolución temporal es ahora parte esencial de la solución, no solamente un proceso de convergencia numérica.

PROTOCOLO RÁPIDO — Prototipo de movimiento: ejecutar primero el caso sphereDrop oficial sin modificar los diccionarios. Registrar la trayectoria y detener el cálculo antes del contacto con el fondo. El ejemplo depende de los tutoriales instalados y no proporciona aún un caso propio completo.
