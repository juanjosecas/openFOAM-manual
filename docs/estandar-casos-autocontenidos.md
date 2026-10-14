# Estándar obligatorio de autocontención para nuevos casos

**Aplicación:** todo nuevo directorio de `cases/`, comenzando por 14A. No confundir propuestas de investigación (14B–22) con casos ejecutables.

## Lista de aceptación

- [ ] Directorio propio `cases/NN-nombre/` con todos los archivos necesarios para generar malla y arrancar solver (`0/`, `constant/`, `system/`, geometría y fuentes auxiliares).
- [ ] `README.md` con versión objetivo, solver, estado real, ecuaciones, hipótesis, propiedades con **unidades**, significado de cada campo, comandos exactos de mallado, verificación, inicialización, solver y posproceso.
- [ ] `Allmesh`, `Allrun`, `Allclean` (limpieza con confirmación, preservando `0/`). Ningún script debe depender silenciosamente de archivos de otros casos o de `scripts/` del repositorio; las dependencias externas (OpenFOAM, Python, Gmsh) se declaran explícitamente.
- [ ] `variants/README.md` con tres cambios pequeños, uno por ensayo, indicando qué archivos cambian y cuándo regenerar la malla.
- [ ] `postprocessing/` con comandos y scripts propios para CSV, PNG y GIF/MP4 cuando el fenómeno tenga tiempo físico; si no corresponde una animación, justificarlo.
- [ ] URL **original exacta** y licencia/atribución si se copian archivos; diferenciar adaptación propia de reproducción fiel.
- [ ] Compatibilidad v2406/v2412 documentada y diferencias Foundation/foam-extend, sin afirmar pruebas no realizadas.
- [ ] Caso enlazado desde `docs/index.md` y `mkdocs.yml`; tutorial o README completo y enlaces internos válidos.
- [ ] Indicar qué verificaciones se hicieron: «revisión estática», «ejecutado», «comparado con referencia» o «validado». No sustituir una por otra.

## Estructura de referencia

```text
cases/NN-nombre/
  0/                      # Condiciones iniciales y patches
  constant/               # Propiedades físicas y modelos
  system/                 # Malla, solver, esquemas, control
  postprocessing/         # Extracción, CSV, gráficos, animaciones
  variants/README.md
  Allmesh
  Allrun
  Allclean
  README.md
```

Si se necesita geometría externa, agregarla en `geometry/` junto con su generador y los datos de entrada autorizados. No hacer referencia a un STL/SVG que no está en el caso. Si el solver no puede utilizarse en la versión objetivo, marcar el caso como **no ejecutable** hasta adaptarlo.

## Independencia y trazabilidad

Cada caso se debe poder copiar a una carpeta aislada y ejecutar con las **dependencias declaradas**, sin consultar otros directorios del repositorio. Los enlaces a la documentación central sirven para ampliar conceptos, pero no para completar archivos que falten. La URL original identifica la procedencia y **no** demuestra por sí misma compatibilidad, licencia o validación.
