# APÉNDICE PRÁCTICO DEL TUTORIAL 01 · Exportación y visualización fuera de ParaView

> **Estado:** migración documental; los diccionarios recuperados requieren prueba en OpenFOAM.com v2406 o v2412.
> **Nota:** los comandos y parámetros que provienen del documento original no se han validado mediante ejecución.

Este apartado se aplica al caso canalPowerLaw2D ya calculado. Distingue entre exportar campos volumétricos (malla, velocidad y presión), extraer datos tabulares y generar imágenes o videos mediante herramientas distintas de ParaView. Los comandos se ejecutan desde la raíz del caso y dentro de un entorno con las utilidades de OpenFOAM disponibles.


### 1. Qué datos produce OpenFOAM y qué conviene exportar

OpenFOAM escribe los campos en directorios numerados: 0/, 100/, 200/, etc. U es un vector (Ux, Uy, Uz), p es una presión cinemática en m²/s² y la geometría de las celdas está almacenada en constant/polyMesh/. Los números de carpeta de simpleFoam corresponden a iteraciones de una solución estacionaria; NO son segundos físicos. Para animaciones físicas debe utilizarse un solver transitorio, por ejemplo pimpleFoam.

VTK conserva geometría y campos y resulta adecuado para PyVista, VTK, VisIt y otros visores. CSV contiene tablas numéricas para Python, R, Excel y gráficos. STL y OBJ exportan superficies pero, por lo general, no incluyen los campos CFD: no son sustitutos de VTK para dibujar vectores de velocidad.


### 2. Exportar toda la malla y los campos a VTK


```cpp
cd ~/Documents/OpenFOAM/canalPowerLaw2D
# Comprobar los instantes/iteraciones disponibles
foamListTimes
# Exportar presión y velocidad del último resultado
foamToVTK -latestTime -fields '(U p)' -ascii
# Exportar la secuencia completa, omitiendo el estado inicial 0/
foamToVTK -noZero -fields '(U p)' -ascii
# Inspeccionar archivos generados
find VTK -type f | head -n 30
```

Por defecto, foamToVTK escribe dentro de VTK/. La estructura exacta y la extensión de los archivos dependen de la versión y del tipo de región. La opción -ascii favorece inspección manual pero puede ocupar más espacio; para resultados grandes, omitirla. La opción -fields evita exportar campos innecesarios. Consultar foamToVTK -help en la instalación concreta para confirmar opciones.

En VisIt se abre la serie exportada desde File → Open; para PyVista los archivos se cargan con pv.read(). En Blender, VTK suele requerir un complemento o una conversión específica: el programa no interpreta de forma nativa todos los atributos CFD.


### 3. Exportar un perfil transversal a CSV con sets

En vez de exportar las 8.000 celdas, se puede muestrear U y p a lo largo de una línea transversal en x = 0,15 m. Definimos un function object llamado perfilCanal en un archivo auxiliar, que no modifica el solver ni los resultados originales.


```bash
mkdir -p system
cat > system/exportPerfilDict <<'EOF'
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object exportPerfilDict;
}

functions
{
    perfilCanal
    {
        type sets;
        libs (sampling);
        writeControl writeTime;
        interpolationScheme cellPoint;
        setFormat csv;
        fields (U p);

        sets
        {
            perfil_x015
            {
                type uniform;
                axis y;
                start (0.15 0.0001 0.0005);
                end   (0.15 0.0199 0.0005);
                nPoints 100;
            }
        }
    }
}
EOF

# Ejecutar el muestreo sobre el último resultado disponible
postProcess -dict system/exportPerfilDict -latestTime
find postProcessing/perfilCanal -type f
```

La línea comienza y termina ligeramente dentro del canal para evitar ambigüedades de interpolación sobre las paredes; z = 0,0005 m corresponde al plano medio del espesor 2D. El archivo CSV resultante contiene coordenadas y componentes de U, con nombres de columnas que deben inspeccionarse antes del análisis. No confundir “100 puntos de muestreo” con 100 celdas de la malla.


### 4. Graficar perfiles en Python sin ParaView


```python
# En el sistema que tenga pandas y matplotlib instalados
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

archivos = sorted(Path('postProcessing/perfilCanal').rglob('*.csv'))
if not archivos:
    raise FileNotFoundError('No hay CSV. Ejecutar postProcess antes.')

df = pd.read_csv(archivos[-1])
print('Archivo:', archivos[-1])
print('Columnas:', list(df.columns))
print(df.head())

# Elegir las columnas reales que aparezcan en la salida
# (la nomenclatura depende de la versión y del writer CSV).
# Por ejemplo, si hay columnas y y U_x:
# plt.plot(df['y'], df['U_x'])
# plt.xlabel('y (m)'); plt.ylabel('Ux (m/s)')
# plt.tight_layout(); plt.savefig('perfil_velocidad.png', dpi=200)
```

El código anterior permite identificar las columnas reales en lugar de asumir un esquema CSV fijo. Una vez identificadas, descomentar y ajustar las últimas líneas para guardar el perfil.


### 5. Dibujar campos y vectores con PyVista

PyVista es una interfaz Python de VTK. Permite mostrar cortes, flechas, superficies y mapas de color sin abrir ParaView. Se instala en el sistema anfitrión mediante python -m pip install pyvista vtk. El ejemplo siguiente localiza los archivos volumétricos VTK exportados y muestra las matrices disponibles; el nombre exacto del archivo y la ubicación de U deben comprobarse en cada versión.


```python
from pathlib import Path
import pyvista as pv

archivos = sorted(Path('VTK').rglob('*.vtk')) + sorted(Path('VTK').rglob('*.vtu'))
if not archivos:
    raise FileNotFoundError('Primero ejecutar foamToVTK.')

mesh = pv.read(str(archivos[-1]))
print('Archivo:', archivos[-1])
print('Cell arrays:', mesh.cell_data.keys())
print('Point arrays:', mesh.point_data.keys())

# Convertir campos de celda a puntos si U no está en point_data
if 'U' not in mesh.point_data and 'U' in mesh.cell_data:
    mesh = mesh.cell_data_to_point_data()

if 'U' not in mesh.point_data:
    raise KeyError('No se encontró U: inspeccionar los arrays exportados.')

corte = mesh.slice(normal=(0, 0, 1), origin=(0.10, 0.01, 0.0005))
plotter = pv.Plotter(off_screen=True, window_size=(1600, 900))
plotter.add_mesh(corte, scalars='U', magnitude=True, cmap='viridis')
plotter.view_xy()
plotter.screenshot('campo_velocidad.png')
plotter.close()
```

Para mostrar vectores, usar el método glyph sobre una muestra dispersa de puntos y la matriz U. Reducir el número de flechas evita que se superpongan. Ejemplo orientativo: flechas = corte.glyph(orient="U", scale="U", factor=0.02), seguido de plotter.add_mesh(flechas). La escala depende de las dimensiones del dominio y debe ajustarse visualmente.


### 6. Videos y animaciones: qué representa realmente cada cuadro

Un video de varios directorios producidos por simpleFoam muestra el proceso de convergencia iterativa, NO la evolución física del fluido. Si se desea ver transporte, aceleración, pulsaciones o partículas en tiempo real, utilizar pimpleFoam, interFoam u otro solver transitorio y guardar estados a intervalos físicos regulares. Una secuencia de 200–300 estados suele ser un prototipo razonable; aumentar la cantidad de cuadros no sustituye una discretización temporal adecuada.

Para un caso transitorio ya exportado a VTK, PyVista puede generar un GIF o MP4 (este último requiere soporte adicional de codecs, normalmente imageio-ffmpeg). Para una primera prueba, el siguiente guion produce un GIF de los archivos volumétricos exportados y fija la escala de colores en toda la secuencia.


```python
from pathlib import Path
import pyvista as pv

archivos = sorted(Path('VTK').rglob('*.vtk')) + sorted(Path('VTK').rglob('*.vtu'))
if len(archivos) < 2:
    raise RuntimeError('Se necesitan al menos dos estados VTK.')

mallas = []
for archivo in archivos:
    malla = pv.read(str(archivo))
    if 'U' not in malla.point_data and 'U' in malla.cell_data:
        malla = malla.cell_data_to_point_data()
    if 'U' in malla.point_data:
        mallas.append(malla)

if len(mallas) < 2:
    raise RuntimeError('No se detectaron campos U en dos estados.')

limite = max(float(__import__('numpy').linalg.norm(m['U'], axis=1).max()) for m in mallas)
p = pv.Plotter(off_screen=True, window_size=(1280, 720))
p.open_gif('evolucion.gif', fps=20)
for m in mallas:
    p.clear()
    sl = m.slice(normal=(0, 0, 1), origin=m.center)
    p.add_mesh(sl, scalars='U', magnitude=True, clim=(0, limite), cmap='viridis')
    p.view_xy()
    p.write_frame()
p.close()
```

Nota de implementación: el fragmento es una plantilla orientativa, ya que los archivos de VTK pueden incluir también paredes y regiones separadas, y su orden lexicográfico no garantiza orden temporal cuando hay sufijos numéricos de distinta longitud. Seleccionar únicamente los archivos de volumen interno, ordenar por el tiempo numérico y calcular magnitudes vectoriales antes de utilizar el video en un análisis formal.


### 7. Otros formatos y programas

VisIt: permite visualizar VTK, campos vectoriales y secuencias temporales. Python/NumPy/pandas: útil para CSV y estadísticas. R: importa CSV con read.csv() o readr::read_csv(). Blender: se usa principalmente para renderización, con una etapa adicional de importación/conversión. MATLAB: analiza CSV directamente y VTK mediante lectores disponibles por separado. EnSight: útil para intercambiar datos geométricos y campos mediante formatos compatibles con EnSight, si la instalación dispone del exportador.

Bibliografía técnica: documentación de OpenFOAM.com sobre foamToVTK, sample sets, surfaces y postProcess; confirmar opciones con -help en la versión instalada. Los resultados exportados mantienen las unidades del campo original; p en estos casos incompresibles es presión cinemática y para expresarla en pascales debe multiplicarse por la densidad de referencia.
