# Variantes numéricas del flujo alrededor de la esfera

Todas las variantes mantienen el fluido newtoniano, el modelo laminar, el solver
estacionario y los nombres de patches del caso base. No requieren editar lógica
Python ni cambiar de solver. Son propuestas de ensayo, no resultados ejecutados.

## Cómo preparar una variante

1. Conservar el resultado base en `runs/`.
2. Modificar los números indicados en la plantilla original antes de ejecutar la
   celda que la copia. Para conservar varias plantillas, copiar primero la carpeta
   del caso y apuntar `SOURCE_CASE` a esa copia.
3. Ejecutar la celda completa: crea una carpeta nueva en `runs/`, genera el STL,
   reconstruye la malla y resuelve. No reutilizar una malla ya refinada.
4. Actualizar `diametro` y `nu` en `graficar_esfera` si cambiaron. La función
   obtiene la velocidad de referencia del patch inlet, pero no infiere esos dos
   parámetros. `rho` solo convierte diferencias de presión a Pa en los gráficos.
5. Comparar perfiles, presión, malla y convergencia; cambiar una variante por vez.
   Los cambios coordinados dentro de una variante se indican explícitamente.

Base: diámetro D=1 m, radio R=0.5 m, U=1e-5 m/s, nu=1e-6 m²/s, Re=10.

## 1. Variar Reynolds cambiando velocidad

En `0/U`, sustituir la componente x tanto en `internalField` como en
`inlet/value`; mantener las componentes y y z en cero.

| Ensayo | Ux [m/s] | Re = U D / nu | Qué comparar |
| --- | ---: | ---: | --- |
| Re1 | `1e-6` | 1 | Flujo dominado por viscosidad frente al caso base |
| Re5 | `5e-6` | 5 | Transición gradual respecto de Re1 y Re10 |
| Base | `1e-5` | 10 | Referencia |
| Re50 | `5e-5` | 50 | Cambios de estela, presión y componentes transversales |
| Re100 | `1e-4` | 100 | Sensibilidad de la estela y mayores exigencias de resolución |

Para comparar distintas velocidades usar `|U|/U∞`, `Cp` y coordenadas divididas
por D. No comparar solo colores con escalas automáticas diferentes. Si aparecen
oscilaciones persistentes o no converge, revisar malla, dominio y estabilidad de
la solución estacionaria; no interpretar el último estado como convergido ni
asumir que aumentar iteraciones siempre resuelve el problema.

## 2. Variar viscosidad manteniendo la velocidad

Cambiar únicamente el último número de `nu` en `constant/transportProperties`.
Conservar las dimensiones `[0 2 -1 0 0 0 0]`.

| nu [m²/s] | Re | Parámetro para los gráficos |
| ---: | ---: | --- |
| `2e-6` | 5 | `nu=2e-6` |
| `1e-6` | 10 | `nu=1e-6` |
| `5e-7` | 20 | `nu=5e-7` |

Esto representa distintas viscosidades del modelo, no una temperatura específica
del agua. Comparar Re5 obtenido por menor velocidad y por mayor viscosidad es un
ensayo de semejanza: en esta geometría y con las mismas condiciones adimensionales,
se esperan campos adimensionales comparables cuando estén bien convergidos.

## 3. Resolver mejor la superficie

En `system/snappyHexMeshDict`, cambiar `refinementSurfaces/sphere/level`.

| Ensayo | level | Objetivo |
| --- | --- | --- |
| Base | `(1 2)` | Permite niveles 1 a 2; no garantiza alcanzar nivel 2 |
| Fino | `(2 2)` | Solicitar nivel 2 en toda la superficie |
| Más fino | `(3 3)` | Solicitar nivel 3 y evaluar convergencia espacial |

Cada nivel reduce aproximadamente a la mitad el tamaño de celda respecto del
anterior. El número de celdas resultante no es una multiplicación fija de la malla
base. Revisar topes `maxLocalCells` y `maxGlobalCells`: como punto de partida para
estas variantes se pueden aumentar de `100000`/`500000` a `500000`/`2000000`,
si la memoria disponible lo permite. Verificar en el log los niveles realmente
alcanzados y aprobar `checkMesh`. No son límites de consumo de RAM.

## 4. Refinamiento global de la caja

En `system/blockMeshDict`, cambiar solo las subdivisiones del bloque:

| Subdivisiones | Celdas de fondo, antes de snappyHexMesh |
| --- | ---: |
| `(24 24 24)` | 13824 |
| `(32 32 32)` | 32768 |
| `(48 48 48)` | 110592 |

Mantener los vértices y los niveles superficiales iguales para esta comparación.
La variante 48³ ya supera el valor base de `maxLocalCells`; revisar los topes como
se indica arriba. Aumentar `resolucion=` en los gráficos no sustituye este ensayo.

## 5. Caja más grande para estudiar confinamiento

En los vértices de `system/blockMeshDict`, cambiar todas las coordenadas de caja
`-2`/`2` a `-4`/`4` m y las subdivisiones de `(24 24 24)` a `(48 48 48)`.
Este cambio coordinado duplica la distancia a las fronteras y mantiene el tamaño
de celda de fondo: 4/24 = 8/48 m. Conservar el STL de radio 0.5 m y los mismos
niveles de refinamiento. Revisar los topes de celdas como en el ensayo anterior.

`locationInMesh (1.5 0 0)` sigue dentro de la caja y fuera de la esfera: no hace
falta cambiarlo. Comparar velocidad y Cp en posiciones x/D, y/D comunes a ambas
cajas. La caja grande es otra prueba, no una garantía de dominio independiente.

## 6. Esfera más pequeña y mismo Reynolds

En el notebook cambiar el argumento numérico `--radius` de `0.5` a `0.25` m.
En `0/U`, cambiar ambas velocidades de `1e-5` a `2e-5` m/s. Mantener `nu=1e-6`:
con D=0.5 m se conserva Re=10. En los gráficos usar `diametro=0.5`.

La caja conserva sus dimensiones físicas, pero el objeto es relativamente más
pequeño. También cambia la resolución relativa cerca de la esfera. Para separar
ambos efectos, subir los dos niveles de superficie en uno: de `(1 2)` a `(2 3)`
conserva aproximadamente la relación tamaño local de celda/diámetro para niveles
correspondientes. Comprobar los niveles efectivos y el tamaño de las celdas; esta
comparación no sustituye un estudio independiente de dominio y resolución.

## 7. Convergencia y escrituras, sin cambiar la física

| Archivo y entrada | Base | Ejemplo | Efecto |
| --- | --- | --- | --- |
| `system/fvSolution`, `SIMPLE/residualControl/p` | `1e-6` | `1e-7` | Criterio de presión más estricto |
| `system/fvSolution`, `SIMPLE/residualControl/U` | `1e-7` | `1e-8` | Criterio de velocidad más estricto |
| `system/fvSolution`, `relaxationFactors/fields/p` | `0.3` | `0.2` | Más subrelajación de presión |
| `system/fvSolution`, `relaxationFactors/equations/U` | `0.7` | `0.5` | Más subrelajación de velocidad |
| `system/controlDict`, `endTime` | `1500` | `3000` | Más iteraciones máximas, si hacen falta |
| `system/controlDict`, `writeInterval` | `100` | `25` | Guardar con más frecuencia |
| `system/controlDict`, `purgeWrite` | `2` | `0` | Conservar todas las escrituras |

Usar tolerancias más estrictas para comparar cuánto cambia el resultado. La
subrelajación puede ayudar a estabilizar iteraciones, pero no corrige por sí sola
la física o una malla inadecuada. SIMPLE puede detenerse antes de `endTime`.
Las escrituras son iteraciones de una solución estacionaria, no frames de tiempo
físico. `deltaT` no se usa aquí como paso temporal para una simulación transitoria.

Cambiar solo la referencia de presión `outlet/value` en `0/p` desplaza el nivel
de p: con velocidad prescrita en la entrada, no es un ensayo de mayor caudal.
Habilitar capas prismáticas, rotación, otro modelo de fluido o evolución temporal
requiere cambios adicionales y queda fuera de estas variantes solo numéricas.
