# Goldschmidt: dependencias no reconstruibles con seguridad

El caso proviene de OpenFOAM Foundation 8 y todavía no es autónomo.

- El modelo de inyección exige `kinematicCloudPositions`, archivo ausente. No se inventan coordenadas de partículas.
- `0/U.air` referencia `alpha.air` y `phi.air`, que no están definidos en los archivos iniciales presentes; su creación depende del solver original.
- El encabezado de `kinematicCloudProperties` declara `object particleProperties`: requiere confirmar la interfaz del modelo de Foundation.
- `DPMFoam` y la física de partículas no están portados a OpenFOAM.com v2406/v2412.

Para completar este caso se necesita el archivo de posiciones del ejemplo original o especificar explícitamente una nueva condición inicial de partículas y elegir un modelo compatible. La malla puede estudiarse de manera independiente; no se recomienda lanzar el solver tal como está.
