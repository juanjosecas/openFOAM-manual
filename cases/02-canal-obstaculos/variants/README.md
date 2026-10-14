# Variantes controladas de 02-canal-obstaculos

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Disminuir la velocidad de entrada un 20 % en 0/U.
2. **Modelo o integración:** Variar n en turbulenceProperties, conservando k, nuMin y nuMax.
3. **Malla o escritura:** Incrementar refinamiento sin romper subdivisiones entre bloques.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/02-canal-obstaculos /tmp/02-canal-obstaculos-variante
cd /tmp/02-canal-obstaculos-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
