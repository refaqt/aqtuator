"""The strip end concept of Niels Bosmans (2026-10-28), at the end x = 0 of the base, side y = 0.
Assembly coordinates, mm: x along the travel (base end face at x = 0), y across, z up.
The other side (y = 210) and the other end (x = 440) are mirror images.

Each strip end has two inserts, one near each side edge. An insert sits in a hole in the strip,
with no thread and no nut. A countersunk screw presses it into the hole. Two flat faces on the
insert slide in a small groove in the base, so it cannot turn. The screw hole in the base sits a
little nearer the base end than the insert when the strip is laid loose, so tightening the screw
centres the insert on it and pulls the strip. Magnets in pockets hold the strip down.

Positions are measured on his drawing (3.44 pixels per mm, from the 74.1 mm pitch of the
carriage-top screws) and rounded. The insert is made a little smaller (Ø6 instead of Ø7.5, with an
M2 screw) and moved 4.7 mm towards the base side (y = 13.2 to 8.5), over the ear of the strip:
the scraper lip behind it then runs over the flat ear only. Further in (y = 12 mm and up), from
about 10 mm behind the carriage end face, the strip rises towards the carriage slope, and a lip
there would touch it. The insert also moves 0.4 mm away from the base end (x = 11.6 to 12.0), so
the slider of the spring end has room for a hold-down screw in front of it.

Spring end: at one strip end the two inserts sit on sliders, each pushed towards the base end by a
compression spring in a pocket milled from the top into the side wall. The spring then sets the
pull, not the hole positions."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper-fit'))
from scraper import *  # noqa: E402  (unzips the CAD files, gives box, cyl, cone, cut, ...)
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace

T = 0.15                     # strip thickness, decision of 2026-10-28
Z_WALL = 40.0                # top of the base
Z_STRIP = Z_WALL + T
# Insert, steel: Ø6, over the ear of the strip, above the side wall
XC, YC = 12.0, 8.5          # insert axis when the pull is set (drawing: x = 11.6, y = 13.2)
INS_D, FLATS = 6.0, 5.0      # diameter, and width across the two flat faces (parallel to the travel)
INS_H = 1.4                  # height: the M2 countersink (1.2 mm) plus 0.2 mm under it
TRAVEL = 0.25                # how far the screw pulls the insert towards the base end
# ISO 14581 M2 x 5, Torx countersunk: dk 3.8, k 1.2, 90 degrees
DK, K, D_SCREW, SCREW_L = 3.8, 1.2, 2.0, 5.0
BORE_D = D_SCREW + 2 * TRAVEL + 0.2    # lets the shank through while the insert is still off centre
TAP_DEPTH = 5.0                        # M2 tapped hole, drilled straight down into the side wall
# Groove for the flat faces, milled from the top with a 6 mm end mill
GROOVE_W = FLATS + 0.1
GROOVE_D = 0.5                         # the insert stands 0.75 mm above the strip, as drawn
# Strip outline at this corner, from the drawing: end at x = 1.5, an ear out to y = 6.5
STRIP_END_X, STRIP_Y0, EAR_Y, EAR_X1, EAR_X2 = 1.5, 12.0, 4.0, 16.0, 21.5
EAR_X1_SPRING = 35.4                   # at the spring end the ear covers the spring pocket
HOLE_D = INS_D + 0.1
# Magnets in pockets, from the drawing (Ø6 x 2 assumed, top flush with the base)
MAGNETS = [(5.8, 39.4), (5.8, 81.2)]
MAG_D, MAG_H = 6.0, 2.0
# Carriage-top end face: 5 mm from the base end at the end of the usable travel, 4 mm at the first
# damper touch, 3 mm past the base end with the dampers fully pressed in (log of the damper pockets).
CARRIAGE_END_X = {'usable travel end': 5.0, 'first damper touch': 4.0, 'dampers fully pressed': -3.0}


def shift(s, dx):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, 0, 0))
    return BRepBuilderAPI_Transform(s, t, True).Shape()


def prism(pts, z0, z1):
    poly = BRepBuilderAPI_MakePolygon()
    for x, y in pts:
        poly.Add(gp_Pnt(x, y, z0))
    poly.Close()
    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    return BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, z1 - z0)).Shape()


# Carriage-top: a shallow pocket in the corner, so carriage-top can pass over the insert.
# Length from the end face: 12 mm is enough up to the first damper touch, 19.5 mm for a crash.
CORNER_DEPTH = 1.0                     # underside z 40.5 -> 41.5; insert top 40.9
CORNER_Y = (YC - INS_D / 2 - 0.5, YC + INS_D / 2 + 0.5)
CORNER_L = {'normal': 12.0, 'crash': 19.5}
CLEAR = 0.3
# Spring end (the end at x = 440 in the stage, built here at x = 0 like the other)
SPRING_D_WIRE, SPRING_D_MEAN, SPRING_N = 1.2, 6.3, 6     # stainless spring wire, EN 10270-3 (1.4310)
SPRING_G = 70000.0                     # typical shear modulus of that wire
SPRING_FREE = 20.0                     # free length
SPRING_AXIS_Z = 35.75
SLIDER = (5.6, 19.6)                   # x range when the pull is set; steel, 8.3 mm wide
SLIDER_TOP = Z_WALL - GROOVE_D         # the insert sits on it, at the same height as at the fixed end
HOLD_X = 6.7                           # M2 screw with a Ø3 sleeve holds the slider down, through a slot
PULL_PER_INSERT = 62.5                 # 125 N for the strip, two inserts per end


def spring_rate():
    return SPRING_G * SPRING_D_WIRE ** 4 / (8 * SPRING_D_MEAN ** 3 * SPRING_N)


def spring_seat_x():
    """Pocket end: the spring is compressed so that it pushes PULL_PER_INSERT."""
    return SLIDER[1] + SPRING_FREE - PULL_PER_INSERT / spring_rate()


SP_POCKET_Y = (YC - 4.25, YC + 4.25)
SP_POCKET_X0, SP_POCKET_FLOOR = 4.5, 31.5


def floor_z(variant=None):
    return Z_WALL - GROOVE_D


def groove_cut(variant=None):
    """Groove (a slot with round ends), tapped hole, and the magnet pockets."""
    zf = floor_z(variant)
    r = GROOVE_W / 2
    # the round ends are centred on the corners of the flat faces, so the corners fit
    half = (INS_D ** 2 / 4 - FLATS ** 2 / 4) ** 0.5
    xa, xb = XC - half - 0.05, XC + half + TRAVEL + 0.05
    g = box(xa, YC - r, zf, xb, YC + r, Z_WALL + 1)
    for x in (xa, xb):
        g = fuse(g, cyl(x, YC, zf, r, Z_WALL + 1 - zf))
    g = fuse(g, cyl(XC, YC, zf - TAP_DEPTH, 0.8, TAP_DEPTH + 0.1))
    for x, y in MAGNETS:
        g = fuse(g, cyl(x, y, Z_WALL - MAG_H - 0.2, MAG_D / 2 + 0.1, MAG_H + 1.2))
    return g


def insert(variant=None, dx=0.0, z0=None):
    """The insert when the pull is set (dx = 0), or when the strip is laid loose (dx = TRAVEL)."""
    zf, xc = (floor_z() if z0 is None else z0), XC + dx
    s = cyl(xc, YC, zf, INS_D / 2, INS_H)
    s = common(s, box(xc - 5, YC - FLATS / 2, zf - 1, xc + 5, YC + FLATS / 2, zf + INS_H + 1))
    s = cut(s, cone(xc, YC, zf + INS_H - K, D_SCREW / 2, DK / 2 + 0.05, K + 0.01))
    return cut(s, cyl(xc, YC, zf - 1, BORE_D / 2, INS_H + 2))


def screw(variant=None):
    """The screw when it is tight: its head sits in the countersink of the insert."""
    top = floor_z(variant) + INS_H
    h = cone(XC, YC, top - K, D_SCREW / 2, DK / 2, K)
    return fuse(h, cyl(XC, YC, top - SCREW_L, D_SCREW / 2, SCREW_L - K))


def strip(dx=0.0, spring_end=False):
    x1 = EAR_X1_SPRING if spring_end else EAR_X1
    pts = [(STRIP_END_X, EAR_Y), (x1, EAR_Y), (x1 + EAR_X2 - EAR_X1, STRIP_Y0), (80, STRIP_Y0), (80, 120), (STRIP_END_X, 120)]
    s = prism([(x + dx, y) for x, y in pts], Z_WALL, Z_STRIP)
    return cut(s, cyl(XC + dx, YC, Z_WALL - 1, HOLE_D / 2, 2))


def magnets():
    return [cyl(x, y, Z_WALL - MAG_H, MAG_D / 2, MAG_H) for x, y in MAGNETS]


def roller_cyls(dx):
    return [shift(r, dx) for r in rollers()]


def swept(shape_top_z):
    """Everything carriage-top and the scraper pass over on their way to the end of the travel: the
    insert footprint, drawn out towards the base end (the carriage comes from the stage middle)."""
    return box(-10, YC - INS_D / 2, floor_z(), XC, YC + INS_D / 2, shape_top_z)


def corner_pocket_cut(length):
    """Shallow pocket in carriage-top (placed as in the assembly, end face at X0)."""
    return box(X0 - 1, CORNER_Y[0], Z_TOP_UNDER - 1, X0 + length, CORNER_Y[1], Z_TOP_UNDER + CORNER_DEPTH)


def spring_pocket_cut():
    p = box(SP_POCKET_X0, SP_POCKET_Y[0], SP_POCKET_FLOOR, spring_seat_x(), SP_POCKET_Y[1], Z_WALL + 1)
    return fuse(p, cyl(HOLD_X, YC, SP_POCKET_FLOOR - 5.0, 0.8, 5.1))     # M2 tapped hole


def slider():
    x0, x1 = SLIDER
    y0, y1 = SP_POCKET_Y[0] + 0.1, SP_POCKET_Y[1] - 0.1
    s = box(x0, y0, SP_POCKET_FLOOR + 0.05, x1, y1, SLIDER_TOP)
    s = cut(s, box(HOLD_X - 1.5 - 1.6, YC - 1.6, SP_POCKET_FLOOR, HOLD_X + 1.5 + 1.6, YC + 1.6, SLIDER_TOP + 1))  # slot
    s = cut(s, box(HOLD_X - 1.5 - 2.1, YC - 2.1, SLIDER_TOP - 2.2, HOLD_X + 1.5 + 2.1, YC + 2.1, SLIDER_TOP + 1))  # for the head
    return cut(s, cyl(XC, YC, SLIDER_TOP - 5.0, 0.8, 5.1))         # M2 thread for the insert screw


def hold_down():
    """ISO 4762 M2 with a Ø3 sleeve: the head stops 0.05 mm above the slider, so the slider can slide."""
    head = cyl(HOLD_X, YC, SLIDER_TOP - 2.2 + 0.05, 1.9, 2.0)
    sleeve = cyl(HOLD_X, YC, SP_POCKET_FLOOR, 1.5, SLIDER_TOP - 2.2 + 0.05 - SP_POCKET_FLOOR)
    return fuse(head, fuse(sleeve, cyl(HOLD_X, YC, SP_POCKET_FLOOR - 4.0, 1.0, 4.0)))


def spring():
    x0, x1 = SLIDER[1], spring_seat_x()
    r_o, r_i = SPRING_D_MEAN / 2 + SPRING_D_WIRE / 2, SPRING_D_MEAN / 2 - SPRING_D_WIRE / 2
    a = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, YC, SPRING_AXIS_Z), gp_Dir(1, 0, 0)), r_o, x1 - x0).Shape()
    b = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0 - 1, YC, SPRING_AXIS_Z), gp_Dir(1, 0, 0)), r_i, x1 - x0 + 2).Shape()
    return cut(a, b)


# Stepped scraper lips, as in the drawing: no lip in front of the insert; a lip behind it instead.
LIP_BACK_X = 11.4                      # from the carriage end face: clears the insert up to the first damper touch
LIP_BACK_W = 1.0


def scraper_pocket_corner_cut():
    """Carriage-top: the scraper pocket grows into the corner (4.5 mm deep), so the scraper can carry
    the back lip. It stays beside the strip proper (y below 12 mm), clear of the slope opening."""
    return box(X0 - 1, CORNER_Y[0], Z_TOP_UNDER - 1, X0 + LIP_BACK_X + LIP_BACK_W + 0.2, CORNER_Y[1], Z_TOP_UNDER + P_DEPTH)


def scraper_stepped():
    s = scraper()
    a, b = CORNER_Y
    s = cut(s, box(X0 - 1, a, Z_TIP - 1, X0 + 3.01, b, Z_PLATE_UNDER - 0.001))       # front lips removed
    s = fuse(s, box(X0 + 9.0, a, Z_PLATE_UNDER, X0 + LIP_BACK_X + LIP_BACK_W, b, Z_TOP_UNDER + P_DEPTH))  # plate
    return fuse(s, box(X0 + LIP_BACK_X, a, Z_TIP, X0 + LIP_BACK_X + LIP_BACK_W, b, Z_PLATE_UNDER + 0.01))
