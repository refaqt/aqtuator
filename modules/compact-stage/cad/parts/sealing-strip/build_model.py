"""Rebuild the seal strip in its preloaded state, in the GUI or headless.

The strip is drawn as it lies in the assembly: flat in its pocket in the base,
bent over the four rollers of the carriage with the carriage in the middle of
its travel, and bent down over the ramp at each base end, where the printed
end clamp holds it. The shape over the rollers comes from the strip model of
the seal strip designer page, run in `simulation/cases/strip-seal-fit/`.

The scaffolding lives in `doqs/scripts/cad_build.py`. Run headless with:

    FreeCADCmd cad/parts/sealing-strip/build_model.py

See `doqs/docs/agent-cad.md` for why the interactive path never saves.
"""

import csv
import math
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

#: Module parameters the strip reads, besides every `strip_*` one. The base and the end
#: clamp read the same rows, so the three parts always fit.
SHARED = ("base_l", "base_w", "base_h", "preload_screw_x", "ramp_r", "ramp_x",
          "clamp_end_gap", "clamp_screw_inset", "clamp_screw_y0", "clamp_boss_d", "boss_gap")

# EN 1.4310, Alleima 11R51, the same as the strip model of the seal strip designer page.
E_STRIP = 185000.0      # MPa
# Roller 1 of the carriage in the middle of its travel (carriage centre x = 220).
ROLLER1_X = 118.77 + (220.0 - 211.603)


class Geometry:
    """Every size of the strip, from the parameter values.

    Ends: the strip centre line follows the ramp of the base (radius ramp_r + strip_t / 2)
    from where the ramp meets the pocket floor (ramp_x from the base end) down to the strip
    end, strip_end_gap from the base end. `side` 0 is the low-x end of the base, 1 the other.
    """

    def __init__(self, v):
        f = lambda k: float(v[k])  # noqa: E731
        self.L, self.W, self.H, self.t = f("base_l"), f("base_w"), f("base_h"), f("strip_t")
        self.floor = self.H - self.t
        self.rx, self.R = f("ramp_x"), f("ramp_r")
        self.Rc = self.R + self.t / 2          # centre line on the ramp
        self.zc = self.floor - self.R          # z of the ramp centres
        self.x_end = f("strip_end_gap")
        gap = f("strip_edge_gap")
        self.y0 = (self.W - f("strip_pocket_w")) / 2 + gap
        self.y1 = (self.W + f("strip_pocket_w")) / 2 - gap
        self.ps = f("preload_screw_x")
        self.y_mid = self.W / 2
        self.d_preload = f("strip_preload_hole_d")
        self.d_relief = f("strip_preload_relief_d")
        self.relief_x = f("strip_preload_relief_x")
        self.sx = f("clamp_end_gap") + f("clamp_screw_inset")
        pitch = (self.W - 2 * f("clamp_screw_y0")) / 5
        self.boss_y = [f("clamp_screw_y0") + k * pitch for k in range(6)]
        self.rb = f("clamp_boss_d") / 2 + f("boss_gap")
        self.slide = f("strip_boss_slide")
        self.pull = f("strip_pull")

    def phi(self, x, r=None):
        """Angle on the ramp of the start end for a point at plan x on a circle of radius r."""
        return math.asin((self.rx - x) / (r or self.Rc))

    def ramp_point(self, phi, r, side, y=0.0):
        from FreeCAD import Vector as V
        sx = -1 if side == 0 else 1
        cx = self.rx if side == 0 else self.L - self.rx
        return V(cx + sx * r * math.sin(phi), y, self.zc + r * math.cos(phi))

    def slot_boss_in(self):
        """Plan x of the inner end of each slot round a clamp boss, at the start end."""
        return self.sx + self.slide + self.rb

    def preload_phi(self):
        """Angle of the centre of the small circle of the preload hole: on the screw axis.
        The cone of the screw touches the outer side of this circle."""
        return self.phi(self.ps)

    def relief_phi(self):
        """Angle of the centre of the large circle of the preload hole: `relief_x` (seen from
        above) from the screw axis, towards the strip middle. It frees the strip where the
        rising ramp would meet the screw head."""
        return self.phi(self.ps + self.relief_x)

    def cut_d(self, d, phi):
        """Diameter of a circle cut square to the strip at angle phi, so that seen from above
        it is d long along X (the strip slopes there)."""
        return d / math.cos(phi)


def read_profile(t, floor):
    """The centre line in assembly axes. The model lets the strip sink up to 0.03 mm into its
    elastic magnet bed next to rollers 1 and 4. The pocket floor is rigid, so the line stops
    there."""
    with open(PROFILE, newline="") as f:
        rows = list(csv.DictReader(f))
    z_min = floor + t / 2
    return [(ROLLER1_X + float(r["x_from_roller1_mm"]), max(z_min, float(r["z_centre_mm"])))
            for r in rows]


def _band_points(profile, t, y):
    """Top and bottom points of the part over the rollers: the centre line offset by t/2."""
    from FreeCAD import Vector as V

    pts = profile[::5] + ([profile[-1]] if (len(profile) - 1) % 5 else [])
    top, bot = [], []
    for i, (x, z) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n, dx / n
        top.append(V(x + nx * t / 2, y, z + nz * t / 2))
        bot.append(V(x - nx * t / 2, y, z - nz * t / 2))
    # The ends are flat, so they meet the flat strip in a straight joint.
    for p, (x, z) in ((top[0], pts[0]), (bot[0], pts[0]), (top[-1], pts[-1]), (bot[-1], pts[-1])):
        p.x = x
    return top, bot


def strip_shape(g, profile):
    """The strip as it lies in the assembly: one side profile, swept across the width,
    with the slots round the clamp bosses and the preload slots."""
    import Part
    from FreeCAD import Vector as V

    y = g.y0
    top, bot = _band_points(profile, g.t, y)
    top[0].z = top[-1].z = g.H
    bot[0].z = bot[-1].z = g.floor
    phi_e = g.phi(g.x_end)
    r_bot, r_top = g.R, g.R + g.t

    def arc(side, r, a0, a1):
        return Part.Arc(g.ramp_point(a0, r, side, y), g.ramp_point((a0 + a1) / 2, r, side, y),
                        g.ramp_point(a1, r, side, y)).toShape()

    def seg(a, b):
        return Part.LineSegment(a, b).toShape()

    def spline(points):
        c = Part.BSplineCurve()
        c.approximate(Points=points, DegMin=3, DegMax=3, Tolerance=1e-4)
        return c.toShape()

    p_s_top, p_s_bot = V(g.rx, y, g.H), V(g.rx, y, g.floor)
    p_e_top, p_e_bot = V(g.L - g.rx, y, g.H), V(g.L - g.rx, y, g.floor)
    edges = [
        seg(g.ramp_point(phi_e, r_bot, 0, y), g.ramp_point(phi_e, r_top, 0, y)),
        arc(0, r_top, phi_e, 0.0),
        seg(p_s_top, top[0]),
        spline(top),
        seg(top[-1], p_e_top),
        arc(1, r_top, 0.0, phi_e),
        seg(g.ramp_point(phi_e, r_top, 1, y), g.ramp_point(phi_e, r_bot, 1, y)),
        arc(1, r_bot, phi_e, 0.0),
        seg(p_e_bot, bot[-1]),
        spline(bot),
        seg(bot[0], p_s_bot),
        arc(0, r_bot, 0.0, phi_e),
    ]
    face = Part.Face(Part.Wire(Part.__sortEdges__(edges)))
    strip = face.extrude(V(0, g.y1 - g.y0, 0))

    # Slots round the clamp bosses: open at the strip end, with room for the slide while the
    # preload screw pulls the strip. A boss is vertical, so the slots are cut vertically.
    z0, hz = g.zc, g.H + 5 - g.zc
    cuts = []
    for side in (0, 1):
        x_in = g.sx + g.slide
        for yb in g.boss_y:
            if yb + g.rb <= g.y0 or yb - g.rb >= g.y1:
                continue
            if side == 0:
                box = Part.makeBox(x_in + 5, 2 * g.rb, hz, V(-5, yb - g.rb, z0))
                cyl = Part.makeCylinder(g.rb, hz, V(x_in, yb, z0))
            else:
                box = Part.makeBox(x_in + 5, 2 * g.rb, hz, V(g.L - x_in, yb - g.rb, z0))
                cyl = Part.makeCylinder(g.rb, hz, V(g.L - x_in, yb, z0))
            cuts += [box, cyl]
        # Preload hole: a small circle on the screw axis and a large circle further in,
        # each cut square to the strip at its centre.
        for ph, d in ((g.preload_phi(), g.d_preload), (g.relief_phi(), g.d_relief)):
            c = g.ramp_point(ph, g.Rc, side, g.y_mid)
            cc = g.ramp_point(ph, 0.0, side, g.y_mid)
            n = (c - cc)
            n.normalize()
            cuts.append(Part.makeCylinder(g.cut_d(d, ph) / 2, 2, c - n * 1, n))
    result = strip.cut(Part.makeCompound(cuts)).removeSplitter()
    # The overlapping cylinders of a slot can leave a sliver with no volume. Keep the strip.
    return max(result.Solids, key=lambda s: s.Volume)


def length_along(g, profile):
    """A function that gives the length along the centre line of the strip, from the middle
    of the base, for a point at plan x (on the flat part, the rollers or a ramp) or for an
    angle on the ramp of the start end."""
    import bisect

    xs = [x for x, _ in profile]
    s = [0.0]
    for (xa, za), (xb, zb) in zip(profile, profile[1:]):
        s.append(s[-1] + math.hypot(xb - xa, zb - za))

    def along(x):
        # From the start of the ramp at the start end (x = ramp_x).
        if x < g.rx:
            return -g.Rc * g.phi(x)
        if x <= xs[0]:
            return x - g.rx
        if x >= xs[-1]:
            if x > g.L - g.rx:
                return (xs[-1] - g.rx) + s[-1] + (g.L - g.rx - xs[-1]) + g.Rc * g.phi(g.L - x)
            return (xs[0] - g.rx) + s[-1] + x - xs[-1]
        i = bisect.bisect_right(xs, x) - 1
        f = (x - xs[i]) / (xs[i + 1] - xs[i])
        return (xs[0] - g.rx) + s[i] + f * (s[i + 1] - s[i])

    s_mid = along(g.L / 2)
    return lambda x: along(x) - s_mid


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


P = "Params."
E_XL = f"{P}base_l / 2 - {P}strip_flat_l / 2"
E_XR = f"{P}base_l / 2 + {P}strip_flat_l / 2"
E_Y0 = f"({P}base_w - {P}strip_pocket_w) / 2 + {P}strip_edge_gap"
E_WIDTH = f"{P}strip_pocket_w - 2 * {P}strip_edge_gap"


def flat_outline_sketch(doc, flat_body):
    """The outline of the strip as cut: a plain rectangle. Every size is an expression on the
    parameter sheet. The length comes from `strip_flat_l`, the width from the strip pocket."""
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    val = _sheet_value(sheet(doc))
    x_l = val("base_l") / 2 - val("strip_flat_l") / 2
    x_r = x_l + val("strip_flat_l")
    y0 = (val("base_w") - val("strip_pocket_w")) / 2 + val("strip_edge_gap")
    y1 = y0 + val("strip_pocket_w") - 2 * val("strip_edge_gap")

    sk = flat_body.newObject("Sketcher::SketchObject", "FlatOutline")
    sk.AttachmentSupport = [(_xy_plane(flat_body), "")]
    sk.MapMode = "FlatFace"
    C = Sketcher.Constraint
    pts = [V(x_l, y0, 0), V(x_r, y0, 0), V(x_r, y1, 0), V(x_l, y1, 0)]
    g = [sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4])) for i in range(4)]
    for i in range(4):
        sk.addConstraint(C("Coincident", g[i], 2, g[(i + 1) % 4], 1))
    sk.addConstraint(C("Horizontal", g[0]))
    sk.addConstraint(C("Horizontal", g[2]))
    sk.addConstraint(C("Vertical", g[1]))
    sk.addConstraint(C("Vertical", g[3]))
    dim(sk, C("DistanceX", -1, 1, g[0], 1, x_l), E_XL, "flat_end_left")
    dim(sk, C("DistanceX", -1, 1, g[0], 2, x_r), E_XR, "flat_end_right")
    dim(sk, C("DistanceY", -1, 1, g[0], 1, y0), E_Y0)
    dim(sk, C("DistanceY", g[1], 1, g[1], 2, y1 - y0), E_WIDTH)
    return sk


def flat_holes_sketch(doc, flat_body):
    """The slots round the clamp bosses and the two preload slots of the strip as cut.

    Each slot is a stadium: its outer arc is centred on the strip end, so the slot is open
    there; its inner arc centre is `strip_flat_slot_x` from the strip end.
    """
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    val = _sheet_value(sheet(doc))
    x_l = val("base_l") / 2 - val("strip_flat_l") / 2
    x_r = x_l + val("strip_flat_l")
    r = val("clamp_boss_d") / 2 + val("boss_gap")
    y_lo = (val("base_w") - val("strip_pocket_w")) / 2 + val("strip_edge_gap")
    y_hi = y_lo + val("strip_pocket_w") - 2 * val("strip_edge_gap")
    pitch = (val("base_w") - 2 * val("clamp_screw_y0")) / 5
    e_pitch = f"({P}base_w - 2 * {P}clamp_screw_y0) / 5"
    e_r = f"{P}clamp_boss_d / 2 + {P}boss_gap"

    sk = flat_body.newObject("Sketcher::SketchObject", "FlatHolesSketch")
    sk.AttachmentSupport = [(_xy_plane(flat_body), "")]
    sk.MapMode = "FlatFace"
    C = Sketcher.Constraint

    for xe, sx, e_xe, sign in ((x_l, 1, E_XL, "+"), (x_r, -1, E_XR, "-")):
        x_in = xe + sx * val("strip_flat_slot_x")
        for k in range(6):
            y = val("clamp_screw_y0") + k * pitch
            if y + r <= y_lo or y - r >= y_hi:
                continue          # this boss is outside the strip
            a_out = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(xe, y, 0), V(0, 0, 1), r),
                                                    math.pi / 2 if sx > 0 else -math.pi / 2,
                                                    3 * math.pi / 2 if sx > 0 else math.pi / 2))
            a_in = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(x_in, y, 0), V(0, 0, 1), r),
                                                   -math.pi / 2 if sx > 0 else math.pi / 2,
                                                   math.pi / 2 if sx > 0 else 3 * math.pi / 2))
            lo, hi = (a_out, a_in) if sx > 0 else (a_in, a_out)
            top = sk.addGeometry(Part.LineSegment(V(max(xe, x_in), y + r, 0), V(min(xe, x_in), y + r, 0)))
            bot = sk.addGeometry(Part.LineSegment(V(min(xe, x_in), y - r, 0), V(max(xe, x_in), y - r, 0)))
            for a, pa, b, pb in ((hi, 2, top, 1), (top, 2, lo, 1), (lo, 2, bot, 1), (bot, 2, hi, 1)):
                sk.addConstraint(C("Tangent", a, pa, b, pb))
            sk.addConstraint(C("Horizontal", top))
            dim(sk, C("Radius", a_out, r), e_r)
            dim(sk, C("Radius", a_in, r), e_r)
            dim(sk, C("DistanceX", -1, 1, a_out, 3, xe), e_xe)
            dim(sk, C("DistanceY", -1, 1, a_out, 3, y),
                f"{P}clamp_screw_y0 + {k} * {e_pitch}" if k else f"{P}clamp_screw_y0")
            dim(sk, C("DistanceX", -1, 1, a_in, 3, x_in), f"{e_xe} {sign} {P}strip_flat_slot_x")
        # Preload hole: the outer part of a small circle (centre `strip_flat_preload_x` from
        # the strip end) joined to a large circle (centre `strip_flat_relief_x` from the end).
        rs = val("strip_flat_preload_d") / 2
        rl = val("strip_flat_relief_d") / 2
        yp = val("base_w") / 2
        xs = xe + sx * val("strip_flat_preload_x")
        xl = xe + sx * val("strip_flat_relief_x")
        d = abs(xl - xs)
        a = (d * d + rs * rs - rl * rl) / (2 * d)       # from the small centre to the chord
        hy = math.sqrt(rs * rs - a * a)
        # Meeting points of the two circles, seen from each centre.
        px = xs + sx * a
        ang_s = math.atan2(hy, px - xs)
        ang_l = math.atan2(hy, px - xl)
        if sx > 0:   # small circle on the outer (low x) side: its arc runs over the left
            small = Part.ArcOfCircle(Part.Circle(V(xs, yp, 0), V(0, 0, 1), rs), ang_s, 2 * math.pi - ang_s)
            large = Part.ArcOfCircle(Part.Circle(V(xl, yp, 0), V(0, 0, 1), rl), -ang_l, ang_l)
        else:
            small = Part.ArcOfCircle(Part.Circle(V(xs, yp, 0), V(0, 0, 1), rs), -ang_s, ang_s)
            large = Part.ArcOfCircle(Part.Circle(V(xl, yp, 0), V(0, 0, 1), rl), ang_l, 2 * math.pi - ang_l)
        g_s = sk.addGeometry(small)
        g_l = sk.addGeometry(large)
        if sx > 0:
            sk.addConstraint(C("Coincident", g_s, 1, g_l, 2))
            sk.addConstraint(C("Coincident", g_s, 2, g_l, 1))
        else:
            sk.addConstraint(C("Coincident", g_s, 2, g_l, 1))
            sk.addConstraint(C("Coincident", g_s, 1, g_l, 2))
        dim(sk, C("Radius", g_s, rs), f"{P}strip_flat_preload_d / 2")
        dim(sk, C("Radius", g_l, rl), f"{P}strip_flat_relief_d / 2")
        dim(sk, C("DistanceX", -1, 1, g_s, 3, xs), f"{e_xe} {sign} {P}strip_flat_preload_x")
        dim(sk, C("DistanceY", -1, 1, g_s, 3, yp), f"{P}base_w / 2")
        dim(sk, C("DistanceX", -1, 1, g_l, 3, xl), f"{e_xe} {sign} {P}strip_flat_relief_x")
        dim(sk, C("DistanceY", -1, 1, g_l, 3, yp), f"{P}base_w / 2")
    return sk


def build(doc, params):
    """The seal strip: 0.15 mm spring steel, preloaded, with the carriage in the middle.

    EN 1.4310 (AISI 301), see docs/decisions/2026-10-28_seal-strip-0-15-mm.md.
    At each base end the strip bends down over the ramp of the base, and the printed end
    clamp presses it there (docs/decisions/2026-11-20_strip-held-by-an-end-clamp.md).
    Before the clamp is tightened, a countersunk screw (ISO 10642 M4) at each end sets the
    pull. The clamp bosses pass through slots that are open at the strip ends.

    The file holds two shapes. `sealing-strip` is the strip as it lies in the
    assembly: bent and pulled. The assembly links only this one.
    `sealing-strip-flat` is the strip as cut from the sheet, a parametric Body:
    it is as long as the centre line of the bent strip, less the stretch of the pull,
    so that its holes land on the screws when it is fitted and pulled. It lies flat at
    z = 0, with its middle at the middle of the base.
    """
    with open(DEFAULTS, newline="") as f:
        rows = [r for r in csv.DictReader(f)
                if r["alias"].startswith("strip_") or r["alias"] in SHARED]
    units = {r["alias"]: r["unit"] for r in rows}
    params = {**{r["alias"]: r["value"] for r in rows}, **params}
    values = {k: (v.Value if hasattr(v, "Value") else v) for k, v in params.items()}

    g = Geometry(values)
    profile = read_profile(g.t, g.floor)
    along = length_along(g, profile)
    eps = g.pull / (E_STRIP * (g.y1 - g.y0) * g.t)
    flat = lambda s: s / (1 + eps)  # noqa: E731 - length on the strip as cut
    s_end = along(g.x_end)
    s_hole = along(g.rx) - g.Rc * g.preload_phi()
    s_relief = along(g.rx) - g.Rc * g.relief_phi()
    # Inner end of a slot: the plan point of the bent slot, then back by the radius.
    s_slot = along(g.slot_boss_in())
    derived = {
        "strip_flat_l": round(-2 * flat(s_end), 4),
        "strip_flat_preload_x": round(flat(s_hole) - flat(s_end), 4),
        "strip_flat_relief_x": round(flat(s_relief) - flat(s_end), 4),
        # The two circles as cut: larger than seen from above by 1 / cos(slope).
        "strip_flat_preload_d": round(g.cut_d(g.d_preload, g.preload_phi()), 4),
        "strip_flat_relief_d": round(g.cut_d(g.d_relief, g.relief_phi()), 4),
        "strip_flat_slot_x": round(flat(s_slot) - flat(s_end) - g.rb, 4),
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
    p.recompute()
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
    shape.Shape = strip_shape(g, profile)
    container.addObject(shape)
    strip_body.BaseFeature = shape
    shape.Visibility = False

    # Frame on the base: the corner of the base, where the part is placed.
    frame(doc, "IF_base", x="0", y="0", z="0", container=container)


main(build, globals(), cad_dir=_HERE)
