"""Strip end clamp at the end x = 0 of the base, version 2. Assembly coordinates, mm.
x along the travel (base end face at x = 0, inward = +x), y across, z up.
The end at x = 440 is the same, mirrored.

Everything is reached and machined from the top: a step milled down into the end wall, vertical
tapped holes in its floor, a bar that hangs the strip tab on pins, and two screws that pull the
bar down. Turning the screws sets the pull in the strip."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper-fit'))
from scraper import *  # noqa: E402  (unzips the CAD files, gives box, cyl, cut, ...)
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder

T = 0.25                     # strip thickness
Z_WALL = 40.0                # top of the base
STRIP_Y = (12.0, 198.0)      # 186 mm strip
# The end wall is 10 mm thick only between these pockets, read from the base:
# damper pockets y 52.5-76.5 and 133.5-157.5 (x 3 to 10), and a half-round pocket in each
# inside corner, y 17-29 and 181-193 (x 4 to 10).
THIN_Y = [(17.0, 29.0), (52.5, 76.5), (133.5, 157.5), (181.0, 193.0)]
# Step in the end wall, milled from the top, open to the end face. One per tab, at least 2 mm
# from the pockets above.
STEPS = [(31.0, 50.5), (79.5, 130.5), (159.5, 179.0)]
STEP_X = 7.0                 # the step runs from the end face to x = 7; 3 mm of wall stays
STEP_FLOOR = 24.0            # 16 mm deep
STEP_R = 3.0                 # inside corners, 6 mm end mill
EDGE_R = 3.0                 # round edge on the wall top where the strip goes down (12 x t)
# Bar: aluminium, hangs in the step on the tab, pulled down by two screws
BAR_X = (0.2, STEP_X - T - 0.1)      # 0.1 mm to the tab
BAR_Z = (28.0, 35.0)                 # nominal height; it moves with the pull
BAR_PLAY, BAR_R = 0.2, 3.5           # y play; rounded corners at the wall side
SCREW_X = 3.3
# ISO 4762 M3 x 16 with a thread locking patch; head 5.5 x 3. Tapped hole 2.5 mm, 12 mm deep.
HEAD_D, HEAD_H, SCREW_L, HOLE_DEPTH = 5.5, 3.0, 16.0, 12.0
# Pins: ISO 8734 dowel 2 x 4, pressed into the bar, sticking out 0.3 mm into the tab holes
PIN_D, PIN_L, PIN_Z = 2.0, 4.0, 31.5
TAB_HOLE_D = 2.1
TAB_Z_END = 29.5
FLAT_END_X = 1.0             # where the strip ends on top, beside the tabs
RELIEF_X = 11.0              # end of the cut beside each tab, 1 mm past the bend
# Travel ends, from the log of the damper pockets: carriage-top end face at x = 5 at the end
# of the usable travel, x = -3 with the dampers fully pressed in.
CARRIAGE_END_X = {'usable travel end': 5.0, 'dampers fully pressed': -3.0}


def tab_y(step):
    """The tab lies on the flat part of the wall face, between the rounded step corners."""
    return step[0] + STEP_R + 0.5, step[1] - STEP_R - 0.5


def screw_ys(step):
    c, w = (step[0] + step[1]) / 2, step[1] - step[0]
    return [c - 5.5, c + 5.5] if w < 30 else [c - 9.0, c + 9.0]


def pin_ys(step):
    c, w = (step[0] + step[1]) / 2, step[1] - step[0]
    return [c - 1.5, c + 1.5] if w < 30 else [c - 18.0, c, c + 18.0]


def ycyl(x, z, r, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), r, y1 - y0).Shape()


def xcyl(x0, y, z, r, h):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y, z), gp_Dir(1, 0, 0)), r, h).Shape()


def shift(s, dx):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, 0, 0))
    return BRepBuilderAPI_Transform(s, t, True).Shape()


def rounded_inner_corners(x0, y0, x1, y1, z0, z1, r):
    """Box with its two vertical edges at x = x1 rounded with radius r."""
    b = box(x0, y0, z0, x1, y1, z1)
    b = cut(b, box(x1 - r, y0 - 1, z0 - 1, x1 + 1, y0 + r, z1 + 1))
    b = cut(b, box(x1 - r, y1 - r, z0 - 1, x1 + 1, y1 + 1, z1 + 1))
    b = fuse(b, box(x1 - r, y0 + r, z0, x1, y1 - r, z1))
    for y in (y0 + r, y1 - r):
        b = fuse(b, cyl(x1 - r, y, z0, r, z1 - z0))
    return common(b, box(x0, y0, z0, x1, y1, z1))


def step_cut():
    """What the base loses at the end x = 0: three steps, round edges, vertical tapped holes."""
    c = None
    for s in STEPS:
        r = rounded_inner_corners(-1, s[0], STEP_X, s[1], STEP_FLOOR, Z_WALL + 1, STEP_R)
        e = box(STEP_X, s[0], Z_WALL - EDGE_R, STEP_X + EDGE_R, s[1], Z_WALL + 1)
        e = cut(e, ycyl(STEP_X + EDGE_R, Z_WALL - EDGE_R, EDGE_R, s[0] - 1, s[1] + 1))
        r = fuse(r, e)
        for y in screw_ys(s):
            r = fuse(r, cyl(SCREW_X, y, STEP_FLOOR - HOLE_DEPTH, 1.25, HOLE_DEPTH + 0.1))
        c = r if c is None else fuse(c, r)
    return c


def strip():
    """The strip near the end: flat on top, a tab bent down into each step."""
    xc, zc = STEP_X + EDGE_R, Z_WALL - EDGE_R
    s = box(FLAT_END_X, STRIP_Y[0], Z_WALL, 60, STRIP_Y[1], Z_WALL + T)
    for st in STEPS:
        a, b = tab_y(st)
        s = cut(s, box(FLAT_END_X - 1, a, Z_WALL - 1, xc, b, Z_WALL + 1))
        for y in (a, b):
            s = cut(s, box(FLAT_END_X - 1, y - 0.25, Z_WALL - 1, RELIEF_X, y + 0.25, Z_WALL + 1))
            s = cut(s, cyl(RELIEF_X, y, Z_WALL - 1, 0.75, 2))
        bend = cut(ycyl(xc, zc, EDGE_R + T, a, b), ycyl(xc, zc, EDGE_R, a - 1, b + 1))
        bend = common(bend, box(STEP_X - 1, a, zc, xc, b, Z_WALL + 1))
        down = box(STEP_X - T, a, TAB_Z_END, STEP_X, b, zc)
        for y in pin_ys(st):
            down = cut(down, xcyl(STEP_X - 1, y, PIN_Z, TAB_HOLE_D / 2, 2))
        s = fuse(s, fuse(bend, down))
    return s


def bars():
    out = []
    for st in STEPS:
        b = rounded_inner_corners(BAR_X[0], st[0] + BAR_PLAY, BAR_X[1], st[1] - BAR_PLAY, BAR_Z[0], BAR_Z[1], BAR_R)
        for y in screw_ys(st):
            b = cut(b, cyl(SCREW_X, y, BAR_Z[0] - 1, 1.7, BAR_Z[1] - BAR_Z[0] + 2))
        for y in pin_ys(st):
            b = cut(b, xcyl(BAR_X[1] - PIN_L + 0.3, y, PIN_Z, PIN_D / 2, PIN_L))
        out.append(b)
    return out


def pins():
    return [xcyl(BAR_X[1] - PIN_L + 0.3, y, PIN_Z, PIN_D / 2, PIN_L) for st in STEPS for y in pin_ys(st)]


def screws():
    out = []
    for st in STEPS:
        for y in screw_ys(st):
            h = cyl(SCREW_X, y, BAR_Z[1], HEAD_D / 2, HEAD_H)
            out.append(fuse(h, cyl(SCREW_X, y, BAR_Z[1] - SCREW_L, 1.5, SCREW_L)))
    return out


def roller_cyls(dx):
    return [shift(r, dx) for r in rollers()]
