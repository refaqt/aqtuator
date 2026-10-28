"""Strip end clamp at the end x = 0 of the base, version 3: an insert pulled by a countersunk
screw. Assembly coordinates, mm. x along the travel (base end face at x = 0, inward = +x),
y across, z up. The end at x = 440 is the same, mirrored.

An insert clamps the strip between its flange (on top) and a square nut (below). The nut slides
in a groove milled from the top into the end wall; its flat sides stop it from turning. The
countersunk screw goes straight down into the groove floor. Its hole in the insert sits a little
towards the stage middle, so the cone of the head pulls the insert, and the strip, towards the
base end when the screw is tightened."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper-fit'))
from scraper import *  # noqa: E402  (unzips the CAD files, gives box, cyl, cone, cut, ...)
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder

T = 0.15                     # strip thickness, decision of 2026-10-28
Z_WALL = 40.0                # top of the base
Z_STRIP = Z_WALL + T
STRIP_Y = (12.0, 198.0)      # 186 mm strip
STRIP_END_X = 0.3            # the strip ends flat on the end wall
Y_C = 105.0                  # one insert per end, on the centre line, clear of the top rollers
# Insert, steel: flange on top of the strip, body through the strip hole, M6 x 0.5 thread
FLANGE_D, FLANGE_H = 9.0, 1.0
BODY_D, HOLE_D = 6.0, 6.2              # body, and the hole in the strip
X_C = 5.2                              # insert axis when the pull is set
ECC = 0.2                              # countersink offset in the insert; made in steps to tune
TRAVEL = 0.15                          # insert travel at this end while the screw is tightened
# ISO 14581 M2.5 x 8, Torx countersunk: dk 4.7, k 1.5, 90 degrees
DK, K, D_SCREW, SCREW_L = 4.7, 1.5, 2.5, 8.0
BORE_D = 2.9 + 2 * 0.5                 # lets the screw through at up to 0.5 mm offset
# Square nut, steel, threaded M6 x 0.5, flat sides in the groove
NUT_Y, NUT_X, NUT_H, NUT_R = 9.0, 8.0, 3.0, 1.5   # corners rounded, to clear the groove
# Groove in the end wall, milled from the top, open towards the stage middle (x = 10)
GROOVE_W, GROOVE_X0, GROOVE_FLOOR, GROOVE_R = 9.1, 1.0, Z_WALL - NUT_H - 0.2, 1.0   # 2 mm end mill
HOLE_DEPTH = 6.0                       # M2.5 tapped hole in the groove floor, drilled from the top
# Scraper: the lips step back around the insert, carriage-top gets a longer pocket there
NOTCH_Y = (Y_C - 7.0, Y_C + 7.0)
LIP_BACK = [(6.5, 7.5), (8.5, 9.5)]    # lips behind the insert, from the carriage end face
POCKET_LONG = 15.0                     # pocket length in carriage-top at the insert, for a crash
# Travel ends, from the log of the damper pockets: carriage-top end face at x = 5 at the end
# of the usable travel, 4 at the first damper touch, -3 with the dampers fully pressed in.
CARRIAGE_END_X = {'usable travel end': 5.0, 'first damper touch': 4.0, 'dampers fully pressed': -3.0}


def xcyl(x0, y, z, r, h):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y, z), gp_Dir(1, 0, 0)), r, h).Shape()


def shift(s, dx):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, 0, 0))
    return BRepBuilderAPI_Transform(s, t, True).Shape()


def screw_x():
    return X_C + ECC                   # the tapped hole; the insert is pulled until it is centred on it


def groove_cut():
    """What the base loses: the groove and the tapped hole."""
    a, b = Y_C - GROOVE_W / 2, Y_C + GROOVE_W / 2
    g = box(GROOVE_X0 + GROOVE_R, a, GROOVE_FLOOR, 10.0, b, Z_WALL + 1)
    g = fuse(g, box(GROOVE_X0, a + GROOVE_R, GROOVE_FLOOR, 10.0, b - GROOVE_R, Z_WALL + 1))
    for y in (a + GROOVE_R, b - GROOVE_R):
        g = fuse(g, cyl(GROOVE_X0 + GROOVE_R, y, GROOVE_FLOOR, GROOVE_R, Z_WALL + 1 - GROOVE_FLOOR))
    return fuse(g, cyl(screw_x(), Y_C, GROOVE_FLOOR - HOLE_DEPTH, 1.025, HOLE_DEPTH + 0.1))


def insert(dx=0.0):
    """Insert at its set position, or moved by dx (loose, before the screw pulls: dx = +TRAVEL)."""
    xc = X_C + dx
    s = fuse(cyl(xc, Y_C, Z_STRIP, FLANGE_D / 2, FLANGE_H), cyl(xc, Y_C, Z_WALL - NUT_H, BODY_D / 2, NUT_H + T))
    xs = xc + ECC                       # the countersink sits off the insert axis
    s = cut(s, cone(xs, Y_C, Z_STRIP + FLANGE_H - K, D_SCREW / 2, DK / 2 + 0.05, K + 0.01))
    return cut(s, cyl(xs, Y_C, Z_WALL - NUT_H - 1, BORE_D / 2, NUT_H + 2))


def nut(dx=0.0):
    xc = X_C + dx
    x0, x1, y0, y1, r = xc - NUT_X / 2, xc + NUT_X / 2, Y_C - NUT_Y / 2, Y_C + NUT_Y / 2, NUT_R
    n = fuse(box(x0 + r, y0, Z_WALL - NUT_H, x1 - r, y1, Z_WALL), box(x0, y0 + r, Z_WALL - NUT_H, x1, y1 - r, Z_WALL))
    for x in (x0 + r, x1 - r):
        for y in (y0 + r, y1 - r):
            n = fuse(n, cyl(x, y, Z_WALL - NUT_H, r, NUT_H))
    return cut(n, cyl(xc, Y_C, Z_WALL - NUT_H - 1, BODY_D / 2, NUT_H + 2))


def screw():
    xs = screw_x()
    h = cone(xs, Y_C, Z_STRIP + FLANGE_H - K, D_SCREW / 2, DK / 2, K)
    return fuse(h, cyl(xs, Y_C, Z_STRIP + FLANGE_H - SCREW_L, D_SCREW / 2, SCREW_L - K))


def strip(dx=0.0):
    s = box(STRIP_END_X + dx, STRIP_Y[0], Z_WALL, 60, STRIP_Y[1], Z_STRIP)
    return cut(s, cyl(X_C + dx, Y_C, Z_WALL - 1, HOLE_D / 2, 2))


def scraper_v3():
    """The scraper with its lips stepped back around the insert (start end, at X0)."""
    s = scraper()
    a, b = NOTCH_Y
    s = cut(s, box(X0 - 1, a, Z_TIP - 1, X0 + 3.01, b, Z_PLATE_UNDER - 0.001))
    for x0, x1 in LIP_BACK:
        s = fuse(s, box(X0 + x0, a, Z_TIP, X0 + x1, b, Z_PLATE_UNDER + 0.01))
    for y0, y1 in ((a - 1, a), (b, b + 1)):               # side lips close the step
        s = fuse(s, box(X0, y0, Z_TIP, X0 + LIP_BACK[-1][1], y1, Z_PLATE_UNDER + 0.01))
    return s


def long_pocket_cut():
    """Optional: carriage-top pocket made longer at the insert, so a crash does not hit it."""
    a, b = NOTCH_Y
    return box(X0 - 1, a - 1, Z_TOP_UNDER - 1, X0 + POCKET_LONG, b + 1, Z_TOP_UNDER + P_DEPTH)


def roller_cyls(dx):
    return [shift(r, dx) for r in rollers()]
