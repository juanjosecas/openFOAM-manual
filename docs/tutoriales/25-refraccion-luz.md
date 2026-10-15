# 25 · Refracción de luz en líquido: 2D y 3D

[**Archivos autocontenidos del caso 25**](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/25-refraccion-luz).

Un rayo atraviesa una interfaz plana aire–agua. Se calculan reflexión y refracción con la ley de Snell:

$$
n_1\sin\theta_1=n_2\sin\theta_2.
$$

Para agua → aire puede existir reflexión interna total cuando $\theta_1>\arcsin(n_2/n_1)$. El modelo muestra tanto la proyección **2D** en el plano de incidencia como la trayectoria **3D**, cuyo azimut se puede variar.

## Ejecutar

```bash
cd cases/25-refraccion-luz
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
bash Allrun
```

Genera CSV y PNG en `plots/`. Para obtener GIF de un **barrido de ángulos**, ejecutar `bash Allrun --gif`. Para modificar la incidencia o el azimut:

```bash
python3 rayos.py --modo 2d --angulo 45
python3 rayos.py --modo 3d --angulo 45 --azimut 70
```

Consultar el [README completo](https://github.com/juanjosecas/openFOAM-manual/blob/main/cases/25-refraccion-luz/README.md) para ecuaciones vectoriales, parámetros con unidades, reflexión interna total, exportación, fuentes y variantes.

**Alcance:** es un modelo geométrico en Python, no CFD ni un solver OpenFOAM; la interfaz es plana y fija. El acoplamiento con `interFoam` es una ampliación futura. **Revisión estática, sin ejecutar ni validar.**
