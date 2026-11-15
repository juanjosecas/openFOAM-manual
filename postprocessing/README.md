# Postprocesamiento

Instalar en el host: `python -m pip install -r requirements-postprocessing.txt`. No se necesita ParaView para los scripts PyVista. Se leen resultados existentes; no se ejecuta CFD.

```bash
python postprocessing/fields.py runs/difusion --field T --normal z --output plots/T.png
python postprocessing/fields.py runs/canal --field U --normal z
python postprocessing/profile.py runs/canal --field U --component 0 --start 0.15 0.0001 0.0005 --end 0.15 0.0199 0.0005
python postprocessing/animate.py runs/presa --field alpha.water --clim 0 1 --output plots/agua.gif
python postprocessing/plot_solver_log.py runs/canal/log.simpleFoam
```

fields.py permite vista interactiva, cortes y exportación CSV de centros de celda; profile.py interpola una línea y marca las muestras fuera de la malla; animate.py usa una escala común para todos los estados. Para vectores, por defecto se representa la magnitud; --component 0/1/2 elige la componente. También se mantienen los análisis específicos de esfera, difusión, calor, viga y óptica, y los scripts de visualización históricos (render_transient.py es una opción con pvpython). Las herramientas nuevas no se han ejecutado. Los tiempos guardados pueden ser iteraciones de un solver estacionario.
