# Gráficos y propiedades de los sistemas

La extracción de datos y la preparación de figuras **no modifican** los casos. Los siguientes comandos consumen resultados previamente calculados; no ejecutan el solver.

## Diagnósticos del solver

Desde la raíz del repositorio:

```bash
python -m pip install matplotlib pandas
python scripts/plot_solver_log.py cases/08-tuberia-cilindrica-3d/log.pimpleFoam --output plots/08
```

El script analiza las líneas `Solving for ... Initial residual` y `Courant Number mean ... max ...` presentes en un log. No todos los solvers registran ambas. Las curvas son **diagnósticos numéricos**, no propiedades físicas, y el eje horizontal de residuos identifica posiciones de registro, no segundos.

## Propiedades físicas

Los campos se visualizan con ParaView mediante el archivo `.foam`, o se exportan mediante `postProcess`/`foamToVTK` según el solver y la versión. Los casos 09, 10A, 10B y 10C ya incluyen `system/sampleDict`: conservar sus definiciones de muestreo y comprobar qué comando de postprocesamiento corresponde a la instalación. No reemplazar ni sobrescribir ese archivo sin revisar su sintaxis.

Para CSV **que ya contiene encabezados de columnas**, usar:

```bash
python scripts/plot_csv.py perfil.csv --x x --y Ux --output plots/velocidad.png
python scripts/plot_csv.py presion.csv --x x --y p --output plots/presion.png
```

Los nombres `x`, `Ux` y `p` son ejemplos: inspeccionar primero las columnas reales del CSV. Si el archivo tiene varias cabeceras, vectores entre paréntesis o delimitación especial, normalizar su estructura antes de ejecutar el script. Para visualizar magnitudes de campos 3D y vectores utilizar ParaView/PyVista, tal como se explica en el anexo de exportación; el script CSV no reemplaza un posprocesador volumétrico.

## Qué graficar en cada tutorial

| Caso | Propiedades prioritarias | Observaciones |
| --- | --- | --- |
| 01, 02, 03 | Perfil de velocidad, presión, magnitud de U, viscosidad efectiva (si se escribe) | `simpleFoam`: gráficos espaciales/iterativos, no evolución temporal física |
| 04 | Fracción de agua `alpha.water`, velocidad y presión `p_rgh` | Faltan archivos esenciales; solo tras completar el caso |
| 05 | Posición/velocidad de la esfera, fuerzas y campo circundante | Sin caso ejecutable; depende del modelo que se elija |
| 06 | Comparación de métricas de las corridas paramétricas | Tutorial de automatización, no caso CFD independiente |
| 07 | Velocidad y presión sobre el dominio importado | Requiere recuperar geometría y scripts |
| 08 | Velocidad axial y transversal, presión, Courant y evolución de caudal | Transitorio; identificar correctamente el eje de la tubería |
| 09 | Velocidad horizontal/vertical, centro del vórtice, residuos | Mantener el `sampleDict` existente |
| 10A–C | Perfil radial de velocidad, presión axial, desarrollo laminar | Mantener `sampleDict`; en 10C no tratar iteraciones como tiempo |
| 11 | `alpha.water`, altura de la interfaz, velocidad, Courant | Ejecutar `setFields` antes del solver en un caso nuevo |
| 12 | Campo gaseoso, cantidad/velocidad de partículas, caudal sólido si disponible | Datos lagrangianos dependen del modelo y compatibilidad |

## Precauciones

Los campos escalares de presión de ciertos solvers incompresibles pueden tener dimensión cinemática ($\mathrm{m^2\,s^{-2}}$): no rotularlos automáticamente en pascales. Usar un rango fijo por variable en animaciones para que las comparaciones temporales sean consistentes. Registrar unidades, instante, geometría y configuración de cada variante. Ningún gráfico se ha generado con simulaciones durante esta revisión.
