# Rotura de presa en 2D

Una columna de agua cae por gravedad, se desplaza sobre el fondo y alcanza un obstáculo. Se utiliza VOF para seguir el frente de agua.

## Configuración base

Solver: `interFoam`. Columna inicial de 146.1 × 292 mm, espesor 14.6 mm; volumen geométrico aproximado 0.623 L. Inicialización con setFields; malla fija.

## Ejecutar

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 11-rotura-de-presa-2d --output runs/presa
bash scripts/run_docker.sh runs/presa
```

Para modificar el modelo, editar la copia antes de ejecutar. Si cambia geometría o resolución, preparar una copia nueva. Con OpenFOAM cargado se puede usar `bash Allrun` dentro de la copia.

## Qué modificar

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `system/setFieldsDict` | `regions/boxToCell/box` | Ancho y altura iniciales. Probar extremo superior (0.1461 0.25 1); la caja debe cubrir el espesor. |
| `0/alpha.water` | `internalField` | Aire inicial (0); setFields asigna 1 a la columna. |
| `0/U, 0/p_rgh` | `internalField, boundaryField` | Reposo inicial, paredes impermeables y atmósfera abierta. |
| `constant/g` | `value` | Gravedad; determina aceleración de la caída. |
| `constant/transportProperties` | `nu, rho, sigma de las fases` | Viscosidad, densidad y tensión superficial. |
| `system/blockMeshDict` | `vertices, blocks` | Dominio, obstáculo y resolución; conservar compatibilidad de bloques. |
| `system/controlDict` | `maxCo, maxAlphaCo, maxDeltaT, writeInterval` | Límites 0.5, paso máximo 0.005 s; reducir a 0.25 para comparar integración. |
| `system/probesDict` | `probeLocations` | Sondas internas de velocidad y presión; requieren invocación explícita. |

Allrun realiza setFields después del mallado. La variante animation guarda estados con mayor frecuencia; --variant animation. El volumen discretizado inicial depende de los centros de celda seleccionados.

## Resultados

Desde la raíz del repositorio, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas:

```bash
python postprocessing/fields.py runs/presa --field alpha.water --normal z --clim 0 1
python postprocessing/animate.py runs/presa --field alpha.water --clim 0 1 --output plots/presa.gif
python postprocessing/statistics.py runs/presa --field alpha.water
python postprocessing/plot_solver_log.py runs/presa/log.interFoam
```

Revisar posición del frente, integral de alpha.water y Courant. Considerar salida por la atmósfera en el balance. Configuración actual sin nueva ejecución.
