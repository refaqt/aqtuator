"""Brass and TPU scraper at the start end of carriage-top (sketch of Niels Bosmans, 2026-11-10).
Assembly coordinates, mm: x along the travel, y across, z up. Sizes are given from the carriage
end face (xr = x - X0), because the whole scraper moves with the carriage.

Parts:
- a brass block at the end face, with a rib along its front edge that stays 0.15 mm above the strip.
  Near each side the rib turns 45 degrees inward, so the corner screw head of the strip can enter
  the corner at the end of the travel without touching it;
- two MISUMI spring plungers (M4, from the top) push the brass down, and two M2.5 pull screws
  (from the top, threaded into the brass) hold it up. Together they set its height;
- four horizontal M3 bolts go through vertical slots in the brass and through the TPU into
  carriage-top. Tightened, they lock the brass;
- a printed TPU wiper behind the brass, with two thin lips that lean apart and press on the strip.

The other end of carriage-top carries the same parts, turned 180 degrees."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper-fit'))
from scraper import box, cyl, cut, fuse, common, vol, dist  # noqa: E402  (unzips the CAD files)
from fcstd_shapes import *  # noqa: E402,F401
from OCP.gp import gp_Ax2, gp_Vec, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity
import zipfile, math
from shapely.geometry import Point

# ---------------------------------------------------------------- the CAD as it is
TOP = placed('carriage-top', 'carriage_top')
BOT = placed('carriage-bottom', 'carriage_bottom001')
BASE = placed('base', 'base')
X0 = bbox(TOP)[0]                  # carriage end face, start end (104.58 mm in the assembly)
zipfile.ZipFile(os.path.join(MODULE, 'cad/parts/sealing-strip/sealing-strip.FCStd')).extractall('strip')
STRIP = shape('strip', 'StripShape')        # preloaded strip, carriage in the middle
CORNER_SCREW = TopoDS_Shape()
BRepTools.Read_s(CORNER_SCREW, 'asm/corner_screw_a_start.Shape.brp', BRep_Builder())  # ISO 7380-2 M4, y = 8

Z_STRIP = 40.0            # strip top: level with the base top (strip pocket 0.15 mm deep)
Z_UNDER = 40.5            # underside of carriage-top
Y_SIDE = (1.0, 209.0)     # side faces of carriage-top
STRIP_Y = (12.2, 197.8)   # strip body under the carriage (185.6 mm wide)

# Top rollers: Ø10 x 20 mm, axis 12.17 mm behind the end face, resting on the strip.
ROLLER_XR, ROLLER_Z, ROLLER_R, ROLLER_L = 116.75 - 104.582, 45.0, 5.0, 20.0
ROLLER_Y = [34.5, 175.5]

# Corner screw head, ISO 7380-2 M4 with collar: Ø10.17 mm (CAD), top 2.2 mm above the strip.
HEAD_X, HEAD_Y, HEAD_R, HEAD_TOP = 6.0, 8.0, 10.174 / 2, 42.2
CLEAR = 0.5               # room kept around the head
# Carriage end face from the base end (x = 0), from the log of the damper pockets
CARRIAGE_END_X = {'usable travel end': 5.0, 'first damper touch': 4.0, 'dampers fully pressed': -3.0}
DESIGN_CASE = 'first damper touch'

# ---------------------------------------------------------------- sizes (xr from the end face)
CUTTER_R = 2.0            # end mill radius for the pocket corners (no sharp inside corners)
Z_CEIL = 50.0             # pocket ceiling: 9.5 mm deep. Keeps 1.7 mm under the M5 drill points at y 25 and 185
BRIDGE_Y = (98.5, 111.5)  # around the middle M5 hole (13 mm drill): the ceiling stays at z 45 there
Z_CEIL_BRIDGE = 45.0
POCKET_L = 10.0           # pocket length in the middle
NOTCHES = [(15.0, 54.0), (156.0, 195.0)]   # in front of the top rollers and their axle slots
NOTCH_L = 6.6             # pocket length there (the roller pocket starts at 6.67 mm)
ROLLER_POCKET_Y = [(21.5, 47.5), (162.5, 188.5)]   # there the pocket runs into the roller pocket: no thin wall
WING_BACK = 22.3          # corner wing of the pocket: xr + y <= 22.3 (and mirrored)
WING_XMAX = 18.7

# brass
PLAY = 0.2                                 # room to the pocket walls
BR_L, BR_L_NOTCH = 6.0, 3.0                # brass length in the middle and in front of the rollers
Z_BR_TOP, Z_BR_TOP_BRIDGE = 49.0, 44.0     # 1 mm under the ceiling: room to adjust up
GAP = 0.15                                 # rib tip above the strip
Z_RIB = Z_STRIP + GAP
RIB_W = 1.0
Z_BR_UNDER = 41.0                          # underside behind the rib
BR_REBATE_X, BR_REBATE_X_NOTCH = 4.3, 1.5  # behind this the underside steps up, over the front lip
Z_BR_REBATE = 43.0
RIB_DIAG = 17.9           # front face of the angled rib: xr + y = 17.9. Tangent behind the head at the design case
Z_RELIEF = 43.0           # brass underside in front of the angled rib: 0.8 mm over the head top
BR_WING_BACK = 22.0       # brass corner wing: xr + y <= 22, xr <= 18.5, y <= 12.2
BR_WING_XMAX, BR_WING_Y = 18.5, 12.2

# TPU
TPU_X = (BR_L, POCKET_L - PLAY)            # 6.0 .. 9.8 in the middle
TPU_X_NOTCH = (BR_L_NOTCH, NOTCH_L - PLAY)  # 3.0 .. 6.4 in front of the rollers
TPU_Y = (12.5, 197.5)                      # ends just inside the strip edge, clear of the head path
Z_TPU_BODY = 43.0                          # lip roots
INTERF = 0.4                               # free lip tip below the strip top
Z_LIP_TIP = Z_STRIP - INTERF               # 39.6
LIP_T = 0.7                                # lip thickness (Raise3D: TPU wall at least 0.6 mm)
LIP_LEAN = 20.0                            # degrees from vertical; the two lips lean apart
LIPS = [(6.2, -1), (7.85, +1)]             # (front edge of the root, lean direction) in the middle
LIPS_NOTCH = [(3.1, -1), (4.45, +1)]       # in front of the rollers; the rear tip stays inside the TPU length

# Height adjustment, from the top of carriage-top
PLUNGER_Y = [70.0, 140.0]                  # MISUMI spring plunger, M4 (part to be chosen, see the log)
PLUNGER_XR, PLUNGER_D, PLUNGER_L, PIN_D = 3.0, 4.0, 10.0, 2.0
PULL_Y = [80.0, 130.0]                     # ISO 4762 M2.5 x 12 pull screws
PULL_XR, PULL_HEAD_D, PULL_HEAD_K, PULL_CB_D, PULL_CB_DEPTH = 3.25, 4.5, 2.5, 5.0, 2.7
PULL_L = 12.0
PULL_TAP_DEPTH = 5.5                       # M2.5 tapped hole in the brass, from its top
# Locking bolts, horizontal
BOLT_Y = [60.0, 92.0, 118.0, 150.0]        # ISO 4762 M3 x 16
BOLT_Z, BOLT_L, BOLT_HEAD_D, BOLT_HEAD_K = 45.8, 16.0, 5.5, 3.0
SLOT_W, SLOT_PLAY = 3.4, 0.5               # vertical slot in the brass: ±0.5 mm of height adjustment
TAP_D, TAP_DEPTH = 2.5, 8.0                # M3 tapped hole in carriage-top behind the pocket

BRASS_DENSITY = 8.5                        # g/cm³, a typical value for brass, not from a data sheet


# ---------------------------------------------------------------- helpers
def X(xr):
    return X0 + xr


def mirror_y(poly):
    return affinity.scale(poly, xfact=1, yfact=-1, origin=(0, 105.0))


def both_sides(poly):
    return unary_union([poly, mirror_y(poly)])


def prism(poly, z0, z1):
    """Shapely plan (xr, y) -> solid between z0 and z1. Holes are not used."""
    out = None
    for p in getattr(poly, 'geoms', [poly]):
        if p.is_empty or p.area < 1e-6:
            continue
        w = BRepBuilderAPI_MakePolygon()
        for x, y in list(p.exterior.coords)[:-1]:
            w.Add(gp_Pnt(X(x), y, z0))
        w.Close()
        f = BRepBuilderAPI_MakeFace(w.Wire()).Face()
        s = BRepPrimAPI_MakePrism(f, gp_Vec(0, 0, z1 - z0)).Shape()
        out = s if out is None else fuse(out, s)
    return out


def prism_xz(pts, y0, y1):
    """Section (xr, z) -> solid between y0 and y1."""
    w = BRepBuilderAPI_MakePolygon()
    for x, z in pts:
        w.Add(gp_Pnt(X(x), y0, z))
    w.Close()
    f = BRepBuilderAPI_MakeFace(w.Wire()).Face()
    return BRepPrimAPI_MakePrism(f, gp_Vec(0, y1 - y0, 0)).Shape()


def cyl_x(xr0, y, z, r, length):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(X(xr0), y, z), gp_Dir(1, 0, 0)), r, length).Shape()


def cyl_y(x, y0, z, r, length):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), r, length).Shape()


def shift_x(s, dx):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, 0, 0))
    return BRepBuilderAPI_Transform(s, t, True).Shape()


def in_notch(y):
    return any(a <= y <= b for a, b in NOTCHES)


# ---------------------------------------------------------------- plans (xr, y)
def pocket_plan():
    main = sbox(-2, Y_SIDE[0] - 2, POCKET_L, Y_SIDE[1] + 2)
    wing = Polygon([(-2, Y_SIDE[0] - 2), (WING_XMAX, Y_SIDE[0] - 2), (WING_XMAX, WING_BACK - WING_XMAX),
                    (WING_BACK - 13.0, 13.0), (-2, 13.0)])
    p = unary_union([main, both_sides(wing)])
    for a, b in NOTCHES:
        p = p.difference(sbox(NOTCH_L, a, 30, b))
    for a, b in ROLLER_POCKET_Y:
        p = p.union(sbox(NOTCH_L - 1, a, 8.5, b))
    return p.buffer(-CUTTER_R, join_style=1).buffer(CUTTER_R, join_style=1)   # what the cutter can reach


def bridge_plan():
    return sbox(-2, BRIDGE_Y[0], POCKET_L + 1, BRIDGE_Y[1]).buffer(CUTTER_R, join_style=1).intersection(
        sbox(-2, 0, POCKET_L + 1, 210))


def brass_plan():
    main = sbox(0, Y_SIDE[0], BR_L, Y_SIDE[1])
    wing = Polygon([(BR_L, Y_SIDE[0]), (BR_WING_XMAX, Y_SIDE[0]), (BR_WING_XMAX, BR_WING_BACK - BR_WING_XMAX),
                    (BR_WING_BACK - BR_WING_Y, BR_WING_Y), (BR_L, BR_WING_Y)])
    p = unary_union([main, both_sides(wing)])
    for a, b in NOTCHES:
        p = p.difference(sbox(BR_L_NOTCH, a, BR_L + 1, b))
    return p


def relief_plan():
    """In front of the angled rib: the brass underside is raised over the screw head."""
    tri = Polygon([(-1, -1), (RIB_DIAG + 1, -1), (-1, RIB_DIAG + 1)])
    return both_sides(tri)


def rib_plan():
    front = sbox(0, 0, RIB_W, 210)
    diag = Polygon([(-1, -1), (RIB_DIAG + 1.414 * RIB_W + 1, -1), (-1, RIB_DIAG + 1.414 * RIB_W + 1)])
    rib = unary_union([front, both_sides(diag)]).difference(relief_plan())
    return rib.intersection(brass_plan())


def rebate_plan():
    r = sbox(BR_REBATE_X, 0, BR_L + 1, 210)
    for a, b in NOTCHES:
        r = r.difference(sbox(BR_REBATE_X, a, BR_L + 1, b)).union(sbox(BR_REBATE_X_NOTCH, a, BR_L + 1, b))
    return r.difference(sbox(-1, 0, 30, BR_WING_Y)).difference(sbox(-1, 210 - BR_WING_Y, 30, 210))


def tpu_plan():
    p = sbox(TPU_X[0], TPU_Y[0], TPU_X[1], TPU_Y[1])
    for a, b in NOTCHES:
        p = p.difference(sbox(TPU_X[0] - 1, a, TPU_X[1] + 1, b)).union(sbox(TPU_X_NOTCH[0], a, TPU_X_NOTCH[1], b))
    return p


# ---------------------------------------------------------------- swept head (carriage frame)
def head_swept_plan(case):
    """Plan of everything the corner screw head passes under, in the carriage frame (xr, y), plus
    CLEAR. The carriage comes from the stage middle, so the head enters from the end face."""
    xr_c = HEAD_X - CARRIAGE_END_X[case]
    r = HEAD_R + CLEAR
    stadium = unary_union([sbox(-40, HEAD_Y - r, xr_c, HEAD_Y + r), Point(xr_c, HEAD_Y).buffer(r, 64)])
    return both_sides(stadium)


def head_swept(case):
    return prism(head_swept_plan(case), Z_STRIP - 0.5, HEAD_TOP + CLEAR)


def head_at(case):
    """The real screw shapes (both sides) moved into the carriage frame at that carriage position."""
    dx = X0 - CARRIAGE_END_X[case]
    a = shift_x(CORNER_SCREW, dx)
    t = gp_Trsf(); t.SetMirror(gp_Ax2(gp_Pnt(0, 105, 0), gp_Dir(0, 1, 0)))
    b = BRepBuilderAPI_Transform(a, t, True).Shape()
    return fuse(a, b)


# ---------------------------------------------------------------- solids
def pocket_cut():
    p = prism(pocket_plan(), Z_UNDER - 1.0, Z_CEIL_BRIDGE)
    p = fuse(p, prism(pocket_plan().difference(bridge_plan()), Z_CEIL_BRIDGE - 0.01, Z_CEIL))
    for y in PLUNGER_Y:                                          # M4 tapped through hole (Ø3.3 drill)
        p = fuse(p, cyl(X(PLUNGER_XR), y, Z_CEIL - 0.1, 3.3 / 2, 60.5 - Z_CEIL))
    for y in PULL_Y:                                             # Ø2.9 clearance and Ø5 counterbore
        p = fuse(p, cyl(X(PULL_XR), y, Z_CEIL - 0.1, 2.9 / 2, 60.5 - Z_CEIL))
        p = fuse(p, cyl(X(PULL_XR), y, 60.0 - PULL_CB_DEPTH, PULL_CB_D / 2, PULL_CB_DEPTH + 0.5))
    for y in BOLT_Y:                                             # M3 tapped hole behind the pocket
        p = fuse(p, cyl_x(POCKET_L - 0.1, y, BOLT_Z, TAP_D / 2, TAP_DEPTH + 0.1))
    return p


def carriage_top_new():
    return cut(TOP, pocket_cut())


def tpu_section(lips, x0, x1, z_top):
    """Section (xr, z) of the TPU: body from Z_TPU_BODY to z_top, and two leaning lips."""
    k = math.tan(math.radians(LIP_LEAN))
    body = [(x0, Z_TPU_BODY), (x1, Z_TPU_BODY), (x1, z_top), (x0, z_top)]
    lip_pts = []
    for xa, d in lips:
        h = Z_TPU_BODY + 0.01 - Z_LIP_TIP
        lip_pts.append([(xa, Z_TPU_BODY + 0.01), (xa + LIP_T, Z_TPU_BODY + 0.01),
                        (xa + LIP_T + d * k * h, Z_LIP_TIP), (xa + d * k * h, Z_LIP_TIP)])
    return body, lip_pts


def tpu():
    """Built in y bands: middle, notch (rollers) and bridge, each with its own section."""
    bands = []
    cuts = sorted({TPU_Y[0], TPU_Y[1], BRIDGE_Y[0], BRIDGE_Y[1]} | {v for ab in NOTCHES for v in ab})
    cuts = [c for c in cuts if TPU_Y[0] <= c <= TPU_Y[1]]
    s = None
    for y0, y1 in zip(cuts[:-1], cuts[1:]):
        ym = (y0 + y1) / 2
        if in_notch(ym):
            x0, x1, lips = TPU_X_NOTCH[0], TPU_X_NOTCH[1], LIPS_NOTCH
        else:
            x0, x1, lips = TPU_X[0], TPU_X[1], LIPS
        z_top = Z_CEIL_BRIDGE if BRIDGE_Y[0] < ym < BRIDGE_Y[1] else Z_CEIL
        body, lps = tpu_section(lips, x0, x1, z_top)
        part = prism_xz(body, y0, y1)
        for lp in lps:
            part = fuse(part, prism_xz(lp, y0, y1))
        s = part if s is None else fuse(s, part)
        bands.append((y0, y1))
    # keep PLAY to the milled pocket walls and corners, and to the bridge over the middle M5 hole
    s = common(s, prism(pocket_plan().buffer(-PLAY, join_style=1), Z_LIP_TIP - 1, Z_CEIL + 1))
    s = cut(s, prism(bridge_plan().buffer(PLAY), Z_CEIL_BRIDGE, Z_CEIL + 1))
    # the front lip stops where the angled rib of the brass crosses it, near each side
    s = cut(s, prism(rib_plan().buffer(PLAY), Z_LIP_TIP - 1, Z_BR_UNDER + PLAY))
    # and the lips stay clear of the corner screw head path
    s = cut(s, prism(head_swept_plan(DESIGN_CASE), Z_LIP_TIP - 1, HEAD_TOP + CLEAR))
    for y in BOLT_Y:
        s = cut(s, cyl_x(-1, y, BOLT_Z, SLOT_W / 2, 20))
    return s


def tpu_body_only():
    """The TPU without its lips: this must not touch the strip."""
    return cut(tpu(), box(X0 - 5, 0, 30, X0 + 30, 210, Z_TPU_BODY - 0.001))


def brass():
    plan = brass_plan()
    s = prism(plan, Z_BR_UNDER, Z_BR_TOP)
    s = cut(s, prism(bridge_plan(), Z_BR_TOP_BRIDGE, Z_BR_TOP + 1))
    s = cut(s, prism(rebate_plan(), Z_BR_UNDER - 1, Z_BR_REBATE))
    s = cut(s, prism(relief_plan(), Z_BR_UNDER - 1, Z_RELIEF))
    s = fuse(s, prism(rib_plan(), Z_RIB, Z_BR_UNDER + 0.01))
    for y in BOLT_Y:   # vertical slot: Ø3.4 wide, 1 mm longer in z
        sl = fuse(cyl_x(-1, y, BOLT_Z - SLOT_PLAY, SLOT_W / 2, 30), cyl_x(-1, y, BOLT_Z + SLOT_PLAY, SLOT_W / 2, 30))
        sl = fuse(sl, box(X(-1), y - SLOT_W / 2, BOLT_Z - SLOT_PLAY, X(29), y + SLOT_W / 2, BOLT_Z + SLOT_PLAY))
        s = cut(s, sl)
    for y in PULL_Y:   # M2.5 tapped hole (Ø2.05 drill)
        s = cut(s, cyl(X(PULL_XR), y, Z_BR_TOP - PULL_TAP_DEPTH, 2.05 / 2, PULL_TAP_DEPTH + 1))
    return s


def bolts():
    """ISO 4762 M3 x 16, head on the brass front face. Shank drawn at the tap drill size (2.5 mm),
    so that it does not overlap the tapped hole in the checks."""
    out = []
    for y in BOLT_Y:
        h = cyl_x(-BOLT_HEAD_K, y, BOLT_Z, BOLT_HEAD_D / 2, BOLT_HEAD_K)
        out.append(fuse(h, cyl_x(0, y, BOLT_Z, TAP_D / 2 - 0.01, BOLT_L)))
    return out


def plungers():
    """Spring plunger, M4 body 10 mm (length to be checked in the MISUMI configurator), pin on the brass."""
    out = []
    for y in PLUNGER_Y:
        b = cyl(X(PLUNGER_XR), y, Z_CEIL, 3.3 / 2 - 0.01, PLUNGER_L)
        out.append(fuse(b, cyl(X(PLUNGER_XR), y, Z_BR_TOP, PIN_D / 2, Z_CEIL - Z_BR_TOP + 0.01)))
    return out


def pull_screws():
    out = []
    for y in PULL_Y:
        h = cyl(X(PULL_XR), y, 60.0 - PULL_CB_DEPTH, PULL_HEAD_D / 2, PULL_HEAD_K)
        out.append(fuse(h, cyl(X(PULL_XR), y, 60.0 - PULL_CB_DEPTH - PULL_L, 2.05 / 2 - 0.01, PULL_L)))
    return out


def rollers():
    return [cyl_y(X(ROLLER_XR), y - ROLLER_L / 2, ROLLER_Z, ROLLER_R, ROLLER_L) for y in ROLLER_Y]
