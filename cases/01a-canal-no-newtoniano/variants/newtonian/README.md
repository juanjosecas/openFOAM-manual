# Referencia newtoniana del canal plano

Misma geometría, caudal de entrada, malla y configuración SIMPLE del caso base. Se utiliza la viscosidad cinemática constante de transportProperties (1e-4 m²/s). La ley powerLaw queda desactivada.

Con H=0.02 m, Umedia=0.01 m/s y z de espesor 0.001 m: Re_H=2, Q=2e-7 m³/s (caudal del dominio extruido). Para flujo plenamente desarrollado entre placas, Ux(y)=6 Umedia (y/H)(1-y/H), Umax=0.015 m/s y -dp/dx=12 nu Umedia/H²=0.03 m/s², donde p es presión cinemática. La condición de entrada uniforme introduce desarrollo hidrodinámico: comparar dentro de la región desarrollada, no en la entrada.

Preparar con `bash scripts/prepare_case.sh 01a-canal-no-newtoniano --variant newtonian --output runs/channel-newtonian`. No se ha ejecutado la variante.
