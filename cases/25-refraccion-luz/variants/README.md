# Variaciones del caso 25

Modificar **un parámetro por vez** y usar `--salida` para conservar resultados.

1. Incidencia: `python3 rayos.py --modo 2d --angulo 10 --salida plots/angulo10` frente a `--angulo 60 --salida plots/angulo60`. Comprobar Snell.
2. Índice del medio 2: `python3 rayos.py --modo 2d --n2 1.4 --salida plots/n2_14`. El valor 1.4 es hipotético.
3. Azimut: `python3 rayos.py --modo 3d --azimut 75 --salida plots/azimut75`. Cambia la orientación espacial, no el ángulo refractado.

**Demostración adicional (cambia varios parámetros):** `python3 rayos.py --desde abajo --n1 1.333 --n2 1.0003 --angulo 60 --salida plots/rit`. Muestra reflexión interna total.

Los GIF muestran barridos de ángulo, no tiempo físico.
