"""Rebuild the printed cooling block from `cad/params/default.csv`, in the GUI or headless.

The cooling block takes the water from the two ends of the cooling channel in
carriage-bottom and brings it to the side face of the carriage. It lies in a
5 mm pocket in the top of carriage-bottom. Its arm crosses over the motor
cable where the cable comes up through the carriage, and runs to the side
face. Outside the side face, a head holds two Festo push-in fittings
NPQH-D-M5-Q4-P10, screwed into M5 threads tapped in the print. The hoses
push into the fittings.

Seals:

* Two standard 5 x 1.5 NBR 70 O-rings, as face seals in the bottom of the
  block, one around each port.
* Each fitting has its own sealing ring under its hex. The end face of the
  head is flat for it.

Three countersunk M2.5 screws come up from below through carriage-bottom and
pull the block onto the pocket floor: two in the wide part, one near the side
face. All three sit on the centre line of the block.

The block is a chain of PartDesign features. Every sketch is fully
constrained, and every size is an expression on the `Params` sheet, which
this script fills from the module parameters. The sketches use
carriage-bottom coordinates: their attachment offset moves them to the block
origin. The outline is the same function as the pocket in carriage-bottom
(`cooling_outline.py`), smaller by `cooling_block_gap`.

Print it in SLA resin (for example a tough resin), with the top face on the
build plate: the top of the block and of the head is one flat face. The head
hangs down outside the side face, so the M5 threads sit lower than the
passages; a short drop in the head joins them. The passages inside are
closed, so a resin print is needed: an FDM print is not water-tight. Tap the
three M2.5 holes and the two M5 holes in the resin.

Run headless with:

    FreeCADCmd modules/compact-stage/cad/parts/cooling-block/build_model.py

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
sys.path.append(str(_HERE))

from cad_build import bind, body, frame, main, part  # noqa: E402
import cooling_outline as co  # noqa: E402

P = "Params."

#: The axes and origin of this part.
AXES = (
    "Origin on the bottom face of the block, on the axis of screw A "
    "(x = cooling_screw_a_x, y = cooling_arm_y0 in carriage-bottom). "
    "X and Y run the same way as in carriage-bottom, Z up. "
    "In carriage-bottom the origin sits on the pocket floor, "
    "z = carriage_top_z - cooling_pocket_depth."
)

#: Sizes made from the module parameters. They go on the sheet too.
DERIVED = {
    "ox": "=cooling_screw_a_x",
    "oy": "=cooling_arm_y0",
    "block_t": "=cooling_pocket_depth - cooling_block_top_gap",
    "passage_z": "=(port_groove_depth + cooling_pocket_depth - cooling_block_top_gap) / 2",
    "ring_od": "=port_oring_id + 2 * port_oring_cs",
    "head_x0": "=carriage_edge_x + cooling_block_gap",
    "head_x1": "=carriage_edge_x + cooling_block_gap + fit_head_l",
    "head_half_w": "=fit_pitch / 2 + fit_thread_d / 2 + fit_wall",
    "head_half_h": "=fit_thread_d / 2 + fit_wall",
    "fit_z": "=cooling_pocket_depth - cooling_block_top_gap - fit_thread_d / 2 - fit_wall",
}

#: Parameters the block reads. They are copied to its sheet.
USED = (
    "carriage_top_z", "carriage_edge_x", "cooling_pocket_depth", "cooling_block_gap",
    "cooling_block_top_gap", "cooling_body_x0", "cooling_body_y0", "cooling_body_y1",
    "cooling_body_r", "cooling_arm_w", "cooling_arm_x0", "cooling_arm_y0",
    "cooling_arm_bend_x", "cooling_arm_y", "cooling_arm_r", "cooling_end_r",
    "port_a_x", "port_a_y", "port_b_x", "port_b_y", "port_oring_id", "port_oring_cs",
    "port_groove_depth", "port_groove_w", "cooling_passage_d", "cooling_passage_offset",
    "cooling_screw_a_x", "cooling_screw_b_x", "cooling_screw_c_x",
    "cooling_tap_depth", "cooling_screw_d", "fit_thread_d", "fit_tap_depth", "fit_wall", "fit_pitch",
    "fit_head_l", "fit_head_r", "fit_jog_x0", "fit_jog_x1",
)


def _fill_sheet(doc, params):
    """The `Params` sheet: one aliased cell per parameter, then the derived sizes."""
    found = doc.getObjectsByLabel("Params")
    sheet = found[0] if found else doc.addObject("Spreadsheet::Sheet", "Params")
    sheet.clearAll()
    row = 1
    for alias in USED:
        value = getattr(params[alias], "Value", params[alias])
        sheet.set(f"A{row}", alias)
        sheet.set(f"B{row}", f"={value} mm")
        sheet.setAlias(f"B{row}", alias)
        row += 1
    for alias, expr in DERIVED.items():
        sheet.set(f"A{row}", alias)
        sheet.set(f"B{row}", expr)
        sheet.setAlias(f"B{row}", alias)
        row += 1
    doc.recompute()
    return sheet


def _reader(sheet):
    def v(alias):
        value = getattr(sheet, alias)
        return float(getattr(value, "Value", value))
    return v


def _xy(body_obj):
    return next(f for f in body_obj.Origin.OriginFeatures if getattr(f, "Role", "") == "XY_Plane")


def _yz(body_obj):
    return next(f for f in body_obj.Origin.OriginFeatures if getattr(f, "Role", "") == "YZ_Plane")


def _sketch(body_obj, name, plane, offset):
    """A sketch on `plane`, moved by `offset`: (x, y, z) expressions in the sketch's own axes."""
    sk = body_obj.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = [(plane, "")]
    sk.MapMode = "FlatFace"
    for axis, expr in zip("xyz", offset):
        if expr is not None:
            bind(sk, f".AttachmentOffset.Base.{axis}", expr)
    return sk


def _clear(doc, block_body):
    for obj in list(block_body.Group):
        if obj.TypeId in ("App::Origin", "PartDesign::CoordinateSystem"):
            continue
        block_body.removeObject(obj)
        doc.removeObject(obj.Name)
    old = doc.getObject("BlockShape")
    if old is not None:
        block_body.BaseFeature = None
        doc.removeObject(old.Name)


def build(doc, params):
    """The printed cooling block between the cooling channel and the two fittings."""
    import FreeCAD

    container = part(doc, "cooling-block")
    block_body = body(doc, "Body", container=container)
    _clear(doc, block_body)
    v = _reader(_fill_sheet(doc, params))
    to_carriage = (f"-{P}ox", f"-{P}oy")

    # The outline, padded up from the bottom face.
    gap = v("cooling_block_gap")
    end_x = v("head_x0") + v("fit_head_l") / 2
    sk = _sketch(block_body, "OutlineSketch", _xy(block_body), (*to_carriage, None))
    co.outline(sk, v, gap, f"{P}cooling_block_gap", end_x, f"{P}head_x0 + {P}fit_head_l / 2")
    pad = block_body.newObject("PartDesign::Pad", "BlockPad")
    pad.Profile = sk
    bind(pad, "Length", f"{P}block_t")

    # The head outside the side face. Its top is flush with the top of the
    # block (the print base), and it hangs down. It holds the two M5 threads
    # with fit_wall of resin around each.
    sk = _sketch(block_body, "HeadSketch", _xy(block_body),
                 (*to_carriage, f"{P}block_t - 2 * {P}head_half_h"))
    x0, x1 = v("head_x0"), v("head_x1")
    ya, hw = v("cooling_arm_y"), v("head_half_w")
    co.rounded_rect(sk, x0, x1, ya - hw, ya + hw, v("fit_head_r"), {
        "x0": f"{P}head_x0", "x1": f"{P}head_x1",
        "y0": f"{P}cooling_arm_y - {P}head_half_w", "y1": f"{P}cooling_arm_y + {P}head_half_w",
        "r": f"{P}fit_head_r"})
    head = block_body.newObject("PartDesign::Pad", "HeadPad")
    head.Profile = sk
    bind(head, "Length", f"2 * {P}head_half_h")

    # Port O-ring grooves in the bottom face, and a riser from each port up
    # to the passage level.
    for tag in ("a", "b"):
        px, py = f"{P}port_{tag}_x - {P}ox", f"{P}port_{tag}_y - {P}oy"
        outer = block_body.newObject("PartDesign::SubtractiveCylinder", f"Groove_{tag}")
        bind(outer, "Radius", f"{P}ring_od / 2")
        bind(outer, "Height", f"{P}port_groove_depth")
        core = block_body.newObject("PartDesign::AdditiveCylinder", f"GrooveCore_{tag}")
        bind(core, "Radius", f"{P}ring_od / 2 - {P}port_groove_w")
        bind(core, "Height", f"{P}port_groove_depth")
        riser = block_body.newObject("PartDesign::SubtractiveCylinder", f"Riser_{tag}")
        bind(riser, "Radius", f"{P}cooling_passage_d / 2")
        bind(riser, "Height", f"{P}passage_z")
        for feat in (outer, core, riser):
            bind(feat, "Placement.Base.x", px)
            bind(feat, "Placement.Base.y", py)

    # The two passages: a circle swept along each path.
    for tag, side in (("a", -1), ("b", 1)):
        spine = _sketch(block_body, f"PassageSketch_{tag}", _xy(block_body),
                        (*to_carriage, f"{P}passage_z"))
        co.passage_spine(spine, v, side)
        prof = _sketch(block_body, f"PassageProfile_{tag}", _yz(block_body),
                       (f"-{P}oy", None, f"{P}port_{tag}_x - {P}ox"))
        co.circles(prof, [((v(f"port_{tag}_y"), v("passage_z"), v("cooling_passage_d") / 2),
                           (f"{P}port_{tag}_y", f"{P}passage_z", f"{P}cooling_passage_d / 2"))])
        pipe = block_body.newObject("PartDesign::SubtractivePipe", f"Passage_{tag}")
        pipe.Profile = prof
        pipe.Spine = (spine, [f"Edge{i}" for i in range(1, 6)])
        pipe.Transition = "Round corner"
        spine.Visibility = prof.Visibility = False
        # In the head, a short drop from the passage level down to the axis
        # of the M5 thread, at the bottom face of the tapped hole.
        drop = block_body.newObject("PartDesign::SubtractiveCylinder", f"Drop_{tag}")
        bind(drop, "Radius", f"{P}cooling_passage_d / 2")
        bind(drop, "Height", f"{P}passage_z - {P}fit_z")
        bind(drop, "Placement.Base.x", f"{P}head_x1 - {P}fit_tap_depth - {P}ox")
        bind(drop, "Placement.Base.y",
             f"{P}cooling_arm_y {'-' if side < 0 else '+'} {P}fit_pitch / 2 - {P}oy")
        bind(drop, "Placement.Base.z", f"{P}fit_z")

    # The M5 threads for the fittings, in the end face of the head.
    sk = _sketch(block_body, "FittingSketch", _yz(block_body),
                 (f"-{P}oy", None, f"{P}head_x1 - {P}ox"))
    co.circles(sk, [((ya + s * v("fit_pitch") / 2, v("fit_z"), v("fit_thread_d") / 2),
                     (f"{P}cooling_arm_y {'+' if s > 0 else '-'} {P}fit_pitch / 2",
                      f"{P}fit_z", f"{P}fit_thread_d / 2")) for s in (-1, 1)])
    hole = block_body.newObject("PartDesign::Hole", "FittingThreads")
    hole.Profile = sk
    hole.Threaded = True
    hole.ThreadType = "ISOMetricProfile"
    hole.ThreadSize = "M5x0.8"
    hole.DepthType = "Dimension"
    bind(hole, "Depth", f"{P}fit_tap_depth")
    hole.DrillPoint = "Flat"

    # The three M2.5 threads for the screws from below, on the centre line.
    sk = _sketch(block_body, "ScrewSketch", _xy(block_body), (*to_carriage, None))
    pts = []
    for tag, y_alias in (("a", "cooling_arm_y0"), ("b", "cooling_arm_y0"),
                         ("c", "cooling_arm_y")):
        pts.append(((v(f"cooling_screw_{tag}_x"), v(y_alias), v("cooling_screw_d") / 2),
                    (f"{P}cooling_screw_{tag}_x", f"{P}{y_alias}", f"{P}cooling_screw_d / 2")))
    co.circles(sk, pts)
    hole = block_body.newObject("PartDesign::Hole", "ScrewThreads")
    hole.Profile = sk
    hole.Threaded = True
    hole.ThreadType = "ISOMetricProfile"
    hole.ThreadSize = "M2.5x0.45"
    hole.DepthType = "Dimension"
    bind(hole, "Depth", f"{P}cooling_tap_depth")
    hole.Reversed = True

    for obj in block_body.Group:
        if obj.TypeId == "Sketcher::SketchObject":
            obj.Visibility = False
    doc.recompute()

    # Frame on the bottom face, on the axis of screw A. It joins the frame
    # IF_cooling_block of carriage-bottom.
    frame(doc, "IF_carriage", x="0", y="0", z="0", container=container)
    # One frame on the axis of each fitting, on the end face of the head.
    # Z points out of the head, along the fitting.
    for tag, s in (("a", "-"), ("b", "+")):
        frame(doc, f"IF_fitting_{tag}", x=f"{P}head_x1 - {P}ox",
                  y=f"{P}cooling_arm_y {s} {P}fit_pitch / 2 - {P}oy", z=f"{P}fit_z",
                  angle="90 deg", axis=(0, 1, 0), container=container)
    # One frame at each port, on the bottom face: the seat of its O-ring.
    for tag in ("a", "b"):
        frame(doc, f"IF_oring_{tag}", x=f"{P}port_{tag}_x - {P}ox",
              y=f"{P}port_{tag}_y - {P}oy", z="0", container=container)
    doc.recompute()


main(build, globals(), cad_dir=_HERE)
