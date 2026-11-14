# Biblioteca operativa de casos

El manual principal queda intacto. Consultar catalog.json para la clasificación.

```bash
bash scripts/prepare_case.sh --list
bash scripts/prepare_case.sh 14a-difusion-de-farmaco --output runs/difusion
cd runs/difusion
openfoam -- bash Allrun
```

Variantes de diccionarios: `--variant transient`, `--variant animation` o `--variant steady` según el caso. Los resultados se escriben en la copia, no en el original. Para recetas paramétricas del canal con obstáculos, preparar una copia base y ejecutar desde ella `openfoam -- bash ...` con la receta copiada a la corrida:

```bash
# Desde la raíz del repositorio
bash scripts/prepare_case.sh 02-flujo-canal-con-obstaculos --output runs/canal
cp cases/02-flujo-canal-con-obstaculos/variants/agua-estela.sh runs/canal/
cd runs/canal
openfoam -- bash agua-estela.sh
openfoam -- bash Allrun
```

No ejecutar recetas dos veces sobre la misma copia. No se requiere Python para preparar y ejecutar casos con blockMesh. Los generadores geométricos de esfera y canguro requieren Python en el host. Python se conserva para análisis, visualización, geometría y generación de documentación. Las antiguas interfaces foam_docker.py, prepare_case.py y variantes_canal.py se retiraron. Los tutoriales oficiales se importan con scripts/import_official_tutorial.sh y se ejecutan con scripts/run_official_tutorial.sh. El manual puede conservar comandos históricos. No hay nueva validación CFD.
