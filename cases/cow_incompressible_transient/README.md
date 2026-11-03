# Vaca: flujo de aire transitorio (2D)

Este caso emplea `pimpleFoam` (URANS kOmegaSST) y reutiliza la malla del caso `cow_incompressible_steady`. Ejecutar `bash Allrun`. Para renderizar: `python3 ../../scripts/animate_cow.py . --field speed`.

Estado: configuración no ejecutada ni validada. La geometría fija y el cierre URANS no resuelven todas las escalas turbulentas. Revisar calidad de malla y estabilidad temporal.
