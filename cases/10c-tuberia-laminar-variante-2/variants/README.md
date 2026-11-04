# Variantes controladas de 10c-tuberia-laminar-case2

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Reducir velocidad impuesta un 20 % si hay patch fixedValue.
2. **Modelo o integración:** Refinar malla conservando geometría.
3. **Malla o escritura:** Ajustar writeInterval: simpleFoam no describe evolución física temporal.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/10c-tuberia-laminar-case2 /tmp/10c-tuberia-laminar-case2-variante
cd /tmp/10c-tuberia-laminar-case2-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
