# 23 — Flexión estática de viga empotrada 3D

**Estado: archivos completos por revisión estática; no ejecutado ni validado.** Solver: solidDisplacementFoam de OpenFOAM.com v2406/v2412 (disponibilidad de binario por comprobar).

Viga rectangular 3D: L=0.1 m en x, b=0.01 m en y, h=0.01 m en z; 40×4×4 celdas. Empotramiento x=0, desplazamiento D=(0,0,0) m. Tracción en la cara x=L: (0,0,-10000) Pa; las demás caras son libres de tracción. Área terminal 1e-4 m², fuerza equivalente Fz=-1 N. E=2e9 Pa, nu=0.3, rho=1200 kg/m³. Valores didácticos, no material calibrado.

$$
I_y=\frac{bh^3}{12}=8.333\cdot10^{-10}\ \mathrm{m}^4,\qquad
D_z(x)\simeq\frac{F_z x^2(3L-x)}{6EI_y},\qquad
D_z(L)\simeq-0.0002\ \mathrm{m}.
$$

El resultado analítico es **orientativo**: Euler–Bernoulli supone viga esbelta y carga puntual equivalente; el caso aplica tracción distribuida en la cara, con malla gruesa. No se exige precisión. La flecha esperada de 0.2 mm es pequeña frente a h=10 mm. No hay gravedad, plasticidad, contacto ni esfuerzos térmicos.

**Chequeos estáticos:** campo D en metros, material en mechanicalProperties (OpenFOAM.com, no physicalProperties de Foundation reciente), thermalStress no, condiciones de tracción libre en caras no cargadas, y d2dt2Schemes=steadyState. Las 120 unidades de endTime son **iteraciones pseudo-temporales, no segundos**. La convergencia no se ha comprobado.

## Ejecución

Con OpenFOAM.com cargado, desde la raíz del repositorio:

~~~bash
cd cases/23-flexion-viga
foamVersion
command -v solidDisplacementFoam
bash Allmesh
bash Allrun
tail -n 50 log.solidDisplacementFoam
foamToVTK
python3 postprocessing/analizar.py
bash Allclean
~~~

Allrun puede mallar automáticamente en una copia limpia. Allclean solo previsualiza; para borrar salidas, ejecutar bash Allclean --yes. Para postproceso se requieren numpy, matplotlib y pyvista. Los resultados CSV (plots/desplazamiento.csv) y PNG (plots/flexion.png) se generan **solo tras correr el solver**. No hay GIF porque el modelo es estático. Consultar variants/README.md para tres cambios de un solo parámetro. Todo el caso es autocontenido.

## Fuentes originales

- [Solver de elasticidad, API oficial v2412](https://api.openfoam.com/2412/solidDisplacementFoam_8C.html).
- [Tutorial oficial de análisis de tensiones, placa con agujero](https://www.openfoam.com/documentation/tutorial-guide/5-stress-analysis/5.1-stress-analysis-of-a-plate-with-a-hole).
- [Referencia conceptual de viga con carga, OpenFOAM Foundation 13](https://github.com/OpenFOAM/OpenFOAM-13/tree/master/tutorials/solidDisplacement/beamEndLoad) — **distribución incompatible; no copiar sus diccionarios**.

Geometría y archivos: elaboración didáctica propia. No se ha ejecutado OpenFOAM.
