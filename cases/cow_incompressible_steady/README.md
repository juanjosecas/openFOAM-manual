# Vaca: flujo de aire incompresible estacionario (2D)

Solver `simpleFoam`, RANS `kOmegaSST`, aire (`nu = 1.5e-5 m²/s`), `U = 10 m/s`.

- Orientación: cola en x bajo, cabeza en x alto (vaca de ≈2.4 m, x ∈ [-1.2, 1.2]).
- Dominio x ∈ [-7.2, 16.8], y ∈ [0, 8.4]. Entrada en x = -7.2 (viento de cola,
  `U = (10 0 0)`), salida en x = 16.8. Para viento de frente, hay que
  invertir el dominio/entrada (la malla actual deja la estela a +x).
- Parches: `inlet`, `outlet`, `cow` (wall), `groundAndTop` (slip), `frontAndBack` (empty).
- Turbulencia de entrada: I = 5 % → `k = 0.375`, `omega = 14`.
- Se calculan `forces` y `forceCoeffs` (lRef = 2.4, Aref = 0.1466 = altura × 0.1 m de espesor).

## Ejecución

    bash Allrun
    bash Allclean --yes   # limpieza

Corrige el error previo "Patch type for patch cow must be wall": `Allrun` aplica
`system/changeDictionaryDict` tras `gmshToFoam`.

Estabilidad: la malla tiene caras muy sesgadas y celdas finas junto a las pezuñas;
se usan esquemas upwind, relajación baja y `system/fvOptions` (limitVelocity,
30 m/s), que al final de la corrida ya no actúa. Verificado con OpenFOAM v2406
(Docker opencfd/openfoam-default:2406): 500 iteraciones sin fallos, Cd ≈ 0.93.
