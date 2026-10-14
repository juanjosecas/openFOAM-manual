# OpenFOAM v2406 — Tutorial 06

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.


### Automatización, simulaciones paramétricas y análisis de resultados con foamlib

Repositorio: gerlero/foamlib Documentación: foamlib — Documentation

foamlib es una biblioteca de Python desarrollada por Gabriel S. Gerlero y Pablo A. Kler que permite trabajar con OpenFOAM sin tener que manipular manualmente todos sus archivos de texto.

Su principal utilidad es conectar OpenFOAM con el ecosistema científico de Python: NumPy, pandas, Matplotlib, SciPy y herramientas de optimización.

La biblioteca tiene una publicación en Journal of Open Source Software (2025) y ofrece soporte tanto para OpenFOAM.com como para OpenFOAM Foundation.


#### Qué permite hacer

Estas interfaces aparecen en el README y la documentación oficial.

La ventaja es que podemos convertir nuestros tutoriales anteriores en experimentos reproducibles, cambiando parámetros de forma programática y recuperando resultados directamente como datos numéricos.

Para este tutorial vamos a reutilizar el canal 2D no newtoniano del Tutorial 01. El objetivo será automatizar tres simulaciones con diferentes velocidades de entrada y analizar sus perfiles de velocidad.


### 1. Instalar foamlib

Como OpenFOAM v2406 ya está funcionando en tu contenedor Docker, la forma más directa es instalar foamlib en un entorno virtual dentro del contenedor.

Primero ingresá al contenedor:


```cpp
docker exec -it openfoam2406-run bash
Comprobá el entorno:

foamVersion
python3 --version
python3 -m pip --version
```

Si está disponible venv, crear un entorno virtual:


```cpp
python3 -m venv ~/foamlib-env

source ~/foamlib-env/bin/activate

python -m pip install --upgrade pip
python -m pip install foamlib numpy pandas matplotlib
```

En un contenedor que no tenga el módulo venv, habrá que instalar el paquete correspondiente a la distribución Linux de la imagen.

Comprobar:


```python
python -c "import foamlib; print(foamlib.__file__)"
```

Y verificar que Python también encuentre OpenFOAM:


```bash
which python
which blockMesh
which simpleFoam
```

Los ejecutables de OpenFOAM deben estar disponibles en el PATH del proceso Python. Activar un entorno virtual no debería eliminar la configuración del entorno OpenFOAM.

Una alternativa es instalar foamlib en Fedora y ejecutar los casos mediante Docker, pero esa integración requiere gestionar rutas montadas y comandos dentro del contenedor. Para comenzar, resulta más sencillo utilizar Python y OpenFOAM en el mismo entorno.


### 2. Preparar el experimento

Usaremos esta estructura:


```cpp
foamlibTutorial/
```

├── canalBase/

│   ├── 0/

│   ├── constant/

│   └── system/

├── analizar_caso.py

├── ejecutar_parametros.py

└── resultados/

canalBase contendrá los ocho archivos de configuración del Tutorial 01, sin necesidad de reescribirlos.

Si ya tenés ese caso funcionando, copiarlo:


```bash
mkdir -p foamlibTutorial/resultados

cp -r canalPowerLaw2D/0 foamlibTutorial/canalBase/
cp -r canalPowerLaw2D/constant foamlibTutorial/canalBase/
cp -r canalPowerLaw2D/system foamlibTutorial/canalBase/

touch foamlibTutorial/analizar_caso.py
touch foamlibTutorial/ejecutar_parametros.py

cd foamlibTutorial
```

El caso base debe contener:


```cpp
canalBase/
```

├── 0/

│   ├── U

│   └── p

├── constant/

│   ├── transportProperties

│   └── turbulenceProperties

└── system/

├── blockMeshDict

├── controlDict

├── fvSchemes

└── fvSolution

Para este ejercicio supondremos que conserva el modelo pseudoplástico powerLaw y que el patch de entrada se llama inlet.

En particular, la velocidad inicial será 0.01 m/s.


### 3. Leer los archivos de OpenFOAM desde Python

Antes de automatizar simulaciones, conviene entender cómo foamlib interpreta los diccionarios.

En una sesión Python:


```python
from foamlib import FoamCase
case = FoamCase("canalBase")
print(case.application)
print(case.control_dict["endTime"])
print(case.control_dict["writeInterval"])
```

FoamCase representa el directorio completo de una simulación.

La propiedad control_dict permite acceder directamente a system/controlDict, sin escribir código para interpretar la sintaxis de OpenFOAM.

También podemos inspeccionar otros archivos:


```cpp
print(case.block_mesh_dict["blocks"])
print(case.transport_properties["nu"])
print(case.turbulence_properties["simulationType"])
```

El contenido se obtiene como objetos Python que representan las estructuras almacenadas en los diccionarios.


#### Modificar parámetros

Por ejemplo:


```cpp
case.control_dict["endTime"] = 1500
case.control_dict["writeInterval"] = 100
```

Esto modifica el archivo system/controlDict del caso.

Para agrupar varias modificaciones y escribirlas una sola vez:


```cpp
with case.control_dict as config:
    config["endTime"] = 1500
    config["writeInterval"] = 100
    config["writeFormat"] = "ascii"
```

Es una característica documentada de FoamFile: las modificaciones realizadas dentro del contexto se guardan al salir de él.


### 4. Modificar condiciones de contorno

Podemos acceder directamente a 0/U.


```cpp
U = case[0]["U"]
print(U.dimensions)
print(U.internal_field)
print(U.boundary_field)
```

Para leer la condición de entrada:


```cpp
inlet = U.boundary_field["inlet"]
print(inlet.type)
print(inlet.value)
```

Y cambiarla:


```cpp
with case[0]["U"] as U:
    U.boundary_field["inlet"].value = [0.02, 0, 0]
```

La velocidad de entrada pasa a ser 0.02 m/s.

Esto es equivalente a modificar manualmente:


```cpp
inlet
{
    type fixedValue;
    value uniform (0.02 0 0);
}
```

La ventaja es que podemos repetir esta operación para decenas de valores sin editar los archivos individualmente.

La API de FoamFieldFile contempla explícitamente internal_field y boundary_field, incluido el atributo value de cada condición de contorno.


### 5. Ejecutar OpenFOAM desde Python

Antes del experimento paramétrico, podemos ejecutar un caso individual.


```python
from foamlib import FoamCase
case = FoamCase("canalBase")
case.block_mesh()
case.run(["checkMesh"])
case.run(["simpleFoam"])
```

La biblioteca ejecuta los comandos dentro del directorio correspondiente al caso y puede guardar sus salidas en archivos log.*.

También permite:

case.run()

Cuando no recibe un comando, run() utiliza las reglas de ejecución definidas en foamlib: puede ejecutar un script Allrun, generar la malla cuando corresponde y ejecutar el solver indicado en controlDict.

Como esos comportamientos dependen de la estructura del caso, para este primer experimento usaremos comandos explícitos.


### 6. Experimento paramétrico: tres velocidades de entrada

Ahora automatizaremos un estudio sencillo.

Mantendremos constantes la geometría, la reología y los métodos numéricos. Modificaremos únicamente la velocidad de entrada.

Queremos determinar cómo cambian el campo de velocidades y la presión cuando duplicamos o reducimos a la mitad el caudal.


#### Archivo ejecutar_parametros.py


```python
from pathlib import Path
from foamlib import FoamCase

base = FoamCase("canalBase")
velocidades = [0.005, 0.010, 0.020]
resultados = Path("resultados")
resultados.mkdir(exist_ok=True)

for velocidad in velocidades:

    nombre = f"U_{velocidad:.3f}".replace(".", "_")
    destino = resultados / nombre
    if destino.exists():
        raise FileExistsError(f"El caso {destino} ya existe")
    print(f"\nSimulando: {nombre}")
    case = base.clone(destino)
    with case[0]["U"] as U:
        U.boundary_field["inlet"].value = [velocidad, 0, 0]
        U.internal_field = [velocidad, 0, 0]
```

Ejecutar desde el directorio foamlibTutorial:


```cpp
python ejecutar_parametros.py
```

La biblioteca generará tres casos independientes:


```cpp
foamlibTutorial/
```

├── canalBase/

├── resultados/

│   ├── U_0_005/

│   │   ├── 0/

│   │   ├── constant/

│   │   ├── system/

│   │   └── ...

│   ├── U_0_010/

│   └── U_0_020/

├── analizar_caso.py

└── ejecutar_parametros.py

Cada caso contendrá sus resultados, logs y archivos de configuración.

Detalle importante: FoamCase.clone() crea una copia limpia. Si el caso original tiene scripts de limpieza personalizados, estos pueden intervenir en el proceso; en nuestro caso simple no hacen falta.

El script detiene la ejecución ante errores. También evita sobrescribir simulaciones anteriores, algo conveniente para preservar la reproducibilidad.


### 7. Recuperar resultados directamente desde Python

Ya no necesitamos abrir ParaView para calcular estadísticas sencillas de los campos.

foamlib puede leer archivos de campo en formato ASCII o binario y acceder a sus valores mediante internal_field.

Ejemplo:


```python
import numpy as np
from foamlib import FoamCase

case = FoamCase("resultados/U_0_010")
ultimo = case[-1]
U = np.asarray(ultimo["U"].internal_field)
p = np.asarray(ultimo["p"].internal_field)
print("Velocidad:", U.shape)
print("Presión:", p.shape)
```

En un campo vectorial no uniforme de 8000 celdas, esperamos un arreglo de velocidades de dimensiones aproximadas (8000, 3).

La magnitud de cada vector se calcula con:


```cpp
magnitud = np.linalg.norm(U, axis=1)
print("Velocidad mínima:", magnitud.min())
print("Velocidad máxima:", magnitud.max())
print("Velocidad media celular:", magnitud.mean())
```

La media celular no equivale necesariamente a la velocidad media transversal ni al caudal. Para calcular estos últimos necesitamos integrar sobre una sección del canal.


#### Una precaución

En OpenFOAM algunos campos pueden almacenarse como valores uniformes en lugar de arreglos con un valor por celda. Por eso, antes de procesar un campo, conviene inspeccionar shape y comprobar que contiene la cantidad esperada de elementos.


### 8. Comparar las tres simulaciones

El siguiente script recupera estadísticas básicas de velocidad y presión, las guarda en CSV y genera dos gráficos.


#### Archivo analizar_caso.py


```python
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from foamlib import FoamCase

resultados = Path("resultados")
filas = []
for directorio in sorted(resultados.iterdir()):
    if not directorio.is_dir():
        continue
    case = FoamCase(directorio)
    ultimo = case[-1]
    U = np.asarray(ultimo["U"].internal_field, dtype=float)
    p = np.asarray(ultimo["p"].internal_field, dtype=float)
    velocidad = np.linalg.norm(U, axis=1)
    entrada = case[0]["U"].boundary_field["inlet"]

python analizar_caso.py
Los archivos generados serán:


resultados/
├── resumen.csv
├── velocidad_maxima.png
├── presion_rango.png
├── U_0_005/
├── U_0_010/
└── U_0_020/
```

El rango de presión calculado como p.max() - p.min() sirve para una primera inspección, pero no equivale necesariamente a la pérdida de carga entre entrada y salida. Para medir esa pérdida correctamente debemos calcular las presiones medias en ambos patches o en secciones interiores definidas.

También es importante verificar la convergencia antes de comparar los tres casos: una diferencia entre iteraciones finales no necesariamente refleja una diferencia física.


### 9. Ejecutar simulaciones en paralelo

Hasta ahora ejecutamos los casos secuencialmente.

foamlib ofrece AsyncFoamCase, con el que podemos distribuir simulaciones independientes entre varios procesos.

No se trata de paralelizar internamente un único solver mediante MPI, sino de ejecutar varios casos simultáneamente.


#### Archivo ejecutar_paralelo.py

Primero crearlo:


```cpp
touch ejecutar_paralelo.py
```

Contenido:


```python
import asyncio
from pathlib import Path
from foamlib import AsyncFoamCase

velocidades = [0.005, 0.010, 0.020]
base = AsyncFoamCase("canalBase")
AsyncFoamCase.max_cpus = 3

async def ejecutar(velocidad):
    nombre = f"U_{velocidad:.3f}".replace(".", "_")
    destino = Path("resultados_paralelos") / nombre
    if destino.exists():
        raise FileExistsError(destino)
    case = await base.clone(destino)
    with case[0]["U"] as U:
        U.boundary_field["inlet"].value = [velocidad, 0, 0]
        U.internal_field = [velocidad, 0, 0]
    with case.control_dict as config:
        config["endTime"] = 1500
        config["writeInterval"] = 100
        config["startFrom"] = "startTime"
        config["startTime"] = 0
    await case.block_mesh()
```

Ejecutar:


```cpp
python ejecutar_paralelo.py
```

El límite max_cpus = 3 controla cuántos recursos de CPU puede utilizar la ejecución concurrente administrada por foamlib. La API también permite establecer límites para evitar sobrecargar la máquina.

Para una computadora con varios núcleos, este enfoque es útil cuando los casos son relativamente pequeños y queremos explorar combinaciones de parámetros.

Para simulaciones individuales grandes, como un caso 3D multifásico, probablemente resulte más conveniente utilizar MPI dentro de cada simulación.


### 10. Aplicaciones más interesantes para nuestros próximos casos

La utilidad de foamlib aumenta cuando reemplazamos ejemplos aislados por estudios paramétricos controlados.

Por ejemplo, en el caso de la estenosis capilar podríamos explorar automáticamente:

Eso produce 16 simulaciones independientes.

Podríamos calcular una matriz de resultados con la caída de presión, la máxima velocidad y los esfuerzos sobre la pared para cada combinación de parámetros. Luego estudiaríamos sensibilidades o ajustaríamos un modelo predictivo.

Para cambiar una geometría definida con blockMesh, foamlib puede administrar los archivos, pero no reemplaza el trabajo geométrico: habría que modificar blockMeshDict o generar ese diccionario mediante Python, como hicimos con los obstáculos del Tutorial 02.


### 11. Referencias y documentación

La documentación oficial separa las funcionalidades en módulos:

FoamFile y FoamFieldFile: lectura y modificación de diccionarios y campos.

FoamCase y AsyncFoamCase: administración, ejecución y clonación de casos.

Documentación general: incluye ejemplos y módulos de estudios paramétricos y posprocesamiento.

Ejemplos en GitHub: ejemplos básicos y estudios paramétricos.

El repositorio también proporciona foamlib.preprocessing y foamlib.postprocessing, además de integración con SLURM. Son especialmente relevantes si después queremos automatizar estudios de sensibilidad, análisis de resultados y optimización de parámetros.

El cambio fundamental en el flujo de trabajo es este:


```cpp
Python
```

│

├── Definir parámetros

│

├── Generar o modificar archivos OpenFOAM

│

├── Crear casos independientes

│

├── Ejecutar OpenFOAM

│

├── Recuperar campos

│

└── Analizar resultados

│

├── pandas / NumPy

├── Matplotlib

├── SciPy

└── Modelos de machine learning

El tutorial se fundamenta en la API documentada de foamlib. Los scripts no han sido ejecutados en tu imagen Docker, por lo que el primer control operativo será verificar la instalación, la disponibilidad de los solvers y la lectura correcta del caso base.
