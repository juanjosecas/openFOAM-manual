# Variantes controladas de 11-dambreak-2d

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Reducir maxCo si existe en controlDict.
2. **Modelo o integración:** Cambiar writeInterval para obtener más estados.
3. **Malla o escritura:** Desplazar ligeramente la columna inicial en setFieldsDict; reejecutar setFields antes del solver.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/11-dambreak-2d /tmp/11-dambreak-2d-variante
cd /tmp/11-dambreak-2d-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
