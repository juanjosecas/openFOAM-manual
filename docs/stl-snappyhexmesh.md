# Tutorial 13 — De STL a malla OpenFOAM

Este tutorial incorpora una **malla de volumen** construida a partir de una superficie STL mediante `snappyHexMesh`. El procedimiento no resuelve todavía Navier–Stokes: enseña a preparar geometría, elegir escala, crear la malla de fondo, adaptar celdas a la superficie y comprobar calidad.

**Caso completo de mallado:** [`cases/13-stl-snappy-esfera/`](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/13-stl-snappy-esfera).

## Lo que ya había en el manual

Los tutoriales 01–04 y 08–12 usan principalmente `blockMesh`. El 07 introduce la importación SVG → Gmsh → `gmshToFoam`, pero no hay en el repositorio previo un procedimiento autocontenido con STL y `snappyHexMesh`. Son flujos distintos:

- **STL:** superficie de triángulos; no contiene celdas volumétricas ni unidades.
- **`snappyHexMesh`:** refina y ajusta una malla de fondo a la superficie del STL.
- **`gmshToFoam`:** importa una malla de volumen creada por Gmsh en formato compatible; no convierte por sí solo una superficie STL en un volumen discretizado.

## 1. Comprobar unidades y escala

STL no declara metros, milímetros ni centímetros. Por ejemplo, una esfera dibujada con radio numérico `25` podría representar 25 mm o 25 m según el programa CAD. Para llevar coordenadas a metros:

| Unidad del STL | Factor |
| --- | ---: |
| metro | 1 |
| centímetro | 0.01 |
| milímetro | 0.001 |

La conversión es $x_{m}=s\,x_{STL}$ y también se aplica a las otras coordenadas. **No basta** con cambiar `scale` en `blockMeshDict`: eso escala las coordenadas de la malla base, no la superficie STL importada. Comprobar las dimensiones físicas de ambas.

Ejemplo de STL en milímetros:

```bash
cd cases/13-stl-snappy-esfera
python ../../scripts/preparar_stl.py --input pieza_mm.stl \
  --units mm --output constant/triSurface/sphere.stl
```

El script imprime los límites geométricos **ya expresados en metros**. Utiliza PyVista para leer STL ASCII o binario.

## 2. Crear la superficie de prueba

Para reproducir el ejemplo sin CAD ni archivos externos:

```bash
cd cases/13-stl-snappy-esfera
python -m pip install pyvista numpy
python ../../scripts/preparar_stl.py \
  --radius 0.5 --output constant/triSurface/sphere.stl
```

La esfera tendrá centro $(0,0,0)$ y radio $0.5$ m. La caja creada con `blockMesh` se extiende entre $-2$ y $2$ m en los tres ejes.

## 3. Inspeccionar la superficie

```bash
surfaceCheck constant/triSurface/sphere.stl
```

Inspeccionar bordes abiertos, orientación de normales, intersecciones y extensión geométrica. Una superficie abierta o autointersecada puede impedir identificar correctamente interior y exterior. La advertencia no debe ignorarse solo porque se haya generado un STL.

## 4. Generar la malla de fondo

```bash
blockMesh
checkMesh
```

El archivo [`system/blockMeshDict`](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/13-stl-snappy-esfera/system/blockMeshDict) define una caja con $(24,24,24)$ celdas base. Es importante que la caja **contenga completamente la esfera** y deje espacio para el flujo exterior.

## 5. Ajustar y refinar cerca de la superficie

```bash
snappyHexMesh -overwrite
checkMesh
```

En [`system/snappyHexMeshDict`](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/13-stl-snappy-esfera/system/snappyHexMeshDict):

- `castellatedMesh true` recorta/refina las celdas próximas a la superficie.
- `snap true` ajusta puntos a los triángulos del STL.
- `addLayers false` omite inicialmente las capas límite.
- `refinementSurfaces` configura el refinamiento local del sólido.
- `locationInMesh (1.5 0 0)` conserva la **región fluida externa**: el punto está dentro de la caja, pero fuera de la esfera.

El `locationInMesh` debe reubicarse si se cambia sustancialmente la geometría. Si queda dentro del sólido, sobre la superficie o fuera de la malla, la selección de celdas será incorrecta.

`-overwrite` reemplaza la malla de fondo por la malla resultante. Si se desea preservar el estado previo, copiar el caso antes del mallado. No repetir `snappyHexMesh -overwrite` sobre una malla ya refinada sin volver a generar la malla base.

## 6. Ver la malla

```bash
touch mesh.foam
```

Abrir `mesh.foam` con ParaView; seleccionar `Surface With Edges`, `Slice` o `Extract Surface` para inspeccionar el refinamiento. También puede leerse mediante `pyvista.OpenFOAMReader` para inspección programática (ver [PyVista](pyvista.md)).

## 7. Variantes sin alterar el objetivo del caso

Probar en copias separadas: malla de fondo $(32,32,32)$, refinamiento superficial `level (2 2)`, o esfera de radio $0.4$ m. Registrar calidad de `checkMesh`, número de celdas y tiempo de mallado. El resultado correcto para una esfera externa es una malla **fuera del sólido**, no un relleno de su interior.

## 8. Errores frecuentes y límites

- **Escala 1000 veces incorrecta:** el STL venía en mm y se interpretó en m.
- **`locationInMesh` dentro del sólido:** se conservó una región equivocada.
- **STL abierto, normales inconsistentes o geometrías que se intersecan:** reparar el modelo antes de confiar en la malla.
- **Malla base demasiado pequeña o demasiado gruesa:** cambiar `blockMeshDict` y volver a empezar el mallado.
- **Flujo interno:** requiere configurar el volumen fluido y puntos de conservación apropiados; este caso es de **flujo externo**.
- **Conversión desde ANSA/Gmsh:** si se dispone de una malla volumétrica en formato importable, utilizar la utilidad de conversión apropiada (`gmshToFoam`, `fluentMeshToFoam`, etc.), en vez de usar el STL como sustituto de una malla de volumen.

**Estado:** caso y documentación preparados, no ejecutados con OpenFOAM.com v2406/v2412.

## Referencias

- [Guía oficial de snappyHexMesh](https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.4-mesh-generation-with-the-snappyhexmesh-utility).
- [Conversión de mallas en OpenFOAM](https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion/4.5-mesh-conversion).
- [CFD Online: from STL to OpenFOAM mesh](https://www.cfd-online.com/Forums/ansa/221052-stl-openfoam-mesh.html).
- [Stack Overflow: tutorial snappyHexMesh STL](https://stackoverflow.com/questions/47364089/tutorial-for-using-snappyhexmesh-with-a-stl-file-in-openfoam).
- [Damogran Labs: fondo, refinamiento, scripts](https://damogranlabs.com/2018/05/openfoam-meshing-shortcuts/).
