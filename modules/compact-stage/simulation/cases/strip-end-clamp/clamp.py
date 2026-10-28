"""Strip end clamp at the end x = 0 of the base. Assembly coordinates, mm.
x along the travel (base end face at x = 0, inward = +x), y across, z up.
The end at x = 440 is the same, mirrored."""
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
# Three tabs bend down over the end edge, where the wall is thick.
TABS = [(31.0, 50.0), (80.0, 130.0), (160.0, 179.0)]
PLAY = 0.5                   # tab to recess wall, each side
# Recess in the end face, one per tab. Open at the top.
REC_D = 2.3                  # depth: 2.0 plate + 0.25 strip + 0.05 below the face
REC_Z = (10.0, Z_WALL)
REC_R = 2.0                  # bottom corners, 4 mm end mill
EDGE_R = 3.0                 # round edge at the top of the recess floor (12 x strip thickness)
# Clamp plate, 1.4301, 2 mm
PLATE_T = 2.0
PLATE_Z = (16.0, 31.0)
PLATE_PLAY = 0.2
SCREW_Z = 23.5               # two screws per plate, at the quarter points
# ISO 14581 M3 x 8, Torx countersunk: dk 5.5, k 1.65. Tapped hole 2.5 mm, 6.7 mm deep.
SCREW_L, HOLE_DEPTH = 8.0, 6.7
# Strip tab: slots for the screws, a hole to pull on during fitting
TAB_Z_END = 11.5
SLOT_W, SLOT_L = 3.4, 8.0
PULL_HOLE_D, PULL_HOLE_Z = 3.4, 13.5
FLAT_END_X = 1.0             # where the strip ends on top, beside the tabs
RELIEF_X = REC_D + EDGE_R + 1.2   # end of the cut beside each tab, past the bend
# Travel ends, from the log of the damper pockets: carriage-top end face at x = 5 at the end
# of the usable travel, x = -3 with the dampers fully pressed in.
CARRIAGE_END_X = {'usable travel end': 5.0, 'dampers fully pressed': -3.0}


def recess_y(tab):
    return tab[0] - PLAY, tab[1] + PLAY


def screw_ys(tab):
    a, b = recess_y(tab)
    return [a + (b - a) / 4, b - (b - a) / 4]


def ycyl(x, z, r, y0, y1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z), gp_Dir(0, 1, 0)), r, y1 - y0).Shape()


def xcyl(x0, y, z, r, h):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y, z), gp_Dir(1, 0, 0)), r, h).Shape()


def shift(s, dx):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, 0, 0))
    return BRepBuilderAPI_Transform(s, t, True).Shape()


def recess_cut():
    """What the base loses at the end x = 0: three recesses, round edges, tapped holes."""
    c = None
    for tab in TABS:
        a, b = recess_y(tab)
        r = box(-1, a, REC_Z[0], REC_D, b, Z_WALL + 1)
        # rounded bottom corners
        r = cut(r, box(-1, a, REC_Z[0], REC_D, a + REC_R, REC_Z[0] + REC_R))
        r = cut(r, box(-1, b - REC_R, REC_Z[0], REC_D, b, REC_Z[0] + REC_R))
        for y in (a + REC_R, b - REC_R):
            r = fuse(r, xcyl(-1, y, REC_Z[0] + REC_R, REC_R, REC_D + 1))
        # round edge between the recess floor and the wall top
        e = box(REC_D, a, Z_WALL - EDGE_R, REC_D + EDGE_R, b, Z_WALL + 1)
        e = cut(e, ycyl(REC_D + EDGE_R, Z_WALL - EDGE_R, EDGE_R, a - 1, b + 1))
        r = fuse(r, e)
        for y in screw_ys(tab):
            r = fuse(r, xcyl(REC_D - 0.1, y, SCREW_Z, 1.25, HOLE_DEPTH + 0.1))
        c = r if c is None else fuse(c, r)
    return c


def strip():
    """The strip near the end: flat on top, three tabs bent down into the recesses."""
    xc, zc = REC_D + EDGE_R, Z_WALL - EDGE_R
    s = box(FLAT_END_X, STRIP_Y[0], Z_WALL, 60, STRIP_Y[1], Z_WALL + T)
    for tab in TABS:
        a, b = tab
        # cut the flat part in front of the tab, so the tab can bend down
        s = cut(s, box(FLAT_END_X - 1, a, Z_WALL - 1, xc, b, Z_WALL + 1))
        # relief cuts beside the tab, 0.5 mm wide, ending in a round hole
        for y in (a, b):
            if STRIP_Y[0] < y < STRIP_Y[1]:
                s = cut(s, box(FLAT_END_X - 1, y - 0.25, Z_WALL - 1, RELIEF_X, y + 0.25, Z_WALL + 1))
                s = cut(s, cyl(RELIEF_X, y, Z_WALL - 1, 0.75, 2))
        bend = cut(ycyl(xc, zc, EDGE_R + T, a, b), ycyl(xc, zc, EDGE_R, a - 1, b + 1))
        bend = common(bend, box(REC_D - 1, a, zc, xc, b, Z_WALL + 1))
        down = box(REC_D - T, a, TAB_Z_END, REC_D, b, zc)
        for y in screw_ys(tab):
            down = cut(down, box(REC_D - 1, y - SLOT_W / 2, SCREW_Z - SLOT_L / 2 + SLOT_W / 2, REC_D + 1,
                                 y + SLOT_W / 2, SCREW_Z + SLOT_L / 2 - SLOT_W / 2))
            for z in (SCREW_Z - SLOT_L / 2 + SLOT_W / 2, SCREW_Z + SLOT_L / 2 - SLOT_W / 2):
                down = cut(down, xcyl(REC_D - 1, y, z, SLOT_W / 2, 2))
        down = cut(down, xcyl(REC_D - 1, (a + b) / 2, PULL_HOLE_Z, PULL_HOLE_D / 2, 2))
        s = fuse(s, fuse(bend, down))
    return s


def plates():
    out = []
    x0 = REC_D - T - PLATE_T
    for tab in TABS:
        a, b = recess_y(tab)
        p = box(x0, a + PLATE_PLAY, PLATE_Z[0], REC_D - T, b - PLATE_PLAY, PLATE_Z[1])
        for y in screw_ys(tab):
            p = cut(p, xcyl(x0 - 1, y, SCREW_Z, 1.7, PLATE_T + 2))
            p = cut(p, BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(x0 - 0.01, y, SCREW_Z), gp_Dir(1, 0, 0)),
                                            2.8, 1.7 - 0.0, 1.1).Shape())
        out.append(p)
    return out


def screws():
    out = []
    x0 = REC_D - T - PLATE_T          # head face, flush with the plate
    for tab in TABS:
        for y in screw_ys(tab):
            h = BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(x0, y, SCREW_Z), gp_Dir(1, 0, 0)), 2.75, 1.5, 1.25).Shape()
            h = fuse(h, xcyl(x0 + 1.25, y, SCREW_Z, 1.5, SCREW_L - 1.25))
            out.append(h)
    return out


def roller_cyls(dx):
    return [shift(r, dx) for r in rollers()]
