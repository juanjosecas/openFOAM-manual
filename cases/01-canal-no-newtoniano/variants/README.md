# Variantes controladas de 01-canal-no-newtoniano

Estas variantes **no sustituyen el caso original** ni se aplican automáticamente. Crear una copia independiente y modificar una sola dimensión del problema por vez:

1. **Condición física:** Disminuir la velocidad de entrada de 0.01 a 0.005 m/s en 0/U, manteniendo consistentemente el campo inicial y el patch inlet.
2. **Modelo o integración:** Cambiar n de 0.5 a 0.7 en constant/turbulenceProperties.
3. **Malla o escritura:** En blockMeshDict cambiar (200 40 1) a (100 20 1); reconstruir malla.

## Procedimiento

```bash
# Desde la raíz del repositorio:
cp -a cases/01-canal-no-newtoniano /tmp/01-canal-no-newtoniano-variante
cd /tmp/01-canal-no-newtoniano-variante
# Editar ÚNICAMENTE el parámetro elegido.
# Si cambia blockMeshDict, reconstruir la malla antes de ejecutar.
```

No copiar resultados ni mezclar archivos temporales. Registrar unidades, archivo editado, valor original y nuevo, y resultado observable. **Los casos heredados de Foundation deben adaptarse previamente a OpenFOAM.com; no se afirma que estas variantes hayan sido ejecutadas.**
