#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "$0")"
src="${FOAM_TUTORIALS:?Cargar OpenFOAM}/multiphase/multiphaseInterFoam/laminar/damBreak4phase"
[[ -d "$src" && ! -e case ]] || { echo "Tutorial ausente o destino existente" >&2; exit 1; }
cp -a "$src" case
cd case
[[ -d 0 ]] || cp -a 0.orig 0
for phase in water oil air; do [[ -f "0/alpha.$phase" ]] || exit 1; done
rm -f 0/alpha.mercury
foamDictionary constant/transportProperties -entry phases -set '(
    water
    {
        transportModel Newtonian;
        nu [0 2 -1 0 0 0 0] 1.002e-06;
        rho [1 -3 0 0 0 0 0] 998;
    }
    oil
    {
        transportModel Newtonian;
        nu [0 2 -1 0 0 0 0] 5.56e-05;
        rho [1 -3 0 0 0 0 0] 900;
    }
    air
    {
        transportModel Newtonian;
        nu [0 2 -1 0 0 0 0] 1.5e-05;
        rho [1 -3 0 0 0 0 0] 1.2;
    }
)'
foamDictionary constant/transportProperties -entry sigmas -set '(
    (air water) 0.072
    (air oil) 0.030
    (water oil) 0.025
)'
cat > system/blockMeshDict <<'EOF'
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object blockMeshDict;
}
convertToMeters 1;
vertices
(
    (0 0 0) (0.03 0 0) (0.03 0.03 0) (0 0.03 0)
    (0 0 0.0002) (0.03 0 0.0002) (0.03 0.03 0.0002) (0 0.03 0.0002)
);
blocks (hex (0 1 2 3 4 5 6 7) (150 150 1) simpleGrading (1 1 1));
edges ();
boundary
(
    walls { type wall; faces ((0 4 5 1) (1 5 6 2) (0 3 7 4)); }
    atmosphere { type patch; faces ((3 2 6 7)); }
    frontAndBack { type empty; faces ((0 1 2 3) (4 7 6 5)); }
);
mergePatchPairs ();
EOF
cat > system/setFieldsDict <<'EOF'
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object setFieldsDict;
}
defaultFieldValues
(
    volScalarFieldValue alpha.water 0
    volScalarFieldValue alpha.oil 0
    volScalarFieldValue alpha.air 1
);
regions
(
    boxToCell
    {
        box (0 0 0) (0.03 0.015 0.0002);
        fieldValues
        (
            volScalarFieldValue alpha.water 1
            volScalarFieldValue alpha.oil 0
            volScalarFieldValue alpha.air 0
        );
    }
    sphereToCell
    {
        centre (0.015 0.020 0.0001);
        radius 0.002;
        fieldValues
        (
            volScalarFieldValue alpha.water 0
            volScalarFieldValue alpha.oil 1
            volScalarFieldValue alpha.air 0
        );
    }
);
EOF
for entry in 'application multiphaseInterFoam' 'startFrom startTime' 'startTime 0' 'endTime 0.15' 'deltaT 1e-6' 'writeControl adjustableRunTime' 'writeInterval 0.002' 'adjustTimeStep yes' 'maxCo 0.2' 'maxAlphaCo 0.2' 'maxDeltaT 1e-4'; do
    foamDictionary system/controlDict -entry "${entry%% *}" -set "${entry#* }"
done
for phase in water oil air; do
    initial=0; [[ "$phase" != air ]] || initial=1
    foamDictionary "0/alpha.$phase" -entry internalField -set "uniform $initial"
    foamDictionary "0/alpha.$phase" -entry boundaryField -set "{ walls { type zeroGradient; } atmosphere { type inletOutlet; inletValue uniform $initial; value uniform 0; } frontAndBack { type empty; } }"
done
foamDictionary 0/U -entry boundaryField -set '{ walls { type noSlip; } atmosphere { type pressureInletOutletVelocity; value uniform (0 0 0); } frontAndBack { type empty; } }'
foamDictionary 0/p_rgh -entry boundaryField -set '{ walls { type fixedFluxPressure; value uniform 0; } atmosphere { type totalPressure; p0 uniform 0; U U; phi phi; rho rho; psi none; gamma 1; value uniform 0; } frontAndBack { type empty; } }'
if [[ -f 0/p ]]; then foamDictionary 0/p -entry boundaryField -set '{ walls { type zeroGradient; } atmosphere { type fixedValue; value uniform 0; } frontAndBack { type empty; } }'; fi
