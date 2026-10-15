# 26 · OpenFOAM y refracción sobre una superficie móvil

**Caso autocontenido:** [cases/26-refraccion-interfoam](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/26-refraccion-interfoam).

Aquí **OpenFOAM interviene realmente**: `interFoam` calcula cómo se mueve una superficie agua–aire bajo gravedad. A partir de los resultados, Python reconstruye aproximadamente la altura $h(x,t)$ desde `alpha.water` y aplica la ley de Snell para obtener la dirección de un rayo refractado.

La física se separa en dos etapas: **CFD bifásico 2D** y **óptica geométrica 2D/3D como postprocesamiento**. El gráfico 3D representa una extrusión de la superficie 2D, no un cálculo CFD tridimensional.

## Ejecución

```bash
cd cases/26-refraccion-interfoam
bash Allrun
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r postprocessing/requirements.txt
python3 postprocessing/trazar.py --gif
```

Genera CSV y PNG de la superficie y las trayectorias, y un GIF de los tiempos físicos guardados por `interFoam`. Para cambiar el ángulo del rayo sin volver a ejecutar el solver:

```bash
python3 postprocessing/trazar.py --angulo 35 --azimut 65
```

Ver el [README técnico](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/26-refraccion-interfoam/README.md) para geometría, malla, condiciones de contorno, unidades, ecuaciones, variantes, limitaciones y fuentes.

**Estado:** revisión estática; OpenFOAM y el postprocesamiento **no ejecutados ni validados**. La aproximación $h(x)=\int\alpha_{\mathrm{water}}\,dz$ no representa superficies multivaluadas, gotas ni rompientes. La óptica no retroalimenta el fluido.
