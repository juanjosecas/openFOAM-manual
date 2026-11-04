# Ejecutar casos OpenFOAM v2406 con Docker

Este método usa la imagen `opencfd/openfoam-default:2406` y **no requiere instalar OpenFOAM en el host**. Solo se necesitan Bash y Docker Engine funcionando. La imagen se descarga automáticamente la primera vez que se ejecuta.

Desde la raíz del repositorio:

```bash
# Mostrar casos y comprobar cuáles contienen Allrun o Allmesh
bash scripts/run_docker.sh --list

# Ejecutar el Allrun de un caso sencillo
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil

# Ejecutar la simulación estacionaria (simpleFoam)
bash scripts/run_docker.sh 27-flujo-estacionario-alrededor-vaca

# Ejecutar la simulación transitoria (pimpleFoam)
bash scripts/run_docker.sh 28-flujo-transitorio-alrededor-vaca

# Construir únicamente la malla si existe Allmesh
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --mesh

# Inspeccionar el comando sin iniciar Docker
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --dry-run
```

Se puede ejecutar el lanzador desde cualquier directorio utilizando la ruta absoluta a `scripts/run_docker.sh`.

## ¿Qué hace el script?

1. Localiza la raíz del repositorio a partir de la ubicación del propio script.
2. Comprueba que existe `cases/<nombre>` y que contiene el `Allrun` o `Allmesh` seleccionado.
3. Inicia un contenedor **temporal** con la imagen `opencfd/openfoam-default:2406`. Se utiliza `--entrypoint /bin/bash` para evitar depender del entrypoint propio de la imagen.
4. Monta el repositorio del host como `/workspace` en modo escritura. Se monta todo el repositorio porque algunos casos leen ficheros de otras carpetas (por ejemplo, la malla de `27-flujo-estacionario-alrededor-vaca` desde `28-flujo-transitorio-alrededor-vaca`).
5. Establece `/workspace/cases/<nombre>` como directorio de trabajo, carga `/usr/lib/openfoam/openfoam2406/etc/bashrc` y ejecuta `bash ./Allrun` (o `bash ./Allmesh`).
6. Ejecuta como el UID/GID del usuario local para que logs y resultados no queden normalmente propiedad de root; al finalizar elimina el **contenedor**, pero no los resultados generados.

El comportamiento concreto de cada caso sigue estando definido en su propio `Allrun`/`Allmesh`: generación de malla, `checkMesh`, solver, archivos de log, etc. **El lanzador no elige ni corrige el solver**. No existe una garantía general de que todos los casos sean ejecutables: algunos solo tienen `Allmesh`, algunos necesitan generar geometrías u otros archivos antes, y otros requieren dependencias adicionales.

## Cómo interpretar los resultados

Por ejemplo, para `09-cavidad-con-tapa-movil` los logs quedan en `cases/09-cavidad-con-tapa-movil/log.*` y los tiempos calculados en sus carpetas numéricas, según `system/controlDict`. No se genera una animación automáticamente: la escritura de tiempos depende de `writeControl`/`writeInterval` del caso y la representación requiere una etapa de postprocesamiento.

La simulación **estacionaria** de la vaca utiliza `simpleFoam` e iteraciones; la **transitoria** utiliza `pimpleFoam` y escribe campos para distintos tiempos. Ambas tienen configuraciones independientes. Antes de ejecutar el transitorio, comprobar que está disponible `27-flujo-estacionario-alrededor-vaca/cow_tunnel.msh`, porque su `Allrun` lo utiliza.

Para verificar Docker en el host:

```bash
docker info
docker pull opencfd/openfoam-default:2406
```

El comando `docker pull` es opcional si Docker puede descargar la imagen al hacer `run`. La invocación asume un daemon local o uno que pueda acceder a las mismas rutas del repositorio.

## Parámetros adicionales

```bash
# Imagen alternativa compatible; el script sigue cargando bashrc de v2406
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --image opencfd/openfoam-default:2406

# Equivalente mediante variable de entorno
FOAM_IMAGE=opencfd/openfoam-default:2406 bash scripts/run_docker.sh 09-cavidad-con-tapa-movil
```

**Importante:** montar el repositorio en modo escritura significa que un `Allrun` puede modificar o eliminar archivos a los que tenga acceso. Conviene revisar los scripts antes de ejecutarlos y no repetir una simulación que ya tenga resultados sin comprobar las condiciones de reinicio. El lanzador no ejecuta `Allclean` ni borra resultados automáticamente.

### Limitación de pruebas

El código se comprobó con `bash -n`, `--list` y `--dry-run` sobre un árbol de prueba, además de errores por casos sin `Allrun`. No se pudo lanzar una simulación CFD real en el entorno de pruebas porque Docker no está instalado allí. Eso no implica que los casos hayan sido validados numéricamente.
