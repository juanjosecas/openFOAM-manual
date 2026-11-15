# Cavidad Re=100

Variante del caso original: U=1 m/s, L=1 m, nu=0.01 m²/s, 64×64×1 celdas, deltaT=0.005 s, t final=40 s. Co nominal U deltaT/dx=0.32. No se ha ejecutado. Verificar Co real y evolución temporal antes de comparar perfiles centrales Ux(y)/U y Uy(x)/U con Ghia et al. (1982), DOI 10.1016/0021-9991(82)90058-4. No es una demostración de convergencia de malla. El caso base Re=10000 permanece disponible.

```bash
bash scripts/prepare_case.sh 09-cavidad-con-tapa-movil --variant re100 --output runs/cavity-re100
bash scripts/run_docker.sh runs/cavity-re100
```
