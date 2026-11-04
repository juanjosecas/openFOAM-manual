# Catálogo de casos CFD

Todos los directorios siguen `NN[-letra]-fenomeno-o-geometria[-modalidad]`, con nombres en español, minúsculas y guiones. Los identificadores numéricos históricos se conservan para mantener la secuencia del manual. `a/b` distingue variantes de un mismo tutorial. Los casos de animación se mantienen separados de sus originales.

| Identificador | Caso | 
|---|---|
| 01b | [01b-exportacion-resultados](01b-exportacion-resultados/) |
| 01a | [01a-canal-no-newtoniano](01a-canal-no-newtoniano/) |
| 02 | [02-flujo-canal-con-obstaculos](02-flujo-canal-con-obstaculos/) |
| 03 | [03-flujo-en-estenosis](03-flujo-en-estenosis/) |
| 04 | [04-chorro-de-agua](04-chorro-de-agua/) |
| 07 | [07-mallado-desde-svg](07-mallado-desde-svg/) |
| 08 | [08-flujo-en-tuberia-3d](08-flujo-en-tuberia-3d/) |
| 09 | [09-cavidad-con-tapa-movil](09-cavidad-con-tapa-movil/) |
| 10a | [10a-tuberia-laminar-base](10a-tuberia-laminar-base/) |
| 10b | [10b-tuberia-laminar-variante-1](10b-tuberia-laminar-variante-1/) |
| 10c | [10c-tuberia-laminar-variante-2](10c-tuberia-laminar-variante-2/) |
| 11 | [11-rotura-de-presa-2d](11-rotura-de-presa-2d/) |
| 12 | [12-transporte-de-particulas](12-transporte-de-particulas/) |
| 13 | [13-mallado-esfera-desde-stl](13-mallado-esfera-desde-stl/) |
| 13b | [13b-flujo-laminar-alrededor-esfera](13b-flujo-laminar-alrededor-esfera/) |
| 14a | [14a-difusion-de-farmaco](14a-difusion-de-farmaco/) |
| 23 | [23-flexion-de-viga](23-flexion-de-viga/) |
| 24 | [24-conduccion-de-calor-1d](24-conduccion-de-calor-1d/) |
| 25 | [25-refraccion-de-luz](25-refraccion-de-luz/) |
| 26 | [26-refraccion-en-interfaz-de-fluidos](26-refraccion-en-interfaz-de-fluidos/) |
| 30 | [30-estela-de-vaca-animacion](30-estela-de-vaca-animacion/) |
| 31 | [31-estela-de-canguro-animacion](31-estela-de-canguro-animacion/) |
| 32 | [32-chorro-de-agua-animacion](32-chorro-de-agua-animacion/) |
| 33 | [33-rotura-de-presa-animacion](33-rotura-de-presa-animacion/) |
| 34 | [34-flujo-transitorio-canal-obstaculos](34-flujo-transitorio-canal-obstaculos/) |
| 35 | [35-gota-de-aceite-sobre-agua](35-gota-de-aceite-sobre-agua/) |
| 27 | [27-flujo-estacionario-alrededor-vaca](27-flujo-estacionario-alrededor-vaca/) |
| 28 | [28-flujo-transitorio-alrededor-vaca](28-flujo-transitorio-alrededor-vaca/) |
| 29 | [29-estela-transitoria-de-canguro](29-estela-transitoria-de-canguro/) |

Para ejecutar desde la raíz:

```bash
bash scripts/run_docker.sh --list
bash scripts/run_docker.sh 34-flujo-transitorio-canal-obstaculos
```

**Migración:** los nombres anteriores se sustituyeron, no se crearon alias. Los comandos antiguos deben actualizarse. La tabla de equivalencias está en [docs/nomenclatura-casos.md](../docs/nomenclatura-casos.md).
