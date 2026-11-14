# 35 · Gota de aceite sobre una superficie de agua (2D)

**Estado: prototipo experimental sin validación de ejecución.** Caso aislado, sin modificar tutoriales existentes.

Se adapta el caso oficial `multiphaseInterFoam/laminar/damBreak4phase` de la instalación OpenFOAM v2406. El script `build_case.py` crea `case/` copiando los archivos oficiales y cambia la física a **agua, aceite y aire**. Si la imagen v2406 no contiene ese tutorial o el solver, se interrumpe explícitamente; no se simula una fase inexistente.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash cases/35-gota-de-aceite-sobre-agua/run_docker.sh
```

Requisitos: Docker accesible sin sudo, imagen `opencfd/openfoam-default:2406`, solver `multiphaseInterFoam` y tutorial `damBreak4phase` incluidos en la imagen. Los scripts no se han probado con una ejecución CFD real.

## Configuración inicial

- Dominio rectangular 2D: 30 × 30 mm; espesor de 0,2 mm; 150 × 150 × 1 celdas.
- Agua en los 15 mm inferiores; aire encima.
- Gota de aceite de diámetro 4 mm, centro a 20 mm del fondo, inicialmente en reposo.
- Agua: 998 kg/m³, viscosidad cinemática 1,002 × 10⁻⁶ m²/s.
- Aceite: 900 kg/m³, viscosidad cinemática 5,56 × 10⁻⁵ m²/s.
- Aire: 1,2 kg/m³, viscosidad cinemática 1,5 × 10⁻⁵ m²/s.
- Tensiones interfaciales: agua/aire 0,072; aceite/aire 0,030; agua/aceite 0,025 N/m.
- Simulación de 0,15 s; escritura cada 0,002 s; `maxCo=0.2` y `maxAlphaCo=0.2`.

**Limitación geométrica:** `sphereToCell` intersectado con un dominio de una celda de espesor representa una sección 2D circular; no conserva la masa ni la dinámica de una gota 3D. La malla de 0,2 mm proporciona ~20 celdas por diámetro. Es una prueba visual inicial, no una simulación de impacto validada.

## Inspección y visualización

Los archivos generados quedan en `cases/35-gota-de-aceite-sobre-agua/case/`. Para ParaView:

```bash
touch cases/35-gota-de-aceite-sobre-agua/case/case.foam
paraview cases/35-gota-de-aceite-sobre-agua/case/case.foam
```

Representar `alpha.oil` y `alpha.water` mediante contornos de valor 0,5. Usar la misma escala y cámara durante toda la animación. Verificar conservación de volumen, suma de fracciones de fase, presión, paso temporal capilar y ausencia de corrientes espurias.

## Antecedentes

- [Tutorial multiphaseInterFoam de cuatro fases](https://www.cfdyna.com/Home/OpenFOAM/of_Tut_Web/multiPhaseInterFoam.pdf).
- [Caso damBreak4phase con agua y aceite](https://www.xsim.info/articles/OpenFOAM/en-US/tutorials/multiphase-multiphaseInterFoam-laminar-damBreak4phase.html).
- [Casos de gotas 2D](https://github.com/JuanMairal/openfoamDroplet).

**Pendiente:** verificar sintaxis y compatibilidad de las condiciones de contorno heredadas con v2406, gravedad, control de tiempo, malla, solver y estabilidad. No utilizar resultados como predicciones cuantitativas antes de esa verificación.
