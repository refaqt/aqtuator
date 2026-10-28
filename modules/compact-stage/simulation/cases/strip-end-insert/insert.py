"""The strip end concept of Niels Bosmans (2026-10-28), at the end x = 0 of the base, side y = 0.
Assembly coordinates, mm: x along the travel (base end face at x = 0), y across, z up.
The other side (y = 210) and the other end (x = 440) are mirror images.

Each strip end has two inserts, one near each side edge. An insert sits in a hole in the strip,
with no thread and no nut. A countersunk screw presses it into the hole. Two flat faces on the
insert slide in a small groove in the base, so it cannot turn. The screw hole in the base sits a
little nearer the base end than the insert when the strip is laid loose, so tightening the screw
centres the insert on it and pulls the strip. Magnets in pockets hold the strip down.

Positions are measured on his drawing (3.44 pixels per mm, from the 74.1 mm pitch of the
carriage-top screws) and rounded."""
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
# Insert, steel, from the drawing: Ø7.5, centred over the side wall
XC, YC = 11.6, 13.2          # insert axis when the pull is set
INS_D, FLATS = 7.5, 6.0      # diameter, and width across the two flat faces (parallel to the travel)
INS_H = 1.7                  # height: the M2.5 countersink (1.5 mm) plus 0.2 mm under it
TRAVEL = 0.25                # how far the screw pulls the insert towards the base end
# ISO 14581 M2.5 x 6, Torx countersunk: dk 4.7, k 1.5, 90 degrees
DK, K, D_SCREW, SCREW_L = 4.7, 1.5, 2.5, 6.0
BORE_D = D_SCREW + 2 * TRAVEL + 0.2    # lets the shank through while the insert is still off centre
TAP_DEPTH = 6.0                        # M2.5 tapped hole, drilled straight down into the side wall
# Groove for the flat faces, milled from the top with a 6 mm end mill
GROOVE_W = FLATS + 0.1
VARIANTS = {'as drawn': 0.5, 'flush': INS_H - T}   # groove depth; 'flush': insert top = strip top
# Strip outline at this corner, from the drawing: end at x = 1.5, an ear out to y = 6.5
STRIP_END_X, STRIP_Y0, EAR_Y, EAR_X1, EAR_X2 = 1.5, 12.0, 6.5, 16.0, 21.5
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


def floor_z(variant):
    return Z_WALL - VARIANTS[variant]


def groove_cut(variant):
    """Groove (a slot with round ends), tapped hole, and the magnet pockets."""
    zf = floor_z(variant)
    r = GROOVE_W / 2
    # the round ends are centred on the corners of the flat faces, so the corners fit
    half = (INS_D ** 2 / 4 - FLATS ** 2 / 4) ** 0.5
    xa, xb = XC - half - 0.05, XC + half + TRAVEL + 0.05
    g = box(xa, YC - r, zf, xb, YC + r, Z_WALL + 1)
    for x in (xa, xb):
        g = fuse(g, cyl(x, YC, zf, r, Z_WALL + 1 - zf))
    g = fuse(g, cyl(XC, YC, zf - TAP_DEPTH, 1.025, TAP_DEPTH + 0.1))
    for x, y in MAGNETS:
        g = fuse(g, cyl(x, y, Z_WALL - MAG_H - 0.2, MAG_D / 2 + 0.1, MAG_H + 1.2))
    return g


def insert(variant, dx=0.0):
    """The insert when the pull is set (dx = 0), or when the strip is laid loose (dx = TRAVEL)."""
    zf, xc = floor_z(variant), XC + dx
    s = cyl(xc, YC, zf, INS_D / 2, INS_H)
    s = common(s, box(xc - 5, YC - FLATS / 2, zf - 1, xc + 5, YC + FLATS / 2, zf + INS_H + 1))
    s = cut(s, cone(xc, YC, zf + INS_H - K, D_SCREW / 2, DK / 2 + 0.05, K + 0.01))
    return cut(s, cyl(xc, YC, zf - 1, BORE_D / 2, INS_H + 2))


def screw(variant):
    """The screw when it is tight: its head sits in the countersink of the insert."""
    top = floor_z(variant) + INS_H
    h = cone(XC, YC, top - K, D_SCREW / 2, DK / 2, K)
    return fuse(h, cyl(XC, YC, top - SCREW_L, D_SCREW / 2, SCREW_L - K))


def strip(dx=0.0):
    pts = [(STRIP_END_X, EAR_Y), (EAR_X1, EAR_Y), (EAR_X2, STRIP_Y0), (80, STRIP_Y0), (80, 120), (STRIP_END_X, 120)]
    s = prism([(x + dx, y) for x, y in pts], Z_WALL, Z_STRIP)
    return cut(s, cyl(XC + dx, YC, Z_WALL - 1, HOLE_D / 2, 2))


def magnets():
    return [cyl(x, y, Z_WALL - MAG_H, MAG_D / 2, MAG_H) for x, y in MAGNETS]


def roller_cyls(dx):
    return [shift(r, dx) for r in rollers()]
