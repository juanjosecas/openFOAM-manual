# Ejecutores Docker independientes por caso

Cada carpeta CFD ejecutable contiene `run_docker.sh`, sin llamadas a `Allrun` ni `Allmesh`. Los scripts usan la imagen `opencfd/openfoam-default:2406` y contienen explícitamente sus etapas de mallado, preparación y solver. Los originales `Allrun` y `Allmesh` permanecen intactos.

## Uso

```bash
cd cases/09-cavity-2d
bash run_docker.sh --dry-run    # muestra la invocación, no modifica archivos
bash run_docker.sh              # ejecuta Docker y las etapas del caso
```

También se puede invocar desde otro directorio con la ruta completa al script. Requiere Bash y Docker Engine accesible, y que la imagen esté disponible localmente o pueda descargarse. No requiere OpenFOAM instalado en el host.

Cada script monta **todo el repositorio** en `/workspace`, porque algunos casos comparten mallas y scripts. El montaje es de lectura/escritura; se ejecuta con el UID/GID del usuario y se elimina el contenedor al terminar. Los resultados quedan en el directorio del caso. `FOAM_IMAGE` permite indicar una imagen compatible, pero el entorno cargado sigue siendo OpenFOAM v2406.

## Casos y etapas

| Casos | Etapas |
|---|---|
| 01-canal-no-newtoniano, 02-canal-obstaculos, 03-estenosis-capilar, 08-tuberia-cilindrica-3d, 09-cavity-2d, 14a-difusion-farmaco, 23-flexion-viga, 24-conduccion-1d | blockMesh (si falta), checkMesh, solver indicado en controlDict |
| 04-chorro-agua | blockMesh, checkMesh, interFoam; no usa setFields |
| 07-svg-gmsh | generación de geometría Python, gmshToFoam, ajuste de patches, checkMesh, simpleFoam |
| 10a/10b/10c-tuberia-laminar, 11-dambreak-2d, 12-goldschmidt-particulas | solo blockMesh y checkMesh: no se presume que el solver heredado sea compatible |
| 13-stl-snappy-esfera | surfaceCheck, blockMesh, checkMesh, snappyHexMesh, checkMesh; solo mallado |
| 13b-esfera-agua-laminar | surfaceCheck, blockMesh, checkMesh, snappyHexMesh, checkMesh, simpleFoam |
| 26-refraccion-interfoam | blockMesh, checkMesh, setFields, interFoam |
| cow_incompressible_steady | gmshToFoam, changeDictionary, checkMesh, simpleFoam |
| cow_incompressible_transient | gmshToFoam desde caso vecino, changeDictionary, checkMesh, pimpleFoam |
| kangarooWake | generación de geometría Python, gmshToFoam, changeDictionary, checkMesh, pimpleFoam |

`01-anexo-exportacion` es material auxiliar, no un caso de solver. `25-refraccion-luz` es un modelo Python de rayos ópticos, no OpenFOAM: no se agregó un lanzador Docker OpenFOAM.

## Controles y limitaciones

- Fallos en comandos detienen el script; cada etapa guarda `log.<etapa>` y muestra el final del log ante errores.
- El solver se contrasta con `system/controlDict`; se rechazan nombres inválidos o ejecutables ausentes.
- No se borran mallas ni resultados. Para evitar sobreescrituras, el solver rechaza carpetas de tiempos positivos existentes. Esto también impide continuar simulaciones interrumpidas: reinicios requieren un procedimiento específico.
- En la vaca se permite el diagnóstico de calidad de malla conocido (`Failed 1 mesh checks`), pero **eso no significa que la malla esté validada**.
- Las dependencias Python/Gmsh auxiliares pueden no estar disponibles en la imagen; se informará el error en los logs. Los scripts no instalan paquetes ni modifican las configuraciones físicas.
- La verificación realizada es estática. **No se ejecutaron simulaciones Docker reales ni se validaron resultados CFD** en este entorno.

Los scripts son independientes de los `Allrun`, pero usan los archivos físicos `0/`, `constant/`, `system/` y las geometrías del repositorio.
