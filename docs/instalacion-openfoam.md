# Instalación de OpenFOAM: Ubuntu, RHEL, Docker y Conda

Este manual utiliza **OpenFOAM.com v2406 (OpenCFD)**. No debe confundirse con **OpenFOAM Foundation** (versiones numeradas como 12, 13 o 14): son distribuciones diferentes y algunos solvers, rutas y diccionarios no son intercambiables.

> **Recomendación para reproducir los tutoriales:** Docker con `opencfd/openfoam-default:2406`. Para trabajo diario en una estación Linux, instalación nativa v2406. Conda-forge es una alternativa, pero su paquete publicado es **2412**, no 2406.

## 1. Ubuntu 22.04 / 24.04: paquetes nativos

OpenCFD publicó paquetes de v2406 para Ubuntu 18.04, 20.04, 22.04 y 24.04. **No utilizar `sudo apt install openfoam` como sinónimo de v2406:** el paquete `openfoam` del repositorio estándar de Ubuntu 24.04 corresponde a la versión **1912**, muy anterior.

### Preparar repositorios

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
lsb_release -a
```

Agregar el repositorio **oficial de OpenCFD** siguiendo las instrucciones de paquetes precompilados de la versión/distribución instalada:

- [Instalación OpenCFD en Linux](https://www.openfoam.com/download/openfoam-installation-on-linux)
- [Repositorio y paquetes precompilados (GitLab)](https://gitlab.com/openfoam/core/openfoam/-/wikis/precompiled)
- [Anuncio y plataformas soportadas de v2406](https://www.openfoam.com/news/main-news/openfoam-v2406)

La URL de paquetes y las claves de firma pueden cambiar. **No incorporar repositorios APT de terceros ni desactivar la comprobación de firmas.** Una vez agregado el repositorio oficial, inspeccionar los nombres disponibles:

```bash
sudo apt update
apt-cache search '^openfoam2406'
apt-cache policy openfoam2406-default
```

Si el repositorio ofrece `openfoam2406-default`, instalarlo:

```bash
sudo apt install openfoam2406-default
```

Si el nombre no aparece, consultar los paquetes disponibles en ese repositorio y no reemplazarlo automáticamente por `openfoam`. El nombre exacto del paquete puede depender de la distribución y del repositorio habilitado.

### Activar y verificar

La instalación típica de OpenCFD ubica el entorno en `/usr/lib/openfoam/openfoam2406/etc/bashrc`; **comprobar la ruta real antes de cargarla**:

```bash
dpkg -L openfoam2406-default | grep '/etc/bashrc$'
source /usr/lib/openfoam/openfoam2406/etc/bashrc
echo "$WM_PROJECT_VERSION"
command -v blockMesh
blockMesh -help | head
```

Si `dpkg -L` muestra otra ruta, usar esa. Para que el entorno se active automáticamente, añadir la línea `source` comprobada a `~/.bashrc` (solo si se desea trabajar siempre con v2406).

## 2. Red Hat Enterprise Linux 9, Rocky Linux 9 y AlmaLinux 9

OpenCFD documenta paquetes de **v2406 para EPEL 9**. Esto no implica que todas las versiones posteriores de RHEL ni todas las arquitecturas dispongan de los mismos RPM. La instalación requiere repositorios habilitados y privilegios administrativos.

### Preparar el sistema

En RHEL 9, habilitar el repositorio CodeReady Builder con la suscripción correspondiente. En Rocky/AlmaLinux 9, el repositorio equivalente suele llamarse CRB.

```bash
cat /etc/os-release
sudo dnf install -y dnf-plugins-core
```

**RHEL 9 (con suscripción habilitada):**

```bash
sudo subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
sudo dnf install -y epel-release
```

**Rocky Linux 9 / AlmaLinux 9:**

```bash
sudo dnf config-manager --set-enabled crb
sudo dnf install -y epel-release
```

Luego consultar la disponibilidad real:

```bash
sudo dnf makecache
dnf search openfoam
dnf list --available '*openfoam*'
```

Si el paquete de **v2406** aparece en los repositorios habilitados, instalarlo con el **nombre exacto que devuelve DNF**:

```bash
sudo dnf install NOMBRE_EXACTO_DEL_PAQUETE_V2406
```

La última línea es una **plantilla**, no un comando para copiar sin reemplazar el nombre. No se garantiza que EPEL 9 mantenga todos los paquetes históricos de v2406 en sus mirrors actuales. Si no aparece, preferir Docker en lugar de instalar un RPM de procedencia incierta.

Localizar el entorno y comprobar la versión:

```bash
rpm -ql NOMBRE_EXACTO_DEL_PAQUETE_V2406 | grep '/etc/bashrc$'
# source /ruta/real/mostrada/etc/bashrc
# echo "$WM_PROJECT_VERSION"
```

**Notas para HPC:** en clusters con Slurm, SELinux o políticas restrictivas, consultar si hay módulos de entorno (`module avail openfoam`) o Apptainer. Docker puede estar prohibido en nodos de cómputo. No desactivar SELinux para ejecutar OpenFOAM.

Fuentes: [OpenCFD v2406 y EPEL 9](https://www.openfoam.com/news/main-news/openfoam-v2406) y [paquetes precompilados](https://gitlab.com/openfoam/core/openfoam/-/wikis/precompiled).

## 3. Docker: método recomendado para estos tutoriales

El repositorio de Docker Hub **sí conserva la etiqueta exacta `2406`** en `opencfd/openfoam-default`. Hay imágenes para `linux/amd64` y `linux/arm64`.

### Instalar y verificar Docker

Instalar Docker Engine mediante los repositorios oficiales de la distribución ([Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [RHEL](https://docs.docker.com/engine/install/rhel/)). Comprobar:

```bash
docker version
docker info
docker pull opencfd/openfoam-default:2406
```

No usar `:latest`: apunta a otra versión. No usar `--privileged` para simulaciones ordinarias.

### Abrir una terminal de OpenFOAM v2406

Desde la raíz del repositorio:

```bash
docker run --rm -it \
  --mount type=bind,source="$(pwd)",target=/work \
  -w /work \
  opencfd/openfoam-default:2406 \
  bash
```

Dentro del contenedor:

```bash
echo "$WM_PROJECT_VERSION"
command -v blockMesh
blockMesh -help | head
```

Si el entorno no se cargó automáticamente, localizar el `etc/bashrc` de OpenFOAM dentro del contenedor y cargarlo con `source`.

Para ejecutar un caso existente **sin escribir comandos Docker a mano**, el repositorio incluye lanzadores:

```bash
bash scripts/run_docker.sh --list
bash scripts/run_docker.sh 09-cavity-2d
bash cases/09-cavity-2d/run_docker.sh
```

Consultar [lanzador general](ejecutar-con-docker.md) y [scripts por caso](docker-por-caso.md). Los resultados se conservan en el directorio del caso según el lanzador. La pertenencia al grupo `docker` concede privilegios elevados sobre el host; evitar agregar usuarios indiscriminadamente.

## 4. Conda-forge / Mamba: sí existe OpenFOAM

Existe un feedstock oficial de conda-forge llamado **`openfoam`**. La versión publicada en Anaconda.org es **2412**, para **Linux x86-64 (`linux-64`)**. No debe presentarse como instalación de v2406 ni como soporte nativo garantizado para Windows/macOS.

- [Paquete en Anaconda.org](https://anaconda.org/channels/conda-forge/packages/openfoam/overview)
- [Receta y mantenedores de conda-forge](https://github.com/conda-forge/openfoam-feedstock)

### Consultar versiones y crear un entorno aislado

```bash
# Con micromamba o mamba instalados previamente
micromamba search -c conda-forge openfoam
micromamba create -n openfoam-cf -c conda-forge openfoam=2412
micromamba activate openfoam-cf

# Diagnóstico: no asumir que la activación cargó todo el entorno CFD
command -v blockMesh
command -v simpleFoam
echo "$WM_PROJECT_VERSION"
```

Alternativa con Conda:

```bash
conda search -c conda-forge openfoam
conda create -n openfoam-cf -c conda-forge openfoam=2412
conda activate openfoam-cf
```

**Comprobar la versión disponible antes de instalar:** las recetas pueden cambiar o retirarse. El paquete puede requerir configuración adicional de variables de entorno o bibliotecas MPI; verificar `blockMesh`, `simpleFoam` y el entorno antes de ejecutar los tutoriales.

### ¿Conda es adecuado para este manual?

- **Sí**, para probar OpenFOAM 2412 en Linux x86-64 sin instalar paquetes de sistema, sujeto a disponibilidad y funcionamiento de la receta.
- **No como sustituto exacto de v2406**, porque las versiones no coinciden. Las diferencias entre versiones deben comprobarse caso por caso.
- Para reproducibilidad estricta de este repositorio, **Docker 2406** es la opción preferida.

## 5. Verificación común de instalación

Con el entorno OpenFOAM cargado:

```bash
echo "Versión: $WM_PROJECT_VERSION"
command -v blockMesh
command -v simpleFoam
command -v pimpleFoam
blockMesh -help | head -n 12
```

Si un comando no aparece, no ejecutar todavía un caso: primero identificar qué distribución, versión y entorno están activos. En versiones recientes algunos solvers se invocan mediante `foamRun` en lugar de ejecutables independientes; **la ausencia de `simpleFoam` en una distribución diferente no demuestra por sí sola una instalación defectuosa**.

Para comprobar el flujo de trabajo del manual, utilizar el [caso 09: cavidad 2D](tutoriales/09-cavity-2d.md), o su lanzador Docker. Una instalación funcional no garantiza que todos los tutoriales estén validados numéricamente.

## 6. Errores habituales

| Síntoma | Diagnóstico |
| --- | --- |
| `blockMesh: command not found` | No se cargó `etc/bashrc`, o se instaló un paquete distinto |
| `WM_PROJECT_VERSION` vacío | Entorno OpenFOAM no activado |
| `apt install openfoam` instala 1912 | Se eligió el paquete genérico de Ubuntu, no el de OpenCFD v2406 |
| `dnf search openfoam` no encuentra v2406 | Repositorios EPEL/CRB incompletos, paquete histórico no disponible o arquitectura incompatible |
| `docker: permission denied` | Revisar permisos y daemon Docker, sin usar `chmod 777 /var/run/docker.sock` |
| Conda instala 2412 | Es la versión del paquete conda-forge; no coincide con los tutoriales v2406 |
| Error al ejecutar `simpleFoam` en otra versión | Verificar compatibilidad del solver y si se requiere `foamRun` |

**Estado de verificación:** disponibilidad y versiones contrastadas con documentación oficial; los comandos nativos dependen del estado de repositorios del host y no se han ejecutado en Ubuntu/RHEL reales durante esta revisión. Docker `:2406` y conda-forge `openfoam=2412` están documentados públicamente; tampoco se ejecutó aquí una simulación CFD.
