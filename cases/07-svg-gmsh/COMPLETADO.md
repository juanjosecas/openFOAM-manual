# Tutorial 07 — Caso de referencia Gmsh para flujo en canal 2D

El SVG histórico y los scripts originales no están disponibles. **No se reconstruyó de forma arbitraria esa geometría**: se añadió una variante de referencia independiente y paramétrica, un canal rectangular de 0.20 × 0.02 × 0.001 m mallado por Gmsh (una celda de espesor).

Este ejemplo **no demuestra importación desde SVG**, sino el flujo completo de una malla Gmsh a OpenFOAM. El tutorial de SVG original permanece como explicación pendiente de un archivo fuente.

```bash
# Desde la raíz del repositorio:
python -m pip install gmsh
cd cases/07-svg-gmsh
python ../../scripts/generar_canal_gmsh.py
gmshToFoam geometry/canal.msh
python ../../scripts/ajustar_patches_gmsh.py
checkMesh
foamDictionary system/controlDict -entry application -value
simpleFoam
```

Como alternativa, desde el caso puede utilizarse `bash Allrun` que recopila logs y se detiene si existe una malla anterior. Los scripts de geometría están en `scripts/` (raíz del repositorio).

**Unidades:** las coordenadas de Gmsh están introducidas directamente en metros. No se debe aplicar otro factor 0.001 al convertir la malla. Como STL, el formato .msh no asegura que las coordenadas hayan sido dibujadas originalmente con las unidades pretendidas: revisar las dimensiones físicas.

**Comprobación de patches:** la geometría produce `inlet`, `outlet`, `walls`, `frontAndBack` y un volumen `fluid`. El segundo script intenta convertir `frontAndBack` al tipo `empty` necesario para el cálculo 2D y se detiene si encuentra más de uno o ninguno.

**Límite:** sin ejecución real no se puede garantizar cómo `gmshToFoam` preservará los Physical Groups de la versión instalada. Si los patches se convierten en nombres diferentes, detenerse y corregir el procedimiento **sin renombrar arbitrariamente campos en 0/**. La validación física y numérica sigue pendiente.
