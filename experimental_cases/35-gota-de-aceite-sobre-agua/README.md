# Gota de aceite sobre agua

Prototipo 2D con tres fases: agua, aceite y aire. build_case.sh genera los diccionarios a partir del tutorial damBreak4phase disponible en la instalación; requiere multiphaseInterFoam.

## Configuración

Dominio 30 × 30 mm, espesor 0.2 mm, malla 150 × 150 × 1. Agua hasta 15 mm de altura; gota de aceite de diámetro 4 mm centrada a 20 mm del fondo.

| Parámetro | Agua | Aceite | Aire |
| --- | ---: | ---: | ---: |
| rho (kg/m³) | 998 | 900 | 1.2 |
| nu (m²/s) | 1.002e-6 | 5.56e-5 | 1.5e-5 |

Tensiones interfaciales agua/aire 0.072, aceite/aire 0.030 y agua/aceite 0.025 N/m.

## Qué modificar

Editar build_case.sh antes de generar el caso, o los diccionarios de case/ antes de resolver:

| Archivo generado | Entrada | Efecto |
| --- | --- | --- |
| constant/transportProperties | phases, sigmas y propiedades de fase | Densidades, viscosidades y tensiones interfaciales. |
| system/setFieldsDict | boxToCell, sphereToCell | Altura de agua, posición y radio de gota. |
| system/blockMeshDict | vertices, blocks | Tamaño y resolución. |
| system/controlDict | endTime, maxCo, maxAlphaCo, writeInterval | 0.15 s, 0.2, 0.2 y 0.002 s. |

## Ejecutar y visualizar

```bash
bash scripts/run_docker.sh experimental_cases/35-gota-de-aceite-sobre-agua
python postprocessing/animate.py experimental_cases/35-gota-de-aceite-sobre-agua/case --field alpha.oil --clim 0 1 --output plots/oil.gif
python postprocessing/statistics.py experimental_cases/35-gota-de-aceite-sobre-agua/case --field alpha.oil
```

El generador no sobrescribe case/ existente. Para ensayos nuevos conservar la corrida anterior y generar otra copia. Revisar suma de fracciones, volumen de cada fase y corrientes espurias. La sección circular extruida no equivale a una gota 3D. Prototipo sin ejecución comprobada.
