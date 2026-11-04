# Variantes controladas de 09-cavity-2d

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Reducir un 20 % la velocidad de la tapa en 0/U.
2. **Modelo o integración:** Reducir deltaT a la mitad y conservar endTime.
3. **Malla o escritura:** Refinar discretización sin alterar dimensiones de la cavidad.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/09-cavity-2d /tmp/09-cavity-2d-variante
cd /tmp/09-cavity-2d-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
