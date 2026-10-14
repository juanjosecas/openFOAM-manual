# OpenFOAM v2406 — Tutorial 05

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.


### Caída de una esfera sólida en agua con superficie libre

En este tutorial vamos a incorporar un cuerpo rígido móvil a una simulación multifásica. La esfera se libera desde una posición inicial, cae por gravedad, atraviesa la superficie del agua y continúa descendiendo bajo la acción de las fuerzas hidrodinámicas.

El objetivo es que OpenFOAM calcule la trayectoria de la esfera, en lugar de imponer manualmente su velocidad.


#### 1. Qué vamos a simular

Las propiedades del cuerpo se obtienen a partir de su radio y densidad.

Para una esfera de radio $r=0.01\ \mathrm m$:

Por lo tanto:

Su momento de inercia respecto de cualquiera de los ejes que atraviesan el centro es:

Estos valores corresponden a una esfera maciza y homogénea.


#### 2. Qué cambia respecto de interFoam

El movimiento del sólido introduce tres problemas adicionales:

La geometría del dominio fluido cambia a cada instante.

Las fuerzas del fluido deben integrarse sobre la superficie del sólido.

La nueva posición del sólido debe utilizarse para actualizar la malla y los campos.

La dificultad principal ya no es resolver solamente agua y aire, sino mantener correctamente el acoplamiento entre el sólido y el fluido.

OpenFOAM v2406 incluye dos tecnologías útiles:

sixDoFRigidBodyMotion, que calcula traslaciones y rotaciones de un cuerpo rígido.

Mallas dinámicas y overset, que permiten representar sólidos en movimiento.

Para desplazamientos grandes, una malla overset evita deformar continuamente toda la malla del recipiente. En esa formulación hay celdas activas, celdas interpoladas y celdas excluidas de la región sólida.


### 3. Elegir un caso compatible con v2406

Para este primer ejercicio utilizaremos como base el caso oficial sphereDrop, distribuido con OpenFOAM.com:

La documentación de OpenFOAM identifica este caso como ejemplo de sixDoFRigidBodyDisplacement, y hay registros de ejecución con OpenFOAM v2406.

El solver es compressibleInterDyMFoam. No es el mismo que utilizamos para el chorro de agua y tampoco utiliza necesariamente mallas overset. Eso importa: la configuración de un solver multifásico con malla deformable no se puede trasladar directamente a overInterDyMFoam.

La decisión para este tutorial es comenzar con sphereDrop y conservar sus archivos originales compatibles con v2406. Todavía no he podido verificar el contenido exacto de todos sus diccionarios, así que no voy a presentar archivos reconstruidos de memoria como si fueran una configuración ejecutable y comprobada.


### 4. Preparar el caso en Docker

Primero verificamos la instalación:


```cpp
foamVersion

which compressibleInterDyMFoam

echo "$FOAM_TUTORIALS"
```

Localizamos el tutorial:


```cpp
find "$FOAM_TUTORIALS" \
    -type d \
    -name sphereDrop
```

Debería devolver una ruta terminada en:

multiphase/compressibleInterDyMFoam/laminar/sphereDrop


#### Crear el directorio de trabajo

En este caso utilizaremos cp en lugar de touch, porque necesitamos conservar también las configuraciones y recursos geométricos originales.


```bash
mkdir -p "$HOME/openfoam/casos"

cp -a \
    "$FOAM_TUTORIALS/multiphase/compressibleInterDyMFoam/laminar/sphereDrop" \
    ./caidaEsfera3D

cd caidaEsfera3D
```

La copia contiene los archivos que necesita el ejemplo de esa instalación. A diferencia de crear archivos vacíos con touch, así evitamos perder bibliotecas, geometrías o configuraciones específicas del modelo de movimiento.


#### Inspeccionar todos los archivos


```cpp
find . -type f | sort
```

Para identificar los diccionarios fundamentales:


```cpp
find system constant 0 -type f 2>/dev/null | sort
```

Si el caso utiliza 0.orig, también hay que inspeccionarlo:


```cpp
find 0.orig -type f 2>/dev/null | sort
```

Para mostrar en pantalla los diccionarios:


```cpp
for file in system/*Dict constant/*Dict; do
    if [ -f "$file" ]; then
        echo
        echo "========== $file"
    fi
done
```

Este caso oficial es una excepción provisional a nuestro formato habitual: todos sus archivos quedan copiados en el directorio de trabajo, aunque todavía no están transcritos individualmente en el chat.


### 5. Entender cómo se mueve la esfera

El elemento que nos interesa identificar es:

type sixDoFRigidBodyDisplacement;

Esta condición de contorno permite relacionar el movimiento de una superficie sólida con la dinámica de un cuerpo rígido.

La configuración incluye propiedades como:

mass

momentOfInertia

centreOfMass

Sus valores deben corresponder al cuerpo representado en la malla.

También pueden aparecer parámetros de amortiguamiento y restricciones de movimiento.


#### Grados de libertad

Un cuerpo rígido tiene seis grados de libertad: tres traslaciones y tres rotaciones.

Para el primer experimento, el movimiento físicamente más sencillo es permitir solamente la traslación vertical. Eso nos permite estudiar la caída sin introducir rotaciones que compliquen la interpretación.

Posteriormente podríamos liberar otros grados de libertad.


#### Qué fuerza hace descender a la esfera

OpenFOAM calcula las fuerzas hidrodinámicas mediante los campos de presión y esfuerzos viscosos sobre la superficie sólida.

La ecuación del movimiento es:

$$ m\mathbf a=m\mathbf g+\mathbf F_{\mathrm{hidro}} $$

Para una esfera de acero completamente sumergida, el empuje hidrostático es aproximadamente:

Con los parámetros elegidos:

$$ F_b\approx0,0411\ \mathrm N $$

El peso de la esfera es:

$$ P=mg\approx0,3226\ \mathrm N $$

Por lo tanto, el empuje hidrostático no alcanza para sostenerla. La esfera tenderá a hundirse, aunque su aceleración dependerá también del arrastre, las fuerzas transitorias y el movimiento del líquido.


### 6. Ejecutar el ejemplo

Primero inspeccioná el script incluido:

La secuencia documentada para sphereDrop incluye:


```bash
blockMesh
topoSet
createPatch
mergeOrSplitBaffles
setFields
solver
```

La preparación geométrica es más compleja que en nuestros canales anteriores: incluye operaciones de modificación de topología y separación de superficies, que no deben omitirse ni reordenarse arbitrariamente.


```cpp
chmod +x Allrun

./Allrun 2>&1 | tee log.tutorial
```

El script deberá ejecutarse desde el directorio del caso. Si encuentra una configuración compatible con la instalación, realizará las operaciones de mallado, inicialización y cálculo definidas por sus autores.


#### Comprobar la ejecución


```cpp
grep -Ei \
    "Time =|sixDoF|centre of rotation|centre of mass|Courant|ExecutionTime|FATAL" \
    log.tutorial | tail -n 80
```

El nombre exacto de las variables impresas depende de los objetos de seguimiento activos en el tutorial.

Conviene verificar especialmente que la posición del centro de masa cambie con el tiempo y que la malla no desarrolle volúmenes negativos.


### 7. Visualizar la caída en ParaView

Creá el archivo de apertura:


```cpp
touch caidaEsfera3D.foam
```

Abrilo en ParaView y seleccioná los campos disponibles.

Para observar la superficie libre, utilizá la fracción volumétrica de agua —si está disponible con ese nombre— y aplicá un filtro Contour con valor 0,5.

Para visualizar la esfera, seleccioná su superficie sólida dentro de los patches.

Después:

Mostrá simultáneamente la superficie del agua y la esfera.

Elegí el último intervalo temporal disponible.

Usá los controles de reproducción para animar el movimiento.

Aplicá un corte longitudinal (Slice) si querés observar el flujo dentro del recipiente.

Representá la magnitud de la velocidad alrededor de la esfera.

Una visualización particularmente útil sería mostrar el agua como una superficie semitransparente y la esfera como un sólido opaco.


### 8. Experimentos para realizar

Una vez que el caso original funcione, modificaríamos una variable por ejecución.

No basta con cambiar mass para simular otro diámetro: también deben modificarse la geometría, el volumen y el momento de inercia.


#### Registrar la trayectoria

Para analizar científicamente el movimiento, necesitamos recuperar:

Y, si es posible, relacionarlos con:

Eso permitiría distinguir tres etapas: caída en aire, entrada al agua y movimiento sumergido.

También podríamos estudiar la energía cinética del sólido:

$$ E_k(t)=\frac12m|\mathbf v(t)|^2 $$

y comprobar qué proporción de su energía mecánica se transfiere al fluido durante el impacto.


### 9. El siguiente paso técnico

Hay dos niveles de dificultad diferentes que conviene separar.

Nivel 1 — sphereDrop: estudiar el movimiento de una esfera usando el caso existente, su malla dinámica y el acoplamiento 6DoF. Es lo que permiten ejecutar los comandos anteriores.

Nivel 2 — Caso propio con overset: construir desde cero un recipiente de dimensiones conocidas, una esfera de radio configurable y dos mallas independientes. Utilizaríamos overInterDyMFoam, dynamicOversetFvMesh, zoneID, sixDoFRigidBodyMotion y los diccionarios necesarios para combinar y actualizar las mallas. La documentación oficial describe estos requisitos, incluidos los solvers asimétricos necesarios para la interpolación overset.

Este segundo nivel permitirá controlar completamente la geometría y tendrá mayor valor para nuestra colección de tutoriales. Sin embargo, requiere verificar las configuraciones concretas de v2406 para entregar todos los archivos sin introducir errores de compatibilidad.

La referencia oficial para continuar es sixDoFRigidBodyDisplacement y, para mallas superpuestas, Overset mesh.

Estado: queda preparado un procedimiento de ejecución y análisis del caso sphereDrop incluido en la instalación, pero todavía no un caso propio completamente especificado. Para eso falta inspeccionar los diccionarios reales de v2406, en particular la configuración de movimiento y las operaciones de construcción de la malla.

PROTOCOLO RÁPIDO — Prototipo de automatización: empezar por una sola ejecución y comprobar lectura de campos y convergencia. Ejecutar después tres valores de velocidad de forma secuencial; reservar la concurrencia para cuando el caso simple funcione.
