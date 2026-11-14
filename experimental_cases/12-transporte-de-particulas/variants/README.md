# Variantes controladas de 12-goldschmidt-particulas

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Después de adaptar DPMFoam, reducir deltaT.
2. **Modelo o integración:** Cambiar writeInterval.
3. **Malla o escritura:** Identificar y modificar ligeramente un parámetro de inyección en kinematicCloudProperties.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/12-goldschmidt-particulas /tmp/12-goldschmidt-particulas-variante
cd /tmp/12-goldschmidt-particulas-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
