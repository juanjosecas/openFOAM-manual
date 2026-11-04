# Casos oficiales v2406: cilindro, escalón y placa perforada

Se incorporan tres tutoriales de OpenCFD mediante **importación íntegra desde la imagen Docker v2406**. El importador copia los archivos originales de cada caso, incluidos los diccionarios de 0/, constant/ y system/. No se generan topologías ni configuraciones físicas incompletas. Los casos importados se almacenan en cases/ y no se sobrescriben.

## Preparación

Desde la raíz del repositorio, con Docker disponible sin sudo:

~~~bash
python3 scripts/import_official_tutorial.py --list
python3 scripts/import_official_tutorial.py 27-cilindro-potencial
python3 scripts/import_official_tutorial.py 28-escalon-turbulento
python3 scripts/import_official_tutorial.py 29-placa-agujero
~~~

El importador verifica que la carpeta de destino no exista y que el tutorial de origen contenga system/controlDict. Para inspeccionar sin importar:

~~~bash
python3 scripts/import_official_tutorial.py 27-cilindro-potencial --dry-run
~~~

Ejecución y logs, persistentes en el repositorio:

~~~bash
python3 scripts/run_official_tutorial.py 27-cilindro-potencial
python3 scripts/run_official_tutorial.py 28-escalon-turbulento
python3 scripts/run_official_tutorial.py 29-placa-agujero
~~~

El ejecutor utiliza el Allrun original cuando existe; de lo contrario intenta blockMesh, checkMesh y el solver correspondiente. Algunos tutoriales necesitan otras etapas de preparación: **revisar los archivos importados antes de ejecutarlos**. No se ha validado aún una ejecución real de los tres casos.

## 27. Cilindro en flujo potencial

- [Tutorial Guide oficial 2.2](https://www.openfoam.com/documentation/tutorial-guide/2-incompressible-flow/2.2-flow-around-a-cylinder).
- Origen: $FOAM_TUTORIALS/basic/potentialFoam/cylinder.
- Solver: potentialFoam.
- Física: flujo incompresible, inviscido, irrotacional y estacionario.
- Ejercicios: variar nNonOrthogonalCorrectors (0, 1, 3); refinar malla; comparar líneas de corriente con solución analítica.

**PIMPLE no corresponde al caso oficial**: potentialFoam no resuelve estelas viscosas ni desprendimiento de vórtices. Una versión pimpleFoam necesitaría otro problema físico, condiciones de contorno, viscosidad y validación; cambiar el nombre del solver no es suficiente.

## 28. Escalón hacia atrás

- [Tutorial Guide oficial 3.1](https://www.openfoam.com/documentation/tutorial-guide/3-compressible-flow/3.1-steady-turbulent-flow-over-a-backward-facing-step).
- Origen: $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily.
- Solver: simpleFoam.
- Física: separación, recirculación, reenganche y flujo turbulento incompresible.
- Ejercicios: gradación de malla, Reynolds, modelos RANS y longitud de reenganche.

Una variante **pimpleFoam sería pertinente** únicamente para estudiar dinámica temporal de la recirculación. Requiere condiciones iniciales y de contorno consistentes, términos temporales en fvSchemes, fvSolution/PIMPLE, control del número de Courant y validación independiente. Se mantiene el caso estacionario oficial hasta verificar esa conversión.

## 29. Placa perforada

- [Tutorial Guide oficial 5.1](https://www.openfoam.com/documentation/tutorial-guide/5-stress-analysis/5.1-stress-analysis-of-a-plate-with-a-hole).
- Origen: $FOAM_TUTORIALS/stressAnalysis/solidDisplacementFoam/plateHole.
- Solver: solidDisplacementFoam.
- Física: elasticidad lineal y concentración de tensiones alrededor de un agujero.
- Ejercicios: refinar cerca del agujero, modificar dimensiones de la placa, comparar con solución analítica.

El factor de concentración de tensiones tiende a 3 para una placa infinita con agujero circular bajo tracción uniaxial; el caso finito puede diferir. **PIMPLE no aplica** a este problema de elasticidad.

## Otros casos ya presentes

La cavidad 2D (09-cavity-2d) y la rotura de presa (11-dambreak-2d) ya tienen implementaciones propias. Se recomienda ampliarlas con estudios de refinamiento, Reynolds y sensibilidad de parámetros, sin duplicar los casos.

## Alcance y límites

- Los archivos importados proceden de la distribución instalada dentro de la imagen oficial. Si una ruta no existe en v2406, el importador falla explícitamente.
- Para reproducibilidad binaria estricta, fijar el digest SHA256 de la imagen además de la etiqueta 2406.
- Los scripts no alteran los casos existentes.
- No se ha ejecutado Docker ni comprobado convergencia numérica en esta sesión.
