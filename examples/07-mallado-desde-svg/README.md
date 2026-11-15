# Malla de Gmsh para un canal 2D

Ejemplo de importación de una malla externa, no de importación directa de SVG. Canal rectangular de 200 × 20 mm, espesor 1 mm.

## Qué modificar

| Archivo | Entrada | Efecto |
| --- | --- | --- |
| geometry/canal.geo | Point | Dimensiones en metros. |
| geometry/canal.geo | Transfinite Curve | Número de puntos por arista (51 longitudinales, 11 transversales). |
| geometry/canal.geo | Extrude, Layers | Espesor y una capa de celdas. |
| geometry/canal.geo | Physical Surface | Nombres de inlet, outlet, walls y frontAndBack. |
| system/changeDictionaryDict | frontAndBack/type | empty para CFD 2D. |
| 0/U | Entrada | Velocidad del flujo. |

## Ejecutar

Con Gmsh y OpenFOAM disponibles:

```bash
cd examples/07-mallado-desde-svg
bash Allrun
```

La secuencia genera MSH, convierte con gmshToFoam, ajusta patches, ejecuta checkMesh y resuelve. Inspeccionar constant/polyMesh/boundary: si los grupos físicos no coinciden con 0/, corregir la conversión. No aplicar un factor de escala adicional. Sin ejecución comprobada.
