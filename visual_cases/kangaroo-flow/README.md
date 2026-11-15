# Kangaroo wake — OpenFOAM.com v2406

Caso **2D transitorio** de flujo incompresible alrededor de una silueta fija de canguro. Inspirado en una animación Lattice Boltzmann D2Q9, pero resuelto aquí con Navier–Stokes por volúmenes finitos y `pimpleFoam`. Contorno poligonal nuevo, editable en `geometry/kangaroo_outline.csv`.

**Estado:** revisión estática; no ejecutado ni validado numéricamente. No se ha comprobado independencia de malla/paso temporal.

## Modelo

- Velocidad incidente `U=(1 0 0) m/s`, dirección +x.
- Fluido newtoniano modelo, `nu=0.008 m²/s` (no representa aire ni agua ambiente).
- Altura característica aproximada 1.164 m; Reynolds aproximado 145.
- Dominio `x=[-5,15]`, `y=[-5,5]`, `z=[0,0.02]` m.
- Una celda de espesor; caras `frontAndBack` de tipo `empty`.
- Parches: `inlet` velocidad fija, `outlet` presión cinemática fija, `farfield` slip, `kangaroo` noSlip.
- Duración 80 s; `maxCo=0.5`; salidas cada 0.5 s.
- Campo derivado: `vorticity`.

## Ejecución

Gmsh CLI debe estar disponible en el entorno de mallado. La geometría editable es `geometry/kangaroo.geo`; el CSV se conserva como referencia del contorno.

```bash
bash scripts/prepare_case.sh kangaroo-flow --output runs/kangaroo
# Si la imagen no contiene Gmsh, generar la malla desde el host:
gmsh runs/kangaroo/geometry/kangaroo.geo -3 -format msh2 -o runs/kangaroo/geometry/kangaroo.msh
bash scripts/run_docker.sh runs/kangaroo
```

## Animaciones

Desde la raíz:

```bash
python postprocessing/animate.py runs/kangaroo --field U --normal z --stride 2 --cmap inferno --output plots/kangaroo-speed.gif
python postprocessing/animate.py runs/kangaroo --field vorticity --component 2 --normal z --stride 2 --cmap coolwarm --output plots/kangaroo-vorticity.gif
```

Si no se guardó vorticidad, se estima a partir del campo U mediante PyVista. Para una imagen fija usar fields.py. No se han ejecutado estos comandos.

## Limitaciones

El animal permanece fijo. El cambio galileano de referencia corresponde a traslación horizontal uniforme, **no a un salto**. La formación de vórtices y sus frecuencias deben verificarse experimentalmente mediante la corrida y pruebas de sensibilidad espacial/temporal. `speed` representa magnitud de velocidad; `omega_z` permite visualizar rotación local. No confundir los mapas.

Inspirado en `cow_incompressible_steady`, `07-svg-gmsh`, `08-tuberia-cilindrica-3d` y `docs/simplefoam-a-transitorio.md`.
