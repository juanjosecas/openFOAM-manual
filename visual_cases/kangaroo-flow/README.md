# Estela de un canguro

Flujo transitorio 2D alrededor de una silueta fija. Solver pimpleFoam; fluido modelo con nu=0.008 m²/s, entrada de 1 m/s y Reynolds aproximado 145 basado en altura.

## Qué modificar

| Archivo | Entrada | Efecto |
| --- | --- | --- |
| geometry/kangaroo.geo | Point y Line | Contorno y dominio; mantener circuito cerrado. |
| geometry/kangaroo.geo | SizeMin, SizeMax, DistMin, DistMax | Refinamiento alrededor del objeto y transición a la malla lejana. |
| 0/U | Velocidad de entrada | Probar 0.5 m/s; paredes del objeto noSlip. |
| constant/transportProperties | nu | Controla Reynolds. |
| system/controlDict | endTime, maxCo, writeInterval | 80 s, 0.5 y salida cada 0.5 s. |
| system/changeDictionaryDict | Patches | Mantener frontAndBack de tipo empty. |

## Ejecutar y visualizar

```bash
bash scripts/prepare_case.sh kangaroo-flow --output runs/kangaroo
# Si Gmsh no está disponible dentro del contenedor, generar en el host:
gmsh runs/kangaroo/geometry/kangaroo.geo -3 -format msh2 -o runs/kangaroo/geometry/kangaroo.msh
bash scripts/run_docker.sh runs/kangaroo
python postprocessing/animate.py runs/kangaroo --field U --normal z --output plots/kangaroo-speed.gif
python postprocessing/animate.py runs/kangaroo --field vorticity --component 2 --normal z --cmap coolwarm --output plots/kangaroo-vorticity.gif
```

La geometría activa es el archivo .geo; el CSV guarda el contorno de referencia. Si se modifica geometría, preparar una copia y generar otra malla. La variante animation cambia la frecuencia de escritura. La silueta no se mueve; no representa un salto. Revisar sensibilidad de estela a malla y paso temporal. Sin ejecución comprobada.
