# De simpleFoam estacionario a una simulación transitoria

Esta guía explica **cuándo conviene** pasar un caso de `simpleFoam` a `pimpleFoam`, qué cambia en los diccionarios y qué información adicional se obtiene. Es una **guía de migración**, no una sustitución automática del solver.

Los tutoriales **01 (canal no newtoniano), 02 (obstáculos), 03 (estenosis), 07 (Gmsh) y 10C (tubería)** emplean `simpleFoam`. El tutorial **08** contiene una configuración `pimpleFoam` transitoria que sirve como referencia de organización. Los casos heredados deben comprobarse contra la edición instalada.

## 1. ¿Para qué convertir un caso?

`simpleFoam` busca una solución estacionaria: presión y velocidad dependen del espacio, pero **no se resuelve su evolución temporal física**. Es adecuado cuando interesan caída de presión, caudal, perfiles y comportamiento medio en condiciones aproximadamente constantes. Los directorios numerados de un cálculo estacionario corresponden a **iteraciones**, no a segundos simulados.

`pimpleFoam` resuelve la evolución de un flujo incompresible mediante un esquema temporal y el acoplamiento PIMPLE. La formulación incluye la variación temporal, esquemáticamente:

$$
\frac{\partial \mathbf{U}}{\partial t}
+\nabla\cdot(\mathbf{U}\otimes\mathbf{U})
=-\nabla p+\nabla\cdot\boldsymbol{\tau}+\mathbf{f}.
$$

Aquí la presión `p` de los solvers incompresibles suele ser **cinemática** (m²/s²); revisar siempre las dimensiones del campo.

**Cuándo merece la pena:** velocidad de entrada pulsátil, arranque o parada del flujo, evolución temporal de recirculaciones, fluctuaciones de presión, respuesta a un pulso y fuerzas variables sobre obstáculos. **Cuándo no:** si el objetivo es solo obtener un perfil de flujo plenamente desarrollado o una pérdida de carga bajo condiciones constantes, el estacionario suele ser más económico.

## 2. ¿Es complicado?

| Situación | Dificultad orientativa | Razón |
| --- | --- | --- |
| Canal newtoniano laminar con malla fija | Baja–media | Cambiar solver, discretización temporal, controles y salida |
| Entrada pulsátil sobre geometría fija | Media | Definir correctamente condición temporal y resolución |
| Obstáculo con desprendimiento de vórtices | Media–alta | Refinamiento espacial/temporal, sensibilidad de resultados |
| Canal no newtoniano de ley de potencia | Media–alta | Comprobar que el modelo constitutivo esté soportado y sea equivalente en el solver transitorio |
| Flujo turbulento con LES o malla móvil | Alta | Modelo, resolución espacial/temporal y validación cambian |

**No basta con escribir `application pimpleFoam;`**: la migración afecta, como mínimo, a `controlDict`, `fvSchemes`, `fvSolution` y la estrategia de inicialización; algunos modelos o condiciones de borde pueden requerir más cambios.

## 3. Trabajar sobre una copia

Partiendo de la raíz del repositorio:

```bash
cp -a cases/02-canal-obstaculos cases/02-canal-obstaculos-transitorio
cd cases/02-canal-obstaculos-transitorio
# No copiar tiempos calculados ni processor*/ a la variante.
# Revisar primero condiciones y modelos antes de ejecutar.
```

Para utilizar una solución estacionaria convergida como condición inicial, transferir **solo campos compatibles** (por ejemplo `U` y `p`, y campos del modelo cuando correspondan) mediante procedimientos de inicialización o mapeo revisados. **No interpretar el índice de iteración de simpleFoam como segundos** ni usar `startFrom latestTime` indiscriminadamente en una copia con directorios numerados procedentes del estacionario.

## 4. system/controlDict: tiempo físico y Courant

Ejemplo **orientativo** para una variante con velocidad y tamaño de celda compatibles:

```cpp
application     pimpleFoam;          // Solver transitorio incompresible.
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         2;                   // 2 segundos de tiempo físico.
deltaT          1e-4;                // Paso de tiempo inicial [s].
adjustTimeStep  yes;                 // Adaptación automática por Courant.
maxCo           0.5;                 // Límite máximo recomendado al inicio.
maxDeltaT       1e-3;                // Techo de paso temporal.
writeControl    adjustableRunTime;
writeInterval   0.01;                // Escribir cada 0.01 s simulados.
```

Es un **fragmento de entradas** de `controlDict`, no un archivo completo: conservar las opciones de formato, precisión y demás controles que necesite el caso. Elegir `deltaT` mediante el tamaño de celda, las velocidades y el número de Courant:

$$
\mathrm{Co}\approx \frac{|\mathbf{U}|\,\Delta t}{\Delta x}.
$$

En un dominio con celdas pequeñas o velocidades altas, `deltaT` puede necesitar ser mucho menor. `writeInterval` cambia la frecuencia de resultados, **no** la precisión temporal de la integración.

## 5. system/fvSchemes: término temporal

El diccionario del tutorial 01 utiliza actualmente:

```cpp
ddtSchemes
{
    default steadyState;
}
```

En una variante transitoria, un punto de partida conservador es:

```cpp
ddtSchemes
{
    default Euler;  // Primer orden temporal, robusto como prueba inicial.
}
```

Posteriormente se puede estudiar un esquema temporal de mayor orden si está admitido por la edición y las condiciones numéricas. También hay que revisar `divSchemes`: un esquema `bounded` pensado para el solver estacionario no necesariamente es la elección apropiada para la variante transitoria. **No copiar sin revisión** el resto de `fvSchemes`, especialmente en modelos no newtonianos o versiones diferentes.

## 6. system/fvSolution: de SIMPLE a PIMPLE

En los tutoriales estacionarios suele existir:

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    residualControl
    {
        p 1e-6;
        U 1e-7;
    }
}
```

En una variante transitoria, revisar y configurar `PIMPLE`, por ejemplo:

```cpp
PIMPLE
{
    momentumPredictor          yes;
    nOuterCorrectors           2;   // Correcciones externas de acoplamiento.
    nCorrectors                2;   // Correcciones presión-velocidad.
    nNonOrthogonalCorrectors   0;   // Aumentar solo si la calidad de malla lo exige.
}
```

Esos valores son un **punto de partida didáctico, no una parametrización validada**. Revisar los solvers de `p`, `pFinal`, `U` y sus tolerancias para la edición elegida. Las entradas de `SIMPLE`, `residualControl` y factores de relajación del caso estacionario no deben conservarse automáticamente como si fueran controles equivalentes de PIMPLE.

## 7. Modelos físicos y condiciones de contorno

- **`0/U`**: si la velocidad de entrada pasa de constante a pulsátil, definir una condición de contorno temporal soportada por la versión (por ejemplo `uniformFixedValue` con una función temporal compatible). La sintaxis exacta debe comprobarse con un tutorial de esa versión.
- **`0/p`**: revisar el tratamiento del outlet, el nivel de referencia y los cambios de signo/unidad; mantener la coherencia con `U`.
- **`constant/transportProperties` y modelo de flujo**: verificar que `pimpleFoam` soporte la misma ley constitutiva y los mismos diccionarios de reología. En particular, **no suponer** que el modelo `generalizedNewtonian/powerLaw` de 01–03 migra sin cambios.
- **Malla**: puede mantenerse en el primer ensayo si es válida, pero fenómenos transitorios (p. ej., estelas vorticosas) pueden exigir más resolución y, en ocasiones, un dominio más largo.
- **Inicialización**: comenzar desde `0/` válido o una solución convergida correctamente mapeada; no combinar resultados viejos de solvers distintos.

## 8. Qué nuevos resultados permite obtener

| Resultado | `simpleFoam` estacionario | `pimpleFoam` transitorio |
| --- | --- | --- |
| Distribución espacial de velocidad y presión | Sí | Sí, en cada instante guardado |
| Caída de presión y caudal en régimen establecido | Sí | Sí; también evolución y promedios temporales |
| Arranque y establecimiento del flujo | No, como fenómeno físico temporal | Sí |
| Respuesta a entrada pulsátil | No en el marco estacionario | Sí |
| Retardo de fase entre entrada y salida | No | Sí |
| Frecuencias dominantes de oscilación o desprendimiento | No | Sí, si el fenómeno aparece y está suficientemente resuelto |
| Animación de dinámica real | No; solo iteraciones | Sí, con estados de tiempo físico |
| Fuerzas variables sobre sólidos | No como función del tiempo | Sí, configurando su postprocesamiento |

En los canales 01–03 y el obstáculo del 02 resultan especialmente útiles **sondas temporales** y perfiles a varios instantes. En un sistema pulsátil puede compararse amplitud, retraso de fase y respuesta de presión. Un GIF de `simpleFoam` no equivale a una animación física.

## 9. Comprobaciones mínimas

1. Confirmar que el solver está instalado y que el modelo de fluido es compatible con él.
2. Ejecutar `checkMesh` sobre la malla que se utilizará.
3. Revisar `Courant Number`, continuidad, residuos y estabilidad del avance físico.
4. Comparar resultados para al menos dos `deltaT`, conservando la física y la malla.
5. Comparar al menos dos resoluciones espaciales cuando el objetivo sea cuantitativo.
6. Configurar sondas y `writeInterval` para capturar la escala temporal de interés.
7. Interpretar resultados posteriores al transitorio inicial por separado de la fase de establecimiento.

## 10. Referencias y ejemplos del manual

- [Tutorial 08: tubería pulsátil con `pimpleFoam`](tutoriales/08-tuberia-cilindrica-3d.md).
- [Ejecución y variantes de los casos](guia-ejecucion-y-variantes.md).
- [Gráficos y propiedades físicas](graficos-y-propiedades.md).
- [PyVista para animaciones](pyvista.md).
- [OpenFOAM: `simpleFoam` estacionario](https://doc.openfoam.com/2306/tools/processing/solvers/rtm/incompressible/simpleFoam/).
- [OpenFOAM: periodic hill, inicialización estacionaria para transitorio](https://doc.openfoam.com/2212/examples/verification-validation/turbulent/periodic-hill/).

**Estado:** explicación y fragmentos ilustrativos, sin una variante transitoria ejecutada para 01–03, 07 o 10C. Una conversión reproducible completa debe fijar primero versión de OpenFOAM, modelo reológico y condiciones temporales.
