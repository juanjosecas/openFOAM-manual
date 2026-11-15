# Postprocesamiento

`python -m pip install -r requirements-postprocessing.txt`

Los scripts trabajan sobre casos ya calculados. Se acepta el directorio del caso o, para campos, perfiles y animaciones, un archivo .foam. No dependen de ParaView ni ejecutan OpenFOAM.

```bash
python postprocessing/fields.py runs/canal --list
python postprocessing/fields.py runs/canal --field U --normal z
python postprocessing/fields.py runs/canal --field p --normal z --output plots/p.png
python postprocessing/fields.py runs/presa --field alpha.water --contour 0.5
python postprocessing/fields.py runs/canal --field U --csv plots/cells.csv --output plots/U.png
python postprocessing/profile.py runs/canal --field U --component 0 --start 0.15 0.0001 0.0005 --end 0.15 0.0199 0.0005
python postprocessing/animate.py runs/presa --field alpha.water --clim 0 1 --output plots/agua.mp4
python postprocessing/animate.py runs/cow --field vorticity --component 2 --cmap coolwarm --stride 2 --max-frames 100
python postprocessing/plot_solver_log.py runs/canal/log.simpleFoam
```

- fields.py: imagen, vista interactiva, cortes, isosuperficie y datos de centros de celda.
- profile.py: perfil interpolado; muestras fuera de la malla marcadas como NaN.
- animate.py: animación con cámara y escala de color fijas; rango temporal opcional.
- plot_solver_log.py: residuos y Courant.
- plot_csv.py y compare_variants.py: datos tabulares.
- graficos_esfera.py y los analizadores de cada caso: referencias físicas y análisis particulares.

Para vectores se representa la magnitud salvo que se indique --component 0/1/2. La vorticidad se lee si existe o se estima desde U; la estimación de PyVista puede diferir del operador discreto de OpenFOAM. La interpolación de celdas a puntos puede suavizar discontinuidades. Las animaciones tienen fps constantes, no necesariamente proporcionales al paso físico. Para el manual histórico, los visualizadores retirados están en Git; usar los comandos anteriores en su lugar. No se ejecutó el código de esta revisión.
