# Tutorial 04 — Chorro de agua en aire

**Estado:** configuración reconstruida documentalmente; sin ejecución ni validación física. Los archivos de condiciones de contorno y propiedades conservan sus valores originales.

## Preparación y cálculo

Desde la raíz del repositorio, con OpenFOAM.com cargado:

```bash
cd cases/04-chorro-agua
foamVersion
blockMesh
checkMesh
foamDictionary system/controlDict -entry application -value
interFoam
```

Alternativamente ejecutar `bash Allrun` desde el caso; no mezclar los dos procedimientos. El lanzador crea la malla, la comprueba y registra la ejecución. `Allmesh` ejecuta solamente mallado y `Allclean` protege resultados con previsualización.

## Decisiones

- `system/controlDict` reconstruido con solver `interFoam`, paso inicial pequeño y límites conservadores de Courant.
- Se conserva el aire inicial en el dominio y el agua entrante (`alpha.water`). **No se requiere `setFields`** para este escenario.
- Sin ejecutar el caso, no se puede garantizar compatibilidad completa de las condiciones de contorno y los esquemas con v2406/v2412.

[Decisiones y detalles](COMPLETADO.md) · [Guía general](../../docs/guia-ejecucion-y-variantes.md)

## Ensayos pequeños

Reducir velocidad de entrada 20 %, reducir `maxCo` a 0.25, o variar `writeInterval`. Probar un parámetro por copia limpia.
