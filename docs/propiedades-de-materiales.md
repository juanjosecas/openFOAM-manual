# Propiedades de materiales: valores de referencia

Los valores son **orientativos**, cercanos a 20 °C y presión atmosférica. Sirven para comparar casos *newtonianos* compatibles y **no reemplazan los valores originales** de los tutoriales.

| Líquido | Densidad, ρ (kg/m³) | Viscosidad dinámica, μ (Pa·s) | Viscosidad cinemática, ν=μ/ρ (m²/s) |
| --- | ---: | ---: | ---: |
| Agua | 998 | 1.00 × 10⁻³ | 1.00 × 10⁻⁶ |
| Etanol puro | 789 | 1.20 × 10⁻³ | 1.52 × 10⁻⁶ |
| Glicerina pura | 1260 | 1.49 | 1.18 × 10⁻³ |

En OpenFOAM, las propiedades deben adaptarse a la sintaxis y dimensiones del solver:

```cpp
// Ejemplo didáctico: agua newtoniana a unos 20 °C.
// nu: viscosidad cinemática [m2/s], NO viscosidad dinámica.
transportModel Newtonian;
nu [0 2 -1 0 0 0 0] 1.00e-6;
```

Para etanol, `nu` sería aproximadamente `1.52e-6`; para glicerina pura, `1.18e-3`. Si el caso emplea densidad `rho`, tensión superficial `sigma` o efectos gravitatorios, **también hay que actualizar esas propiedades**.

### Casos no newtonianos

Los modelos `powerLaw` presentes en el manual usan parámetros `k`, `n`, `nuMin` y `nuMax`. No deben sustituirse por la viscosidad de agua, etanol o glicerina sin cambiar coherentemente el modelo constitutivo. Es una **modificación física**, no un ajuste mínimo de un caso existente.

### Casos multifásicos

Los archivos `transportProperties` de los tutoriales 04 y 11 contienen propiedades para **agua y aire**. Las densidades, viscosidades y la tensión superficial `sigma` corresponden al par de fases elegido: la tabla de tres líquidos no proporciona tensiones interfaciales ni permite sustituir fases directamente.

### Comprobaciones

- `nu` se expresa en m²/s, mientras que `mu` se expresa en Pa·s.
- Una propiedad tomada a 20 °C no debe extrapolarse sin revisión a otra temperatura.
- No confundir presión cinemática con presión física en pascales.
- Conservar una copia del caso original y modificar un único parámetro por ensayo.

Fuentes de consulta: [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/) y bases especializadas de propiedades termofísicas. Los valores numéricos de esta tabla no se consideran valores certificados de referencia.
