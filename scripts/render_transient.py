#!/usr/bin/env pvpython
"""Render OpenFOAM time steps as an MP4 or image sequence with ParaView pvpython.

Run with: pvpython scripts/render_transient.py cases/32-chorro-animado --output video.mp4
Requires ParaView with video writer support (or choose .png for a frame).
"""
import argparse
from pathlib import Path
from paraview.simple import (
    OpenFOAMReader, GetAnimationScene, GetActiveViewOrCreate,
    Show, Hide, ColorBy, GetColorTransferFunction, GetScalarBar,
    SaveAnimation, ResetCamera, UpdatePipeline,
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("case", type=Path)
parser.add_argument("--output", type=Path, default=Path("animation.avi"))
parser.add_argument("--field", default="U")
parser.add_argument("--fps", type=int, default=24)
parser.add_argument("--width", type=int, default=1280)
parser.add_argument("--height", type=int, default=720)
args = parser.parse_args()

case = args.case.resolve()
if not (case / "system" / "controlDict").exists():
    parser.error("No existe system/controlDict en el caso.")
if not (case / "constant" / "polyMesh" / "points").exists():
    parser.error("Falta la malla: ejecutar primero Allrun.")
foam = case / "case.foam"
foam.touch(exist_ok=True)
reader = OpenFOAMReader(FileName=str(foam))
reader.MeshRegions = ["internalMesh"]
reader.UpdatePipeline()
scene = GetAnimationScene()
scene.UpdateAnimationUsingDataTimeSteps()
view = GetActiveViewOrCreate("RenderView")
view.ViewSize = [args.width, args.height]
rep = Show(reader, view)
rep.Representation = "Surface"
ColorBy(rep, ("CELLS", args.field, "Magnitude") if args.field == "U" else ("CELLS", args.field))
rep.RescaleTransferFunctionToDataRange(True, False)
rep.SetScalarBarVisibility(view, True)
view.ResetCamera()
args.output.parent.mkdir(parents=True, exist_ok=True)
SaveAnimation(str(args.output.resolve()), view, FrameRate=args.fps,
              ImageResolution=[args.width, args.height])
print(f"Animación: {args.output.resolve()}")
