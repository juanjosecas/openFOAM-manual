# Variantes del mallado STL

Cambiar un parámetro por vez, sobre una **copia limpia** y regenerando siempre la malla de fondo:

1. **Resolución base:** pasar de (24 24 24) a (32 32 32) en `system/blockMeshDict`.
2. **Refinamiento superficial:** cambiar `level (1 2)` por `level (2 2)` en `system/snappyHexMeshDict`.
3. **Dimensión del objeto:** generar una nueva esfera de radio 0.4 m mediante `scripts/preparar_stl.py`.

La malla sigue representando el fluido exterior. Comprobar `surfaceCheck`, `locationInMesh` y `checkMesh`; los cambios de escala pueden requerir recalcular todos los límites de dominio.
