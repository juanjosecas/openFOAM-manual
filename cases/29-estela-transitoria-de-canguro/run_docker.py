#!/usr/bin/env python3
"""Ejecuta el caso mediante scripts/foam_docker.py del repositorio."""
from pathlib import Path
import argparse
import subprocess
import sys

CASE = Path(__file__).resolve().parent
REPO = CASE.parent.parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image',default='opencfd/openfoam-default:2406')
    parser.add_argument('--timeout',type=int,default=7200)
    args = parser.parse_args()
    sys.path.insert(0,str(REPO))
    from scripts.foam_docker import foam_run
    if not (CASE/'constant/polyMesh/points').is_file():
        subprocess.run([sys.executable,str(CASE/'geometry/build_mesh.py')],check=True)
        for command in ('gmshToFoam geometry/kangaroo.msh','changeDictionary','checkMesh'):
            foam_run(command,case_dir=CASE,repo_dir=REPO,image=args.image,timeout=300)
    foam_run('pimpleFoam',case_dir=CASE,repo_dir=REPO,
             image=args.image,timeout=args.timeout,verbose=False)

if __name__=='__main__':
    main()
