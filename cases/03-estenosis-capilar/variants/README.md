# Variantes controladas de 03-estenosis-capilar

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Reducir la velocidad de entrada un 20 % en 0/U.
2. **Modelo o integración:** Cambiar n de 0.5 a 0.7 en turbulenceProperties.
3. **Malla o escritura:** Aumentar subdivisiones en la garganta manteniendo compatibles los bloques.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/03-estenosis-capilar /tmp/03-estenosis-capilar-variante
cd /tmp/03-estenosis-capilar-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
