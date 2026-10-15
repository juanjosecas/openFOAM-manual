# Manual práctico de OpenFOAM

Portal de contenidos del repositorio [openFOAM-manual](https://github.com/juanjosecas/openFOAM-manual). El manual está escrito en español y toma como referencia principal **OpenFOAM.com v2406**. Los casos de otras versiones se identifican como heredados y no se consideran automáticamente compatibles.

> **Importante:** las instrucciones y scripts son material didáctico. Los casos no han sido validados mediante ejecución en esta revisión. Algunos están incompletos; consultar las advertencias de cada uno antes de utilizarlos.

## Cómo empezar

1. [Estructura del repositorio y convenciones editoriales](estructura-y-estilo.md): archivos `0/`, `constant/`, `system/`, unidades y comentarios.
2. [Ejecución y pequeñas variantes por caso](guia-ejecucion-y-variantes.md): preparación, malla, preprocesamiento y solver.
3. [Gráficos y propiedades físicas](graficos-y-propiedades.md): perfiles, residuos, campos y diagnóstico.
4. [Propiedades de materiales](propiedades-de-materiales.md): tablas rápidas de sólidos, líquidos y gases; viscosidad, densidad, calor específico, conductividad y difusividades.
5. [PyVista](pyvista.md): lectura de resultados, cortes, vectores y animaciones.
6. [STL y snappyHexMesh](stl-snappyhexmesh.md): escalas, superficies STL y generación de mallas volumétricas.

## Tutoriales de simulación

| Tutorial | Tema y documentación | Archivos del caso | Estado |
| --- | --- | --- | --- |
| 01 | [Canal 2D no newtoniano](tutoriales/01-canal-no-newtoniano.md) | [Caso 01](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/01-canal-no-newtoniano) | Configuración disponible; `simpleFoam` estacionario |
| 02 | [Canal con obstáculos](tutoriales/02-canal-obstaculos.md) | [Caso 02](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/02-canal-obstaculos) | Configuración disponible; `simpleFoam` estacionario |
| 03 | [Estenosis capilar](tutoriales/03-estenosis-capilar.md) | [Caso 03](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/03-estenosis-capilar) | Configuración disponible; `simpleFoam` estacionario |
| 04 | [Chorro de agua](tutoriales/04-chorro-agua.md) | [Caso 04](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/04-chorro-agua) | Control temporal reconstruido; pendiente de validación |
| 05 | [Esfera en agua](tutoriales/05-esfera-agua.md) | — | Conceptual: no existe un caso autónomo completo |
| 06 | [Automatización con foamlib](tutoriales/06-foamlib.md) | — | Guía Python; no es un caso CFD independiente |
| 07 | [Geometrías SVG/Gmsh](tutoriales/07-svg-gmsh.md) | [Caso 07](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/07-svg-gmsh) | Alternativa Gmsh disponible; SVG original pendiente |
| 08 | [Tubería cilíndrica 3D transitoria](tutoriales/08-tuberia-cilindrica-3d.md) | [Caso 08](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/08-tuberia-cilindrica-3d) | `pimpleFoam`; revisión documental |
| 09 | [Cavidad 2D con tapa móvil](tutoriales/09-cavity-2d.md) | [Caso 09](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/09-cavity-2d) | Heredado de Foundation; `icoFoam` |
| 10A | [Tubería laminar, variante 0](tutoriales/10a-tuberia-laminar-case0.md) | [Caso 10A](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/10a-tuberia-laminar-case0) | Heredado; `icoFoam` |
| 10B | [Tubería laminar, variante 1](tutoriales/10b-tuberia-laminar-case1.md) | [Caso 10B](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/10b-tuberia-laminar-case1) | Heredado; `icoFoam` |
| 10C | [Tubería laminar, variante 2](tutoriales/10c-tuberia-laminar-case2.md) | [Caso 10C](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/10c-tuberia-laminar-case2) | Heredado; `simpleFoam` estacionario |
| 11 | [Rotura de presa 2D](tutoriales/11-dambreak-2d.md) | [Caso 11](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/11-dambreak-2d) | Heredado; requiere `setFields` |
| 12 | [Goldschmidt: partículas](tutoriales/12-goldschmidt-particulas.md) | [Caso 12](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/12-goldschmidt-particulas) | Heredado de Foundation 8; migración pendiente |
| 13 | [STL → snappyHexMesh](stl-snappyhexmesh.md) | [Caso 13](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/13-stl-snappy-esfera) | Generación de malla, no incluye solver CFD |

## Postprocesamiento y visualización

| Recurso | Uso |
| --- | --- |
| [Exportación a VTK, CSV y otros programas](tutoriales/01-anexo-exportacion.md) | Preparación de resultados para aplicaciones externas |
| [PyVista](pyvista.md) | Lectura directa de `.foam`, cortes, vectores y GIF |
| [Gráficos de propiedades](graficos-y-propiedades.md) | Comparación de perfiles y diagnósticos |
| [`plot_csv.py`](https://github.com/juanjosecas/openFOAM-manual/blob/main/scripts/plot_csv.py) | Gráficos de columnas exportadas a CSV |
| [`plot_solver_log.py`](https://github.com/juanjosecas/openFOAM-manual/blob/main/scripts/plot_solver_log.py) | Residuos y número de Courant |
| [`pyvista_openfoam.py`](https://github.com/juanjosecas/openFOAM-manual/blob/main/scripts/pyvista_openfoam.py) | Capturas PNG y GIF desde datos de OpenFOAM |

## Geometría y preparación

| Recurso | Uso |
| --- | --- |
| [STL y snappyHexMesh](stl-snappyhexmesh.md) | Importar STL, revisar unidades y generar malla volumétrica |
| [`preparar_stl.py`](https://github.com/juanjosecas/openFOAM-manual/blob/main/scripts/preparar_stl.py) | Crear esfera STL o convertir milímetros/centímetros a metros |
| [SVG y Gmsh](tutoriales/07-svg-gmsh.md) | Flujo de trabajo con Gmsh; archivos auxiliares pendientes |
| [`audit_cases.py`](https://github.com/juanjosecas/openFOAM-manual/blob/main/scripts/audit_cases.py) | Auditoría estructural de casos sin ejecutarlos |

## Archivos del proyecto

- [README del repositorio](https://github.com/juanjosecas/openFOAM-manual/blob/main/README.md).
- [Todos los casos](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases).
- [Todos los scripts](https://github.com/juanjosecas/openFOAM-manual/tree/main/scripts).
- [Convenciones de documentación y nomenclatura](estructura-y-estilo.md).

## Mantenimiento del índice

**Regla editorial:** todo nuevo tutorial debe incorporarse a esta página, a la navegación en `mkdocs.yml` y, cuando corresponda, vincular su directorio en `cases/`. Si se añade un caso sin tutorial, describirlo aquí como caso auxiliar. No anunciar un enlace ni el estado «ejecutable» hasta confirmar que el archivo existe y que los componentes necesarios están presentes. Las ecuaciones se escriben como `$...$` (en línea) y `$$...$$` (en bloque).


## Archivos opcionales y ampliaciones

Los directorios `variants/` documentan tres ajustes pequeños por caso. No sustituyen las condiciones originales: copiar un caso antes de aplicar una variante y modificar **un parámetro por vez**.

- Los casos **01, 02, 03 y 08** contienen `postprocessing/probes.function`: configuración de sondas *opcional*, sin activar automáticamente.
- Los casos con malla `blockMesh` tienen `Allmesh` para construir y comprobar la malla, y `Allclean` con previsualización de archivos a limpiar. Para borrar resultados hay que usar `bash Allclean --yes`; **no se elimina `0/`**.
- Los casos 01–03, 08–12 y 13 incluyen `variants/README.md`, con propuestas de variación y criterios para conservar el caso base.
- [`compare_variants.py`](https://github.com/juanjosecas/openFOAM-manual/blob/main/scripts/compare_variants.py) genera una comparación de perfiles CSV de distintas corridas; no ejecuta el solver.

Las extensiones **no resuelven** los archivos ausentes de los casos 04 y 07 ni adaptan automáticamente el caso 12, procedente de OpenFOAM Foundation 8. El tutorial 05 continúa siendo conceptual y el 06 corresponde a automatización, no a un caso CFD independiente.


## Actualizaciones de los casos previamente incompletos

- [Chorro de agua: configuración temporal reconstruida](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/04-chorro-agua/COMPLETADO.md).
- [SVG/Gmsh: alternativa rectangular reproducible](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/07-svg-gmsh/COMPLETADO.md). El SVG histórico no está disponible.
- [Goldschmidt: dependencias que no es seguro inventar](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/12-goldschmidt-particulas/PENDIENTES.md).


## De régimen estacionario a transitorio

[Guía de conversión `simpleFoam` → `pimpleFoam`](simplefoam-a-transitorio.md): cuándo conviene, qué diccionarios cambian, dificultad, número de Courant, inicialización y resultados adicionales que pueden obtenerse.


## Investigación externa y futuras aplicaciones científicas

- [Catálogo de fuentes con URL original](investigacion-fuentes-openfoam.md): transporte escalar, biofísica, calor, turbulencia, FSI y referencias de malla; clasifica duplicados y dependencias.
- [Proyecto 14A–14E: difusión y liberación de fármacos](propuesta-difusion-farmacos.md): ecuaciones, unidades, modelos de liberación, condiciones de contorno, validación analítica y observables.
- [Hoja de ruta de aplicaciones nuevas](investigacion-hoja-de-ruta.md): prioridades y requisitos antes de convertir fuentes externas en casos reproducibles.

**Importante:** estos documentos son una **investigación y propuestas**, no nuevos casos CFD ejecutables; los enlaces originales no implican compatibilidad automática con OpenFOAM.com v2406/v2412.


## Nuevo caso 14A: difusión de concentración normalizada

- [Caso 14A autocontenido](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/14a-difusion-farmaco): `scalarTransportFoam`, `0/T`, `0/U`, `DT`, malla 1D, scripts propios y CSV/PNG/GIF. **Revisión estática; no ejecutado.**
- [Estándar obligatorio para futuros casos](estandar-casos-autocontenidos.md): estructura, scripts, variantes, procedencia y verificaciones.

Las fases 14B–14E y los casos 15–22 siguen siendo propuestas, no carpetas de simulación.
