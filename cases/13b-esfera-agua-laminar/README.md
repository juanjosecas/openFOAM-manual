# 13B · Agua alrededor de una esfera STL: flujo laminar estacionario

Continuación del caso de mallado `13-stl-snappy-esfera`. Se conserva el caso
original y se añaden campos y condiciones de contorno compatibles con
OpenFOAM.com v2406. El dominio está completamente lleno de agua: no hay aire,
interfaz ni `alpha.water`.

## Configuración física y numérica

- Esfera de radio 0,5 m y diámetro 1 m, centrada en el origen.
- Caja de fondo: [-2, 2] m en los tres ejes; 24 × 24 × 24 celdas base.
- Entrada en x = -2 m: U = (1e-5, 0, 0) m/s.
- Salida en x = 2 m: presión cinemática relativa p = 0 m²/s².
- Laterales: `slip` (velocidad normal nula, sin esfuerzo tangencial).
- Esfera: `noSlip`.
- Agua newtoniana idealizada, viscosidad cinemática nu = 1e-6 m²/s.
- Reynolds basado en diámetro: U D / nu = 10.
- `simpleFoam`, estado estacionario, modelo `laminar`.
- Máximo de 1500 iteraciones; criterios SIMPLE: p < 1e-6, U < 1e-7.
- Escritura cada 100 iteraciones, conservando dos escrituras; OpenFOAM
  también escribe la solución al detectar convergencia.

`p` es presión cinemática: para una diferencia de presión en Pa, multiplicar
la diferencia de p por la densidad elegida para el agua. Los directorios
numéricos representan iteraciones, no segundos físicos.

## Parámetros comentados y variantes

Los diccionarios incluyen comentarios sobre unidades, significado de las
entradas y cambios numéricos coordinados. Los valores activos del caso base
se conservan. Consultar [variantes numéricas](variants/README.md) para ensayos
de Reynolds, viscosidad, resolución, confinamiento y convergencia. Los ejemplos
propuestos todavía no se han ejecutado como un estudio paramétrico.

## Ejecución

Trabajar en una copia nueva dentro de `runs/`. Desde la raíz del repositorio:

1. Copiar esta carpeta al directorio de ejecución.
2. Generar el STL con el Python del notebook:
   `python scripts/preparar_stl.py --radius 0.5 --output RUTA_CASO/constant/triSurface/sphere.stl`.
3. En el directorio del caso, con OpenFOAM cargado: `bash Allrun`.

En el notebook, ejecutar por separado mediante `scripts.foam_docker.foam_run`:

```text
surfaceCheck constant/triSurface/sphere.stl
blockMesh
checkMesh
snappyHexMesh -overwrite
checkMesh
simpleFoam
```

No combinar esta secuencia con `Allrun` en la misma copia. Crear `esfera-agua.foam`
para leer los resultados con PyVista. No se necesita `setFields`.

## Validación realizada

El 2026-10-22, en Docker `opencfd/openfoam-run:2406`, se ejecutó la secuencia
completa en una copia temporal con el STL de esfera de 4416 triángulos generado
previamente por `preparar_stl.py`. Ambas comprobaciones de malla confirmaron
`Mesh OK.` y SIMPLE alcanzó los criterios de convergencia en 171 iteraciones.

Es una verificación de ejecución y convergencia numérica, no una validación
física. La caja es pequeña para representar una esfera en un medio ilimitado,
los laterales slip producen confinamiento y no se han añadido capas prismáticas.
Comparar dominio, refinamiento y resultados antes de usar fuerzas o gradientes
de pared con fines cuantitativos.

## Galería de resultados desde el notebook

Instalar `pyvista`, `numpy` y `matplotlib`; `plotly` habilita los HTML 3D.
La función no usa un renderer OpenGL ni necesita ParaView. Se utiliza el último
resultado guardado y se infiere U_inf del patch inlet. El centro debe ser el
origen y el flujo paralelo a +x.

```python
from scripts.foam_docker import foam_run
from scripts.graficos_esfera import graficar_esfera

# Volúmenes calculados por OpenFOAM: evita inconsistencias de VTK en celdas wedge.
foam_run(["postProcess", "-func", "writeCellVolumes", "-latestTime"],
         case_dir=CASE_DIR, repo_dir=REPO_DIR, timeout=120, verbose=False)

graficos = graficar_esfera(CASE_DIR, diametro=1.0, nu=1e-6, rho=1000.0,
                           mostrar=True, interactivo=True)
```

Genera 11 figuras PNG/PDF, 3 tablas CSV, 2 HTML 3D y un índice HTML, en una
carpeta única dentro de `CASE_DIR/plots/`. Guarda también parámetros en JSON.
`rho=1000 kg/m³` es una densidad elegida para convertir diferencias de presión
a Pa; no se utiliza en el solver incomprensible. Mantener `nu` y `diametro`
coherentes con el caso. El interior sólido se enmascara; aumentar `resolucion`
solo aumenta la densidad del muestreo gráfico. Las derivadas son aproximaciones
posprocesadas y no sustituyen los diagnósticos de continuidad del solver.

Validación de la galería: generación completa con los resultados de iteración
171 y comprobación de exportaciones PNG/PDF/CSV/HTML, sin ejecutar de nuevo CFD.
