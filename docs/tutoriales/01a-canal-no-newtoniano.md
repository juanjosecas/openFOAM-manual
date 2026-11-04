# Tutorial 01 — Flujo no newtoniano en un canal 2D

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Nivel inicial

CFD 2D

Fluido pseudoplástico


```cpp
simpleFoam
```

Vamos a construir una simulación completa desde cero, sin partir de un tutorial existente. El objetivo es entender cómo se representa la geometría, cómo se construye la malla, cómo se describe un fluido y cómo OpenFOAM resuelve sus ecuaciones.

Usaremos un líquido cuya viscosidad disminuye cuando aumenta la tasa de deformación (shear-thinning). Es un comportamiento característico de determinadas soluciones poliméricas, geles y suspensiones.

Hay una distinción importante: un fluido newtoniano también tiene viscosidad. Lo que lo caracteriza es que, a temperatura y presión dadas, su viscosidad no depende de la tasa de corte. En este ejercicio estudiaremos precisamente esa dependencia.


### 1. Qué vamos a simular

Esquema conceptual del dominio. Las flechas representan un perfil de velocidad, no resultados calculados.

El dominio será un canal recto de paredes paralelas. Técnicamente, al trabajar en 2D representamos un canal plano, no una tubería circular. Una tubería cilíndrica puede estudiarse después mediante una geometría axisimétrica o tridimensional.

La tercera dimensión tendrá una sola celda, y sus caras tendrán una condición empty. De este modo, OpenFOAM usa una malla hexaédrica, pero resuelve un problema estrictamente bidimensional.


#### Qué queremos observar

Cómo se desarrolla el perfil de velocidad desde la entrada.

Cómo disminuye la presión a lo largo del conducto.

Cómo cambia la viscosidad según la posición dentro del canal.

Qué diferencias produce el índice reológico n.


### 2. La física del problema

Usaremos las ecuaciones de continuidad y conservación de cantidad de movimiento para un fluido incompresible e isotérmico:

$$ \nabla\cdot\mathbf{U}=0 $$

$$ \rho(\mathbf U\cdot\nabla)\mathbf U =-\nabla p_{\mathrm{fís}}+\nabla\cdot\boldsymbol{\tau} $$

Para un fluido newtoniano, la viscosidad dinámica  es constante respecto de la tasa de corte. En un fluido de ley de potencia:

$$ \tau = k \cdot \dot{\gamma}^n $$

donde $\dot\gamma=\sqrt{2\mathbf D:\mathbf D}$, con $\mathbf D=(\nabla\mathbf U+\nabla\mathbf U^T)/2$.

k: índice de consistencia.

n: índice de comportamiento.

γ̇: tasa de corte, en s⁻¹.

μ_app: viscosidad dinámica aparente.


#### Cómo afecta n a la viscosidad

Índice reológico n

0.50

0.3 — pseudoplástico | 1.0 — newtoniano | 1.5 — dilatante

Pseudoplástico: la viscosidad disminuye al aumentar la tasa de corte.

En nuestro caso, n = 0,5: el fluido es pseudoplástico y su viscosidad aparente disminuye con la tasa de corte.

En este modelo OpenFOAM utiliza viscosidad cinemática ν = μ/ρ, expresada en m²/s. Usaremos un coeficiente de referencia  a una tasa de corte de referencia de 1 s⁻¹, con límites numéricos para evitar valores extremos de viscosidad.

Para este primer ejercicio elegimos simpleFoam, que utiliza el algoritmo SIMPLE para resolver flujo incompresible estacionario. La rama OpenFOAM.com incluye modelos de viscosidad no newtoniana en su marco de flujo laminar, incluyendo powerLaw, BirdCarreau y HerschelBulkley.


### 3. Estructura del directorio

Dentro de tu contenedor openfoam2406-run vamos a preparar esta estructura:


```cpp
canalPowerLaw2D/
```

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

Son ocho archivos. La geometría se define dentro de blockMeshDict; no hay que descargar modelos CAD.

Desde la terminal donde tengas acceso a los comandos de OpenFOAM, ejecutá:


```bash
mkdir -p canalPowerLaw2D/0 canalPowerLaw2D/constant canalPowerLaw2D/system
touch canalPowerLaw2D/0/U canalPowerLaw2D/0/p
touch canalPowerLaw2D/constant/transportProperties canalPowerLaw2D/constant/turbulenceProperties
```

touch canalPowerLaw2D/system/blockMeshDict canalPowerLaw2D/system/controlDict canalPowerLaw2D/system/fvSchemes canalPowerLaw2D/system/fvSolution


```cpp
touch canalPowerLaw2D/0/U canalPowerLaw2D/0/p
```

touch canalPowerLaw2D/system/blockMeshDict canalPowerLaw2D/system/controlDict canalPowerLaw2D/system/fvSchemes canalPowerLaw2D/system/fvSolution

Esto supone que openfoam2406-run es el nombre de un contenedor en ejecución, no solamente de una imagen Docker. Si los casos están montados como volumen, conviene crearlos en ese volumen para conservarlos.


### 4. Construir el canal con blockMesh

El archivo system/blockMeshDict define la geometría y la discretización espacial.

OpenFOAM representa el volumen mediante vértices, bloques y superficies. Para este canal necesitamos un único hexaedro, subdividido en 8000 celdas.


#### 4.1. Definir los vértices

Numeración de los ocho vértices del bloque, con x longitudinal, y vertical y z como espesor.

Cada punto tiene tres coordenadas (x y z).

El bloque queda definido por:

Vértices 0–3: plano inferior en z=0.

Vértices 4–7: plano superior en z=0.001.

Caras en x=0 y x=0.2: entrada y salida.

Caras en y=0 y y=0.02: paredes.

La numeración importa porque determina la orientación del bloque y de sus caras.


#### 4.2. Archivo system/blockMeshDict


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
    (0      0      0)
    (0.20   0      0)
    (0.20   0.02   0)
    (0      0.02   0)

    (0      0      0.001)
    (0.20   0      0.001)
    (0.20   0.02   0.001)
    (0      0.02   0.001)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (200 40 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
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
            (1 2 6 5)
        );
    }

    lowerWall
    {
        type wall;
        faces
        (
            (0 1 5 4)
        );
    }

    upperWall
    {
        type wall;
        faces
        (
            (3 7 6 2)
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
);
```


#### Qué significa cada instrucción

vertices: posiciones de los ocho vértices. La escala está expresada directamente en metros.

hex (0 1 2 3 4 5 6 7): construye un bloque hexaédrico conectando esos vértices.

(200 40 1): subdivide el bloque en 200 celdas longitudinales, 40 verticales y una sola celda en profundidad.

Por lo tanto:

simpleGrading (1 1 1): las celdas se distribuyen uniformemente en todas las direcciones.

boundary: identifica las superficies físicas. Es fundamental entender que un patch agrupa caras de la malla que posteriormente recibirán condiciones de borde.

wall: identifica superficies sólidas. empty indica que no resolveremos variaciones en la dirección perpendicular al plano XY.

edges: está vacío porque todas las aristas son rectas.

mergePatchPairs: está vacío porque usamos un solo bloque y no hay interfaces que unir.


#### 4.3. Generar la malla

Ejecutar desde el directorio raíz del caso:


```bash
blockMesh
Después:

checkMesh
```

El resultado esperado es una malla de 8000 celdas, con cinco regiones de contorno y una verificación final satisfactoria.

blockMesh crea el directorio constant/polyMesh/, que contiene los archivos internos de malla. No necesitamos editarlos manualmente.


### 5. Definir el fluido

Ahora describimos el modelo reológico.


#### 5.1. Archivo constant/transportProperties


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

transportModel Newtonian;

nu [0 2 -1 0 0 0 0] 1e-4;
```

Puede parecer contradictorio que aparezca Newtonian. En este caso, transportProperties suministra una viscosidad cinemática de referencia y la dependencia no newtoniana se incorpora mediante el modelo generalizedNewtonian en turbulenceProperties.


```cpp
Es la organización introducida en la línea OpenFOAM.com para los modelos laminares generalizados.
```

La expresión:

incluye las dimensiones físicas de la variable.

OpenFOAM utiliza siete exponentes dimensionales:

Para la viscosidad cinemática:


```cpp
De ahí [0 2 -1 0 0 0 0].
```


#### 5.2. Archivo constant/turbulenceProperties


```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType laminar;

laminar
{
    model           generalizedNewtonian;
    viscosityModel  powerLaw;

    nuMin           1e-6;
    nuMax           1e-2;

    k               1e-4;
    n               0.5;
}
Esta configuración especifica:
El comportamiento efectivo será aproximadamente:
```

La función clip indica que el resultado se limita al intervalo especificado.

Esto evita la singularidad matemática que tendría una ley de potencia pseudoplástica ideal cuando la tasa de corte tiende a cero.

Los valores son ilustrativos, no parámetros experimentales de un polímero determinado. Para modelar un líquido real necesitaríamos una curva reométrica y el ajuste de sus parámetros.


### 6. Condiciones iniciales y de contorno

En el directorio 0/ se definen los campos que el solver necesita para empezar a calcular.

OpenFOAM trata la velocidad como un campo vectorial U y la presión como un campo escalar p.


#### 6.1. Archivo 0/U


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

internalField define el valor inicial de velocidad para las celdas interiores. La simulación comienza con una velocidad uniforme de 0.01 m/s en la dirección X.


```cpp
inlet fija esa velocidad durante el cálculo.
```

outlet utiliza zeroGradient, permitiendo que la velocidad de salida se determine a partir de la solución interior sin imponerle un valor fijo.


```cpp
noSlip establece velocidad nula en las paredes sólidas:
```

Este es el mecanismo por el cual aparece un gradiente de velocidad entre las paredes y el interior.


#### 6.2. Archivo 0/p


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

En los solvers incompresibles de esta familia, p es presión cinemática, con dimensiones m²/s², y no presión directamente expresada en pascales.

Si usamos una densidad de referencia constante de 1000 kg/m³, la diferencia de presión física se recupera mediante:

Por ejemplo, una diferencia de presión cinemática de 0.4 m²/s² corresponde a 400 Pa.

Al establecer p=0 en la salida fijamos una referencia de presión. El cálculo determinará la presión necesaria aguas arriba para sostener el flujo impuesto.


### 7. Configurar los métodos numéricos

Aquí entramos en la parte que suele resultar menos intuitiva para quienes venimos de otras áreas científicas.

OpenFOAM utiliza el método de volúmenes finitos. Divide el dominio en celdas y aproxima los balances físicos mediante flujos a través de las caras de cada celda.

Los siguientes archivos determinan cómo se resuelven matemáticamente esas ecuaciones.


#### 7.1. Archivo system/fvSchemes


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
Las instrucciones principales son:
steadyState: buscamos una solución estacionaria, no una evolución temporal.
Gauss linear: aproxima determinados gradientes mediante integración sobre las caras de las celdas e interpolación lineal.
```

upwind: esquema de primer orden para la convección de velocidad. Es robusto para comenzar, aunque introduce difusión numérica.

corrected: permite corregir determinados términos geométricos en mallas no ortogonales. En nuestra malla rectangular la corrección debería ser pequeña o nula.

El término div((nuEff*dev2(T(grad(U))))) forma parte de la discretización de los esfuerzos viscosos en esta familia de solvers.


#### 7.2. Archivo system/fvSolution


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
        solver          GAMG;
        tolerance       1e-8;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;
        relTol          0.1;
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
Aquí hay dos niveles de cálculo:
```

Primero, OpenFOAM debe resolver sistemas de ecuaciones algebraicas para las variables p y U. Para eso elegimos GAMG y smoothSolver.

Segundo, SIMPLE itera entre presión y velocidad para encontrar una solución consistente que satisfaga continuidad y cantidad de movimiento.

relaxationFactors controla cuánto se actualizan las variables entre iteraciones. Los factores menores que uno reducen el riesgo de inestabilidad.

residualControl establece condiciones para detener las iteraciones cuando los residuos alcanzan umbrales suficientemente bajos.

Un residuo pequeño por sí solo no demuestra que una simulación sea físicamente correcta. Más adelante comprobaremos conservación de masa, perfiles y sensibilidad a la malla.


#### 7.3. Archivo system/controlDict


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

endTime 1000;

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
application define el solver que usaremos.
```

endTime 1000 y deltaT 1 permiten un máximo de 1000 iteraciones. Como utilizamos steadyState, esos valores no representan una simulación física de 1000 segundos.


```cpp
writeInterval 100 guarda campos cada 100 iteraciones, además de los campos que pudieran escribirse al finalizar.
runTimeModifiable true permite que ciertos diccionarios sean releídos durante la ejecución.
```


### 8. Ejecutar la simulación

Ya tenemos configurados los ocho archivos necesarios.

Desde canalPowerLaw2D/, ejecutar en este orden:


```bash
# 1. Verificar la versión
foamVersion

# 2. Generar la malla
blockMesh > log.blockMesh 2>&1

# 3. Comprobar la malla
checkMesh > log.checkMesh 2>&1

# 4. Ejecutar el solver
simpleFoam > log.simpleFoam 2>&1

# 5. Inspeccionar las últimas iteraciones
tail -n 40 log.simpleFoam
```

Para observar el cálculo mientras se ejecuta, usar en cambio:


```cpp
simpleFoam 2>&1 | tee log.simpleFoam
```

En el log deberían aparecer iteraciones similares a:


```cpp
Time = 1

smoothSolver: Solving for Ux ...
GAMG: Solving for p ...

time step continuity errors ...
```

Los residuos reales dependen de la malla, las condiciones de contorno y los parámetros del solver. El caso está construido para v2406, pero no lo he ejecutado en tu imagen Docker, por lo que todavía no está verificado contra sus binarios exactos.

Si aparece un FOAM FATAL IO ERROR, las primeras verificaciones son foamVersion, el nombre exacto del archivo indicado y los modelos disponibles en esa instalación.


#### ¿Qué genera OpenFOAM?

Después de una ejecución que llegue a las iteraciones de escritura, la estructura se amplía:

canalPowerLaw2D/

├── 0/

├── 100/

│   ├── U

│   └── p

├── 200/

├── ...

├── constant/

│   ├── polyMesh/

│   ├── transportProperties

│   └── turbulenceProperties

├── system/

├── log.blockMesh

├── log.checkMesh

└── log.simpleFoam

En cada directorio de resultados se guardan los campos correspondientes a esa iteración. Pueden aparecer otros campos adicionales si los modelos los escriben.


### 9. Visualizar en ParaView

OpenFOAM no genera imágenes directamente. Genera campos numéricos definidos sobre una malla que después podemos representar.

Si el caso está montado en una carpeta accesible desde tu Fedora, podés abrirlo con ParaView en el host, sin instalar una interfaz gráfica en Docker.

En el directorio del caso:


```cpp
touch canalPowerLaw2D.foam
```

Después abrir canalPowerLaw2D.foam en ParaView.

En la interfaz:

Seleccionar el archivo y pulsar Apply.

Seleccionar el último paso disponible en el control temporal.

En Coloring, seleccionar U y luego Magnitude o el componente X.

Cambiar la cámara a +Z para observar el plano XY.

Utilizar Rescale to Data Range para ajustar la escala de colores.


#### A. Campo de velocidad

dev.to

Referencia visual de un campo de velocidad en un canal; no corresponde a una ejecución de nuestro caso.

Esperamos una velocidad prácticamente nula junto a las paredes y mayor en la zona central.

Al principio, nuestro perfil impuesto es uniforme en la entrada, pero las paredes frenan el fluido y generan una región de desarrollo hidrodinámico.

En un tramo suficientemente desarrollado, el perfil se estabiliza.


#### B. Presión

Cambiar Coloring a p.

La presión debería disminuir desde la entrada hacia la salida. En régimen estacionario, la caída de presión compensa la resistencia viscosa del flujo.

Si queremos expresarla en pascales, podremos utilizar una expresión calculada en ParaView:

Esto es válido para la densidad constante de referencia elegida.


#### C. Perfiles transversales

Para estudiar la velocidad en una sección del canal, utilizar Filters → Data Analysis → Plot Over Line.

Definir los extremos de la línea:

Así obtendremos  en función de , a 15 cm de la entrada.

También puede exportarse la tabla a CSV.


### 10. ¿Qué resultados físicos deberían aparecer?

Hay una predicción analítica útil para validar la forma del perfil.

Para un fluido de ley de potencia ideal entre dos placas paralelas, en flujo laminar completamente desarrollado:

Para n = 0,5, el exponente (n + 1)/n vale 3.


#### Perfil de velocidad teórico según el índice reológico

Ley de potencia

Newtoniano (n=1)

Índice n

0.50

Curvas analíticas normalizadas para flujo completamente desarrollado, sin efectos de entrada ni límites de viscosidad activos.

La diferencia más importante es que un fluido pseudoplástico presenta un perfil más aplanado en la región central que el perfil parabólico newtoniano.

Sin embargo, esta solución analítica supone una ley de potencia ideal, mientras que nuestra simulación tiene límites nuMin y nuMax. Además, tenemos una región de entrada. No debemos exigir coincidencia exacta sin comprobar ambas condiciones.


#### Relación entre velocidad máxima y media

Para el flujo completamente desarrollado entre placas:

Para n = 0,5:

Con una velocidad media impuesta de 0,01 m/s, el máximo teórico sería aproximadamente 0,0133 m/s.

Este resultado constituye una prueba cuantitativa de referencia, siempre que el flujo alcance un desarrollo suficiente y el modelo opere dentro de su región de ley de potencia.


### 11. Comprobar que la simulación tiene sentido

No alcanza con obtener una imagen atractiva o residuos bajos.

En el log podés inspeccionar los residuos y errores de continuidad con:


```cpp
grep -E "Solving for|continuity errors" log.simpleFoam | tail -n 40
```

Y detectar problemas graves:


```cpp
grep -Ei "fatal|error|floating|nan|bounding" log.simpleFoam
```


#### Una limitación importante de este primer caso

La distancia de desarrollo hidrodinámico no es necesariamente pequeña respecto de la longitud del canal. Por lo tanto, antes de comparar con la solución analítica hay que comprobar que los perfiles transversales dejan de cambiar con .

Una buena prueba consiste en comparar cortes en x=0.10, x=0.15 y x=0.19 m. Si siguen evolucionando apreciablemente, la solución aún no está completamente desarrollada.


### 12. Experimentos para modificar el caso

Una vez obtenida una solución estable, podemos hacer experimentos cambiando solamente algunos parámetros.

Cada cambio debería ejecutarse como un caso separado, evitando mezclar campos anteriores con condiciones nuevas.

Para comparar exclusivamente el efecto de , conviene mantener la misma geometría, velocidad, coeficiente de referencia y malla.


### 13. Siguiente nivel: fluidos con reología más realista

La ley de potencia es útil para aprender, pero tiene limitaciones: puede producir viscosidades extremadamente altas o bajas fuera de un intervalo de tasas de corte.

En una futura versión del canal podemos reemplazarla por modelos más apropiados para diferentes fenómenos.

Carreau / Carreau–Yasuda

Adecuado para representar una viscosidad elevada a bajo corte, una transición pseudoplástica y una viscosidad límite a alto corte. Interesante para soluciones poliméricas y fluidos biológicos.

Herschel–Bulkley

Incorpora un esfuerzo umbral de fluencia. Permite estudiar materiales que permanecen prácticamente inmóviles hasta que el esfuerzo aplicado es suficientemente grande.

Canal con estrechamiento

Introduce una geometría menos trivial: aceleración local, gradientes de presión, deformación intensa y, dependiendo de las condiciones, recirculación. Muy adecuado para estudiar diferencias entre modelos reológicos.


```bash
blockMesh
Geometría multibloque
powerLaw
simpleFoam
```
