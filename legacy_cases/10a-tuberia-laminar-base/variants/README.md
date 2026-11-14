# Variantes controladas de 10a-tuberia-laminar-case0

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Reducir velocidad impuesta un 20 % si hay patch fixedValue.
2. **Modelo o integración:** Reducir deltaT a la mitad.
3. **Malla o escritura:** Cambiar writeInterval sin alterar dimensiones físicas.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/10a-tuberia-laminar-case0 /tmp/10a-tuberia-laminar-case0-variante
cd /tmp/10a-tuberia-laminar-case0-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
