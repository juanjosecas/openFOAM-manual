# Investigación de fuentes para ampliar el manual de OpenFOAM

**Fecha de recopilación:** 14 de octubre de 2026. **Objetivo:** conservar fuentes originales, no solo ideas, para convertirlas más adelante en tutoriales reproducibles. Referencia principal del manual: **OpenFOAM.com v2406/v2412**.

> **Estado:** inventario documental procedente de una investigación externa y de una revisión complementaria de enlaces. **No son casos implementados ni simulados.** La compatibilidad con v2406/v2412 y la licencia de cada recurso deben comprobarse antes de importar código o datos. «Archivos» significa que la página o el proyecto los describe; no que hayan sido descargados, auditados o ejecutados aquí.

## Selección prioritaria: nuevas aplicaciones, no duplicados

| Prioridad | Aplicación y fuente original | Qué aprenderíamos | Material disponible / cautela |
| --- | --- | --- | --- |
| **P0** | [Transporte escalar: tutorial de Paterson, Virginia Tech (PDF)](https://www.researchgate.net/profile/Ingo-Riess/post/How_to_model_smoke_propagation_for_an_existing_velocity_field_using_scalarTransportFoam_in_OpenFOAM/attachment/5cee6f723843b0b98254daac/AS:763860613099524@1559129970722/download/5-scalarTransportFoamTutorial.pdf) | Advección–difusión de un escalar pasivo; base para un **modelo idealizado de concentración de fármaco** | Guía de taller, ecuación de transporte y fuentes volumétricas. PDF alojado en ResearchGate: acceso y compatibilidad por verificar. **No es un tutorial biomédico validado.** |
| **P0** | [Conducción transitoria 1D con laplacianFoam — OpenFOAM.es](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam) | Ecuación de difusión, escala $L^2/D$, número de Fourier y solución analítica | Página paso a paso con diccionarios, Allrun/Allclean y comparación. Usa temperatura `T`; **adaptar a concentración exige revisar dimensiones y solver**. |
| **P0** | [hemodynamic4Foam — EhsanGLB](https://github.com/EhsanGLB/hemodynamic4Foam) | Hemodinámica y transporte de nanopartículas, difusión browniana y efectos termo-foréticos | Repositorio, `tutorials4HD/` y documentación. **foam-extend 4.1**: no trasladar directamente a OpenFOAM.com. |
| **P1** | [Convección natural en cavidad — OpenFOAM.es](https://openfoam.es/tutoriales/conveccion-natural-cavidad-diferencial-termica) | Acoplamiento temperatura–densidad–velocidad, flotabilidad y Nusselt | Tutorial `buoyantSimpleFoam`, condiciones térmicas, scripts; versión exacta y modelo térmico por comprobar. |
| **P1** | [Escalón hacia atrás con k-ω SST — OpenFOAM.es](https://openfoam.es/tutoriales/backward-facing-step-k-omega-sst) | Separación turbulenta, longitud de reenganche, sensibilidad a malla y modelo RANS | Caso con campos `U,p,k,omega,nut` y posprocesamiento descrito. Distinto del canal con obstáculos existente. |
| **P1** | [Desprendimiento de vórtices de un cilindro 2D — OpenFOAM.es](https://openfoam.es/tutoriales/cilindro-2d-vortex-shedding-pimplefoam) | Transitorio real, sustentación $C_L(t)$, FFT, número de Strouhal | `pimpleFoam`, caso y análisis de frecuencia descritos; no es el ejemplo de esfera en agua. |
| **P1** | [Flujo sobre placa caliente / FSI y calor — preCICE](https://precice.org/tutorials) | Transferencia conjugada y acoplamiento multifísico | Casos y adaptadores con dependencias externas. Repositorio: [precice/tutorials](https://github.com/precice/tutorials). |
| **P1** | [Aleta elástica perpendicular — preCICE](https://precice.org/tutorials-perpendicular-flap.html) | Interacción fluido–estructura: desplazamiento y fuerza transitorios | `pimpleFoam` y solver estructural acoplado; requiere preCICE y adaptador. |
| **P1** | [LES de canal turbulento — OpenFOAM Journal](https://journal.openfoam.com/index.php/ofj/article/view/159) | LES, comparación con DNS, estadísticas y espectros de turbulencia | Artículo pedagógico con archivos de caso y posproceso enlazados; alto costo computacional. |
| **P2** | [CoronaryHemodynamics — alundilong](https://github.com/alundilong/CoronaryHemodynamics) | Hemodinámica coronaria, perfiles fisiológicos y salidas Windkessel | Proyecto basado en **blueCFD-core**; revisar disponibilidad de tutoriales, código, dependencias y licencia. |
| **P2** | [preCICE: placa caliente estacionaria](https://precice.org/tutorials-flow-over-heated-plate-steady-state) | Transferencia de calor fluido–sólido con `code_aster` | Acoplamiento estacionario y varias dependencias; alternativa al caso transitorio. |
| **P2** | [preCICE: placa caliente con flujo particionado](https://precice.org/tutorials-flow-over-heated-plate-partitioned-flow) | Acoplamiento térmico con varios participantes | Avanzado; requiere comprender la estrategia de acoplamiento. |
| **P2** | [preCICE: aleta con transferencia de tensiones](https://precice.org/tutorials-perpendicular-flap-stress) | Diferencia entre transferir fuerzas y tensiones | Extensión del caso de aleta, no nuevo problema físico. |
| **P2** | [preCICE: múltiples aletas](https://precice.org/tutorials-multiple-perpendicular-flaps) | Acoplamiento FSI de tres participantes | Ejemplo avanzado con dos sólidos deformables. |
| **P2** | [preCICE: placa caliente, mapeo nearest-projection](https://precice.org/tutorials-flow-over-heated-plate-nearest-projection) | Sensibilidad al mapeo de datos entre mallas | Intercambio térmico con `buoyantPimpleFoam` y `laplacianFoam`. |

### Otros recursos identificados: consulta y contexto

| Fuente con URL original | Uso real para el manual | Clasificación |
| --- | --- | --- |
| [Portal OpenFOAM.es — catálogo](https://openfoam.es/tutoriales) | Buscar casos con diccionarios y pasos legibles; revisar siempre la versión indicada por cada página | Índice, no caso autónomo |
| [Referencia laplacianFoam — OpenFOAM.es](https://openfoam.es/referencia/solvers/laplacianfoam) | Identificar ecuación difusiva y propiedad `DT` | Referencia de solver |
| [OpenFOAM Basic Training — CFD.at, PDF](https://www.cfd.at/sites/default/files/tutorialsV7/OFTutorialSeries.pdf) | Ejercicios de difusión, discretización y fundamentos | PDF de formación, versión heredada |
| [CFD-Online: uso de STL en snappyHexMesh](https://www.cfd-online.com/Forums/openfoam-meshing/227156-setting-up-case-using-stl-files.html) | Refinar explicación de malla base, etapas y `-overwrite` | **Complemento** del caso 13 |
| [CFD-Online: escala de STL](https://www.cfd-online.com/Forums/openfoam-meshing/67168-stl-snappyhexmesh-dimensions-mismatch.html) | Unidades y geometría; comprobar sintaxis de escala para la versión | **Complemento** del caso 13 |
| [CFDMonkey: consejos de snappyHexMesh](https://cfdmonkey.com/tips-and-tricks-for-significantly-improving-your-snappyhexmesh/) | Calidad, refinamiento y capas | **Complemento** del caso 13 |
| [Wolf Dynamics: Advanced Meshing](https://www.wolfdynamics.com/our-services/training/topenfoam-advanced-training.html?id=53) | Temario para control de calidad de mallas; no se identificó un caso libre completo | Material descriptivo |
| [PyVista — sitio oficial](https://pyvista.org/) y [documentación](https://docs.pyvista.org/getting-started/) | Ampliar animaciones, isosuperficies, líneas de corriente y exportación | **Complemento** de `docs/pyvista.md` |
| [Cavidad 2D con icoFoam — OpenFOAM.es](https://openfoam.es/tutoriales/cavidad-lid-driven-icofoam) | Validación frente a Ghia y mejoras al caso 09 | **Duplicado temático:** ya existe caso 09 |
| [preCICE: tutoriales y archivos](https://github.com/precice/tutorials) | Repositorio fuente de múltiples ejemplos acoplados | Índice y archivos originales |

**Fuentes citadas en la investigación sin URL específica recuperable:** un PDF de «Heat Transfer» de FOAMacademy y una descripción de recursos de ParaView. No se incorpora un enlace inventado; se localizarán sus direcciones exactas antes de usarlos como referencia formal.

## Casos existentes que NO conviene duplicar

- **09 cavity** ya cubre la cavidad con tapa móvil: el tutorial externo de `icoFoam` serviría para **validación**, no para numerar un caso nuevo.
- **11 damBreak** ya cubre rotura de presa: la variante FSI de preCICE es nueva **solo si incluye la interacción con el sólido**.
- **12 Goldschmidt** ya introduce partículas: su incompatibilidad pendiente no se resuelve citando `DPMFoam` o `MPPICFoam`.
- **13 STL/snappyHexMesh** ya cubre la generación de mallas: los foros aportan buenas prácticas, no otra aplicación física.
- **PyVista** ya tiene documentación y script: ampliar observables, no crear otro tutorial introductorio.
- **01–03 y 08** ya incluyen reología, estenosis y tubería pulsátil: un nuevo caso de fármacos debe incorporar **un campo de concentración y transporte de masa**, no solo cambiar la geometría.

## Fuentes mencionadas como posibilidades, pero sin tutorial directo suficientemente identificado

Se mencionaron **combustión con `reactingFoam`**, **sprayFoam**, **MPPICFoam**, **`chtMultiRegionFoam`**, aerodinámica NACA0012 y hemodinámica con nanopartículas. **No** hay en esta recopilación una URL directa verificada de un caso concreto y completo para cada uno. Son líneas de búsqueda futuras, **no** resultados confirmados.

## Cómo usar este inventario

1. Abrir la **URL original** y comprobar que sigue accesible y que contiene los archivos prometidos.
2. Registrar licencia de cada archivo antes de copiarlo al repositorio; preferir reconstrucción didáctica propia y citar la procedencia.
3. Anotar la edición exacta de OpenFOAM y el solver disponible en v2406/v2412.
4. Elegir un fenómeno nuevo, definir condiciones físicas, malla y parámetros con unidades.
5. Crear carpeta `cases/NN-...`, tutorial `docs/tutoriales/NN-...`, `Allmesh`, `Allrun`, variantes y posprocesamiento.
6. Verificar **sin ejecutar** estructura y consistencia; ejecutar y validar numéricamente solo en una fase autorizada.

Para priorización: [hoja de ruta](investigacion-hoja-de-ruta.md). Para el proyecto más interesante en biofísica: [difusión y liberación de fármacos](propuesta-difusion-farmacos.md).
