# Variantes pequeñas

Copiar el caso antes de editar diccionarios y modificar **una variable por vez**.

1. **Óptica: ángulo de incidencia:** después del mismo CFD, comparar `--angulo 10` y `--angulo 40` en `postprocessing/trazar.py`. El campo `alpha.water` no cambia.
2. **Óptica: índice del líquido:** comparar `--n-agua 1.333` y `--n-agua 1.4`. El segundo valor es hipotético, no agua real.
3. **CFD: gravedad:** cambiar `constant/g` de `-9.81` a `-4.905` m/s². Limpiar, repetir solver y observar la evolución de h(x). El modelo de refracción no cambia.
4. **CFD: altura inicial derecha:** cambiar el límite z de `0.022` a `0.025` m en la segunda región de `system/setFieldsDict`. Repetir desde limpio.

La representación 3D extruye en y el CFD 2D; no constituye un flujo tridimensional.
