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
