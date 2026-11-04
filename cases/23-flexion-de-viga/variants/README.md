# Tres variantes (usar copias separadas)

1. Carga: cambiar solo 0/D, traccion z de -10000 a -5000 Pa; actualizar F en postprocessing/analizar.py.
2. Material: cambiar solo E en constant/mechanicalProperties de 2e9 a 4e9 Pa; actualizar E en el script.
3. Malla: cambiar solo (40 4 4) a (80 4 4) en system/blockMeshDict y regenerar malla.

No combinar cambios en la misma comparación.
