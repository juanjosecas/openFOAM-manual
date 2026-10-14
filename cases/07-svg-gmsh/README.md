# Tutorial 07 — Importación de Gmsh a OpenFOAM

**Estado:** variante de referencia documentada, no ejecutada. La geometría SVG original **no está disponible** y no se simuló su recuperación.

## Caso alternativo: canal rectangular

Desde la raíz del repositorio:

```bash
python -m pip install gmsh
cd cases/07-svg-gmsh
python ../../scripts/generar_canal_gmsh.py
gmshToFoam geometry/canal.msh
python ../../scripts/ajustar_patches_gmsh.py
checkMesh
foamDictionary system/controlDict -entry application -value
simpleFoam
```

También existe `bash Allrun` que genera geometría y recoge logs, y se detiene si ya hay una malla.

El generador usa coordenadas directamente en **metros**, con geometría de 0.20 × 0.02 × 0.001 m, una celda de espesor y patches `inlet`, `outlet`, `walls` y `frontAndBack`. El conversor `gmshToFoam` puede variar en la nomenclatura de patches según versión: inspeccionar `constant/polyMesh/boundary` antes del solver. `frontAndBack` debe ser `empty` para el modelo 2D.

**Limitación:** no se ha comprobado el comportamiento real de la malla Gmsh con OpenFOAM.com v2406/v2412. El ejemplo SVG original sigue pendiente de su archivo fuente.

[Procedimiento y decisiones](COMPLETADO.md) · [Tutorial conceptual de SVG/Gmsh](../../docs/tutoriales/07-svg-gmsh.md)

## Ensayos pequeños

Cambiar densidad de malla Gmsh, reducir 20 % velocidad de entrada, o variar frecuencia de escritura de iteraciones. `simpleFoam` es estacionario.
