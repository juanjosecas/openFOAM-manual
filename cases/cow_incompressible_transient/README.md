# Vaca: flujo de aire transitorio (2D)

Caso `pimpleFoam` con cierre URANS `kOmegaSST` y la **misma geometría** del caso [estacionario](../cow_incompressible_steady/README.md).

- OpenFOAM.com v2406; flujo incompresible.
- Aire: `nu=1.5e-5 m²/s`; entrada `U=(10 0 0) m/s`.
- Tiempo de simulación 5 s, `maxCo=0.5`, techo de `deltaT=1e-3 s`.
- Escritura cada 0.05 s, con `purgeWrite=0`.
- Campos `U`, `p`, `k`, `omega`, `nut`, vorticidad y fuerzas.
- Silueta inmóvil; caras frontales/posteriores con `empty`.

Ejecutar desde esta carpeta:

```bash
bash Allrun
python3 ../../scripts/animate_cow.py . --field speed --fps 20
python3 ../../scripts/animate_cow.py . --field vorticity --fps 20
```

Se reutiliza `../cow_incompressible_steady/cow_tunnel.msh` sin duplicar 11 MB de malla. Para la animación instalar `pyvista`, `numpy` e `imageio`.

**Estado: revisión estática, no ejecutado.** URANS 2D y esquemas upwind pueden amortiguar las oscilaciones de la estela; evaluar independencia de malla/paso, fuerzas temporales y estabilidad. Las celdas sesgadas cerca de las pezuñas son una limitación conocida. El limitador `limitVelocity` existente puede intervenir durante la integración y debe auditarse.
