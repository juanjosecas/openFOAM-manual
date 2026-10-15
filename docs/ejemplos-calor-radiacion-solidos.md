# Ejemplos adicionales para ampliar el manual: calor, radiación y sólidos

**Fecha de revisión:** 2026-10-15. Las URLs son referencias externas; **no** son garantía de compatibilidad ni de ejecución. Los casos 23 y 24 se construyeron de forma original a partir de las ecuaciones documentadas.

| Tema | Fuente original | Posible caso | Estado |
| --- | --- | --- | --- |
| Flexión de viga 3D | [API solidDisplacementFoam v2412](https://api.openfoam.com/2412/solidDisplacementFoam_8C.html) y [beamEndLoad Foundation 13](https://github.com/OpenFOAM/OpenFOAM-13/tree/master/tutorials/solidDisplacement/beamEndLoad) | Voladizo con tracción y comparación Euler–Bernoulli | **23 implementado, no ejecutado** |
| Conducción 1D estacionaria | [Documentación laplacianFoam](https://doc.openfoam.com/2312/tools/processing/solvers/rtm/basic/laplacianFoam/) | Barra entre dos temperaturas fijas | **24 implementado, no ejecutado** |
| Conducción 1D transitoria | [OpenFOAM.es: pared transitoria](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam) | Cambio brusco de temperatura, perfiles T(x,t), Fourier | Propuesta distinta de 24 |
| Tensiones térmicas | [Tutorial oficial de placa con agujero](https://www.openfoam.com/documentation/tutorial-guide/5-stress-analysis/5.1-stress-analysis-of-a-plate-with-a-hole) | Dilatación de barra con thermalStress y restricciones | Propuesta; requiere T y propiedades térmicas |
| Convección natural | [OpenFOAM.es: cavidad con diferencia térmica](https://openfoam.es/tutoriales/conveccion-natural-cavidad-diferencial-termica) | Rayleigh, Nusselt, T, U | Propuesta 15, no implementada |
| Radiación superficie-superficie | [Modelo viewFactor v2406](https://api.openfoam.com/2406/classFoam_1_1radiation_1_1viewFactor.html), [createViewFactors v2406](https://www.openfoam.com/news/main-news/openfoam-v2406/pre-processing) | Dos placas grises, intercambio radiativo | Propuesta: requiere geometría, emisividades, radiationProperties, factores de vista y solver térmico compatible |
| Radiación volumétrica | [Modelo fvDOM v2406](https://api.openfoam.com/2406/classFoam_1_1radiation_1_1fvDOM.html) | Medio participante con absorción/emisión | Propuesta avanzada; no confundir con conducción pura |
| Flujo radiativo de pared | [viewFactorHeatFlux v2406](https://www.openfoam.com/news/main-news/openfoam-v2406/post-processing) | Postproceso de qr [W/m²] | Ampliación de un caso radiativo futuro |
| Transferencia conjugada | [preCICE: placa calentada](https://precice.org/tutorials-flow-over-heated-plate-steady-state) | Acoplar sólido y fluido | Propuesta 19, requiere configuración multirregión o acoplamiento externo |

## Orden recomendado

1. Ejecutar y comprobar 24 (solución analítica lineal), luego convertirlo en conducción transitoria.
2. Ejecutar y comprobar 23 (deflexión y equilibrio de fuerzas), después activar tensiones térmicas.
3. Convección natural (15) y transferencia conjugada (19) para enlazar temperatura con velocidad.
4. Radiación de superficies grises (viewFactor) antes de fvDOM, por ser conceptualmente más simple.

**Limitaciones:** las fuentes externas pueden usar distintas distribuciones de OpenFOAM. La API documenta modelos, pero no sustituye a un tutorial autocontenido. Para radiación no se adjunta aún un caso: inventar un radiationProperties o una matriz de factores de vista sin verificar la interfaz del solver sería engañoso.
