# 32-chorro-animado

**Caso transitorio independiente**, derivado de `04-chorro-agua`. El original permanece intacto.

- Solver: `interFoam`.
- Malla: system/blockMeshDict.
- Ejecución: `bash run_docker.sh` desde este directorio, o `bash scripts/run_docker.sh 32-chorro-animado` desde la raíz.
- Solo malla: `bash run_docker.sh --mesh`.
- Limpiar (destructivo): `bash Allclean --yes`.
- Resultados: campos temporales dentro de esta carpeta; abrirlos con ParaView en el host.
- Visualización: usar escala fija para `mag(U)`; extraer isosuperficie alpha.water = 0.5 y animarla.
- Estado: **revisión estática, sin simulación ni validación numérica**. El resultado visual depende de malla, paso temporal y estabilidad.

El `Allrun` genera la malla si falta y luego ejecuta el solver. Para reiniciar desde cero, eliminar los resultados de forma explícita.
