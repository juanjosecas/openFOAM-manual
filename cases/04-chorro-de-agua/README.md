# Tutorial 04 — Chorro de agua en aire

**Estado:** configuración reconstruida documentalmente; sin ejecución ni validación física. Los archivos de condiciones de contorno y propiedades conservan sus valores originales.

## Preparación y cálculo

Desde la raíz del repositorio, con OpenFOAM.com cargado:

```bash
cd cases/04-chorro-de-agua
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

[Guía general](../../docs/guia-ejecucion-y-variantes.md)

## Ensayos pequeños

Reducir velocidad de entrada 20 %, reducir `maxCo` a 0.25, o variar `writeInterval`. Probar un parámetro por copia limpia.

## Revisión estática v2406

Dominio 300 × 200 mm, espesor numérico 1 mm, 9600 celdas. Entrada de 10 mm de altura a 1 m/s: Re basado en altura=10000 para agua; solo cuatro celdas atraviesan la entrada. El modelo laminar y 2D no resuelve turbulencia tridimensional, atomización ni gotas pequeñas. Se conserva la física original. El caudal nominal de agua es 1e-5 m³/s para el espesor de representación; la atmósfera superior y lateral permite salida, por lo que la masa del agua dentro del dominio no tiene que ser constante. Revisar balance de fase, límites alpha.water, Co y resolución de la interfaz. El caso de 20 s puede guardar unas 4000 escrituras (base) o 1000 (animation); para diagnóstico reducir endTime en la copia. No se ha ejecutado.

El paso inicial es 1e-5 s, maxCo y maxAlphaCo son 0.35; el campo inicial de aire se conserva.
