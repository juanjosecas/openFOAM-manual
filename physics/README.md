# Generador de propiedades físicas

Independiente de geometry/generate.py. Lee los nombres de patches de una geometría ya generada y escribe un caso OpenFOAM nuevo. No modifica la malla fuente ni requiere Gmsh para esta etapa. Python 3.11+ (biblioteca estándar).

## Flujo de trabajo

Desde la raíz:

```bash
# Etapa 1: geometría (solo se repite si cambia la forma o malla)
python geometry/generate.py geometry/templates/obstacles.toml --output runs/geometry-demo

# Etapa 2: física (editar el TOML antes de preparar cada ensayo)
python physics/generate.py physics/templates/steady.toml --geometry runs/geometry-demo --output runs/agua

# Etapa 3: importar y comprobar; todavía sin solver
bash scripts/run_docker.sh runs/agua --mesh

# Etapa 4: resolver usando la malla importada
bash scripts/run_docker.sh runs/agua --solve-only
```

También se puede ejecutar directamente bash scripts/run_docker.sh runs/agua en una copia sin malla. Para repetir con otra viscosidad o velocidad, generar un nuevo caso usando la misma carpeta geométrica. El generador se niega a sobrescribir salidas.

## Variables

| Sección | Significado |
| --- | --- |
| fluid.rho | Densidad [kg/m³]. |
| fluid.nu o fluid.mu | Viscosidad cinemática [m²/s] o dinámica [Pa·s]; elegir una. |
| simulation.mode | steady (simpleFoam) o transient (pimpleFoam). |
| simulation.end | Iteraciones en steady; segundos en transient. |
| simulation.write_interval | Iteraciones o segundos respectivamente. |
| simulation.delta_t, max_delta_t, max_co | Controles temporales del modo transient. |
| initial.velocity, initial.pressure_pa | Estado uniforme inicial. |
| boundaries.NOMBRE | Condición para un patch existente. |

Puertos: type="velocity" con speed positivo (dirección normal hacia el fluido calculada desde side) o velocity=[Ux,Uy,0]; type="pressure" con pressure_pa relativa. Se requiere declarar cada puerto y al menos una presión fija. Se permiten diferencias de presión entre puertos y múltiples entradas de velocidad. El kind de geometría es una etiqueta: la condición física la determina este TOML.

Paredes: noSlip por defecto; slip opcional por patch. frontAndBack siempre empty.

La presión interna de simpleFoam/pimpleFoam es cinemática: p=presión_Pa/rho. rho queda en case.json, ya que el solver incompresible de densidad constante utiliza nu. No se calcula flujo compresible.

La resolución numérica usa esquemas iniciales conservadores (upwind) y tolerancias predefinidas; editar los diccionarios generados si se necesita mayor precisión.

## Archivos generados

0/U, 0/p, constant/transportProperties, constant/turbulenceProperties, system/controlDict, system/fvSchemes, system/fvSolution y system/changeDictionaryDict; copia de channel.msh y configuraciones de origen. Allrun y Allclean son copias de los lanzadores compartidos.

Se admite flujo laminar incompresible plano newtoniano y powerLaw. Calor, turbulencia, transporte de especies y multifase quedan fuera del alcance. No se ha ejecutado el generador, la importación ni el solver.

## Ensayos adicionales

Los archivos de templates/ se usan con la misma geometría de ejemplo:

- flow_rate.toml: caudal volumétrico o másico constante hacia el dominio, mediante flowRateInletVelocity. En 2D el caudal incluye el espesor físico de extrusión. No imponer a la vez velocidad y caudal en un puerto.
- pulsatile.toml: tabla [tiempo, velocidad normal] interpolada linealmente mediante uniformFixedValue. Debe cubrir desde cero hasta end; no repite ciclos automáticamente ni permite flujo inverso.
- power_law.toml: viscosidad cinemática efectiva limitada entre nu_min y nu_max, con ley k * gammaDot^(n-1). k tiene unidades m²·s^(n−2); nu/mu es el valor de transporte base, no la viscosidad efectiva. La densidad es constante. n<1 adelgaza por cizalla; n>1 espesa, dentro de las cotas. Estos valores son ilustrativos.

```bash
python physics/generate.py physics/templates/pulsatile.toml --geometry runs/geometry-demo --output runs/pulso
bash scripts/run_docker.sh runs/pulso --mesh
bash scripts/run_docker.sh runs/pulso --solve-only
```

Referencia de sintaxis: https://api.openfoam.com/2406/classFoam_1_1flowRateInletVelocityFvPatchVectorField.html . Los diccionarios powerLaw y uniformFixedValue siguen la estructura de los casos 01a y 08 del repositorio. Sin pruebas de ejecución.
