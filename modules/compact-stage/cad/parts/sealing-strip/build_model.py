"""Rebuild the seal strip in its preloaded state, in the GUI or headless.

The strip is drawn as it lies in the assembly: flat in its pocket in the base,
and bent over the four rollers of the carriage, with the carriage in the middle
of its travel. The bent shape comes from the strip model of the seal strip
designer page, run in `simulation/cases/strip-seal-fit/`.

The scaffolding lives in `doqs/scripts/cad_build.py`. Run headless with:

    FreeCADCmd cad/parts/sealing-strip/build_model.py

See `doqs/docs/agent-cad.md` for why the interactive path never saves.
"""

import csv
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

from cad_build import body, frame, main, part, sheet  # noqa: E402

#: The axes and origin of this part.
AXES = (
    "Assembly axes: X along the travel, Y across, Z up; origin at the corner of "
    "the base. The part is placed at the origin of the assembly."
)

#: The module parameters. cad_build looks for cad/params.csv, which this module does not
#: have, so the build reads this file itself.
DEFAULTS = _HERE.parents[1] / "params" / "default.csv"

#: Centre line of the bent strip: x from roller 1, z in assembly axes.
PROFILE = _HERE.parents[2] / "simulation" / "results" / "strip-seal-fit" / "profile.csv"

# From the base (Sketch007 of Pocket005 and Hole002) and the assembly, 2026-10-29.
BASE_L = 440.0          # length of the base along X
POCKET_FLOOR = 39.85    # floor of the strip pocket
POCKET_Y = (12.0, 198.0)   # sides of the strip body in the pocket
EAR_Y = (3.0, 207.0)       # outer sides of the ears in the pocket
PRELOAD_SCREWS = [(6.5, 105.0), (433.5, 105.0)]
CORNER_SCREWS = [(5.0, 8.0), (5.0, 202.0), (435.0, 8.0), (435.0, 202.0)]
# ISO 10642 M4: the cone of the head meets the shank at 4 mm. The cone rests on
# the pocket floor (the base has no countersink), so at the top of the strip it
# is 4 + 2 * strip_t wide. The outer edge of the strip hole touches it there.
CONE_D_AT_FLOOR = 4.0
# Roller 1 of the carriage in the middle of its travel (carriage centre x = 220).
ROLLER1_X = 118.77 + (220.0 - 211.603)


def pocket_outline():
    """The strip pocket of the base (Pocket005), as one face at z = 0."""
    import Part
    from FreeCAD import Vector as V

    import math
    r = 4.0
    c45 = r * math.cos(math.radians(45))
    step_x = 18.0   # the 45° step from an ear ends on the body side, this far from the end

    def ear(xe, side):
        # xe: end of the base (0 or 440); side: +1 for high Y, -1 for low Y
        sx = 1 if xe == 0 else -1
        yo = EAR_Y[1] if side > 0 else EAR_Y[0]
        yb = POCKET_Y[1] if side > 0 else POCKET_Y[0]
        yc = yo - side * r                 # centre of the R4 arc
        # The 45° step is tangent to the arc and ends at (step_x, body side).
        xc = xe + sx * (step_x - side * (yc - yb) - r * math.sqrt(2))
        return [
            (xe, yo),
            (xc, yo),
            (xc + sx * c45, yc + side * c45),
            (xe + sx * step_x, yb),
            (xc, yc),
        ]

    left_hi, left_lo = ear(0.0, 1), ear(0.0, -1)
    right_hi, right_lo = ear(BASE_L, 1), ear(BASE_L, -1)
    edges = []

    def seg(a, b):
        edges.append(Part.LineSegment(V(*a, 0), V(*b, 0)).toShape())

    def arc(a, m, b):
        edges.append(Part.Arc(V(*a, 0), V(*m, 0), V(*b, 0)).toShape())

    def arc_mid(xc, yc, a, b):
        ang = (math.atan2(a[1] - yc, a[0] - xc) + math.atan2(b[1] - yc, b[0] - xc)) / 2
        return (xc + r * math.cos(ang), yc + r * math.sin(ang))

    # Walk round: left end low to high, top side, right end high to low, bottom side.
    seg(left_lo[0], (0.0, 105.0))
    seg((0.0, 105.0), left_hi[0])
    seg(left_hi[0], left_hi[1])
    arc(left_hi[1], arc_mid(left_hi[4][0], EAR_Y[1] - r, left_hi[1], left_hi[2]), left_hi[2])
    seg(left_hi[2], left_hi[3])
    seg(left_hi[3], right_hi[3])
    seg(right_hi[3], right_hi[2])
    arc(right_hi[2], arc_mid(right_hi[4][0], EAR_Y[1] - r, right_hi[2], right_hi[1]), right_hi[1])
    seg(right_hi[1], right_hi[0])
    seg(right_hi[0], right_lo[0])
    seg(right_lo[0], right_lo[1])
    arc(right_lo[1], arc_mid(right_lo[4][0], EAR_Y[0] + r, right_lo[1], right_lo[2]), right_lo[2])
    seg(right_lo[2], right_lo[3])
    seg(right_lo[3], left_lo[3])
    seg(left_lo[3], left_lo[2])
    arc(left_lo[2], arc_mid(left_lo[4][0], EAR_Y[0] + r, left_lo[2], left_lo[1]), left_lo[1])
    seg(left_lo[1], left_lo[0])
    return Part.Face(Part.Wire(Part.__sortEdges__(edges)))


def read_profile(t):
    """The centre line in assembly axes. The model lets the strip sink up to 0.03 mm into its
    elastic magnet bed next to rollers 1 and 4. The pocket floor is rigid, so the line stops
    there."""
    with open(PROFILE, newline="") as f:
        rows = list(csv.DictReader(f))
    z_min = POCKET_FLOOR + t / 2
    return [(ROLLER1_X + float(r["x_from_roller1_mm"]), max(z_min, float(r["z_centre_mm"])))
            for r in rows]


def bent_band(profile, t, y0, y1):
    """The bent part of the strip: the centre line offset by t/2 up and down, across y0..y1."""
    import math
    import Part
    from FreeCAD import Vector as V

    pts = profile[::5] + ([profile[-1]] if (len(profile) - 1) % 5 else [])
    top, bot = [], []
    for i, (x, z) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n, dx / n
        top.append(V(x + nx * t / 2, y0, z + nz * t / 2))
        bot.append(V(x - nx * t / 2, y0, z - nz * t / 2))
    # The ends are flat, so the band meets the flat strip in two vertical faces.
    top[0].x = bot[0].x = pts[0][0]
    top[-1].x = bot[-1].x = pts[-1][0]
    st = Part.BSplineCurve()
    st.approximate(Points=top, DegMin=3, DegMax=3, Tolerance=1e-4)
    sb = Part.BSplineCurve()
    sb.approximate(Points=bot, DegMin=3, DegMax=3, Tolerance=1e-4)
    wire = Part.Wire([
        st.toShape(),
        Part.LineSegment(top[-1], bot[-1]).toShape(),
        sb.toShape(),
        Part.LineSegment(bot[0], top[0]).toShape(),
    ])
    return Part.Face(Part.Wire(Part.__sortEdges__(wire.Edges))).extrude(V(0, y1 - y0, 0))


def strip_shape(params):
    import Part
    from FreeCAD import Vector as V

    t = float(params["strip_t"])
    end_gap = float(params["strip_end_gap"])
    edge_gap = float(params["strip_edge_gap"])
    d_corner = float(params["strip_corner_hole_d"])
    slot_l = float(params["strip_corner_slot_l"])
    d_preload = float(params["strip_preload_hole_d"])

    outline = pocket_outline().makeOffset2D(-edge_gap, join=0)
    clip = Part.makeBox(BASE_L - 2 * end_gap, 300, 1, V(end_gap, -50, -0.5))
    outline = outline.common(clip)
    outline = Part.Face(outline.Faces[0].OuterWire) if len(outline.Faces) == 1 else outline.Faces[0]
    flat = outline.extrude(V(0, 0, t))
    flat.translate(V(0, 0, POCKET_FLOOR))

    profile = read_profile(t)
    x_lo, x_hi = profile[0][0], profile[-1][0]
    y0, y1 = POCKET_Y[0] + edge_gap, POCKET_Y[1] - edge_gap
    flat = flat.cut(Part.makeBox(x_hi - x_lo, 300, 10, V(x_lo, -50, POCKET_FLOOR - 5)))
    strip = flat.fuse(bent_band(profile, t, y0, y1)).removeSplitter()

    # Holes. The corner holes are slots along X, centred on the screw, so the strip
    # can slide under the collars while the preload is set. The preload hole sits off
    # the screw axis, towards the strip middle, so that its outer edge touches the
    # cone of the screw at the top of the strip.
    r_cone = CONE_D_AT_FLOOR / 2 + t
    for x, y in CORNER_SCREWS:
        z = POCKET_FLOOR - 5
        slot = Part.makeCylinder(d_corner / 2, 10, V(x - slot_l / 2, y, z)).fuse([
            Part.makeCylinder(d_corner / 2, 10, V(x + slot_l / 2, y, z)),
            Part.makeBox(slot_l, d_corner, 10, V(x - slot_l / 2, y - d_corner / 2, z)),
        ])
        strip = strip.cut(slot)
    for x, y in PRELOAD_SCREWS:
        sx = 1 if x < BASE_L / 2 else -1
        xh = x + sx * (d_preload / 2 - r_cone)
        strip = strip.cut(Part.makeCylinder(d_preload / 2, 10, V(xh, y, POCKET_FLOOR - 5)))
    return strip


def build(doc, params):
    """The seal strip: 0.15 mm spring steel, preloaded, with the carriage in the middle.

    EN 1.4310 (AISI 301), see docs/decisions/2026-10-28_seal-strip-0-15-mm.md.
    The strip ends sit `strip_end_gap` from the base ends. Two countersunk
    screws (ISO 10642 M4) set the pull; four button head screws with collar
    (ISO 7380-2 M4) clamp the corners, through slots 1 mm long.
    """
    with open(DEFAULTS, newline="") as f:
        params = {**{r["alias"]: r["value"] for r in csv.DictReader(f)
                     if r["alias"].startswith("strip_")}, **params}
    p = sheet(doc)
    p.clearAll()
    for row, (alias, value) in enumerate(params.items(), start=1):
        p.set(f"A{row}", alias)
        p.set(f"B{row}", str(value))
        p.setAlias(f"B{row}", alias)
    doc.recompute()

    container = part(doc, "sealing-strip")
    strip_body = body(doc, "Body", container=container)
    for obj in list(strip_body.Group):
        if obj.TypeId.startswith("PartDesign::") and obj.TypeId != "PartDesign::CoordinateSystem":
            strip_body.removeObject(obj)
            doc.removeObject(obj.Name)
    old = doc.getObject("StripShape")
    if old is not None:
        strip_body.BaseFeature = None
        doc.removeObject(old.Name)
    values = {k: (v.Value if hasattr(v, "Value") else v) for k, v in params.items()}
    shape = doc.addObject("Part::Feature", "StripShape")
    shape.Label = "StripShape (preloaded, carriage in the middle)"
    shape.Shape = strip_shape(values)
    container.addObject(shape)
    strip_body.BaseFeature = shape
    shape.Visibility = False

    # Frame on the base: the corner of the base, where the part is placed.
    frame(doc, "IF_base", x="0", y="0", z="0", container=container)


main(build, globals(), cad_dir=_HERE)
