# Sondas y perfiles opcionales

Este ejemplo añade un **fragmento de función** de OpenFOAM, pero no modifica automáticamente el archivo `controlDict`.

Para habilitarlo, incorporar el contenido de [`probes.function`](probes.function) como una entrada dentro de `functions { ... }` en `system/controlDict`, con el formato y bibliotecas requeridos por la edición instalada. La función `probes` registra `U` y `p` para los puntos seleccionados.

Las sondas se sitúan aguas arriba, en la garganta y aguas abajo; confirmar que los puntos permanecen dentro del fluido.

Se recomienda comparar series con `scripts/compare_variants.py` después de exportarlas como CSV. Para obtener perfiles continuos en lugar de puntos de sondeo, usar el muestreo disponible del caso o PyVista sobre los resultados. **Ninguna configuración opcional se ha ejecutado ni verificado para v2406/v2412.**
