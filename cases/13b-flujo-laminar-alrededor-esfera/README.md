# 13B · Agua alrededor de una esfera: flujo laminar estacionario

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

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 13b-flujo-laminar-alrededor-esfera --output runs/sphere
bash scripts/run_docker.sh runs/sphere
```

La configuración actual usa searchableSphere en snappyHexMeshDict; no requiere STL. La ejecución anterior con STL se conserva como antecedente, no como validación del caso actualizado.

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

## Postprocesamiento

```bash
python postprocessing/sphere.py runs/sphere --diameter 1 --nu 1e-6
python postprocessing/fields.py runs/sphere --field U --normal z --streamlines
python postprocessing/fields.py runs/sphere --field strain --normal z
python postprocessing/fields.py runs/sphere --field U --normal z --edges
python postprocessing/plot_solver_log.py runs/sphere/log.simpleFoam
```

sphere.py conserva los perfiles axial y transversal, Cp de superficie y parámetros de referencia. Usa promedios de inlet/outlet y bandas angulares ponderados por área, presión cinemática y dimensiones explícitas. No calcula arrastre. La galería histórica PNG/PDF/HTML se retiró; los gráficos generales se generan cuando se necesitan. No se requiere el campo V. Las herramientas nuevas no se han ejecutado.

## Criterios de extensión del modelo

Se conservaron los diccionarios de la ejecución histórica. El dominio tiene relación ancho/diámetro=4 y bloqueo frontal geométrico pi/64≈4.9%; el arrastre no equivale al de una esfera en dominio ilimitado. Re=10 tampoco corresponde al límite asintótico de Stokes (Cd=24/Re). Antes de usar fuerzas cuantitativas, comparar sensibilidad a tamaño de dominio y refinamiento cerca de la esfera, y separar contribuciones de presión y viscosidad. La verificación histórica no cubre el nuevo lanzador Bash. No se repitió la ejecución.

