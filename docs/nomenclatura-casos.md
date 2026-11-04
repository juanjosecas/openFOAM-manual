# Convención de nombres de casos

- **Formato:** `NN[-letra]-descripcion-fisica[-modalidad]`.
- Usar español y ASCII, minúsculas y guiones. Evitar abreviaturas crípticas (`dambreak`, `cavity`, `case0`) cuando hay términos descriptivos.
- Conservar la numeración de tutoriales existentes. El número **no** codifica solver ni dificultad.
- Identificar variantes con un sufijo explícito: `-animacion`, `-transitorio`, `-estacionario`, `-variante-1`.
- No incorporar subdirectorios de variantes en otros casos; cada caso conserva sus propios archivos y scripts.

## Equivalencias de migración

| Nombre anterior | Nombre actual |
|---|---|
| `01-anexo-exportacion` | `01b-exportacion-resultados` |
| `01-canal-no-newtoniano` | `01a-canal-no-newtoniano` |
| `02-canal-obstaculos` | `02-flujo-canal-con-obstaculos` |
| `03-estenosis-capilar` | `03-flujo-en-estenosis` |
| `04-chorro-agua` | `04-chorro-de-agua` |
| `07-svg-gmsh` | `07-mallado-desde-svg` |
| `08-tuberia-cilindrica-3d` | `08-flujo-en-tuberia-3d` |
| `09-cavity-2d` | `09-cavidad-con-tapa-movil` |
| `10a-tuberia-laminar-case0` | `10a-tuberia-laminar-base` |
| `10b-tuberia-laminar-case1` | `10b-tuberia-laminar-variante-1` |
| `10c-tuberia-laminar-case2` | `10c-tuberia-laminar-variante-2` |
| `11-dambreak-2d` | `11-rotura-de-presa-2d` |
| `12-goldschmidt-particulas` | `12-transporte-de-particulas` |
| `13-stl-snappy-esfera` | `13-mallado-esfera-desde-stl` |
| `13b-esfera-agua-laminar` | `13b-flujo-laminar-alrededor-esfera` |
| `14a-difusion-farmaco` | `14a-difusion-de-farmaco` |
| `23-flexion-viga` | `23-flexion-de-viga` |
| `24-conduccion-1d` | `24-conduccion-de-calor-1d` |
| `25-refraccion-luz` | `25-refraccion-de-luz` |
| `26-refraccion-interfoam` | `26-refraccion-en-interfaz-de-fluidos` |
| `30-vaca-estela-animada` | `30-estela-de-vaca-animacion` |
| `31-canguro-estela-animada` | `31-estela-de-canguro-animacion` |
| `32-chorro-animado` | `32-chorro-de-agua-animacion` |
| `33-rotura-presa-animada` | `33-rotura-de-presa-animacion` |
| `34-canal-obstaculos-pimple` | `34-flujo-transitorio-canal-obstaculos` |
| `35-gota-aceite-agua` | `35-gota-de-aceite-sobre-agua` |
| `cow_incompressible_steady` | `27-flujo-estacionario-alrededor-vaca` |
| `cow_incompressible_transient` | `28-flujo-transitorio-alrededor-vaca` |
| `kangarooWake` | `29-estela-transitoria-de-canguro` |

Se renombraron los directorios y las páginas de tutorial que compartían su nombre. Las referencias conocidas de documentación y lanzadores se actualizaron. Los comandos externos, enlaces permanentes de GitHub y rutas guardadas fuera del repositorio deben actualizarse manualmente. Esta migración no altera los diccionarios CFD salvo las referencias de rutas en scripts.
