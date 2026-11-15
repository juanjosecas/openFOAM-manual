# Generador de canales 2D

Define el dominio, los obstáculos y las aberturas en TOML. Genera una malla de volumen de una sola capa en z, con grupos físicos para OpenFOAM. No ejecuta CFD ni impone condiciones físicas.

## Uso

Python 3.11 o posterior:

```bash
python -m pip install -r geometry/requirements.txt
python geometry/generate.py geometry/templates/obstacles.toml --output runs/geometry-demo --show
```

--show abre Gmsh para inspeccionar la malla. Omitirlo en servidores. La salida debe ser nueva.

| Sección | Parámetros |
| --- | --- |
| domain | length, height, thickness [m]. Origen (0,0,0). |
| mesh | size [m], tamaño objetivo global. |
| ports | name, kind (inlet/outlet/opening), side (left/right/top/bottom), start, end [m]. |
| obstacles | name, shape (circle/rectangle/ellipse), center [x,y], rotation [grados]. |
| obstacles.refinement | size y distance [m]: tamaño cerca del sólido y distancia de transición. |

En left/right los intervalos se miden en y desde abajo; en top/bottom se miden en x desde la izquierda. Omitir start/end para ocupar toda la cara. Se admiten varias entradas y salidas, siempre que no se superpongan. El resto del perímetro se llama walls. Cada obstáculo tiene su propio patch wall. Los obstáculos deben estar separados entre sí y de las paredes; esta versión no admite estenosis, obstáculos unidos al borde ni dominios curvos.

## Importar en OpenFOAM

La carpeta de salida contiene channel.msh, changeDictionaryDict, geometry.toml y patches.json. Para usarla, preparar un caso compatible con flujo plano y adaptar **todos** los archivos de 0/ a los nombres de patches de patches.json antes de resolver. Copiar los archivos generados:

```bash
# Desde la raíz, ejemplo con una copia limpia de un caso existente:
bash scripts/prepare_case.sh 01a-canal-no-newtoniano --output runs/canal-nuevo
cp runs/geometry-demo/channel.msh runs/canal-nuevo/
cp runs/geometry-demo/changeDictionaryDict runs/canal-nuevo/system/
bash scripts/run_docker.sh runs/canal-nuevo -- gmshToFoam channel.msh
bash scripts/run_docker.sh runs/canal-nuevo -- changeDictionary
bash scripts/run_docker.sh runs/canal-nuevo -- checkMesh
# Editar los campos de 0/; solo entonces:
bash scripts/run_docker.sh runs/canal-nuevo --solve-only
```

No ejecutar blockMesh después de importar. El diccionario generado asigna wall a sólidos y paredes, patch a puertos y empty a frontAndBack. El tipo inlet/outlet del TOML es descriptivo: la velocidad, presión, caudal o condición de abertura se definen en 0/U, 0/p y otros campos, no en la geometría. Revisar que la malla tenga exactamente una capa y que checkMesh confirme Mesh OK.

Implementación mediante API Gmsh/OpenCASCADE. [Documentación](https://gmsh.info/doc/texinfo/gmsh.html). Primera versión sin ejecución comprobada; no se garantizan todavía conversión MSH, clasificación CAD o calidad de malla en tiempo de ejecución.
