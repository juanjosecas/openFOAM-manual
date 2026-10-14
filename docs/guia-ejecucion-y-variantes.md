# Ejecución de los casos y variantes controladas

La presente guía describe **secuencias de comandos, no resultados ejecutados**. Los archivos heredados de OpenFOAM Foundation requieren migración a OpenFOAM.com v2406/v2412 antes de considerarse compatibles. Ejecutar desde la raíz del repositorio, con el entorno OpenFOAM cargado. No borrar resultados previos sin respaldo.

## Convención común

```bash
cd cases/NOMBRE_DEL_CASO
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
foamDictionary system/controlDict -entry application -value
# Ejecutar solamente el solver identificado y compatible.
```

Para los casos con `Allrun`, `bash Allrun` ya genera la malla si falta, la comprueba y ejecuta el solver indicado por `controlDict`. El script no vuelve a crear la malla si existe `constant/polyMesh/points`; si cambió `blockMeshDict`, usar una copia nueva o regenerar la malla manualmente. Una malla previa no significa necesariamente una malla actualizada.

Para una variante, copiar el directorio original a otro nombre y **modificar solo un parámetro**. Los experimentos propuestos no están validados por ejecución.

## Tutoriales 01–03: canal y estenosis

**01 – Canal no newtoniano.** `cd cases/01-canal-no-newtoniano`, `blockMesh`, `checkMesh`, `simpleFoam`. También dispone de `bash Allrun`. Ensayos: reducir `0/U` de 0.01 a 0.005 m/s; variar `n` de 0.5 a 0.7 en `constant/turbulenceProperties`; cambiar `(200 40 1)` a `(100 20 1)` en `blockMeshDict`, conservando una celda en Z. Comparar perfil y caída de presión.

**02 – Canal con obstáculos.** `cd cases/02-canal-obstaculos`, `blockMesh`, `checkMesh`, `simpleFoam` o `bash Allrun`. Ensayos: reducir 25 % la velocidad de entrada; aumentar `n` de 0.5 a 0.7; refinar celdas cerca del obstáculo **sin romper las subdivisiones comunes entre bloques**. Comparar gradientes y recirculación, si aparece.

**03 – Estenosis capilar.** `cd cases/03-estenosis-capilar`, `blockMesh`, `checkMesh`, `simpleFoam` o `bash Allrun`. Ensayos: reducir 20 % la velocidad impuesta; cambiar `n` de 0.5 a 0.7; refinar únicamente el estrechamiento manteniendo la conectividad. Comparar velocidad máxima local y caída de presión.

Los tres utilizan `simpleFoam`: **sus carpetas numeradas son iteraciones, no instantes físicos**. Para convertirlos en transitorios se necesita un tutorial derivado, no cambiar solamente `application`.

## Tutorial 04: chorro de agua

**Estado: incompleto.** Contiene `system/blockMeshDict` y campos, pero **no** `system/controlDict`. Los únicos comandos de ejecución inequívocos son:

```bash
cd cases/04-chorro-agua
blockMesh
checkMesh
```

No ejecutar `interFoam` hasta reconstruir `controlDict` y verificar la sintaxis multifásica de v2406. Ensayos posteriores, sobre una copia comprobada: reducir 20 % la velocidad de entrada; reducir `maxCo` a la mitad; cambiar `writeInterval` para guardar más cuadros. Cambiar `writeInterval` no altera la discretización temporal.

## Tutorial 05: esfera en agua

**Estado: conceptual; sin carpeta de caso completa en `cases/`.** No existe una secuencia reproducible para mallado, inicialización y solver. Antes de crear variantes, determinar si corresponde una esfera rígida con malla móvil, overset o un modelo alternativo. No confundir una partícula lagrangiana con un sólido rígido mallado.

## Tutorial 06: foamlib

**Estado: herramienta de automatización, no caso CFD autónomo.** Ejecutar ejemplos Python solo después de instalar `foamlib` y seleccionar un caso existente. Ensayos: cambiar el intervalo de parámetros de una barrida, el número de casos derivados o los observables exportados. No cambiar simultáneamente la física y el código de automatización.

## Tutorial 07: SVG y Gmsh

**Estado: incompleto.** Faltan en `cases/07-svg-gmsh` el SVG fuente y `geometry/svg_to_gmsh.py` / `geometry/ajustar_patches.py`. La cadena prevista es:

```bash
cd cases/07-svg-gmsh
# Tras recuperar y verificar scripts y geometría:
python geometry/svg_to_gmsh.py
gmshToFoam dominio.msh
python geometry/ajustar_patches.py
checkMesh
simpleFoam
```

Los comandos anteriores son **secuencia prevista**, no ejecutable en el estado actual. Variantes: cambiar el tamaño característico de Gmsh; reducir 20 % la velocidad de entrada; aumentar la frecuencia de escritura de iteraciones. Debe conservarse el patch 2D `empty` cuando corresponda.

## Tutorial 08: tubería cilíndrica 3D

```bash
cd cases/08-tuberia-cilindrica-3d
blockMesh
checkMesh
pimpleFoam
```

También dispone de `bash Allrun`. Variantes: reducir el máximo de `0/U` de 0.020 a 0.015 m/s, conservando los tiempos de la tabla; reducir `maxCo` de 0.5 a 0.25; aumentar `writeInterval` de 0.01 a 0.02 s para menos cuadros. **Es transitorio**: las carpetas de tiempo representan segundos simulados.

## Tutorial 09: cavidad con tapa móvil

```bash
cd cases/09-cavity-2d
blockMesh
checkMesh
icoFoam
```

Dispone de `bash Allrun`, pero procede de OpenFOAM Foundation 4.x: comprobar compatibilidad de diccionarios antes de utilizarlo en OpenFOAM.com. Ensayos: reducir 20 % la velocidad de la tapa en `0/U`; reducir `writeInterval` a la mitad; refinar divisiones de `blockMeshDict` conservando dimensiones físicas.

## Tutoriales 10A–10C: tubería laminar heredada

```bash
cd cases/10a-tuberia-laminar-case0  # o 10b-tuberia-laminar-case1
blockMesh
checkMesh
icoFoam
```

Para `10c-tuberia-laminar-case2`, emplear `simpleFoam` en lugar de `icoFoam`, como figura en su `controlDict`. Antes, verificar compatibilidad de cada caso con la edición instalada y comprobar si `modifyMeshDict` forma parte del procedimiento que se pretende reproducir; no ejecutarlo por defecto.

Variantes de 10A/10B: cambiar la velocidad de entrada un 20 % cuando se imponga mediante `fixedValue`; reducir `deltaT` a la mitad; cambiar `writeInterval` manteniendo `writeControl`. Variante de 10C: variar la velocidad un 20 %; refinar subdivisiones; modificar intervalo de escritura de **iteraciones**, no de tiempo físico.

## Tutorial 11: rotura de presa

```bash
cd cases/11-dambreak-2d
blockMesh
checkMesh
setFields
interFoam
```

`setFields` se ejecuta **después del mallado y antes del solver** para inicializar `alpha.water` desde `system/setFieldsDict`. Es un caso procedente de Foundation 3.0.x: revisar y adaptar su configuración multifásica antes de ejecutarlo en OpenFOAM.com v2406/v2412.

Variantes: reducir `maxCo` cuando exista en `controlDict`; cambiar `writeInterval` para almacenar más fotogramas; modificar ligeramente la altura inicial del agua en `setFieldsDict` (sin modificar la geometría ni los patches) y volver a ejecutar `setFields` sobre una copia nueva.

## Tutorial 12: Goldschmidt, nube de partículas

```bash
cd cases/12-goldschmidt-particulas
blockMesh
checkMesh
foamDictionary system/controlDict -entry application -value
# DPMFoam  # No ejecutar sin migración de diccionarios.
```

Es un caso de Foundation 8 basado en `DPMFoam`; los archivos lagrangianos y campos como `U.air` requieren revisión de compatibilidad. No basta con encontrar el nombre del solver. Ensayos **tras migrar el caso**: reducir `deltaT` a la mitad, variar el intervalo de escritura, o modificar un parámetro de inyección pequeño identificado previamente en `constant/kinematicCloudProperties`; evitar cambios simultáneos.

## Comprobaciones mínimas antes de interpretar resultados

- Revisar `checkMesh`, errores de continuidad y mensajes `FOAM FATAL ERROR`.
- Distinguir cambios de física (velocidad, geometría, viscosidad) de cambios numéricos (`deltaT`, `maxCo`, esquemas) y de salida (`writeInterval`).
- Nunca interpretar estados de `simpleFoam` como un movimiento físico.
- Mantener por separado el caso original y las variantes; no ejecutar una variante sobre resultados viejos.


## Conversión de un caso estacionario a transitorio

En los casos `simpleFoam` (01–03, 07, 10C), pasar a `pimpleFoam` exige revisar más que `application`: esquemas temporales, algoritmo de presión-velocidad, paso físico, modelo constitutivo, condiciones de entrada y salidas. Consultar la [guía paso a paso](simplefoam-a-transitorio.md). Las iteraciones estacionarias no son segundos simulados.
