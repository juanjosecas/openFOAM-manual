# Casos científicos

Cada caso incluye sus diccionarios físicos y numéricos, instrucciones y lanzadores. Las variantes cambian solo los archivos necesarios sobre una copia del caso base.

## Flujo de trabajo

Desde la raíz:

```bash
bash scripts/prepare_case.sh --list
bash scripts/prepare_case.sh 14a-difusion-de-farmaco --output runs/difusion
# Editar los diccionarios en runs/difusion antes de calcular.
bash scripts/run_docker.sh runs/difusion
```

Usar `--variant NOMBRE` al preparar si existe una variante con diccionarios. Los scripts de recetas del caso 02 se copian y se aplican antes del mallado; ver su README.

`--mesh` crea la malla sin resolver; `--solve-only` usa una malla existente. Dentro de una copia, `bash Allclean` previsualiza la limpieza y `bash Allclean --yes` borra salidas generadas (no restaura campos de 0/ alterados por setFields). Para ensayos independientes, preferir copias nuevas.

## Archivos comunes

| Ubicación | Qué contiene |
| --- | --- |
| 0/ | Campos iniciales y condiciones de contorno |
| constant/ | Propiedades físicas, gravedad y modelos |
| system/blockMeshDict | Vértices, bloques, resolución y patches |
| system/controlDict | Solver, duración o iteraciones y escritura |
| system/fvSchemes | Discretización |
| system/fvSolution | Algoritmo y tolerancias |
| variants/ | Cambios preparados o recetas |
| Allrun / Allmesh / Allclean | Lanzadores Bash compartidos |

Los casos originales usan los scripts del repositorio; las copias preparadas incluyen los lanzadores necesarios. Las herramientas Python están en [postprocessing/](../postprocessing/README.md). El estado de ejecución se describe en cada caso. No confundir revisión estática, convergencia numérica y validación física.
