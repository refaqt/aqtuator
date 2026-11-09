"""Rebuild the printed read head cable clamp from `cad/params/default.csv`, in the GUI or headless.

Two printed halves hold the read head cable where it leaves carriage-bottom. Each half
has a half-round groove as wide as the cable. The halves lie in a pocket in the
top of carriage-bottom, and carriage-top closes the pocket. When both halves
touch the cable, the stack is `cable_clamp_squeeze` higher than the pocket is
deep. So carriage-top presses the halves onto the cable and holds it. Each
half is `cable_clamp_side_gap` smaller than the pocket on every side.

Every size is an expression on the `Params` sheet, which this script fills
from the module parameters. Print both halves in a tough material; they carry
no water.

Run headless with:

    FreeCADCmd modules/compact-stage/cad/parts/read-head-cable-clamp/build_model.py

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
sys.path.append(str(_HERE.parent / "cooling-block"))

from cad_build import bind, body, frame, main, part  # noqa: E402
import cooling_outline as co  # noqa: E402

P = "Params."

#: The axes and origin of this part.
AXES = (
    "Origin on the floor of the clamp pocket in carriage-bottom, under the "
    "cable axis, in the middle of the clamp length. X along the cable "
    "(the same way as carriage-bottom X), Z up."
)

CABLE = "read_head_cable_d"

DERIVED = {
    "cable_r": f"={CABLE} / 2",
    "half_h": f"={CABLE} / 2 + cable_clamp_wall",
    "half_w": f"={CABLE} / 2 + cable_clamp_side_wall",
    "half_l": "=cable_clamp_l / 2",
}

USED = (CABLE, "cable_clamp_l", "cable_clamp_wall", "cable_clamp_side_wall", "cable_clamp_r")


def _fill_sheet(doc, params):
    found = doc.getObjectsByLabel("Params")
    sheet = found[0] if found else doc.addObject("Spreadsheet::Sheet", "Params")
    sheet.clearAll()
    row = 1
    for alias in USED:
        sheet.set(f"A{row}", alias)
        sheet.set(f"B{row}", f"={params[alias]} mm")
        sheet.setAlias(f"B{row}", alias)
        row += 1
    for alias, expr in DERIVED.items():
        sheet.set(f"A{row}", alias)
        sheet.set(f"B{row}", expr)
        sheet.setAlias(f"B{row}", alias)
        row += 1
    doc.recompute()
    return sheet


def _plane(b, role):
    return next(f for f in b.Origin.OriginFeatures if getattr(f, "Role", "") == role)


def _half(doc, container, label, z_expr, v):
    """One half: a block with rounded corners and a half-round groove for the cable."""
    import Sketcher

    b = body(doc, label, container=container)
    for obj in list(b.Group):
        if obj.TypeId not in ("App::Origin", "PartDesign::CoordinateSystem"):
            b.removeObject(obj)
            doc.removeObject(obj.Name)
    sk = b.newObject("Sketcher::SketchObject", f"{label}Outline")
    sk.AttachmentSupport = [(_plane(b, "XY_Plane"), "")]
    sk.MapMode = "FlatFace"
    if z_expr:
        bind(sk, ".AttachmentOffset.Base.z", z_expr)
    hl, hw = v("half_l"), v("half_w")
    co.rounded_rect(sk, -hl, hl, -hw, hw, v("cable_clamp_r"), {
        "x0": f"-{P}half_l", "x1": f"{P}half_l", "y0": f"-{P}half_w", "y1": f"{P}half_w",
        "r": f"{P}cable_clamp_r"})
    pad = b.newObject("PartDesign::Pad", f"{label}Pad")
    pad.Profile = sk
    bind(pad, "Length", f"{P}half_h")
    gs = b.newObject("Sketcher::SketchObject", f"{label}GrooveSketch")
    gs.AttachmentSupport = [(_plane(b, "YZ_Plane"), "")]
    gs.MapMode = "FlatFace"
    co.circles(gs, [((0.0, v("half_h"), v("cable_r")), ("0 mm", f"{P}half_h", f"{P}cable_r"))])
    groove = b.newObject("PartDesign::Pocket", f"{label}Groove")
    groove.Profile = gs
    groove.Type = "ThroughAll"
    groove.SideType = "Symmetric"
    sk.Visibility = gs.Visibility = False
    return b


def build(doc, params):
    """Two printed halves of the read head cable clamp."""
    container = part(doc, "read-head-cable-clamp")
    sheet = _fill_sheet(doc, params)

    def v(alias):
        val = getattr(sheet, alias)
        return float(getattr(val, "Value", val))

    _half(doc, container, "Lower", None, v)
    _half(doc, container, "Upper", f"{P}half_h", v)
    doc.recompute()
    # The upper half starts on the split plane. Both grooves are the same
    # circle on the split plane, so the cable fills both.
    frame(doc, "IF_carriage", x="0", y="0", z="0", container=container)


main(build, globals(), cad_dir=_HERE)
