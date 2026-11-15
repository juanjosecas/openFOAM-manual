# Transporte de partículas: Goldschmidt

Prototipo de flujo de aire con partículas lagrangianas. Los diccionarios se conservan como punto de partida, pero la simulación completa requiere adaptar el modelo de nube y verificar el solver.

## Archivos de interés

| Archivo | Qué modificar |
| --- | --- |
| 0/U.air, 0/p | Campos iniciales y condiciones del gas. |
| constant/kinematicCloudProperties | Inyección, propiedades de partículas y submodelos de interacción. |
| constant/momentumTransport.air | Modelo de transporte del gas. |
| constant/transportProperties | Propiedades del medio. |
| constant/g | Gravedad. |
| system/blockMeshDict | Geometría, resolución y patches. |
| system/controlDict | Solver, paso temporal y escritura. |

## Mallado únicamente

Desde la raíz:

```bash
bash scripts/run_docker.sh experimental_cases/12-transporte-de-particulas --mesh
```

No hay Allrun. No iniciar el solver hasta resolver los pendientes de [PENDIENTES.md](PENDIENTES.md). Después de adaptar el modelo, comparar distribución espacial, velocidad de partículas y balance de masa. Sin ejecución comprobada.
