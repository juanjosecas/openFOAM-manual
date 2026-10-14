# Tutorial 10B · Tubería laminar · case1

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/p`
- `constant/transportProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/fvSolution`
- `system/sampleDict`

**Advertencia:** requiere comprobar migración desde versiones anteriores y cualquier preprocesamiento adicional antes de ejecutar.

## Ejecución

Este caso no dispone todavía de un lanzador verificado. Consultar los pasos de preparación del tutorial.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/10b-tuberia-laminar-case1
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
foamDictionary system/controlDict -entry application -value
icoFoam 2>&1 | tee log.icoFoam
```

**Estado:** Caso heredado: revisar compatibilidad con OpenFOAM.com antes de ejecutar. No hay un `Allrun` verificado para este caso.

## Variaciones pequeñas

Reducir velocidad 20%; reducir deltaT; aumentar frecuencia de escritura.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).
