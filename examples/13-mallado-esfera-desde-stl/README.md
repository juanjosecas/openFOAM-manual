# Mallado externo de una superficie STL

Generar una malla volumétrica alrededor de un sólido triangulado con blockMesh y snappyHexMesh. No incluye simulación de flujo; para ello usar [el caso de esfera](../../cases/13b-flujo-laminar-alrededor-esfera/README.md).

## Qué modificar

| Archivo | Entrada | Efecto |
| --- | --- | --- |
| geometry/sphere.geo | Sphere | Centro y radio de demostración. |
| geometry/sphere.geo | MeshSizeMin, MeshSizeMax | Resolución de triangulación STL. |
| system/blockMeshDict | vertices, blocks | Caja de fondo y resolución. |
| system/snappyHexMeshDict | geometry | STL y nombre de patch. |
| system/snappyHexMeshDict | refinementSurfaces/sphere/level | Refinamiento local; probar (2 2). |
| system/snappyHexMeshDict | locationInMesh | Punto en el fluido que se desea conservar. |

## Ejecutar

Con Gmsh y OpenFOAM disponibles:

```bash
cd examples/13-mallado-esfera-desde-stl
bash Allmesh
```

Para usar un STL propio, guardarlo como constant/triSurface/sphere.stl; si cambia el nombre, actualizar geometry y refinamientos. STL no tiene unidades: si está en milímetros, convertir a metros antes de mallar. El scale de blockMeshDict no escala el STL. Ajustar caja y locationInMesh, comprobar superficie cerrada con surfaceCheck y malla final con checkMesh. Existió una ejecución satisfactoria con el STL anterior; la generación actual con Gmsh no fue probada.
