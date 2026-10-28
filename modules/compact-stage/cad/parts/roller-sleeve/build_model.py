"""Rebuild the seal strip roller sleeve from `cad/params.csv`, in the GUI or headless.

Copy this file to `<module>/cad/build_model.py` and replace `build()` with your
part.  This file is the reviewable artefact in a pull request: a text diff,
where the `.FCStd` beside it is an opaque binary blob.

The scaffolding — transactions, save discipline, fingerprinting — lives in
`doqs/scripts/cad_build.py` and updates with the submodule.  Do not copy it
here.  Run headless with:

    FreeCADCmd cad/build_model.py

A good run ends with "Rebuilt and saved <document>".  A run that built nothing
prints an ERROR and exits 1.

See `doqs/docs/agent-cad.md` for why the interactive path never saves.
"""

import sys
from pathlib import Path

try:
    _HERE = Path(__file__).resolve().parent
except NameError:  # exec()'d from the FreeCAD console
    _HERE = Path.cwd() / "cad"


def _doqs_scripts(start):
    """Find `doqs/scripts/` by walking up from this module's `cad/`."""
    for base in [start, *start.parents]:
        candidate = base / "doqs" / "scripts"
        if (candidate / "cad_build.py").is_file():
            return candidate
    raise RuntimeError(
        f"doqs/scripts/cad_build.py not found above {start} — "
        "run from inside a machine repository with the doqs submodule checked out."
    )


sys.path.insert(0, str(_doqs_scripts(_HERE)))

from cad_build import bind, body, frame, main, part, sheet  # noqa: E402


#: The axes and origin of this part.
AXES = (
    "Z along the sleeve axis; origin at the centre of the sleeve, which runs "
    "from Z = -sleeve_l / 2 to Z = +sleeve_l / 2."
)


def build(doc, params):
    """The seal strip roller sleeve: a tube cut to length, one bearing in each end.

    Made from precision tube, 10 mm outside with a 2 mm wall, cut to
    `sleeve_l` and reamed to the bearing diameter at both ends. Each NSK
    F692ZZ bearing goes into one end, and its flange rests on the end face.
    See docs/decisions/2026-10-28_seal-strip-rollers-on-flanged-ball-bearings.md.
    """
    # The sheet holds the values of cad/params.csv, then the sizes that follow
    # from them. It is rewritten on every build.
    p = sheet(doc)
    p.clearAll()
    rows = [(alias, str(value)) for alias, value in params.items()] + [
        ("r_out", "=roller_d / 2"),
        ("r_in", "=bearing_d_out / 2"),
        ("z_start", "=-sleeve_l / 2"),
        ("z_end", "=sleeve_l / 2"),
        ("flip", "=180"),
    ]
    for row, (alias, value) in enumerate(rows, start=1):
        p.set(f"A{row}", alias)
        p.set(f"B{row}", value)
        p.setAlias(f"B{row}", alias)
    doc.recompute()

    container = part(doc, "roller-sleeve")
    sleeve = body(doc, "Sleeve", container=container)
    for obj in list(sleeve.Group):
        if obj.TypeId.startswith("PartDesign::") and obj.TypeId != "PartDesign::CoordinateSystem":
            sleeve.removeObject(obj)
            doc.removeObject(obj.Name)
    tube = sleeve.newObject("PartDesign::AdditiveCylinder", "Tube")
    bind(tube, "Radius", "Params.r_out")
    bind(tube, "Height", "Params.sleeve_l")
    bind(tube, ".Placement.Base.z", "Params.z_start")
    bore = sleeve.newObject("PartDesign::SubtractiveCylinder", "Bore")
    bind(bore, "Radius", "Params.r_in")
    bind(bore, "Height", "Params.sleeve_l")
    bind(bore, ".Placement.Base.z", "Params.z_start")

    # Joints attach to these frames. IF_centre sits on the axis in the middle
    # of the sleeve: the axle frame of the whole roller. IF_end_a and IF_end_b
    # sit on the two end faces, with Z pointing out of the sleeve, where the
    # flange of a bearing rests.
    frame(doc, "IF_centre", x="0", y="0", z="0", container=container)
    frame(doc, "IF_end_a", x="0", y="0", z="Params.z_start",
          angle="Params.flip", axis=(1, 0, 0), container=container)
    frame(doc, "IF_end_b", x="0", y="0", z="Params.z_end", container=container)


# Keep this line exactly as it is.  Do not put it under
# `if __name__ == "__main__":` -- FreeCADCmd 1.1 sets __name__ to "build_model",
# so that test is false and the build is skipped without a word.  main() builds
# unless this file is being imported.
main(build, globals(), cad_dir=_HERE)
