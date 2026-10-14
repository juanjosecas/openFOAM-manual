#!/usr/bin/env python3
"""Genera una malla 3D de canal delgado con Gmsh, sin requerir un SVG externo.
Caso alternativo demostrativo: NO recupera la geometría SVG histórica.
"""
from pathlib import Path
import gmsh

out=Path("geometry/canal.msh")
out.parent.mkdir(parents=True,exist_ok=True)
gmsh.initialize()
try:
    gmsh.model.add("canal_ref")
    geo=gmsh.model.geo
    x,y,z=0.2,0.02,0.001
    # Rectángulo XY extruido en Z. Cuatro caras laterales y dos caras empty.
    p=[geo.addPoint(0,0,0),geo.addPoint(x,0,0),geo.addPoint(x,y,0),geo.addPoint(0,y,0)]
    lines=[geo.addLine(p[i],p[(i+1)%4]) for i in range(4)]
    loop=geo.addCurveLoop(lines)
    surf=geo.addPlaneSurface([loop])
    for idx,line in enumerate(lines):
        geo.mesh.setTransfiniteCurve(line, 51 if idx%2==0 else 11)
    geo.mesh.setTransfiniteSurface(surf)
    geo.mesh.setRecombine(2,surf)
    generated=geo.extrude([(2,surf)],0,0,z,numElements=[1],recombine=True)
    geo.synchronize()
    # Orden documentado de geo.extrude para superficie: superior, volumen y
    # cuatro laterales correspondientes al orden de las líneas de contorno.
    if len(generated)<6:
        raise RuntimeError(f"Extrusión inesperada: {generated}")
    cap2=generated[0][1]
    vol=next(tag for dim,tag in generated if dim==3)
    sides=[tag for dim,tag in generated[2:] if dim==2]
    if len(sides)!=4:
        raise RuntimeError(f"Se esperaban 4 caras laterales; se obtuvieron {len(sides)}")
    groups={"inlet":[sides[3]],"outlet":[sides[1]],
            "walls":[sides[0],sides[2]],"frontAndBack":[surf,cap2]}
    for name,tags in groups.items():
        g=gmsh.model.addPhysicalGroup(2,tags)
        gmsh.model.setPhysicalName(2,g,name)
    v=gmsh.model.addPhysicalGroup(3,[vol])
    gmsh.model.setPhysicalName(3,v,"fluid")
    gmsh.option.setNumber("Mesh.MshFileVersion",2.2)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(out))
    print("Malla exportada:",out)
    print("Unidades geométricas: METROS; dimensiones:",(x,y,z))
finally:
    gmsh.finalize()
