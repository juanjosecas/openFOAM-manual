# Vaca: flujo de aire transitorio (2D)

Caso `pimpleFoam` con cierre URANS `kOmegaSST` y la **misma geometría** del caso estacionario (`variants/steady`).

- OpenFOAM.com v2406; flujo incompresible.
- Aire: `nu=1.5e-5 m²/s`; entrada `U=(10 0 0) m/s`.
- Tiempo de simulación 5 s, `maxCo=0.5`, techo de `deltaT=1e-3 s`.
- Escritura cada 0.05 s, con `purgeWrite=0`.
- Campos `U`, `p`, `k`, `omega`, `nut`, vorticidad y fuerzas.
- Silueta inmóvil; caras frontales/posteriores con `empty`.

Desde la raíz del repositorio:

```bash
bash scripts/prepare_case.sh cow-flow --output runs/cow
bash scripts/run_docker.sh runs/cow
python postprocessing/animate.py runs/cow --field U --normal z --cmap inferno --output plots/cow-speed.gif
python postprocessing/animate.py runs/cow --field vorticity --component 2 --normal z --cmap coolwarm --output plots/cow-vorticity.gif
```

La malla se conserva en `meshes/cow_tunnel.msh`. Para imágenes fijas usar fields.py. Los nuevos comandos de visualización no se han ejecutado.

**Estado: revisión estática, no ejecutado.** URANS 2D y esquemas upwind pueden amortiguar las oscilaciones de la estela; evaluar independencia de malla/paso, fuerzas temporales y estabilidad. Las celdas sesgadas cerca de las pezuñas son una limitación conocida. El limitador `limitVelocity` existente puede intervenir durante la integración y debe auditarse.
