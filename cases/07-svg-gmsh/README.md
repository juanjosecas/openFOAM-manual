# Tutorial 07 — Geometrías SVG y Gmsh

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/p`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `system/controlDict`
- `system/fvSchemes`
- `system/fvSolution`

**Advertencia:** requiere comprobar migración desde versiones anteriores y cualquier preprocesamiento adicional antes de ejecutar.

## Ejecución

Este caso no dispone todavía de un lanzador verificado. Consultar los pasos de preparación del tutorial.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/07-svg-gmsh
foamVersion
# PENDIENTE: recuperar SVG y geometry/svg_to_gmsh.py
# python geometry/svg_to_gmsh.py
# gmshToFoam dominio.msh
# python geometry/ajustar_patches.py
# checkMesh
# simpleFoam
```

**Estado:** No ejecutar todavía: faltan el SVG y los scripts de conversión y patches. No hay un `Allrun` verificado para este caso.

## Variaciones pequeñas

Cambiar resolución de Gmsh; variar velocidad de entrada 20%; variar writeInterval tras recuperar SVG y scripts.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).
