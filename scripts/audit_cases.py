#!/usr/bin/env python3
"""Auditoría estructural conservadora de casos OpenFOAM. No sustituye foamDictionary/checkMesh."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1] / 'cases'
REQUIRED = ('system/controlDict','system/fvSchemes','system/fvSolution')


def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'//[^\n]*', '', s)


def audit(case):
    failures, warnings = [], []
    for file in REQUIRED:
        if not (case / file).is_file():
            warnings.append(f'No existe {file} (puede ser un ejemplo parcial).')
    config_files = [p for folder in ('0','constant','system') for p in (case/folder).rglob('*') if p.is_file()]
    for path in config_files:
        try: text = path.read_text(encoding='utf8')
        except (UnicodeDecodeError, OSError):
            warnings.append(f'{path.relative_to(case)}: no se pudo leer como UTF-8.'); continue
        if path.name in {'g','U','p','p_rgh','alpha.water','controlDict','fvSchemes','fvSolution','blockMeshDict','transportProperties','turbulenceProperties'}:
            raw=strip_comments(text)
            for opening,closing in (('{','}'),('(',')')):
                if raw.count(opening)!=raw.count(closing):
                    failures.append(f'{path.relative_to(case)}: delimitadores {opening}{closing} desequilibrados')
        if path.name in ('U','p','p_rgh') and 'boundaryField' not in text:
            failures.append(f'{path.relative_to(case)}: falta boundaryField')
    ctrl=case/'system/controlDict'
    if ctrl.is_file():
        m=re.search(r'\bapplication\s+(\w+)\s*;',strip_comments(ctrl.read_text()))
        if not m: failures.append('controlDict: application faltante')
        else:
            solver=m.group(1)
            schemes=case/'system/fvSchemes'
            if solver=='simpleFoam' and schemes.exists() and not re.search(r'\bsteadyState\s*;',schemes.read_text()):
                warnings.append('simpleFoam sin steadyState explícito en fvSchemes')
            if solver=='pimpleFoam' and (case/'system/fvSolution').exists() and not re.search(r'\bPIMPLE\s*\{', (case/'system/fvSolution').read_text()):
                warnings.append('pimpleFoam sin subdiccionario PIMPLE explícito')
    return failures,warnings

if __name__ == '__main__':
    total_errors=0
    for case in sorted(ROOT.iterdir()):
        if not case.is_dir():continue
        errors,warnings=audit(case)
        total_errors+=len(errors)
        print(f'[{"ERROR" if errors else "REVISAR" if warnings else "OK"}] {case.name}')
        for msg in errors: print('  ERROR:',msg)
        for msg in warnings: print('  AVISO:',msg)
    sys.exit(bool(total_errors))
