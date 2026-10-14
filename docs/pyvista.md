# Postprocesamiento con PyVista

[PyVista](https://docs.pyvista.org/getting-started/) es una interfaz Python para VTK que permite crear figuras reproducibles, inspeccionar campos y guardar animaciones. Su lector `OpenFOAMReader` admite directamente un archivo `.foam` y las carpetas de tiempo o iteración; **no es necesario convertir previamente a VTK**. <https://docs.pyvista.org/api/readers/_autosummary/pyvista.openfoamreader>

## Instalación

En un entorno virtual de Python distinto del entorno CFD, si corresponde:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pyvista numpy matplotlib imageio
```

En servidores sin pantalla puede ser necesario instalar bibliotecas OpenGL/Xvfb o usar un entorno gráfico adecuado para renderizar. Estos comandos no ejecutan OpenFOAM.

## Uso con cualquier caso del manual

En la raíz del repositorio, después de disponer de resultados reales:

```bash
touch cases/08-tuberia-cilindrica-3d/tuberia.foam
python scripts/pyvista_openfoam.py cases/08-tuberia-cilindrica-3d/tuberia.foam \
  --output plots/08-pyvista
```

Produce una imagen PNG de **magnitud de velocidad** en un corte central. También puede utilizarse `--time-index 0` para elegir un estado. El script inspecciona el campo `U`, convierte velocidades de celda a puntos cuando es necesario y detecta el bloque interno de la malla.

### Animación

```bash
python scripts/pyvista_openfoam.py cases/08-tuberia-cilindrica-3d/tuberia.foam \
  --output plots/08-pyvista --gif --fps 15
```

Produce un GIF de los estados disponibles y utiliza **una escala de color constante** para que las diferencias entre fotogramas sean comparables. Un GIF puede resultar grande; reducir el número de estados guardados o convertirlo posteriormente a MP4 con `ffmpeg`.

**Importante:** en los tutoriales basados en `simpleFoam`, los estados corresponden a *iteraciones*, no a instantes físicos. Un GIF de ese solver representa evolución hacia una solución estacionaria, **no movimiento real del fluido**.

## Ejemplo Python básico

```python
import pyvista as pv

reader = pv.OpenFOAMReader("cases/08-tuberia-cilindrica-3d/tuberia.foam")
print("Tiempos disponibles:", reader.time_values)
reader.set_active_time_value(reader.time_values[-1])
blocks = reader.read()
print(blocks)  # Multiblock con malla interna y patches
```

En OpenFOAM, el resultado puede ser un `MultiBlock`, no una única malla. Es necesario identificar `internalMesh` antes de aplicar `slice`, `glyph` o `streamlines`. Además, `U` puede residir en `cell_data` y requerir `cell_data_to_point_data()`.

## Otros gráficos útiles

- **Campos:** `grid.slice(normal="z").plot(scalars="p")` para presión en un plano, cuando el campo está disponible.
- **Vectores:** `grid.glyph(orient="U", scale="U", factor=0.1)`, idealmente después de reducir densidad espacial para evitar miles de flechas.
- **Perfiles:** `grid.sample_over_line(pointa, pointb, resolution=100)`, seguido de Matplotlib para graficar componentes o magnitudes.
- **Líneas de corriente:** `grid.streamlines(vectors="U", n_points=100)`, tras asegurar que `U` esté definido en puntos.
- **Animaciones:** `Plotter.open_gif()` y `Plotter.write_frame()`.

Para exportar SVG/PDF desde una escena configurada, consultar `Plotter.save_graphic()`. Algunas geometrías se rasterizan durante la exportación.

## Selección de variables por tutorial

| Tutorial | Variables sugeridas |
| --- | --- |
| 01–03, 07 y 10C | `U`, `p` y perfiles espaciales; estados de `simpleFoam` no son tiempo físico |
| 04 y 11 | `alpha.water`, `U` y `p_rgh` |
| 08, 09 y 10A–10B | `U`, `p` y animaciones temporales |
| 12 | `U.air` y datos lagrangianos, si el lector y la configuración permiten acceder a ellos |

El script incluido requiere `U`: no se aplica directamente al caso 12, cuyo campo está denominado `U.air`. Los casos 04, 07 y 12 tienen además limitaciones estructurales o de compatibilidad documentadas.

## Referencias oficiales

- [Introducción](https://docs.pyvista.org/getting-started/)
- [OpenFOAMReader](https://docs.pyvista.org/api/readers/_autosummary/pyvista.openfoamreader)
- [Selección de tiempos](https://docs.pyvista.org/api/readers/_autosummary/pyvista.openfoamreader.set_active_time_value)
- [Animaciones GIF](https://docs.pyvista.org/examples/02-plot/gif)
