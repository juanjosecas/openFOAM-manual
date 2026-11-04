# Tutorial 03 — Estenosis capilar 2D

**Estado:** Revisión estática; **sin ejecución comprobada**.

## Archivos presentes

- `0/U`
- `0/p`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `system/blockMeshDict`
- `system/controlDict`
- `system/fvSchemes`
- `system/fvSolution`

## Lectura de la configuración

Los diccionarios y los scripts están comentados sin cambiar sus valores ni
comandos. En OpenFOAM, `clave valor;` define una entrada, `{ ... }` agrupa
subdiccionarios y `( ... )` contiene listas o vectores. `//` y `/* ... */`
introducen comentarios que no se ejecutan. Los scripts Bash usan `#`.

| Archivo | Función y significado en este caso |
| --- | --- |
| `0/U` | Velocidad inicial, entrada prescrita, paredes inmóviles y condición 2D. |
| `0/p` | Presión cinemática y referencia relativa en la salida. |
| `constant/transportProperties` | Transporte base; su `nu` no sustituye la ley efectiva del modelo laminar. |
| `constant/turbulenceProperties` | Régimen laminar y ley de viscosidad `generalizedNewtonian/powerLaw`. |
| `system/blockMeshDict` | Canal planar, estrechamiento, seis bloques y conectividad. |
| `system/controlDict` | Iteraciones, escrituras y selección de `simpleFoam` estacionario. |
| `system/fvSchemes` | Aproximaciones de convección, difusión y gradientes. |
| `system/fvSolution` | Solvers lineales, acoplamiento SIMPLE y tolerancias de parada. |
| `postprocessing/probes.function` | Fragmento opcional de sondas antes, en y después de la garganta. |
| `Allmesh`, `Allrun`, `Allclean` | Mallado, ejecución y limpieza con previsualización. |

## Interpretación hemodinámica del ejemplo

La geometría tiene **100 µm de longitud**, **10 µm de abertura** en la entrada y
**5 µm en la garganta**, situada en x=50 µm. Es una reducción del **50 % de la
altura de un canal 2D**, no una clasificación clínica de estenosis de un vaso
cilíndrico. El espesor de 1 µm permite construir la malla con una celda en z y
condiciones `empty`; no representa el diámetro de un capilar. La malla base
contiene 4000 celdas.

La entrada impone **0.5 mm/s** y las paredes permanecen rígidas e inmóviles.
Esto permite estudiar redistribución de velocidad y presión al atravesar el
estrechamiento. Al fijar la velocidad entrante, el modelo calcula la presión
compatible con ese flujo: no representa automáticamente la disminución de
caudal que se observaría al estrechar un conducto manteniendo su diferencia de
presión. El caudal derivado del espesor artificial tampoco debe interpretarse
directamente como perfusión de un tejido.

La presión `p` está en **m²/s²**. Para convertir una diferencia a Pa hace falta
una densidad justificada: `DeltaP = rho * Deltap`. El valor cero de salida es
una referencia, no presión sanguínea absoluta. Los esfuerzos de pared requieren
la viscosidad efectiva local y el gradiente de velocidad; la velocidad por sí
sola no mide esfuerzo ni daño endotelial.

### Reología realmente configurada

`transportModel Newtonian` selecciona el transporte base, mientras que el
modelo laminar `generalizedNewtonian` aplica `powerLaw`. Son dos niveles de
configuración, no dos simulaciones alternativas. Esta selección también aparece
en el log existente de la ejecución del notebook. El esquema está documentado
por [OpenCFD: modelos newtonianos generalizados](https://www.openfoam.com/news/main-news/openfoam-v20-12/solver-and-physics).

La ley es `nu_eff = min(nuMax, max(nuMin, k * gammaDot^(n-1)))`. Con `n=0.5`,
la viscosidad disminuye al aumentar la tasa de cizallamiento dentro del intervalo
no limitado por las cotas. `nuMin=1e-6` y `nuMax=1e-4` acotan la viscosidad
cinemática; `k` es el coeficiente de consistencia de esa ley. No son un
hematocrito ni umbrales médicos, y el caso no documenta una calibración
experimental de estos valores. No calcular un único Reynolds usando el `nu`
base como si fuera toda la viscosidad efectiva del dominio.

### Qué aporta la analogía capilar y qué no representa

En microvasos, los eritrocitos deformables, el hematocrito y la interacción con
la pared influyen en la resistencia al flujo; un fluido homogéneo no los resuelve
individualmente. La relación entre calibre y viscosidad aparente tampoco queda
reproducida solo por elegir una ley dependiente de cizalla. El ejemplo carece de
eritrocitos explícitos, glicocálix y una pared deformable. Por ello, sirve como
idealización de un estrechamiento microvascular, no como predicción de paso de
células, trombosis, hemólisis o isquemia. Véase [Secomb y Pries, 2013, *Blood
viscosity in microvessels: Experiment and theory*](https://comptes-rendus.academie-sciences.fr/physique/item/10.1016/j.crhy.2013.04.002.pdf).

La anotación biológica no añade modelos, sondas activas ni condiciones nuevas.
`simpleFoam` sigue siendo estacionario: sus directorios numéricos y los registros
de las sondas, si se habilitan, son iteraciones y no tiempos fisiológicos.

## Ejecución

Desde esta carpeta y con OpenFOAM cargado: `./Allrun`. Conserva logs y no elimina resultados previos.


## Preparación y ejecución

Desde la raíz del repositorio, con el entorno OpenFOAM cargado:

```bash
cd cases/03-flujo-en-estenosis
foamVersion
blockMesh 2>&1 | tee log.blockMesh
checkMesh 2>&1 | tee log.checkMesh
foamDictionary system/controlDict -entry application -value
simpleFoam 2>&1 | tee log.simpleFoam
```

**Estado:** Comandos documentados, no comprobados mediante ejecución. Alternativamente, ejecutar `bash Allrun` desde la carpeta del caso; no combinar los dos procedimientos.

## Variaciones pequeñas

Reducir la velocidad de entrada 20%; variar n; refinar la garganta sin desplazar vértices.

Modificar **una sola variable** en cada copia del caso y conservar el original. Si cambia `blockMeshDict`, regenerar la malla; no reutilizar resultados antiguos. Los casos `simpleFoam` son estacionarios y sus iteraciones no representan tiempo físico. Consultar también la [guía general](../../docs/guia-ejecucion-y-variantes.md).


## Gráficos de propiedades y diagnóstico

Consultar [Gráficos y propiedades](../../docs/graficos-y-propiedades.md) para seleccionar campos físicos y generar perfiles a partir de CSV exportados. Si hay un archivo `log.NOMBRE_SOLVER`, ejecutar desde la raíz del repositorio:

```bash
python scripts/plot_solver_log.py cases/03-flujo-en-estenosis/log.NOMBRE_SOLVER --output plots/03-flujo-en-estenosis
```

Reemplazar `NOMBRE_SOLVER` por el solver real del caso. **Este comando solo procesa logs existentes**; no inicia el cálculo. Para curvas espaciales usar `scripts/plot_csv.py` sobre CSV con columnas adecuadas. Los casos 09 y 10A–10C ya incluyen `system/sampleDict`, que se conserva.


## Ampliación transitoria

Este caso utiliza `simpleFoam` estacionario. Si interesa estudiar arranques, pulsaciones o fluctuaciones físicas, consultar la [guía de conversión a `pimpleFoam`](../../docs/simplefoam-a-transitorio.md). La transición requiere una **copia independiente** y revisar esquemas, algoritmo, compatibilidad de modelos y condiciones de contorno; no cambiar únicamente `application`.
