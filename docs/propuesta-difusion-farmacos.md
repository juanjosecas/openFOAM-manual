# Proyecto biofísico: difusión y liberación controlada de un fármaco

**Estado:** propuesta de tutorial **nuevo**, derivada de fuentes de difusión escalar y transferencia de masa; **no** es un caso ya disponible en el repositorio ni una validación farmacológica. La [investigación de fuentes](investigacion-fuentes-openfoam.md) conserva las URL originales.

## Objetivo y progresión recomendada

Crear una secuencia de casos independientes y verificables, sin partir directamente de una geometría vascular compleja:

| Fase | Fenómeno | Variable principal | Resultado |
| --- | --- | --- | --- |
| **14A** | Difusión pura 1D desde una concentración inicial localizada | $C(x,t)$ | Perfil, anchura de dispersión, conservación de masa |
| **14B** | Liberación desde un depósito o membrana en un canal sin flujo | $C(x,t)$ y flujo difusivo | Curva de liberación acumulada y efecto de $D$ |
| **14C** | Advección–difusión en un canal con velocidad conocida | $C(\mathbf{x},t)$ | Frente transportado, dispersión, tiempo de llegada |
| **14D** | Captación o degradación de primer orden | $C(\mathbf{x},t)$ | Fracción remanente, competencia transporte–reacción |
| **14E** | Transferencia entre compartimentos o tejido poroso | $C$ en dominios distintos | Partición, permeabilidad y retardo; requiere interfaces y propiedades verificadas |

La prioridad inicial es **14A**, porque puede verificarse contra una solución analítica antes de agregar advección, fuentes, membranas o reacciones.

## Ecuación física

Para una concentración $C$ en un medio homogéneo e incompresible:

$$
\frac{\partial C}{\partial t}
+\nabla\cdot(\mathbf{u}C)
=\nabla\cdot(D\nabla C)+S_C-kC.
$$

- $C$: concentración, por ejemplo mol/m³ o kg/m³; **definir una convención y conservarla**.
- $D$: difusividad molecular en m²/s.
- $\mathbf{u}$: velocidad del fluido en m/s.
- $S_C$: fuente volumétrica de concentración por segundo (sus unidades dependen de las de $C$).
- $k$: constante de degradación de primer orden en s⁻¹.

La forma anterior supone una convención compatible de flujo y concentración. Si el solver emplea **flujo volumétrico** o **másico**, densidad variable, porosidad o un campo adimensional, se debe rederivar y comprobar la ecuación implementada. **La difusividad de un fármaco no es la viscosidad cinemática `nu` del fluido.** Tampoco la concentración debe confundirse con `alpha.water`, que en VOF representa fracción de fase.

### Escalas y parámetros sin dimensiones

$$
t_D=\frac{L^2}{D},\qquad
Pe=\frac{UL}{D},\qquad
Da=\frac{kL^2}{D}.
$$

$Pe\ll1$ indica predominio difusivo; $Pe\gg1$, transporte advectivo. $Da$ compara degradación con difusión. Estos cocientes ayudan a elegir la longitud, velocidad, paso temporal y refinamiento, pero no sustituyen una prueba de independencia de malla/tiempo.

## Primera práctica: difusión pura 1D

**Geometría propuesta:** lámina unidimensional de longitud $L$, con una celda en las direcciones transversales y patches `empty` adecuados. Malla con 100, 200 y 400 celdas en $x$ como ensayo de convergencia; **no se han generado los archivos**.

**Estado inicial:** concentración uniforme $C=0$ en el interior, con $C=C_0$ impuesto en el extremo izquierdo para $t>0$ y una condición definida explícitamente en el derecho. Alternativamente, una distribución inicial localizada permite estudiar dispersión con fronteras de flujo nulo. **Son problemas físicos distintos: no mezclar sus soluciones analíticas.**

**Escala ilustrativa, NO valor farmacológico recomendado:** $L=1\ \mathrm{mm}=10^{-3}\ \mathrm{m}$, $D=10^{-10}\ \mathrm{m^2/s}$ implica $t_D=10^4\ \mathrm{s}$. El valor de $D$ debe reemplazarse por datos medidos o bibliográficos del soluto y medio concretos, con temperatura, unidades y referencia.

**Condiciones de contorno:** concentración fija para representar un reservorio ideal; gradiente cero para pared impermeable; condición de flujo o permeabilidad para membrana. Una condición `fixedValue` en la fuente representa un **reservorio inagotable**, no un implante que se vacía: para liberación finita es necesario un balance de masa del depósito.

**Solver:** usar la fuente de [`laplacianFoam` para conducción transitoria](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam) como **verificación de una ecuación matemática difusiva**, con el campo de temperatura `T` y propiedad `DT`. **No presentar `T` automáticamente como concentración física**: su dimensión es térmica, y para un campo `C` con dimensiones químicas se requiere una implementación de transporte escalar que soporte ese campo y esas dimensiones. Revisar los solvers o functionObjects disponibles en OpenFOAM.com v2406/v2412 antes de escribir diccionarios.

## Verificación analítica

Para difusión en un medio **semiinfinito**, inicialmente $C=0$, con frontera en $x=0$ mantenida a $C_0$:

$$
\frac{C(x,t)}{C_0}=\operatorname{erfc}\!\left(\frac{x}{2\sqrt{Dt}}\right).
$$

**Condiciones de validez:** $x\ge0$, $t>0$, $D$ constante, sin advección ni reacción, y frontera derecha suficientemente lejana durante el intervalo analizado. No comparar con esta solución si el dominio es corto y la frontera derecha influye, si el depósito se agota o si $D$ cambia espacialmente.

Comparar perfiles para varios tiempos y reportar errores (por ejemplo $L_2$), con estudio espacial y temporal. Graficar $C/C_0$ frente a $x/\sqrt{Dt}$.

## Segunda práctica: liberación desde un implante idealizado

Dos opciones físicamente diferenciadas:

1. **Reservorio mantenido a $C_0$:** reproduce una fuente de concentración constante; medir flujo $J=-D\nabla C$ en la interfaz.
2. **Depósito finito:** representar explícitamente la masa inicial $M_0$ y su disminución, mediante un dominio adicional, un modelo de flujo de interfaz o un balance acoplado. La masa liberada acumulada es $M_{\mathrm{lib}}(t)=M_0-M_{\mathrm{dep}}(t)$ si no existen otros mecanismos de pérdida.

**Comprobación obligatoria:** masa inicial = masa restante + masa liberada al medio + masa eliminada por salidas/reacción (según el dominio elegido), dentro del error numérico.

Una membrana con permeabilidad $P$ puede modelarse conceptualmente con $J=P(C_1-KC_2)$, donde $K$ representa partición y deben verificarse las unidades y el signo. **No inventar** un tipo de boundary condition de OpenFOAM sin verificar que exista y que implemente esa ley.

## Tercera práctica: fármaco transportado por flujo

Utilizar un campo de velocidad de un caso **newtoniano sencillo** como primer acoplamiento y luego explorar pulsaciones o reología. El [tutorial de `scalarTransportFoam` de Virginia Tech](https://www.researchgate.net/profile/Ingo-Riess/post/How_to_model_smoke_propagation_for_an_existing_velocity_field_using_scalarTransportFoam_in_OpenFOAM/attachment/5cee6f723843b0b98254daac/AS:763860613099524@1559129970722/download/5-scalarTransportFoamTutorial.pdf) es una referencia de transporte pasivo, **no una garantía de sintaxis para v2406/v2412**.

Secuencia de trabajo prevista, no comandos ejecutados:

1. Obtener y comprobar $\mathbf{u}$ y su flujo $\phi$; identificar si es estacionario o transitorio.
2. Definir concentración inicial, inyección y salida; elegir el campo escalar y su dimensión.
3. Revisar esquema temporal, advección, difusión y Courant escalar.
4. Calcular concentración a la salida, tiempo de llegada, fracción transportada y mapas espaciales.
5. Comparar $Pe$ alto/bajo y con/sin flujo, conservando $D$ y la misma masa inicial.

**Atención:** una velocidad estacionaria puede alimentar un transporte **transitorio** de concentración; no se deduce de ello que el fluido sea transitorio. Si hay acoplamiento de concentración con densidad, viscosidad o reacción química, deja de ser un escalar pasivo.

## Datos para solicitar antes de interpretar el caso como biofísico

- Nombre y estado del soluto, tamaño molecular y concentración o dosis inicial.
- Medio (agua, plasma, gel, tejido), temperatura, pH y difusividad $D$ medida o bibliográfica.
- Geometría, porosidad y tortuosidad si corresponde, y unidades originales de CAD/STL.
- Flujo, velocidad o presión; condiciones de entrada/salida; presencia de pulsatilidad.
- Mecanismo de liberación: concentración constante, depósito finito, disolución, degradación, adsorción o permeabilidad.
- Escalas de tiempo y longitud y variable experimental con la que se contrastará el modelo.

No utilizar parámetros inventados para afirmar eficacia terapéutica, dosis segura o exposición fisiológica real.

## Gráficos y entregables que debería producir el futuro tutorial

- PNG de $C(x,t)$ para varios tiempos, junto con la curva analítica.
- GIF/MP4 de concentración a **tiempos físicos**, no iteraciones estacionarias.
- CSV de concentración en sondas y curva de llegada al outlet.
- CSV de masa liberada/acumulada, fracción remanente y error de balance.
- Comparación de $D$, $Pe$ y $k$ variando **un parámetro por vez**.
- Tablas de sensibilidad espacial y temporal.

## Fuentes originales

- [Virginia Tech — Walkthrough and tutorial for scalarTransportFoam (PDF)](https://www.researchgate.net/profile/Ingo-Riess/post/How_to_model_smoke_propagation_for_an_existing_velocity_field_using_scalarTransportFoam_in_OpenFOAM/attachment/5cee6f723843b0b98254daac/AS:763860613099524@1559129970722/download/5-scalarTransportFoamTutorial.pdf).
- [OpenFOAM.es — Conducción transitoria 1D con laplacianFoam](https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam).
- [OpenFOAM.es — Referencia de laplacianFoam](https://openfoam.es/referencia/solvers/laplacianfoam).
- [CFD.at — OpenFOAM Basic Training (PDF)](https://www.cfd.at/sites/default/files/tutorialsV7/OFTutorialSeries.pdf).
- [hemodynamic4Foam — toolbox especializado, foam-extend 4.1](https://github.com/EhsanGLB/hemodynamic4Foam).

**Próximo paso propuesto:** implementar 14A como caso nuevo **solo después de verificar el solver y la sintaxis en OpenFOAM.com v2406/v2412**. No hay archivos CFD del caso 14 creados en esta incorporación documental.
