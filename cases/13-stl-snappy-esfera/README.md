# Ejemplo 13: STL a malla OpenFOAM con snappyHexMesh

**Objetivo:** obtener una malla de volumen **externa** alrededor de una esfera triangulada. Este es un caso de **mallado**, no incluye campos `0/U`, `0/p` ni solver CFD. No ejecutar simulación hasta asignar condiciones de contorno correctas.

## Pasos desde la raíz del repositorio

```bash
python -m pip install pyvista numpy
cd cases/13-stl-snappy-esfera
python ../../scripts/preparar_stl.py --output constant/triSurface/sphere.stl
surfaceCheck constant/triSurface/sphere.stl
blockMesh
checkMesh
snappyHexMesh -overwrite
checkMesh
touch mesh.foam
```

Alternativa: ejecutar `bash Allrun` **después de generar el STL**, desde la carpeta del caso. Guarda los logs. El script se detiene si la malla ya existe.

## Sustituir la esfera por un STL propio

1. Guardarlo en `constant/triSurface/` y confirmar las unidades de origen.
2. Convertir su escala si corresponde. Ejemplo: `python ../../scripts/preparar_stl.py --input pieza_mm.stl --units mm --output constant/triSurface/sphere.stl`. La conversión se aplica a las coordenadas: 25 mm se convierten en 0.025 m.
3. Si se conserva el nombre `sphere.stl`, no es necesario modificar la clave `geometry`; el nombre de patch `sphere` representa ahora el objeto importado. Para más claridad, se recomienda renombrar archivo y entrada de geometría conjuntamente.
4. Redimensionar la caja de `system/blockMeshDict` para que contenga el sólido **y el fluido**, con margen. Adaptar las celdas según la escala.
5. Colocar `locationInMesh` **dentro de la región de fluido que se desea conservar**, nunca dentro del STL sólido, sobre su superficie ni fuera de la malla de fondo.
6. Comprobar topología con `surfaceCheck`, ejecutar `blockMesh`, `snappyHexMesh -overwrite` y finalmente `checkMesh`. Si la geometría está abierta o presenta caras inconsistentes, repararla previamente.

Para un flujo **interno** (un tubo, por ejemplo) la caja, el punto de conservación y las superficies de cierre requieren otra configuración; no reutilizar este ejemplo externo sin adaptarlo.

## Modificaciones pequeñas

- Cambiar las subdivisiones de la caja de (24 24 24) a (32 32 32); no modificar sus dimensiones físicas.
- Cambiar `refinementSurfaces/sphere/level` de `(1 2)` a `(2 2)` para aproximar mejor la esfera.
- Cambiar el radio de la esfera de demostración de 0.5 a 0.4 m, regenerando el STL y la malla en una copia nueva.

## Interpretación de la escala

STL guarda triángulos **sin unidades**. Si el archivo fue exportado en milímetros y se interpreta como metros, el objeto será 1000 veces mayor de lo esperado. El `scale` de `blockMeshDict` **solo afecta a la malla de fondo**; no reescala automáticamente `sphere.stl`. El ejemplo genera un STL directamente en metros.

`snappyHexMesh` necesita una malla base: no se limita a convertir un STL a `polyMesh`. La superficie STL representa límites geométricos, mientras que las celdas volumétricas de la región fluida se obtienen del refinamiento de `blockMesh`.

**Estado:** revisión documental, sin ejecución comprobada en OpenFOAM.com v2406/v2412.
