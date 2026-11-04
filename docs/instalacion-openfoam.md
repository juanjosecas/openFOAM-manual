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
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil
bash cases/09-cavidad-con-tapa-movil/run_docker.sh
```

Consultar [lanzador general](ejecutar-con-docker.md) y [scripts por caso](docker-por-caso.md). Los resultados se conservan en el directorio del caso según el lanzador. La pertenencia al grupo `docker` concede privilegios elevados sobre el host; evitar agregar usuarios indiscriminadamente.


### Docker sin sudo

En Ubuntu, RHEL, Rocky y AlmaLinux, Docker Engine suele requerir privilegios para acceder al daemon. Hay dos opciones:

**Grupo docker (sencillo, pero equivalente a privilegios de root sobre el host):**

~~~bash
sudo groupadd -f docker
sudo usermod -aG docker "$USER"
newgrp docker
docker info
docker run --rm hello-world
~~~

La pertenencia al grupo se aplica tras abrir una nueva sesión o ejecutar `newgrp docker`. **El grupo docker otorga acceso prácticamente equivalente a root**: no utilizarlo en servidores multiusuario sin evaluar esa implicancia. No modificar los permisos del socket con `chmod 666` ni `chmod 777`. Documentación: [Docker post-install](https://docs.docker.com/engine/install/linux-postinstall/).

**Docker rootless (daemon sin root):**

~~~bash
# Ubuntu con Docker Engine instalado desde el repositorio oficial
sudo apt install -y uidmap docker-ce-rootless-extras
dockerd-rootless-setuptool.sh install
systemctl --user enable --now docker
docker context ls
docker context use rootless
docker info
~~~

Si se necesita mantener el daemon del usuario activo sin sesión abierta, el administrador puede habilitar `loginctl enable-linger` para ese usuario. En RHEL/Rocky/Alma los nombres de paquetes y las dependencias son diferentes; consultar [instalación rootless oficial](https://docs.docker.com/engine/security/rootless/). Rootless requiere soporte para namespaces de usuario y puede tener restricciones de red/almacenamiento. No ejecutar el instalador rootless con sudo. Si `DOCKER_HOST` está definido, puede prevalecer sobre el contexto seleccionado.

### Terminal interactiva de OpenFOAM v2406

Desde la raíz de `openFOAM-manual`:

~~~bash
docker run --rm -it --init \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$(pwd):/workspace" \
  -w /workspace \
  --entrypoint /bin/bash \
  opencfd/openfoam-default:2406 \
  -c 'source /usr/lib/openfoam/openfoam2406/etc/bashrc; exec bash -i'
~~~

| Opción | Función |
| --- | --- |
| `-it` | Abre una terminal interactiva con entrada estándar y TTY |
| `--rm` | Elimina el contenedor al salir, no los archivos de la carpeta montada |
| `--init` | Reenvía señales y recoge procesos hijos |
| `--user "$(id -u):$(id -g)"` | Evita crear resultados propiedad de root |
| `-e HOME=/tmp` | Proporciona un directorio HOME escribible |
| `-v "$(pwd):/workspace"` | Comparte el repositorio con el host |
| `-w /workspace` | Abre Bash en la carpeta compartida |
| `--entrypoint /bin/bash` | Evita depender del entrypoint de la imagen |
| `source .../etc/bashrc` | Carga el entorno de OpenFOAM v2406 |

Dentro de la terminal:

~~~bash
echo "$WM_PROJECT_VERSION"
which blockMesh
cd cases/09-cavidad-con-tapa-movil
ls
bash Allrun
exit
~~~

Para ejecutar comandos sin interacción, **no agregar `-it`**. El montaje es esencial: los archivos fuera de `/workspace` se pierden al borrar el contenedor con `--rm`.

### Función de Bash para abrir el contenedor con un comando

Agregar a `~/.bashrc` del host:

~~~bash
foam2406() {
  local repo
  repo="$(realpath "$HOME/openFOAM-manual")"
  if [[ ! -d "$repo/cases" ]]; then
    echo "No se encuentra el repositorio: $repo" >&2
    return 1
  fi
  docker run --rm -it --init \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    --mount "type=bind,source=$repo,target=/workspace" \
    -w /workspace \
    --entrypoint /bin/bash \
    opencfd/openfoam-default:2406 \
    -c 'source /usr/lib/openfoam/openfoam2406/etc/bashrc; exec bash -i'
}
~~~

Recargar Bash y entrar:

~~~bash
source ~/.bashrc
foam2406
~~~

Si el repositorio no está en `~/openFOAM-manual`, cambiar la ruta dentro de la función. Este atajo no instala OpenFOAM en el host y deja todos los resultados del repositorio en el host.

### Ejecutar un caso sin entrar a Docker

Los lanzadores del repositorio ya configuran UID/GID, montaje, directorio de trabajo y carga de `etc/bashrc`:

~~~bash
bash scripts/run_docker.sh --list
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --mesh
bash scripts/run_docker.sh 09-cavidad-con-tapa-movil --dry-run
~~~

Para ejecutar casos desde cualquier carpeta, añadir a `~/.bashrc`:

~~~bash
foamrun() {
  bash "$HOME/openFOAM-manual/scripts/run_docker.sh" "$@"
}
~~~

Entonces:

~~~bash
source ~/.bashrc
foamrun --list
foamrun 09-cavidad-con-tapa-movil
foamrun 28-flujo-transitorio-alrededor-vaca
~~~

Si se clonó el repositorio en otra ubicación, modificar la ruta del atajo. Los resultados permanecen en `cases/`. `--rm` no borra los datos montados.

### Opciones útiles para simulaciones

- **Recursos:** agregar `--cpus 4 --memory 8g` al comando `docker run` para limitar CPU y RAM. Esto **no** activa MPI automáticamente.
- **ParaView:** usar ParaView instalado en el host para abrir resultados de `cases/`; normalmente no se necesita X11 ni `--privileged`.
- **SELinux (RHEL/Rocky/Alma):** si un bind mount privado falla por etiquetado, evaluar `-v "$(pwd):/workspace:Z"`. `:Z` cambia etiquetas SELinux y puede afectar otros procesos: no aplicarlo a carpetas compartidas sin comprobarlo.
- **Reinicio de simulaciones:** conservar archivos `.cpt` y usar el mecanismo de continuación adecuado al solver. Los scripts `Allrun` no necesariamente reanudan un cálculo.
- **Almacenamiento:** `docker system df` muestra uso de disco; evitar `docker system prune -a --volumes` sin revisar los datos que eliminaría.
- **Imágenes:** fijar la etiqueta `2406`, no `latest`; para reproducibilidad estricta puede utilizarse un digest SHA256 verificado.
- **Puertos:** los casos CFD no necesitan `-p`. Si se utiliza Jupyter, publicar el puerto exclusivamente en `127.0.0.1` salvo necesidad justificada.
- **Comprobación:** `docker context ls`, `docker info`, `id -nG` y `docker image inspect opencfd/openfoam-default:2406` ayudan a diagnosticar problemas.

### Errores frecuentes de Docker

| Error | Comprobación |
| --- | --- |
| `permission denied /var/run/docker.sock` | Grupo `docker` con sesión renovada o daemon rootless |
| `Cannot connect to Docker daemon` | `systemctl status docker` / `systemctl --user status docker` y `docker context ls` |
| Archivos creados como root | Usar `--user "$(id -u):$(id -g)"` |
| `blockMesh: command not found` | Cargar `source /usr/lib/openfoam/openfoam2406/etc/bashrc` |
| `the input device is not a TTY` | Eliminar `-it` en scripts y CI |
| `permission denied` en bind mount de RHEL | Verificar UID/GID y SELinux; evaluar `:Z` |
| Archivos desaparecen al salir | Montar el directorio de resultados; `--rm` elimina el sistema de archivos interno |

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

Para comprobar el flujo de trabajo del manual, utilizar el [caso 09: cavidad 2D](tutoriales/09-cavidad-con-tapa-movil.md), o su lanzador Docker. Una instalación funcional no garantiza que todos los tutoriales estén validados numéricamente.

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
