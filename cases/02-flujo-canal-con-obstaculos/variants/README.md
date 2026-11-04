# Variantes del canal y de la interacción con el obstáculo

Las recetas JSON se aplican a una **copia nueva** de la plantilla original con
`scripts.variantes_canal.preparar_canal_obstaculos`. No modifican `cases/`.
La copia guarda `variante.json` y los diccionarios efectivos, y queda lista para
`blockMesh`, `checkMesh` y `simpleFoam`.

## Ejemplos preparados

| Receta | Fluido | Objeto | Qué comparar |
| --- | --- | --- | --- |
| `base` | `powerLaw` original | `noSlip` | Referencia original |
| `objeto-slip` | Igual a la base | `slip` | Deslizamiento ideal frente a adherencia |
| `objeto-parcial` | Igual a la base | `partialSlip`, fracción 0.5 | Interacción intermedia |
| `agua-estela` | Newtoniano, nu=1e-6 m²/s | `noSlip` | Estela con mayor influencia de inercia que en la base viscosa |
| `agua-slip` | Igual a `agua-estela` | `slip` | Efecto del objeto a fluido y velocidad constantes |
| `malla-fina` | Igual a la base | `noSlip` | Doble resolución en x e y; 31360 celdas |

En **todas** las variantes las paredes `lowerWall` y `upperWall` permanecen
`noSlip`, la entrada es 0.01 m/s y la geometría no cambia. El obstáculo ya tiene
un patch independiente, por lo que no hay que separar caras ni reconstruir su
geometría para cambiar su condición de velocidad.

`base` conserva el límite original de 1500 iteraciones. Las recetas de interacción y agua elevan el máximo a 5000; `malla-fina` usa
8000. Estas recetas conservan dos escrituras recientes con 12 dígitos, para
dejar margen a la convergencia y controlar el espacio de salida. El criterio de parada
se mantiene en p=1e-6 y U=1e-7; puede finalizar antes del máximo.

## Qué significa la interacción elegida

### Objeto fijo adherente: noSlip

```cpp
obstacle
{
    type noSlip;
}
```

Velocidad cero en el objeto fijo. Es la condición original y la misma interacción
que conservan las paredes del canal.

### Objeto impermeable con deslizamiento ideal: slip

```cpp
obstacle
{
    type slip;
}
```

Impide flujo normal al objeto y permite deslizamiento tangencial sin fricción
ideal. No elimina el objeto ni permite atravesarlo. `type wall` en la malla sigue
siendo correcto: es una clasificación geométrica, no obliga a usar `noSlip`.

### Deslizamiento parcial: partialSlip

```cpp
obstacle
{
    type partialSlip;
    refValue uniform (0 0 0);
    valueFraction uniform 0.5;
    value uniform (0 0 0);
}
```

Con referencia cero, `valueFraction=0` corresponde al extremo `slip` y `1` al
extremo de velocidad cero. `0.2`, `0.5` y `0.8` permiten comparar una transición;
un valor mayor implica más peso de la referencia nula. `value` es el valor
inicial del patch y no reemplaza el cálculo de la condición mixta.

La fracción es adimensional, **no es una longitud de deslizamiento, coeficiente
de rugosidad o propiedad calibrada de un material**. A fracción fija, cambiar la
resolución normal puede cambiar el deslizamiento físico equivalente. No usarlo
como condición de Navier calibrada sin estudiar esa dependencia. Documentación:
[OpenCFD, partialSlip](https://doc.openfoam.com/2306/tools/processing/boundary-conditions/rtm/derived/wall/partialSlip/).

### Agua newtoniana y estela

Las recetas de agua cambian de forma coordinada `nu` en `transportProperties` a
`1e-6` y el bloque `laminar` a `{ model Stokes; }`. Se conserva
`transportModel Newtonian`. El nombre `Stokes` designa aquí el modelo de esfuerzo
laminar de OpenFOAM: **no elimina la convección de las ecuaciones de simpleFoam**.
Cambiar solo `nu` habría dejado activo el `powerLaw` del caso base.

Con altura del obstáculo h=0.004 m y U=0.01 m/s, `Re_h=U*h/nu=40`.
Especificar h importa: usando la longitud axial del objeto, 0.020 m, se obtendría
Re=200. Comparar `agua-estela` con `agua-slip` a escalas de color comunes.
`simpleFoam` muestra estados estacionarios: no produce un desprendimiento de
vórtices que evolucione en el tiempo. Para ello se necesita un caso transitorio.

No imponer una velocidad uniforme no nula a todas las caras del objeto para
simular su traslación: en las caras frontal/posterior introduciría velocidad
normal a una geometría fija. Movimiento real, deformación o permeabilidad
requieren otra configuración y no están incluidos en estas recetas.

## Uso desde el notebook

```python
from pathlib import Path
from scripts.variantes_canal import preparar_canal_obstaculos
from scripts.foam_docker import foam_run

REPO_DIR = Path('.').resolve(strict=True)
CASE_DIR = preparar_canal_obstaculos(REPO_DIR, variante='objeto-parcial')
options = dict(case_dir=CASE_DIR, repo_dir=REPO_DIR, verbose=True)

foam_run(['blockMesh'], timeout=120, **options)
mesh_result = foam_run(['checkMesh'], timeout=120, **options)
if 'Mesh OK.' not in mesh_result.log_path.read_text():
    raise RuntimeError(f'Revisar malla: {mesh_result.log_path}')
result = foam_run(['simpleFoam'], timeout=600, **options)
if 'SIMPLE solution converged' not in result.log_path.read_text():
    raise RuntimeError(f'Revisar convergencia: {result.log_path}')
(CASE_DIR / 'canal_obstaculos.foam').touch(exist_ok=True)
```

Editar una receta para probar otros números o copiarla con otro nombre. Las
entradas se modifican con `foamDictionary`, no con sustituciones de texto del
notebook. Los parámetros de `agua-*` cambian la física; `malla-fina` conserva la
física y cambia la resolución. No atribuir las diferencias entre agua y powerLaw
únicamente al tipo de interacción superficial.

## Verificación realizada con Docker v2406

Se ejecutaron `blockMesh`, `checkMesh` y `simpleFoam` en copias temporales el
2026-10-22. Todas las mallas confirmaron `Mesh OK.` y todas las recetas finales
alcanzaron los criterios SIMPLE configurados:

| Receta | Celdas | Iteración de convergencia |
| --- | ---: | ---: |
| `base` | 7840 | 1453 |
| `objeto-slip` | 7840 | 1909 |
| `objeto-parcial` | 7840 | 1456 |
| `agua-estela` | 7840 | 274 |
| `agua-slip` | 7840 | 288 |
| `malla-fina` | 31360 | 5414 |

Se verificó velocidad nula en las paredes del canal y flujo normal `phi=0` en
el obstáculo, también con deslizamiento. Las variantes `agua-*` presentaron
pequeñas zonas de velocidad axial negativa aguas abajo. Este resultado es un
indicador de retorno local, no una validación independiente de la estela o de
los esfuerzos. El límite inicial de 5000 iteraciones no alcanzó para la malla
fina y se amplió a 8000 conservando las tolerancias. No se ha demostrado
independencia de malla ni se han validado fuerzas experimentalmente.
