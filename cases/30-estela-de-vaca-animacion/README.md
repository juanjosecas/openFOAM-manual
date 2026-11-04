# 30-estela-de-vaca-animacion

**Caso transitorio independiente**, derivado de `cow_incompressible_transient`. El original permanece intacto.

- Solver: `pimpleFoam`.
- Malla: cow_tunnel.msh incluido en este directorio.
- Ejecución: `bash run_docker.sh` desde este directorio, o `bash scripts/run_docker.sh 30-estela-de-vaca-animacion` desde la raíz.
- Solo malla: `bash run_docker.sh --mesh`.
- Limpiar (destructivo): `bash Allclean --yes`.
- Resultados: campos temporales dentro de esta carpeta; abrirlos con ParaView en el host.
- Visualización: usar escala fija para `mag(U)`; mostrar cortes de velocidad y vorticidad; evaluar Q-criterion solo si la geometría lo permite.
- Estado: **revisión estática, sin simulación ni validación numérica**. El resultado visual depende de malla, paso temporal y estabilidad.

El `Allrun` genera la malla si falta y luego ejecuta el solver. Para reiniciar desde cero, eliminar los resultados de forma explícita.
