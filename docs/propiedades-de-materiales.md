# Propiedades de materiales — tablas rápidas de referencia

Esta página permite responder «¿qué valores tiene el acero?» o «¿qué viscosidad uso para el aire?» **sin abrir archivos de configuración**. Los números son **ejemplos para enseñanza**, no propiedades certificadas ni una biblioteca válida para todas las temperaturas y presiones.

**Cómo leer las tablas:**
- **A — transcrito:** valor leído directamente en los archivos de sólidos facilitados por el usuario (\`aluminium.s\`, \`copper.s\`, \`steel.s\`), sin corregirlo.
- **B — orientativo:** valor de referencia aproximado para **20 °C y 1 atm**, agregado como ayuda práctica; **no se afirma que provenga de los archivos adjuntos**.
- **—:** propiedad no incluida o no contrastada. No inventar el contenido de un archivo que no se ha podido leer.
- Para materiales sólidos, los valores originales no especificaban aquí temperatura ni composición de aleación: **no asumir que describen una aleación particular**.

## 1. Sólidos: densidad, calor y conducción

| Material | $\rho$ (kg/m³) | $C_p$ (J/kg·K) | $k$ o $\kappa$ (W/m·K) | $D_T$ original (m²/s) | Origen |
| --- | ---: | ---: | ---: | ---: | --- |
| **Aluminio** | **2712** | **910** | **205** | **8.418 × 10⁻⁵** | A: \`aluminium.s\` |
| **Cobre** | **8940** | **390** | **401** | **1.15012 × 10⁻⁴** | A: \`copper.s\` |
| **Acero** | **7740** | **490** | **16** | **3.352 × 10⁻⁶** | A: \`steel.s\` |

Los tres archivos indicaban también \`Hf = 0\` (valor de referencia de entalpía de formación en esos datos) y \`molWeight\`: aluminio **26.98**, cobre **63.546**, acero **55.85** (convención habitual: g/mol o kg/kmol). **Para «acero», el peso molecular 55.85 corresponde esencialmente al hierro**: no define la composición química de una aleación de acero. No extrapolar \`Hf = 0\` a una afirmación universal sobre termodinámica de materiales.

**Control de coherencia:** si la difusividad térmica está definida como $\alpha=k/(\rho C_p)$, se obtiene:

| Material | $k/(\rho C_p)$ calculada (m²/s) | $D_T$ original (m²/s) | Interpretación |
| --- | ---: | ---: | --- |
| Aluminio | 8.31 × 10⁻⁵ | 8.418 × 10⁻⁵ | Diferencia pequeña (~1.3 %) |
| Cobre | 1.150 × 10⁻⁴ | 1.15012 × 10⁻⁴ | Consistentes |
| Acero | 4.22 × 10⁻⁶ | 3.352 × 10⁻⁶ | Diferencia apreciable (~20.6 % respecto al valor calculado) |

**No se corrigió** el dato original de acero. Para un problema térmico, revisar cuál es la propiedad usada realmente por el solver y qué valores corresponden a la aleación y temperatura seleccionadas.

**Cuándo sirven:** $\rho$ y $C_p$ determinan la **inercia térmica** (energía para aumentar la temperatura); $k$ determina la **conducción** a través del sólido; $\alpha$ determina la **rapidez de propagación de un cambio térmico**. Por ejemplo, una placa de cobre distribuye calor más rápido que una de acero con igual geometría, según estos valores. En \`laplacianFoam\` puede utilizarse una difusividad térmica; en transferencia conjugada, revisar si el solver necesita $\rho$, $C_p$ y $k$ por separado.

## 2. Líquidos: flujo y transferencia térmica

Valores **B, orientativos**, próximos a 20 °C; no están transcritos de \`water.l\`. La glicerina es muy sensible a temperatura y pureza.

| Líquido | $\rho$ (kg/m³) | $\mu$ (Pa·s) | $\nu=\mu/\rho$ (m²/s) | $C_p$ (J/kg·K) | $k$ (W/m·K) |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Agua** | 998 | 1.00 × 10⁻³ | 1.00 × 10⁻⁶ | ~4182 | ~0.60 |
| **Etanol puro** | 789 | 1.20 × 10⁻³ | 1.52 × 10⁻⁶ | ~2440 | ~0.17 |
| **Glicerina pura** | 1260 | 1.49 | 1.18 × 10⁻³ | ~2410 | ~0.29 |

**Cuándo sirven:** $\mu$ o $\nu$ para pérdidas de carga, número de Reynolds y flujo laminar; $\rho$ para inercia y presión; $C_p$ y $k$ para calentamiento/enfriamiento. Para \`simpleFoam\` y \`pimpleFoam\` incompresibles suele aparecer $\nu$; otros modelos piden $\mu$ y $\rho$. En \`interFoam\` también pueden ser necesarias tensión superficial $\sigma$ y propiedades de **ambas fases**.

## 3. Gases: comparación rápida

Valores **B, aproximados**, de gases puros cerca de **20 °C y 1 atm**; no son una transcripción de los archivos \`.g\`. Se incluyen los 12 nombres suministrados para consulta rápida. La densidad de los gases varía especialmente con presión y temperatura; en mezclas, estas propiedades no se obtienen copiando las de un gas puro.

| Gas | $\rho$ (kg/m³) | $\mu$ (Pa·s) | $C_p$ (J/kg·K) | $k$ (W/m·K) | Uso ilustrativo |
| --- | ---: | ---: | ---: | ---: | --- |
| **Aire** | ~1.20 | ~1.81 × 10⁻⁵ | ~1005 | ~0.026 | Convección y ventilación |
| **Nitrógeno** | ~1.16 | ~1.76 × 10⁻⁵ | ~1040 | ~0.026 | Gas inerte y mezcla |
| **Oxígeno** | ~1.33 | ~2.04 × 10⁻⁵ | ~918 | ~0.026 | Transporte de especies |
| **Dióxido de carbono** | ~1.84 | ~1.47 × 10⁻⁵ | ~844 | ~0.017 | Transporte de CO₂ |
| **Monóxido de carbono** | ~1.16 | ~1.75 × 10⁻⁵ | ~1040 | ~0.024 | Especie trazadora idealizada; gas tóxico |
| **Helio** | ~0.166 | ~1.96 × 10⁻⁵ | ~5190 | ~0.15 | Convección de gas ligero |
| **Argón** | ~1.66 | ~2.23 × 10⁻⁵ | ~520 | ~0.018 | Gas inerte |
| **Hidrógeno** | ~0.084 | ~8.8 × 10⁻⁶ | ~14300 | ~0.18 | Difusión y transferencia térmica |
| **Metano** | ~0.67 | ~1.1 × 10⁻⁵ | ~2220 | ~0.034 | Flujo de combustible, sin reacción |
| **Propano** | ~1.83 | ~8.2 × 10⁻⁶ | ~1680 | ~0.018 | Flujo de gas, sin reacción |
| **Amoníaco** | ~0.71 | ~9.8 × 10⁻⁶ | ~2060 | ~0.025 | Transporte de especie |
| **Acetileno** | ~1.09 | ~9.5 × 10⁻⁶ | ~1670 | ~0.019 | Transporte de gas, sin reacción |

**Precaución:** estos valores redondeados son una **tabla orientativa editorial**, no parámetros validados de química reactiva. Para combustión, toxicología, diseño industrial o transporte multiespecie, consultar datos a la temperatura y presión del problema, modelos de mezclas y coeficientes de difusión binaria. Las propiedades de gases combustibles no bastan para modelar una reacción.

## 4. Qué representa cada propiedad y dónde usarla

| Símbolo | Propiedad | Unidad SI | Cuándo se necesita | Ejemplos OpenFOAM |
| --- | --- | --- | --- | --- |
| $\rho$ | Densidad | kg/m³ | Inercia, flotabilidad, transporte de energía, flujos compresibles | \`buoyantPimpleFoam\`, \`interFoam\`, modelos térmicos |
| $\mu$ | Viscosidad **dinámica** | Pa·s | Esfuerzo cortante $\tau=\mu\,\partial u/\partial y$ en fluido newtoniano | Modelos que solicitan \`mu\` |
| $\nu$ | Viscosidad **cinemática** | m²/s | Reynolds $Re=UL/\nu$ y difusión de cantidad de movimiento | \`simpleFoam\`, \`pimpleFoam\`, \`icoFoam\` según modelo |
| $C_p$ | Capacidad calorífica específica | J/(kg·K) | Almacenamiento de calor, cambios de temperatura | Solvers de energía |
| $k$, $\kappa$ | Conductividad térmica | W/(m·K) | Flujo de calor $\mathbf q=-k\nabla T$ | Conducción, convección, transferencia conjugada |
| $\alpha$ o $D_T$ | Difusividad **térmica** | m²/s | Escala $t\sim L^2/\alpha$ de difusión de temperatura | Ecuación de calor; \`laplacianFoam\` según configuración |
| $D_{AB}$ | Difusividad **molecular de especie A en medio B** | m²/s | Difusión de fármacos, oxígeno, CO₂ o contaminantes | Transporte escalar/especies; **no confundir con $D_T$** |
| $\sigma$ | Tensión superficial | N/m | Interfaces agua–aire, gotas, capilaridad | \`interFoam\` |
| $M$ / \`molWeight\` | Masa molar | kg/mol o kg/kmol, según convención | Gases ideales, composición, reacciones | Termofísica de gases |
| $H_f$ | Entalpía de formación | Depende de la base del modelo | Energía química y reacciones | Modelos termoquímicos |

La misma letra **$k$** puede significar conductividad térmica, energía cinética turbulenta o un coeficiente de una ley reológica, según el diccionario. **No identificar propiedades únicamente por el nombre de la variable.**

### Cómo elegir rápidamente

- **Flujo de agua en una tubería:** usar $\rho$ y $\nu$ (o $\mu$); $C_p$ y $k$ solo si se resuelve energía.
- **Placa de acero que se calienta:** usar $\rho$, $C_p$ y $k$ o la difusividad térmica coherente con el solver; **no tiene sentido asignar viscosidad al acero rígido**.
- **Aire que enfría una placa:** usar propiedades del gas para flujo y energía, y del sólido para conducción.
- **Difusión de un fármaco en agua:** usar propiedades del agua si se calcula el flujo, pero obtener **por separado** $D_{\mathrm{fármaco,agua}}$ a la temperatura y composición apropiadas.
- **Oxígeno disuelto en sangre o tejido:** **no** usar la viscosidad ni la difusividad térmica del oxígeno gaseoso como coeficiente de difusión en líquido/tejido; requiere un $D$ de especie en ese medio.
- **Canal no newtoniano:** la viscosidad depende de la tasa de deformación; una sola $\mu$ constante no describe la ley reológica.
- **Gota de agua en aire:** se necesitan propiedades de ambas fases y $\sigma$, además de condiciones iniciales/interfaz.

## 5. Cómo convertir valores a diccionarios

Ejemplo de fluido newtoniano incompresible con agua a ~20 °C; **adaptar a la sintaxis del solver y versión**:

\`\`\`cpp
// Ejemplo conceptual para transportProperties:
transportModel Newtonian;
nu [0 2 -1 0 0 0 0] 1.00e-6;  // m²/s
\`\`\`

Conversión:

$$
\nu=\frac{\mu}{\rho},\qquad
\alpha=\frac{k}{\rho C_p}.
$$

Si el solver usa una variable \`DT\`, comprobar **qué ecuación resuelve** antes de cargarle el número. En particular, el [caso 14A](https://github.com/juanjosecas/openFOAM-manual/tree/main/cases/14a-difusion-farmaco) usa \`DT\` como **difusividad de un escalar normalizado**, mientras que en los archivos de sólidos el campo \`DT\` es compatible conceptualmente con una **difusividad térmica**. La igualdad de nombres **no** hace intercambiables sus significados físicos.

## 6. Procedencia, limitaciones y fuentes para contrastar

- **Valores A:** transcripción de los tres archivos de sólidos facilitados en la conversación; solo se publican sus **números**, **no** se incorporan los archivos \`.s\`, \`.g\` ni \`.l\`.
- **Valores B:** estimaciones ilustrativas a ~20 °C y 1 atm para consulta rápida, **no verificadas contra los archivos adjuntos**. En particular, las tablas de gases no deben citarse como transcripción de \`air.g\`, \`water.l\` u otros ficheros.
- Para propiedades termofísicas con estado de referencia documentado: [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/) y [NIST REFPROP](https://www.nist.gov/srd/refprop). Consultar fichas y condiciones concretas antes de usar números en resultados científicos.
- Para unidades, estructura de diccionarios y modelos de OpenFOAM.com: [Guía de archivos de entrada](https://www.openfoam.com/documentation/user-guide/2-openfoam-cases/2-2-basic-inputoutput-file-format).

**Regla editorial:** si se dispone más adelante del contenido verificable de los archivos de gases y agua, reemplazar o complementar las cifras B por una columna de **valor original** con condiciones de referencia y procedencia explícitas. No modificar en silencio los datos transcritos.
