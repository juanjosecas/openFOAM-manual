# Hoja de ruta: de fuentes externas a casos reproducibles

**Estado:** plan editorial basado en la [investigación de fuentes](investigacion-fuentes-openfoam.md), **sin fechas comprometidas**. Cada fase requiere revisar compatibilidad, licencias, condiciones físicas y validación.

## Orden de trabajo recomendado

| Orden | Futuro caso o ampliación | Fuente directa | Entregable mínimo | Dificultad |
| --- | --- | --- | --- | --- |
| 1 | **14A: difusión 1D** | [Conducción transitoria, laplacianFoam](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam) | Caso base, perfiles vs solución analítica, error y sensibilidad | Baja–media |
| 2 | **14B–14D: liberación y transporte de fármaco** | [Tutorial scalarTransportFoam (PDF)](https://www.researchgate.net/profile/Ingo-Riess/post/How_to_model_smoke_propagation_for_an_existing_velocity_field_using_scalarTransportFoam_in_OpenFOAM/attachment/5cee6f723843b0b98254daac/AS:763860613099524@1559129970722/download/5-scalarTransportFoamTutorial.pdf) | $C(x,t)$, masa liberada, advección y reacción opcional | Media–alta |
| 3 | **15: convección natural** | [OpenFOAM.es](https://openfoam.es/tutoriales/conveccion-natural-cavidad-diferencial-termica) | Campos $T,U,p_{rgh}$, Nusselt, variaciones de $\Delta T$ | Media |
| 4 | **16: escalón turbulento** | [OpenFOAM.es](https://openfoam.es/tutoriales/backward-facing-step-k-omega-sst) | $k,\omega,\nu_t$, longitud de reenganche, estudio de malla | Media–alta |
| 5 | **17: vórtices de cilindro 2D** | [OpenFOAM.es](https://openfoam.es/tutoriales/cilindro-2d-vortex-shedding-pimplefoam) | $C_L(t)$, FFT, Strouhal, GIF | Media–alta |
| 6 | **18: hemodinámica con transporte** | [hemodynamic4Foam](https://github.com/EhsanGLB/hemodynamic4Foam) | Modelo conceptual con fuentes y límites; adaptación propia solo si se confirma compatibilidad | Alta |
| 7 | **19: transferencia conjugada** | [preCICE](https://precice.org/tutorials) | Fluido+sólido, temperaturas de interfaz, energía intercambiada | Alta |
| 8 | **20: aleta deformable** | [Aleta preCICE](https://precice.org/tutorials-perpendicular-flap.html) | Desplazamiento, fuerzas y estabilidad del acoplamiento | Muy alta |
| 9 | **21: LES de canal** | [OpenFOAM Journal](https://journal.openfoam.com/index.php/ofj/article/view/159) | Perfiles estadísticos, espectros, dependencia de malla | Muy alta |
| 10 | **22: hemodinámica coronaria** | [CoronaryHemodynamics](https://github.com/alundilong/CoronaryHemodynamics) | Condiciones Windkessel y magnitudes fisiológicas, sin prometer portabilidad | Muy alta |

Las numeraciones son **reservas editoriales**, no directorios `cases/` existentes. Si se crean, actualizar `docs/index.md` y `mkdocs.yml` y distinguir «borrador», «configuración completa», «ejecutado» y «validado».

## Ampliaciones sin duplicar ejemplos

- Caso 09: añadir validación con Ghia usando la [guía de cavidad](https://openfoam.es/tutoriales/cavidad-lid-driven-icofoam), **no crear otra cavidad**.
- Caso 11: documentar FSI de rotura de presa con columna flexible desde [preCICE](https://precice.org/tutorials), sin confundirlo con el damBreak ya existente.
- Caso 12: mantener [pendientes de Goldschmidt](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/12-goldschmidt-particulas/PENDIENTES.md) antes de cualquier expansión lagrangiana.
- Caso 13: agregar mejores controles de calidad de malla y unidades desde [CFD-Online](https://www.cfd-online.com/Forums/openfoam-meshing/227156-setting-up-case-using-stl-files.html) y [CFDMonkey](https://cfdmonkey.com/tips-and-tricks-for-significantly-improving-your-snappyhexmesh/).
- Postprocesamiento: ampliar [PyVista](pyvista.md) para campos escalares, isosuperficies, sondas, series de tiempo y balances.

## Criterio de aceptación para cada nuevo caso

1. **Procedencia:** URL de origen, autor/proyecto, licencia, versión y fecha de consulta.
2. **Física:** ecuaciones, dimensiones, supuestos, magnitudes observables y valores de referencia.
3. **Archivos:** `0/`, `constant/`, `system/`, geometría o generador, `Allmesh`, `Allrun`, `Allclean` y README.
4. **Procedimiento:** comandos exactos desde malla hasta solver y posprocesamiento, con variantes pequeñas y controladas.
5. **Resultados:** CSV/VTK, PNG y, cuando tenga sentido, GIF del **tiempo físico**.
6. **Validación:** comparación analítica/experimental o benchmark, sensibilidad a malla y paso temporal; no anunciarla antes de ejecutarla.
7. **Compatibilidad:** verificar en **OpenFOAM.com v2406/v2412**; no asumir equivalencia con Foundation, foam-extend o blueCFD.

## Advertencias sobre el informe fuente

La investigación original sugería importar nuevamente `cavity`, `damBreak`, `Goldschmidt`, PyVista y STL, pero **esos temas ya están en el manual**. Por eso se preservan sus enlaces como complementos, no como nuevos tutoriales. También mencionaba archivos de algunos sitios sin descargarlos ni verificar su licencia; aquí se los trata como **recursos por inspeccionar**. No se copió código ajeno.


## Implementación documental inicial

El [caso 14A](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/14a-difusion-farmaco) ya tiene estructura, diccionarios y postprocesamiento autocontenidos, **sin ejecución ni validación**. El resto de casos numerados de esta hoja sigue pendiente de implementación. Consultar el [estándar de autocontención](estandar-casos-autocontenidos.md).
