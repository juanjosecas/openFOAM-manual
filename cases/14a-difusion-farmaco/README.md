# 14A — Difusión 1D de una concentración normalizada (modelo biofísico idealizado)

**Estado:** archivos completos por revisión estática; **no ejecutado ni validado**. Solver objetivo: `scalarTransportFoam` de **OpenFOAM.com v2406** (comprobar disponibilidad y sintaxis también en v2412). No se requiere ningún archivo de otro caso ni de `scripts/` en la raíz del repositorio.

## Física, magnitudes y límites

Representa un soluto hipotético que difunde desde un reservorio mantenido a concentración constante hacia un medio homogéneo en reposo. El solver resuelve el campo escalar **`T = C/C0`**, adimensional: **NO es temperatura**. Se usa `T` porque ese es el nombre que espera `scalarTransportFoam`.

$$
\frac{\partial (C/C_0)}{\partial t} = D\frac{\partial^2(C/C_0)}{\partial x^2},\qquad
J=-D\frac{\partial C}{\partial x}.
$$

- Longitud `L=0.002 m` (2 mm), sección transversal ficticia de 0.1 × 0.1 mm, 200 celdas longitudinales, 1 transversal en cada eje; `transverse` es `empty`.
- Difusividad ilustrativa `DT=1e-9 m²/s`. **No representa un fármaco real** y debe reemplazarse por un dato de soluto, medio y temperatura documentados.
- Velocidad `U=(0,0,0) m/s`: sin advección ni flujo de solvente.
- Estado inicial `T=0`; fuente `T=1` (`fixedValue`, reservorio inagotable); extremo opuesto `zeroGradient` (sin salida de masa).
- Tiempo simulado `0–200 s`, `deltaT=1 s`, escritura cada `20 s`.
- Escala difusiva `L²/D=4000 s`; la frontera lejana influye menos al principio. La referencia `erfc` supone medio semiinfinito, así que **no es exacta para todo el intervalo** de un dominio finito.

La variable es `C/C0`; para convertir a concentración real, especificar `C0` con unidades y multiplicar los resultados. No representa disolución, depósito agotable, permeabilidad de tejido, metabolismo ni eficacia terapéutica.

## Estructura autocontenida

```text
14a-difusion-farmaco/
├── 0/T                         # Concentración normalizada inicial y contornos
├── 0/U                         # Velocidad nula
├── constant/transportProperties # DT
├── system/blockMeshDict        # Dominio y patches
├── system/controlDict          # Solver, tiempo, salidas
├── system/fvSchemes            # Discretización
├── system/fvSolution           # Solver lineal
├── postprocessing/analizar.py  # CSV, PNG, GIF, referencia erfc
├── Allmesh
├── Allrun
├── Allclean
├── variants/README.md
└── README.md
```

## Procedimiento exacto

Cargar OpenFOAM.com v2406/v2412 en el entorno (en Docker o en host según la instalación) y, desde la raíz del repositorio:

```bash
cd cases/14a-difusion-farmaco
foamVersion
command -v scalarTransportFoam
bash Allmesh
# Leer log.checkMesh y confirmar que no hay errores de malla.
scalarTransportFoam > log.scalarTransportFoam 2>&1
```

**Alternativa desde una copia limpia**: `bash Allrun` realiza el mallado si no existe y después ejecuta el solver. No ejecutar `Allrun` tras el procedimiento manual sobre resultados existentes. `bash Allclean` muestra lo que se borraría; `bash Allclean --yes` limpia únicamente salidas generadas, **conserva `0/` y diccionarios**.

## Exportación y gráficos

Con resultados ya generados y Python con `numpy`, `matplotlib`, `pyvista`, `imageio`:

```bash
python3 -m pip install numpy matplotlib pyvista imageio
python3 postprocessing/analizar.py
# CSV: plots/perfiles.csv
# PNG: plots/perfil_*.png
# GIF: plots/difusion.gif
foamToVTK
```

El script lee **los resultados del propio caso** con PyVista, calcula la curva de referencia `erfc` y escribe CSV, PNG y GIF. **No ejecuta el solver**. `foamToVTK` exporta a `VTK/` para ParaView u otros programas. Los gráficos solo se crean si existen tiempos simulados. La referencia seminf. es aproximada en un dominio finito y la difusividad del script debe mantenerse sincronizada con `DT`.

## Variaciones

Ver [variants/README.md](variants/README.md): cambiar `DT`, el número de celdas o la concentración normalizada de la fuente. Hacer **una modificación por copia**, regenerar malla si cambia `blockMeshDict`, y comparar perfiles y error.

## URL de origen y compatibilidad

- **Solver y ecuación originales:** https://doc.openfoam.com/2212/tools/processing/solvers/rtm/basic/scalarTransportFoam/
- **Código de `scalarTransportFoam` de OpenFOAM.com v2406:** https://api.openfoam.com/2406/dir_000015_000503.html
- **Fundamentos de difusión:** https://openfoam.es/tutoriales/conduccion-transitoria-pared-laplacianfoam
- **Investigación de biofísica del manual:** https://github.com/juanjosecas/openFOAM-manual/blob/main/docs/propuesta-difusion-farmacos.md

La configuración y la geometría de este ejemplo son **elaboración propia**, inspiradas en la ecuación de transporte escalar documentada, no una copia de un tutorial biomédico. OpenFOAM Foundation, foam-extend y OpenFOAM.com pueden diferir en estructura y modelos. No se verificó la ejecución de estos diccionarios en v2406/v2412; el primer intento debe revisar especialmente `transportProperties`, `SIMPLE` y las condiciones `empty`.
