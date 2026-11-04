# Variantes controladas de 08-tuberia-cilindrica-3d

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Reducir un 25 % la amplitud de la tabla de velocidad de 0/U; conservar los mismos instantes.
2. **Modelo o integración:** En controlDict cambiar maxCo de 0.5 a 0.25.
3. **Malla o escritura:** Cambiar writeInterval de 0.01 a 0.02 s; conservar el esquema temporal.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/08-tuberia-cilindrica-3d /tmp/08-tuberia-cilindrica-3d-variante
cd /tmp/08-tuberia-cilindrica-3d-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
