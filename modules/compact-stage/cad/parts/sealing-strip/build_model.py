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

from cad_build import bind, body, dim, frame, main, part, sheet  # noqa: E402

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
EAR_R = 4.0             # radius at the outer end of each ear
EAR_STEP_X = 18.0       # the 45° step from an ear ends on the body side, this far from the end
SCREW_Y_MID = 105.0     # the preload screws sit in the middle of the width
PRELOAD_SCREWS = [(6.5, SCREW_Y_MID), (433.5, SCREW_Y_MID)]
# Corner screws 6 mm from the base ends (Niels Bosmans 2026-10-30, was 5 mm).
CORNER_SCREW_X = 6.0
CORNER_SCREW_Y = (8.0, 202.0)
CORNER_SCREWS = [(x, y) for x in (CORNER_SCREW_X, BASE_L - CORNER_SCREW_X) for y in CORNER_SCREW_Y]
# EN 1.4310, Alleima 11R51, the same as the strip model of the seal strip designer page.
E_STRIP = 185000.0      # MPa
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
    r = EAR_R
    c45 = r * math.cos(math.radians(45))
    step_x = EAR_STEP_X

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
        xh = preload_hole_x(x, d_preload, t)
        strip = strip.cut(Part.makeCylinder(d_preload / 2, 10, V(xh, y, POCKET_FLOOR - 5)))
    return strip


def preload_hole_x(x, d_preload, t):
    """Centre of the preload hole for the screw at x: off the axis, towards the strip middle,
    so that its outer edge touches the cone of the screw at the top of the strip."""
    sx = 1 if x < BASE_L / 2 else -1
    return x + sx * (d_preload / 2 - (CONE_D_AT_FLOOR / 2 + t))


def flat_map(profile, t, pull, width):
    """A function that turns an x of the bent, pulled strip into an x of the strip as cut.

    On the flat strip, a point lies as far from the strip middle as it does along the bent
    centre line, less the stretch of the pull. The stretch is taken as the same along the whole
    strip; beyond the preload holes there is no pull, which changes less than 0.001 mm.
    """
    import bisect
    import math

    xs = [x for x, _ in profile]
    s = [0.0]
    for (xa, za), (xb, zb) in zip(profile, profile[1:]):
        s.append(s[-1] + math.hypot(xb - xa, zb - za))

    def arc(x):
        # Length along the strip from the start of the profile; flat outside it.
        if x <= xs[0]:
            return x - xs[0]
        if x >= xs[-1]:
            return s[-1] + x - xs[-1]
        i = bisect.bisect_right(xs, x) - 1
        f = (x - xs[i]) / (xs[i + 1] - xs[i])
        return s[i] + f * (s[i + 1] - s[i])

    eps = pull / (E_STRIP * width * t)
    mid = BASE_L / 2
    s_mid = arc(mid)
    return lambda x: mid + (arc(x) - s_mid) / (1 + eps)


def _sheet_value(q):
    """A function that reads one alias of the sheet as a number in mm (or N)."""
    def val(alias):
        v = q.get(alias)
        return float(getattr(v, "Value", v))
    return val


def _xy_plane(body_obj):
    """The XY plane of a Body's own origin."""
    return next(f for f in body_obj.Origin.OriginFeatures if getattr(f, "Role", "") == "XY_Plane")


def _remove_features(doc, body_obj):
    """Remove every feature of a Body, so a rebuild starts clean."""
    for obj in list(body_obj.Group):
        if obj.TypeId in ("App::Origin", "PartDesign::CoordinateSystem"):
            continue
        body_obj.removeObject(obj)
        doc.removeObject(obj.Name)


def flat_outline_sketch(doc, flat_body):
    """The outline of the strip as cut: two end lines, two body sides and four ears.

    Each ear has a straight outer side, an arc and a 45° step to the body side, as in the
    strip pocket of the base, with the edge gap taken off. Every size is an expression on
    the parameter sheet. The lengths along X come from `strip_flat_l`.
    """
    import math
    import Part
    import Sketcher
    from FreeCAD import Vector as V


    val = _sheet_value(sheet(doc))
    gap, end_gap = val("strip_edge_gap"), val("strip_end_gap")
    r = val("strip_ear_r") - gap
    x_l = val("strip_base_l") / 2 - val("strip_flat_l") / 2
    x_r = x_l + val("strip_flat_l")
    # From the strip end to the ear arc centre, and to the end of the 45° step.
    c_off = (val("strip_ear_step_x") - (val("strip_ear_y1") - val("strip_ear_r") - val("strip_pocket_y1"))
             - val("strip_ear_r") * math.sqrt(2) - end_gap)
    k_off = val("strip_ear_step_x") + gap - gap * math.sqrt(2) - end_gap
    y_out = (val("strip_ear_y0") + gap, val("strip_ear_y1") - gap)
    y_body = (val("strip_pocket_y0") + gap, val("strip_pocket_y1") - gap)
    y_c = (val("strip_ear_y0") + val("strip_ear_r"), val("strip_ear_y1") - val("strip_ear_r"))

    P = "Params."
    e_xl = f"{P}strip_base_l / 2 - {P}strip_flat_l / 2"
    e_xr = f"{P}strip_base_l / 2 + {P}strip_flat_l / 2"
    e_c = (f"({P}strip_ear_step_x - ({P}strip_ear_y1 - {P}strip_ear_r - {P}strip_pocket_y1)"
           f" - {P}strip_ear_r * sqrt(2) - {P}strip_end_gap)")
    e_k = f"({P}strip_ear_step_x + {P}strip_edge_gap * (1 - sqrt(2)) - {P}strip_end_gap)"
    e_r = f"{P}strip_ear_r - {P}strip_edge_gap"
    e_yc = (f"{P}strip_ear_y0 + {P}strip_ear_r", f"{P}strip_ear_y1 - {P}strip_ear_r")
    e_yb = (f"{P}strip_pocket_y0 + {P}strip_edge_gap", f"{P}strip_pocket_y1 - {P}strip_edge_gap")

    sk = flat_body.newObject("Sketcher::SketchObject", "FlatOutline")
    sk.AttachmentSupport = [(_xy_plane(flat_body), "")]
    sk.MapMode = "FlatFace"

    def pt(a, cx, cy):
        return V(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), 0)

    def line(a, b):
        return sk.addGeometry(Part.LineSegment(a, b))

    def arc(cx, cy, a0, a1):
        return sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(cx, cy, 0), V(0, 0, 1), r),
                                               math.radians(a0), math.radians(a1)))

    # Ears: (end, side) -> centre x, arc angles; the arc runs counter-clockwise.
    ears = {}
    for end, xe, sx in (("L", x_l, 1), ("R", x_r, -1)):
        for side in (0, 1):
            cx = xe + sx * c_off
            kx = xe + sx * k_off
            ears[end, side] = (cx, y_c[side], kx)

    # Walk round counter-clockwise from the left end, low side, up.
    g_end_l = line(V(x_l, y_out[0], 0), V(x_l, y_out[1], 0))
    cx, cy, kx = ears["L", 1]
    g_ear_lh = line(V(x_l, y_out[1], 0), V(cx, y_out[1], 0))
    g_arc_lh = arc(cx, cy, 45, 90)
    g_step_lh = line(pt(45, cx, cy), V(kx, y_body[1], 0))
    cx2, cy2, kx2 = ears["R", 1]
    g_body_h = line(V(kx, y_body[1], 0), V(kx2, y_body[1], 0))
    g_step_rh = line(V(kx2, y_body[1], 0), pt(135, cx2, cy2))
    g_arc_rh = arc(cx2, cy2, 90, 135)
    g_ear_rh = line(V(cx2, y_out[1], 0), V(x_r, y_out[1], 0))
    g_end_r = line(V(x_r, y_out[1], 0), V(x_r, y_out[0], 0))
    cx3, cy3, kx3 = ears["R", 0]
    g_ear_rl = line(V(x_r, y_out[0], 0), V(cx3, y_out[0], 0))
    g_arc_rl = arc(cx3, cy3, 225, 270)
    g_step_rl = line(pt(225, cx3, cy3), V(kx3, y_body[0], 0))
    cx4, cy4, kx4 = ears["L", 0]
    g_body_l = line(V(kx3, y_body[0], 0), V(kx4, y_body[0], 0))
    g_step_ll = line(V(kx4, y_body[0], 0), pt(315, cx4, cy4))
    g_arc_ll = arc(cx4, cy4, 270, 315)
    g_ear_ll = line(V(cx4, y_out[0], 0), V(x_l, y_out[0], 0))

    C = Sketcher.Constraint
    # Plain corners, and the tangent joints at both ends of every arc.
    for a, pa, b, pb in ((g_end_l, 2, g_ear_lh, 1), (g_step_lh, 2, g_body_h, 1),
                         (g_body_h, 2, g_step_rh, 1), (g_ear_rh, 2, g_end_r, 1),
                         (g_end_r, 2, g_ear_rl, 1), (g_step_rl, 2, g_body_l, 1),
                         (g_body_l, 2, g_step_ll, 1), (g_ear_ll, 2, g_end_l, 1)):
        sk.addConstraint(C("Coincident", a, pa, b, pb))
    for a, pa, b, pb in ((g_ear_lh, 2, g_arc_lh, 2), (g_arc_lh, 1, g_step_lh, 1),
                         (g_step_rh, 2, g_arc_rh, 2), (g_arc_rh, 1, g_ear_rh, 1),
                         (g_ear_rl, 2, g_arc_rl, 2), (g_arc_rl, 1, g_step_rl, 1),
                         (g_step_ll, 2, g_arc_ll, 2), (g_arc_ll, 1, g_ear_ll, 1)):
        sk.addConstraint(C("Tangent", a, pa, b, pb))
    for g in (g_ear_lh, g_body_h, g_ear_rh, g_ear_rl, g_body_l, g_ear_ll):
        sk.addConstraint(C("Horizontal", g))
    for g in (g_end_l, g_end_r):
        sk.addConstraint(C("Vertical", g))

    dim(sk, C("DistanceX", -1, 1, g_end_l, 1, x_l), e_xl, "flat_end_left")
    dim(sk, C("DistanceX", -1, 1, g_end_r, 1, x_r), e_xr, "flat_end_right")
    dim(sk, C("DistanceY", -1, 1, g_body_h, 1, y_body[1]), e_yb[1])
    dim(sk, C("DistanceY", -1, 1, g_body_l, 1, y_body[0]), e_yb[0])
    for g, (cx, cy, kx), step, pk, e_x, e_kx in (
            (g_arc_lh, ears["L", 1], g_step_lh, 2, f"{e_xl} + {e_c}", f"{e_xl} + {e_k}"),
            (g_arc_rh, ears["R", 1], g_step_rh, 1, f"{e_xr} - {e_c}", f"{e_xr} - {e_k}"),
            (g_arc_rl, ears["R", 0], g_step_rl, 2, f"{e_xr} - {e_c}", f"{e_xr} - {e_k}"),
            (g_arc_ll, ears["L", 0], g_step_ll, 1, f"{e_xl} + {e_c}", f"{e_xl} + {e_k}")):
        side = 1 if cy > y_body[0] + 50 else 0
        dim(sk, C("Radius", g, r), e_r)
        dim(sk, C("DistanceX", -1, 1, g, 3, cx), e_x)
        dim(sk, C("DistanceY", -1, 1, g, 3, cy), e_yc[side])
        dim(sk, C("DistanceX", -1, 1, step, pk, kx), e_kx)
    return sk


def flat_holes_sketch(doc, flat_body):
    """The four corner slots and the two preload holes of the strip as cut."""
    import math
    import Part
    import Sketcher
    from FreeCAD import Vector as V


    val = _sheet_value(sheet(doc))
    x_l = val("strip_base_l") / 2 - val("strip_flat_l") / 2
    x_r = x_l + val("strip_flat_l")
    r = val("strip_corner_hole_d") / 2
    half = val("strip_corner_slot_l") / 2

    P = "Params."
    e_xl = f"{P}strip_base_l / 2 - {P}strip_flat_l / 2"
    e_xr = f"{P}strip_base_l / 2 + {P}strip_flat_l / 2"

    sk = flat_body.newObject("Sketcher::SketchObject", "FlatHolesSketch")
    sk.AttachmentSupport = [(_xy_plane(flat_body), "")]
    sk.MapMode = "FlatFace"
    C = Sketcher.Constraint

    for xe, sx, e_xe, sign in ((x_l, 1, e_xl, "+"), (x_r, -1, e_xr, "-")):
        xc = xe + sx * val("strip_flat_corner_x")
        for i, y in enumerate((val("strip_corner_screw_y0"), val("strip_corner_screw_y1"))):
            a1 = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(xc - half, y, 0), V(0, 0, 1), r),
                                                 math.pi / 2, 3 * math.pi / 2))
            a2 = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(xc + half, y, 0), V(0, 0, 1), r),
                                                 -math.pi / 2, math.pi / 2))
            top = sk.addGeometry(Part.LineSegment(V(xc + half, y + r, 0), V(xc - half, y + r, 0)))
            bot = sk.addGeometry(Part.LineSegment(V(xc - half, y - r, 0), V(xc + half, y - r, 0)))
            for a, pa, b, pb in ((a2, 2, top, 1), (top, 2, a1, 1), (a1, 2, bot, 1), (bot, 2, a2, 1)):
                sk.addConstraint(C("Tangent", a, pa, b, pb))
            sk.addConstraint(C("Horizontal", top))
            dim(sk, C("Radius", a1, r), f"{P}strip_corner_hole_d / 2")
            dim(sk, C("Radius", a2, r), f"{P}strip_corner_hole_d / 2")
            dim(sk, C("DistanceX", -1, 1, a1, 3, xc - half),
                f"{e_xe} {sign} {P}strip_flat_corner_x - {P}strip_corner_slot_l / 2")
            dim(sk, C("DistanceY", -1, 1, a1, 3, y), f"{P}strip_corner_screw_y{i}")
            dim(sk, C("DistanceX", a1, 3, a2, 3, 2 * half), f"{P}strip_corner_slot_l")
        xh = xe + sx * val("strip_flat_preload_x")
        c = sk.addGeometry(Part.Circle(V(xh, val("strip_screw_y_mid"), 0), V(0, 0, 1),
                                       val("strip_preload_hole_d") / 2))
        dim(sk, C("Diameter", c, val("strip_preload_hole_d")), f"{P}strip_preload_hole_d")
        dim(sk, C("DistanceX", -1, 1, c, 3, xh), f"{e_xe} {sign} {P}strip_flat_preload_x")
        dim(sk, C("DistanceY", -1, 1, c, 3, val("strip_screw_y_mid")), f"{P}strip_screw_y_mid")
    return sk


def build(doc, params):
    """The seal strip: 0.15 mm spring steel, preloaded, with the carriage in the middle.

    EN 1.4310 (AISI 301), see docs/decisions/2026-10-28_seal-strip-0-15-mm.md.
    The strip ends sit `strip_end_gap` from the base ends. Two countersunk
    screws (ISO 10642 M4) set the pull; four button head screws with collar
    (ISO 7380-2 M4) clamp the corners, through slots 1 mm long.

    The file holds two shapes. `sealing-strip` is the strip as it lies in the
    assembly: bent and pulled. The assembly links only this one.
    `sealing-strip-flat` is the strip as cut from the sheet, a parametric Body:
    it is longer by the extra length of the bends over the rollers, and
    shorter by the stretch of the pull, so that its holes land on the screws
    when it is fitted and pulled. It lies flat at z = 0, with its middle at the middle of
    the base.
    """
    with open(DEFAULTS, newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["alias"].startswith("strip_")]
    units = {r["alias"]: r["unit"] for r in rows}
    params = {**{r["alias"]: r["value"] for r in rows}, **params}
    values = {k: (v.Value if hasattr(v, "Value") else v) for k, v in params.items()}

    # The flat strip: where the strip end, a corner slot and a preload hole land, as cut.
    t = float(values["strip_t"])
    width = POCKET_Y[1] - POCKET_Y[0] - 2 * float(values["strip_edge_gap"])
    to_flat = flat_map(read_profile(t), t, float(values["strip_pull"]), width)
    end_x = float(values["strip_end_gap"])
    flat_end = to_flat(end_x)
    hole_x = preload_hole_x(PRELOAD_SCREWS[0][0], float(values["strip_preload_hole_d"]), t)
    derived = {
        # Sizes of the base, for the expressions of the flat strip.
        "strip_base_l": BASE_L,
        "strip_pocket_y0": POCKET_Y[0], "strip_pocket_y1": POCKET_Y[1],
        "strip_ear_y0": EAR_Y[0], "strip_ear_y1": EAR_Y[1],
        "strip_ear_r": EAR_R, "strip_ear_step_x": EAR_STEP_X,
        "strip_corner_screw_y0": CORNER_SCREW_Y[0], "strip_corner_screw_y1": CORNER_SCREW_Y[1],
        "strip_screw_y_mid": SCREW_Y_MID,
        # The strip as cut, computed from the bent shape and the pull.
        "strip_flat_l": round(2 * (BASE_L / 2 - flat_end), 4),
        "strip_flat_corner_x": round(to_flat(CORNER_SCREW_X) - flat_end, 4),
        "strip_flat_preload_x": round(to_flat(hole_x) - flat_end, 4),
    }
    units.update({k: "mm" for k in derived})

    # Remove the flat features first: they read the sheet that is cleared next.
    flat_container = part(doc, "sealing-strip-flat")
    flat_body = body(doc, "FlatBody", container=flat_container)
    _remove_features(doc, flat_body)

    p = sheet(doc)
    p.clearAll()
    for row, (alias, value) in enumerate({**params, **derived}.items(), start=1):
        unit = units.get(alias, "")
        text = str(getattr(value, "Value", value))
        p.set(f"A{row}", alias)
        p.set(f"B{row}", f"={text} {unit}" if unit in ("mm", "N") and not text.startswith("=") else text)
        p.setAlias(f"B{row}", alias)
    doc.recompute()

    outline = flat_outline_sketch(doc, flat_body)
    pad = flat_body.newObject("PartDesign::Pad", "FlatPad")
    pad.Profile = outline
    bind(pad, "Length", "Params.strip_t")
    holes = flat_holes_sketch(doc, flat_body)
    pocket = flat_body.newObject("PartDesign::Pocket", "FlatHoles")
    pocket.Profile = holes
    pocket.Type = "ThroughAll"
    pocket.Midplane = True
    outline.Visibility = holes.Visibility = False
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
    shape = doc.addObject("Part::Feature", "StripShape")
    shape.Label = "StripShape (preloaded, carriage in the middle)"
    shape.Shape = strip_shape(values)
    container.addObject(shape)
    strip_body.BaseFeature = shape
    shape.Visibility = False

    # Frame on the base: the corner of the base, where the part is placed.
    frame(doc, "IF_base", x="0", y="0", z="0", container=container)


main(build, globals(), cad_dir=_HERE)
