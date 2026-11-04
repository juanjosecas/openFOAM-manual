# Sondas y perfiles opcionales

Este ejemplo añade un **fragmento de función** de OpenFOAM, pero no modifica automáticamente el archivo `controlDict`.

Para habilitarlo, incorporar el contenido de [`probes.function`](probes.function) como una entrada dentro de `functions { ... }` en `system/controlDict`, con el formato y bibliotecas requeridos por la edición instalada. La función `probes` registra `U` y `p` para los puntos seleccionados.

La posición de la primera sonda está antes del obstáculo; comprobar que ninguna cae dentro de la región sólida.

Se recomienda comparar series con `scripts/compare_variants.py` después de exportarlas como CSV. Para obtener perfiles continuos en lugar de puntos de sondeo, usar el muestreo disponible del caso o PyVista sobre los resultados. **Se comprobó la lectura del fragmento con `foamDictionary` de v2406; las sondas no se activaron y no se verificó con v2412.**

Las sondas están en x=50, 120 y 180 mm, a y=10 mm y z=0.5 mm.
Comparar valores puntuales no sustituye promedios de sección. Los registros
de simpleFoam son iteraciones, no tiempos de una trayectoria de partículas.
