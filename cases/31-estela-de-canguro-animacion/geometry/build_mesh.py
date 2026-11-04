#!/usr/bin/env python3
"""Genera malla 2D extruida con agujero poligonal (metros)."""
from pathlib import Path
import csv
import gmsh

HERE = Path(__file__).resolve().parent
Z = 0.02
XMIN, XMAX, YMIN, YMAX = -5., 15., -5., 5.

def near(a, b):
    return abs(a-b) < 1e-5

def main():
    with (HERE / 'kangaroo_outline.csv').open(newline='') as f:
        xy = [(float(r['x']), float(r['y'])) for r in csv.DictReader(f)]
    gmsh.initialize()
    try:
        gmsh.model.add('kangaroo_wake_2d')
        g = gmsh.model.geo
        corners = [(XMIN,YMIN),(XMAX,YMIN),(XMAX,YMAX),(XMIN,YMAX)]
        op = [g.addPoint(x,y,0) for x,y in corners]
        outer = g.addCurveLoop([g.addLine(op[i],op[(i+1)%4]) for i in range(4)])
        xy.reverse()
        hp = [g.addPoint(x,y,0) for x,y in xy]
        hole_curves = [g.addLine(hp[i],hp[(i+1)%len(hp)]) for i in range(len(hp))]
        hole = g.addCurveLoop(hole_curves)
        fluid = g.addPlaneSurface([outer,hole])
        result = g.extrude([(2,fluid)],0,0,Z,numElements=[1],recombine=False)
        g.synchronize()
        volumes = [tag for dim,tag in result if dim==3]
        if len(volumes)!=1:
            raise RuntimeError('Se esperaba un volumen fluido')
        surfaces = [tag for dim,tag in gmsh.model.getBoundary([(3,volumes[0])],oriented=False)]
        groups = {name:[] for name in ('inlet','outlet','farfield','kangaroo','frontAndBack')}
        for tag in surfaces:
            x0,y0,z0,x1,y1,z1 = gmsh.model.getBoundingBox(2,tag)
            if near(z0,z1) and (near(z0,0) or near(z0,Z)):
                name='frontAndBack'
            elif near(x0,x1) and near(x0,XMIN):
                name='inlet'
            elif near(x0,x1) and near(x0,XMAX):
                name='outlet'
            elif near(y0,y1) and (near(y0,YMIN) or near(y0,YMAX)):
                name='farfield'
            else:
                name='kangaroo'
            groups[name].append(tag)
        for name,tags in groups.items():
            if not tags:
                raise RuntimeError('Grupo vacío: '+name)
            group = gmsh.model.addPhysicalGroup(2,tags)
            gmsh.model.setPhysicalName(2,group,name)
        group = gmsh.model.addPhysicalGroup(3,volumes)
        gmsh.model.setPhysicalName(3,group,'fluid')
        field = gmsh.model.mesh.field
        field.add('Distance',1)
        field.setNumbers(1,'CurvesList',hole_curves)
        field.setNumber(1,'Sampling',200)
        field.add('Threshold',2)
        for key,val in {'InField':1,'SizeMin':0.035,'SizeMax':0.4,'DistMin':0.18,'DistMax':2.5}.items():
            field.setNumber(2,key,val)
        field.setAsBackgroundMesh(2)
        for option in ('Mesh.MeshSizeFromPoints','Mesh.MeshSizeFromCurvature','Mesh.MeshSizeExtendFromBoundary'):
            gmsh.option.setNumber(option,0)
        gmsh.option.setNumber('Mesh.MshFileVersion',2.2)
        gmsh.option.setNumber('Mesh.Binary',0)
        gmsh.model.mesh.generate(3)
        gmsh.write(str(HERE/'kangaroo.msh'))
        print('Physical patches:', {k:len(v) for k,v in groups.items()})
    finally:
        gmsh.finalize()

if __name__=='__main__':
    main()
