# Variantes pequeñas del caso 14A

Trabajar sobre copias del directorio `14a-difusion-farmaco`, nunca modificar los resultados base. **Un cambio por vez**.

1. **Difusividad:** modificar `DT` de `1e-9` a `5e-10 m²/s` en `constant/transportProperties`; cambiar `D` en `postprocessing/analizar.py` al mismo valor. Comparar anchura del perfil a igual tiempo. **No** interpretar esos números como propiedades farmacológicas reales.
2. **Malla:** cambiar `(200 1 1)` a `(400 1 1)` en `system/blockMeshDict`; reconstruir con `Allmesh` en una copia limpia. Comparar error respecto de la solución seminf. para tiempos tempranos.
3. **Concentración de fuente:** cambiar `T=1` a `T=0.5` en `0/T`. En este caso, **la normalización respecto de la referencia cambia**: la curva erfc de `analizar.py` debe multiplicarse por 0.5; no comparar la nueva curva con la referencia de amplitud 1 sin ajustarla.

Cambiar solo `writeInterval` modifica la frecuencia de salida, **no** la precisión de integración. Reducir `deltaT` sí permite estudiar convergencia temporal.
