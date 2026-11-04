#!/usr/bin/env python3
"""Genera GIF/PNG de rapidez o vorticidad mediante PyVista."""
from pathlib import Path
import argparse
import numpy as np
import pyvista as pv
import imageio.v2 as imageio

CASE = Path(__file__).resolve().parents[1]

def internal_mesh(block):
    if 'internalMesh' in block.keys():
        return block['internalMesh']
    for child in block:
        if hasattr(child,'keys'):
            try:
                return internal_mesh(child)
            except KeyError:
                pass
    raise KeyError('internalMesh no encontrado')

def add_scalar(mesh,field):
    name = 'U' if field=='speed' else 'vorticity'
    target = 'speed' if field=='speed' else 'omega_z'
    for association in ('cell_data','point_data'):
        data = getattr(mesh,association)
        if name in data:
            arr = np.asarray(data[name])
            data[target] = np.linalg.norm(arr,axis=1) if field=='speed' else arr[:,2]
            return target
    raise KeyError(f'Campo {name} ausente: {mesh.array_names}')

def main(field,stride,max_frames):
    pv.OFF_SCREEN = True
    foam = CASE/'kangarooWake.foam'
    foam.touch(exist_ok=True)
    reader = pv.OpenFOAMReader(str(foam))
    reader.skip_zero_time = True
    if field=='vorticity':
        reader.enable_all_cell_arrays()
    times = list(reader.time_values)[::stride][:max_frames]
    if not times:
        raise RuntimeError('No hay resultados')
    out = CASE/'postprocessing'
    with imageio.get_writer(out/f'{field}.gif',mode='I',duration=0.08,loop=0) as writer:
        for i,t in enumerate(times):
            reader.set_active_time_value(float(t))
            mesh = internal_mesh(reader.read()).copy(deep=True)
            scalar = add_scalar(mesh,field)
            section = mesh.slice(normal=(0,0,1),origin=(0,0,0.01))
            pl = pv.Plotter(off_screen=True,window_size=(1280,640))
            pl.set_background('#0c1017')
            pl.add_mesh(section,scalars=scalar,cmap='inferno' if field=='speed' else 'coolwarm',
                        clim=(0,1.8) if field=='speed' else (-3,3),
                        scalar_bar_args={'title':scalar})
            pl.camera_position = [(2.5,0,12),(2.5,0,0),(0,1,0)]
            pl.camera.parallel_projection = True
            pl.camera.parallel_scale = 3.
            pl.add_text(f'Kangaroo wake | t = {t:.2f} s',font_size=12,position='upper_left')
            pic = pl.screenshot(return_img=True)
            writer.append_data(pic[:,:,:3])
            if i==0:
                imageio.imwrite(out/f'{field}_preview.png',pic[:,:,:3])
            pl.close()
    print(out/f'{field}.gif')

if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--field',choices=('speed','vorticity'),default='speed')
    ap.add_argument('--stride',type=int,default=2)
    ap.add_argument('--max-frames',type=int,default=120)
    args = ap.parse_args()
    if args.stride<=0 or args.max_frames<=0:
        ap.error('stride y max-frames deben ser positivos')
    main(args.field,args.stride,args.max_frames)
