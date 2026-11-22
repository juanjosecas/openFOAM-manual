# Canal plano con fluido no newtoniano

Flujo laminar estacionario entre dos paredes paralelas. El fluido adelgaza por cizallamiento; interesa medir cómo cambian el perfil de velocidad y la caída de presión con la reología.

## Configuración base

- **OpenFOAM:** v2406 (distribución OpenCFD).
- **Solver:** `simpleFoam`, flujo estacionario.
- **Canal:** longitud 200 mm, altura 20 mm, espesor de representación 1 mm.
- **Malla:** `200 × 40 × 1` celdas (8 000 celdas); una sola celda en la dirección z y caras `empty` para representar un problema bidimensional.
- **Entrada:** velocidad uniforme de 0.01 m/s. **Paredes:** `noSlip`. **Salida:** presión de referencia.
- **Modelo:** `powerLaw`, `n = 0.5`, `k = 1e-4`.

## Antes de empezar: qué es ejecutar un caso

**Entrar al contenedor y ver los archivos no inicia la simulación.** Un caso OpenFOAM contiene instrucciones, pero la malla y los campos calculados se generan al ejecutar comandos:

1. `blockMesh` lee `system/blockMeshDict` y crea `constant/polyMesh/`.
2. `checkMesh` verifica la malla que ya existe. No la construye.
3. `simpleFoam` resuelve las ecuaciones utilizando la malla y los archivos de condiciones iniciales/de contorno.
4. Los resultados se guardan en directorios numéricos como `100/`, `200/`, etc., según `system/controlDict`.

Estructura relevante:

```text
0/                           Condiciones iniciales y de borde: U, p...
constant/                    Propiedades del fluido y modelo físico
system/blockMeshDict         Geometría y resolución de la malla
system/controlDict           Solver, iteraciones y escritura de resultados
system/fvSchemes             Discretización
system/fvSolution            Solvers lineales y acoplamiento
constant/polyMesh/           Malla GENERADA por blockMesh (no existe inicialmente)
100/, 200/, ...              Resultados GENERADOS por simpleFoam
```

**Elegí una de las siguientes formas de ejecución.** Todas usan los mismos archivos de configuración; cambia dónde se ejecutan los comandos. Se recomienda trabajar en una copia para no ensuciar el caso original.

## Forma A — Docker automatizado (recomendada)

Requiere Docker funcionando en el host. **Estos comandos se ejecutan en la terminal de Linux, fuera del contenedor.**

Desde la raíz del repositorio:

```bash
# Crear una copia independiente y editable del tutorial
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --output runs/canal

# Preparar malla, verificarla y ejecutar el solver en OpenFOAM v2406
bash scripts/run_docker.sh runs/canal
```

El lanzador monta `runs/canal` en `/workspace` y ejecuta `Allrun` allí. Se generan `log.blockMesh`, `log.checkMesh` y `log.simpleFoam`, además de la malla y los resultados.

**Importante:** `runs/canal` debe ser una ruta que todavía no exista. Para repetir el experimento, elegí otro nombre, por ejemplo `runs/canal_n05`. El script rechaza ejecutar desde cero sobre una copia con resultados existentes.

Para construir **solo la malla**:

```bash
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --output runs/canal_malla
bash scripts/run_docker.sh runs/canal_malla --mesh
```

Luego, para resolver ese mismo caso con la malla ya creada:

```bash
bash scripts/run_docker.sh runs/canal_malla --solve-only
```

## Forma B — Docker interactivo, comandos manuales

Útil para aprender o para quienes ya tienen una función de terminal (por ejemplo, `openfoam`) que abre el contenedor con el directorio del caso montado en `/workspace`.

**Primero, en el host**, desde la raíz del repositorio, creá una copia:

```bash
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --output runs/canal_manual
```

Para entrar en el contenedor usando el lanzador del repositorio:

```bash
bash scripts/run_docker.sh runs/canal_manual -- bash
```

Alternativamente, entrá con tu propia función `openfoam`, asegurándote de montar **`runs/canal_manual`**, no necesariamente el caso original. Comprobá que el directorio de trabajo sea el que contiene `0/`, `constant/` y `system/`:

```bash
pwd
ls
```

**Dentro del contenedor** (por ejemplo, en `/workspace`):

```bash
blockMesh                     # Genera constant/polyMesh/
checkMesh                     # Debe informar Mesh OK.
simpleFoam | tee log.simpleFoam
```

Para consultar resultados:

```bash
ls -d [0-9]*
tail -n 30 log.simpleFoam
```

Para salir del contenedor:

```bash
exit
```

Los archivos generados permanecen en el host porque el directorio está montado como volumen.

**¿Puedo usar directamente `cases/01a-canal-no-newtoniano` en mi función `openfoam`?** Sí: `blockMesh`, `checkMesh` y `simpleFoam` funcionan si los archivos del caso están accesibles y tenés permisos de escritura. Sin embargo, modificarás el directorio fuente y dejarás allí los resultados. Preferí una copia.

**¿Por qué `bash Allrun` puede fallar en mi contenedor personalizado?** El `Allrun` del caso original llama a `../../scripts/run_prepared_case.sh`, que está **fuera** del directorio del caso. Si solo montaste ese directorio en `/workspace`, el script compartido no existe dentro del contenedor. La ejecución manual de tres comandos no depende de ese script. El lanzador oficial `run_docker.sh` contempla los montajes necesarios.

En una **copia preparada**, `Allrun` sí está autocontenido: podés ejecutarlo dentro de un contenedor con OpenFOAM cargado usando `bash Allrun`, **si todavía no generaste una malla**.

## Forma C — OpenFOAM instalado directamente en Linux (sin Docker)

Requiere una instalación compatible de OpenFOAM y el entorno cargado. No basta con tener el comando `docker`: los ejecutables `blockMesh`, `checkMesh` y `simpleFoam` deben estar disponibles en la terminal.

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --output runs/canal_local
cd runs/canal_local

# Verificar que OpenFOAM esté cargado
command -v blockMesh
command -v simpleFoam

# Opción automatizada: malla + verificación + solver
bash Allrun
```

Si preferís ejecutar los pasos por separado, **en lugar de `bash Allrun`**:

```bash
blockMesh
checkMesh
simpleFoam | tee log.simpleFoam
```

No ejecutes `Allrun` después de generar la malla manualmente: el script detecta una malla previa y se detiene. Para usar esa malla con el script de la copia preparada, ejecutá `bash Allrun --solve-only`.

## Errores comunes y comprobaciones

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| `Cannot find file "points" in directory "polyMesh"` al ejecutar `checkMesh` | Todavía no existe la malla | Ejecutar `blockMesh` antes de `checkMesh`. |
| `blockMesh: command not found` | OpenFOAM no está cargado | Entrar al contenedor correcto o cargar el entorno de OpenFOAM instalado. |
| `Allrun` no encuentra `../../scripts/run_prepared_case.sh` | Se montó solo el caso fuente | Usar `run_docker.sh`, una copia preparada o los comandos manuales. |
| `Resultados existentes` o `Malla previa` | El script protege casos ya ejecutados | Crear una copia nueva, o `--solve-only` si ya se generó la malla y aún corresponde resolver. |
| No aparecen directorios `100/`, `200/` | El solver no escribió resultados o terminó antes | Revisar `log.simpleFoam` y `system/controlDict`. |

Para comprobar el estado del caso dentro del contenedor:

```bash
pwd
ls system/blockMeshDict system/controlDict 0/U 0/p
ls constant/polyMesh/points  # Solo después de ejecutar blockMesh
```

## Cambiar parámetros y repetir experimentos

Editá **una copia preparada antes de la primera ejecución**. Archivos principales:

| Archivo | Entrada | Efecto / prueba sugerida |
| --- | --- | --- |
| `0/U` | `internalField`, `inlet/value` | Velocidad inicial y de entrada (m/s). Probar 0.005 en vez de 0.01. |
| `0/p` | `outlet/value` | Referencia de presión cinemática; cambiarla desplaza el nivel de p. |
| `constant/turbulenceProperties` | `n`, `k`, `nuMin`, `nuMax` | `n=0.5`: adelgazamiento; probar 0.7. `k` fija la consistencia; los límites 1e-6 y 1e-2 acotan `nu` efectiva. |
| `constant/transportProperties` | `nu` | Viscosidad base; no desactiva `powerLaw`. |
| `system/blockMeshDict` | `vertices`, `blocks` | Dimensiones y resolución. Probar 100 × 20 × 1 o 400 × 80 × 1; mantener una celda en z. |
| `system/controlDict` | `endTime`, `writeInterval` | Máximo de 1000 iteraciones y escritura cada 100; no son segundos físicos. |

Si modificás geometría o resolución, hay que **reconstruir la malla** con `blockMesh`. Si modificás únicamente velocidad, presión o propiedades reológicas, la geometría puede mantenerse. Para comparar experimentos reproducibles, prepará una copia diferente por variante; así conservás entradas, logs y resultados de cada corrida.

Para limpiar resultados de **una copia preparada**, desde ella y con acceso a Bash:

```bash
bash Allclean          # Previsualiza lo que se borraría
bash Allclean --yes    # Borra malla, logs y tiempos generados
```

Esto permite volver a ejecutar el caso desde cero. Comprobá la ruta actual antes de limpiar.

### Variante newtoniana y comparación física

Dentro de los límites de viscosidad, `nu_eff = k·gammaDot^(n−1)`. La variante `newtonian` aplica viscosidad constante sin cambiar la geometría:

```bash
# Desde la raíz del repositorio, en el host
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --variant newtonian --output runs/canal_newtoniano
bash scripts/run_docker.sh runs/canal_newtoniano
```

Comparar ambos a igual caudal; el perfil parabólico es la referencia plenamente desarrollada, no el perfil uniforme impuesto en la entrada.

`system/fvSchemes` controla la discretización y `system/fvSolution` los solvers lineales y el acoplamiento. No confundir tolerancia numérica con precisión física.

## Resultados y postprocesamiento

Desde la **raíz del repositorio**, con las dependencias de [postprocesamiento](../../postprocessing/README.md) instaladas en el host:

```bash
python postprocessing/fields.py runs/canal --field U --normal z
python postprocessing/profile.py runs/canal --field U --component 0 --start 0.15 0.0001 0.0005 --end 0.15 0.0199 0.0005
python postprocessing/statistics.py runs/canal --patch inlet outlet
python postprocessing/plot_solver_log.py runs/canal/log.simpleFoam
```

Reemplazá `runs/canal` por la ruta de tu copia si usaste otro nombre. Comparar perfil transversal, diferencia de presión y caudal; `p` es presión cinemática (m²/s²).

**Estado de validación:** la configuración del caso fue revisada estáticamente; estos cambios de documentación no constituyen una nueva ejecución numérica verificada.
