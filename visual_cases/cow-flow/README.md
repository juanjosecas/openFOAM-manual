# Flujo alrededor de una silueta de vaca

Flujo de aire 2D alrededor de un objeto fijo. El caso transitorio usa pimpleFoam y kOmegaSST (URANS); la variante steady permite comparar con una solución estacionaria.

## Configuración y cambios

| Archivo | Entrada | Efecto |
| --- | --- | --- |
| 0/U | Velocidad de entrada | 10 m/s en x; probar 5 m/s. |
| constant/transportProperties | nu | Viscosidad cinemática del aire: 1.5e-5 m²/s. |
| 0/k, 0/omega | Condiciones de entrada | Intensidad y escala de turbulencia; revisar juntas al cambiar velocidad. |
| system/controlDict | endTime, maxCo, maxDeltaT | 5 s, 0.5 y 0.001 s. Reducir el paso para estudiar sensibilidad temporal. |
| system/controlDict | writeInterval | 0.05 s; la variante animation aumenta frecuencia de salida. |
| meshes/cow_tunnel.msh | Malla compartida | Cambiar geometría implica remallar; cow-silhouette.svg es referencia editable, no un generador automático. |

## Ejecutar y visualizar

Desde la raíz:

```bash
bash scripts/prepare_case.sh cow-flow --output runs/cow
bash scripts/run_docker.sh runs/cow
python postprocessing/animate.py runs/cow --field U --normal z --output plots/cow-speed.gif
python postprocessing/animate.py runs/cow --field vorticity --component 2 --normal z --cmap coolwarm --output plots/cow-vorticity.gif
```

Agregar --variant steady o --variant animation al preparar otra copia. Revisar checkMesh antes de resolver: hay celdas sesgadas cerca de las pezuñas y el lanzador exige Mesh OK. El limitador limitVelocity puede afectar resultados; comprobar su intervención. URANS 2D puede amortiguar la estela. Sin nueva ejecución.
