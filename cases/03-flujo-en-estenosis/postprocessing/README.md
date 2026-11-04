# Sondas y perfiles opcionales

Este ejemplo añade un **fragmento de función** de OpenFOAM, pero no modifica automáticamente el archivo `controlDict`.

Para habilitarlo, incorporar el contenido de [`probes.function`](probes.function) como una entrada dentro de `functions { ... }` en `system/controlDict`, con el formato y bibliotecas requeridos por la edición instalada. La función `probes` registra `U` y `p` para los puntos seleccionados.

Las sondas se sitúan aguas arriba, en la garganta y aguas abajo; confirmar que los puntos permanecen dentro del fluido.

En esta geometría, los puntos están en x=20, 50 y 80 µm, sobre el eje y=5 µm,
a mitad del espesor de malla (z=0.5 µm). Son puntos fijos: no siguen células ni
partículas. Sus diferencias de presión son diferencias puntuales, no promedios
de sección ni una medida directa de perfusión. Con `simpleFoam`, los registros
corresponden a iteraciones de convergencia, no a latidos o tiempos de tránsito.
`p` es presión cinemática; para convertir diferencias a Pa hace falta una
densidad elegida y justificada. El fragmento permanece opcional e inactivo.

Se recomienda comparar series con `scripts/compare_variants.py` después de exportarlas como CSV. Para obtener perfiles continuos en lugar de puntos de sondeo, usar el muestreo disponible del caso o PyVista sobre los resultados. **Se comprobó la lectura del fragmento con `foamDictionary` de v2406; no se activó ni ejecutó el objeto de sondas y no se verificó con v2412.**
