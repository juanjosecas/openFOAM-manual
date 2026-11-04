# Tutorial 04 — Chorro de agua (caso completado documentalmente)

Se reconstruyó `system/controlDict` para la configuración `interFoam` de agua/aire, conservando `0/U`, `0/alpha.water`, `0/p_rgh`, `constant/transportProperties`, `system/fvSchemes` y `system/fvSolution`.

**Decisión conservadora de inicialización:** `0/alpha.water` prescribe `internalField uniform 0` (el dominio comienza con aire), y `waterInlet` prescribe `value uniform 1` (ingresa agua). **No se añade `setFieldsDict`** porque no hay un volumen inicial de agua que delimitar: hacerlo introduciría una condición física diferente.

Desde la raíz del repositorio:

```bash
cd cases/04-chorro-agua
foamVersion
blockMesh
checkMesh
foamDictionary system/controlDict -entry application -value
interFoam
```

Alternativamente, ejecutar `bash Allrun` desde la carpeta del caso. Este lanzador se detiene si detecta malla previa y conserva los logs. La configuración emplea `deltaT=1e-5` s inicial, `maxCo=0.35`, `maxAlphaCo=0.35` y una escritura cada `0.005` s.

**Advertencia:** la existencia de `controlDict` no garantiza compatibilidad completa de los esquemas de transporte de fracción volumétrica y las condiciones de contorno con la edición de OpenFOAM. Los diccionarios siguen sin validación funcional en v2406/v2412.

Variantes pequeñas: reducir un 20 % la velocidad de `waterInlet`, reducir `maxCo` a 0.25, o cambiar `writeInterval` a 0.01 s. Solo modificar un parámetro por copia del caso.
