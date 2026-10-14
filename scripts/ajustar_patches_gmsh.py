#!/usr/bin/env python3
"""Convierte el patch frontAndBack a empty en polyMesh/boundary.

Comprueba presencia y unicidad. NO renombra patches ni corrige mallas.
"""
from pathlib import Path
import re
f=Path("constant/polyMesh/boundary")
s=f.read_text()
m=list(re.finditer(r"(?m)^\s*frontAndBack\s*\{([^{}]*)\}",s))
if len(m)!=1:
    raise SystemExit(f"Esperaba un único patch frontAndBack; encontré {len(m)}. Inspeccionar boundary manualmente.")
block=m[0].group(1)
if not re.search(r"\btype\s+\w+\s*;",block):
    raise SystemExit("El patch no tiene una entrada type.")
new=re.sub(r"\btype\s+\w+\s*;","type empty;",block,count=1)
f.write_text(s[:m[0].start(1)]+new+s[m[0].end(1):])
print("frontAndBack convertido a empty.")
