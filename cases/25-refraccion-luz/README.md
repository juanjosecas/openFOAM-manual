# Caso 25: refracción de la luz en líquido (2D y 3D)

**Modelo autocontenido de óptica geométrica en Python, no un solver OpenFOAM.**
No se requieren malla ni carpetas `0/`, `constant/` y `system/`: la interfaz es el plano analítico `z=0`. **Estado: revisión estática; no ejecutado ni validado experimentalmente.**

## Física y ecuaciones

Se modela un rayo que pasa del medio 1 al medio 2, con reflexión especular y refracción. Para medios homogéneos e isótropos:

$$
n_1\sin\theta_1=n_2\sin\theta_2.
$$

Los ángulos se miden **desde la normal** a la superficie. Si el rayo parte desde arriba, la dirección incidente es

$$
\mathbf d_1=(\sin\theta_1\cos\phi,\ \sin\theta_1\sin\phi,\ -\cos\theta_1).
$$

La dirección refractada es

$$
\mathbf d_2=\left(\frac{n_1}{n_2}\sin\theta_1\cos\phi,\
\frac{n_1}{n_2}\sin\theta_1\sin\phi,\
-\sqrt{1-\left(\frac{n_1}{n_2}\sin\theta_1\right)^2}\right).
$$

Desde abajo se invierte el signo vertical. Si `(n1/n2)*sin(theta1)>1`, hay **reflexión interna total** y no se dibuja rayo transmitido. Se dibuja el rayo reflejado incluso cuando existe transmisión, **sin asignarle intensidad**: no se implementan coeficientes de Fresnel.

La vista **2D** usa la coordenada `s` del plano de incidencia y `z`. La vista **3D** usa `x,y,z`, con el azimut `phi` para girar el plano de incidencia. En medios isótropos con interfaz plana, los rayos permanecen coplanares.

## Parámetros

| Opción | Descripción | Predeterminado | Unidad |
| --- | --- | --- | --- |
| `--n1` | Índice del medio de origen (aire orientativo) | 1.0003 | — |
| `--n2` | Índice del medio de destino (agua orientativa) | 1.333 | — |
| `--angulo` | Ángulo respecto a la normal | 35 | grados |
| `--azimut` | Giro del plano de incidencia | 30 | grados |
| `--desde` | Lado de origen | arriba | — |
| `--altura` | Distancia vertical inicial | 0.02 | m |
| `--longitud` | Longitud de los rayos salientes | 0.03 | m |
| `--x0`, `--y0` | Coordenadas iniciales horizontales | 0, 0 | m |
| `--pasos` | Subdivisiones CSV por rama | 60 | — |
| `--modo` | Vista de salida | ambos | 2d/3d/ambos |

Los índices dependen de temperatura, longitud de onda y composición; los valores por defecto son **ilustrativos**, no un conjunto de datos espectrales calibrado.

## Ejecución

Desde la raíz del repositorio:

```bash
cd cases/25-refraccion-luz
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
bash Allrun
```

Solo 2D, solo 3D y reflexión interna total:

```bash
python3 rayos.py --modo 2d --angulo 45
python3 rayos.py --modo 3d --angulo 45 --azimut 70
python3 rayos.py --modo ambos --desde abajo --n1 1.333 --n2 1.0003 --angulo 60
```

GIF del barrido de ángulos de 0° a 75°:

```bash
bash Allrun --gif --fotogramas 24
```

**El GIF es un barrido paramétrico, NO una evolución temporal del rayo.** No se simula la velocidad de la luz ni el movimiento del líquido.

## Archivos y resultados

- `rayos.py`: ley de Snell, cálculo de trayectorias, CSV, PNG y GIF.
- `tests/test_rayos.py`: comprobaciones de Snell, incidencia normal, reflexión interna total y geometría 3D (no ejecutadas aquí).
- `variants/README.md`: cambios pequeños de un parámetro.
- `Allrun`, `Allclean`: ejecución y limpieza segura; `requirements.txt`: dependencias.
- `plots/trayectoria_2d.csv`, `plots/trayectoria_3d.csv`: ramas, posiciones `x_m,y_m,z_m,s_m`, índices, ángulos, RIT.
- `plots/trayectoria_2d.png`, `plots/trayectoria_3d.png`: gráficos.
- `plots/barrido_2d.gif`, `plots/barrido_3d.gif`: opcionales.

El CSV se puede abrir en pandas, LibreOffice o ParaView. No se genera VTK porque no hay malla volumétrica.

```bash
bash Allclean          # Solo muestra qué se borraría
bash Allclean --yes    # Elimina únicamente plots/
```

## Limitaciones y OpenFOAM

Este ejemplo no resuelve Navier–Stokes, ondas electromagnéticas, dispersión cromática, absorción, polarización, intensidad, caústicas ni difracción. **No utiliza OpenFOAM.com v2406 ni v2412**: no hay diferencias de versión que adaptar. Los modelos de radiación térmica de OpenFOAM no equivalen automáticamente a trazado óptico refractivo.

**Extensión futura (no implementada):** obtener una interfaz libre `alpha.water=0.5` desde `interFoam`, estimar normales locales y aplicar Snell a los puntos de intersección. No se ha implementado esa lectura ni la búsqueda de intersecciones.

## Origen y referencias

Implementación didáctica propia, sin copiar código de terceros. Referencias:

- Ley de Snell: https://en.wikipedia.org/wiki/Snell%27s_law
- Reflexión interna total: https://en.wikipedia.org/wiki/Total_internal_reflection
- Matplotlib 3D: https://matplotlib.org/stable/users/explain/toolkits/mplot3d.html
- CSV en Python: https://docs.python.org/3/library/csv.html

Los enlaces no son afirmaciones de compatibilidad de un solver óptico con OpenFOAM.
