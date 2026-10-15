# Manual práctico de OpenFOAM

Tutoriales reproducibles de dinámica de fluidos computacional (CFD) **en español**, centrados en **OpenFOAM.com v2406**. Las diferencias con v2412 u otras versiones se registrarán únicamente si se comprueban.

El objetivo es construir geometrías sin software CAD externo, ejecutar **simulaciones transitorias** sencillas y producir representaciones de campos, vectores y animaciones. Los parámetros iniciales sirven para **prototipado visual** y no implican validación numérica.

## Estructura del repositorio

- `docs/`: capítulos teóricos, explicaciones y tutoriales en Markdown.
- `cases/`: casos OpenFOAM autocontenidos, con `0/`, `constant/`, `system/` y scripts de ejecución.
- `scripts/`: generación de geometrías, exportaciones y postprocesamiento.
- `assets/`: figuras ligeras y esquemas.
- `references/`: fuentes y procedencia de los casos heredados.

**Portal y tabla de contenidos:** [abrir el índice maestro](docs/index.md).

Leer las [convenciones editoriales y técnicas](docs/estructura-y-estilo.md).

## Estado de los tutoriales

Cada caso debe declarar su versión de OpenFOAM, solver, estado de revisión, fecha de prueba y limitaciones. **Revisión estática no equivale a ejecución ni a validación física**.

La migración de los tutoriales existentes se realizará de manera progresiva sin modificar silenciosamente los datos originales.

## Referencias oficiales

- [Código fuente de OpenFOAM](https://gitlab.com/openfoam/core/openfoam).
- [Estructura de casos](https://www.openfoam.com/documentation/user-guide/2-openfoam-cases/2.1-file-structure-of-openfoam-cases).
- [Formato de archivos y diccionarios](https://www.openfoam.com/documentation/user-guide/2-openfoam-cases/2-2-basic-inputoutput-file-format).


## Extensiones opcionales

Los casos contienen scripts `Allmesh` y `Allclean` cuando usan `blockMesh`, y varias carpetas `variants/` y `postprocessing/` para ampliar los ejemplos sin modificar el original. Consultar [el portal de contenidos](docs/index.md#archivos-opcionales-y-ampliaciones).


## Investigación de nuevas aplicaciones

Se incorporó un [catálogo de tutoriales externos con sus URLs originales](docs/investigacion-fuentes-openfoam.md), una [propuesta biofísica de difusión y liberación de fármacos](docs/propuesta-difusion-farmacos.md) y una [hoja de ruta de futuros casos](docs/investigacion-hoja-de-ruta.md). Son referencias y proyectos **no implementados ni validados**; no se han copiado ni ejecutado casos externos.


## Nuevos ejemplos mínimos de sólidos y calor

- [23: flexión estática de viga 3D](cases/23-flexion-viga/README.md), solidDisplacementFoam.
- [24: conducción térmica estacionaria 1D](cases/24-conduccion-1d/README.md), laplacianFoam.
- [Otras fuentes: radiación, convección y tensiones térmicas](docs/ejemplos-calor-radiacion-solidos.md).

Ambos casos tienen estructura autocontenida y postprocesamiento; **solo revisión estática, sin ejecución ni validación**.


## Modelo óptico 2D/3D (sin CFD)

- [25: refracción de rayos en una interfaz aire–agua](cases/25-refraccion-luz/README.md): ley de Snell, reflexión interna total, CSV, PNG, GIF y variantes. Modelo Python autocontenido, sin OpenFOAM; **no ejecutado ni validado**.


## Refracción con OpenFOAM

- [26: superficie libre calculada con interFoam y rayos refractados](cases/26-refraccion-interfoam/README.md). CFD agua–aire 2D con postprocesamiento óptico 2D/3D, CSV, PNG y GIF temporal. **Revisión estática; sin ejecutar.**
