"""Scraper for the start end of carriage-top. Assembly coordinates, mm.
x along travel (carriage end face at X0, inward = +x), y across, z up."""
from fcstd_shapes import *
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.gp import gp_Ax2
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

X0 = 106.6          # end face of carriage-top (start end)
Z_TOP_UNDER = 40.5  # underside of carriage-top
Z_STRIP_TOP = 40.15 # 0.15 mm strip on the base top at z = 40
# pocket in carriage-top
P_LEN, P_Y0, P_Y1, P_DEPTH = 10.0, 6.0, 204.0, 4.5
# scraper
CLR = 0.2                       # side play in the pocket (y and x inner end)
PLATE_T = 3.5                   # plate: z 41.5 .. 45.0
Z_PLATE_UNDER = Z_TOP_UNDER + P_DEPTH - PLATE_T   # 41.5
GAP = 0.15                      # lip tip above the strip
Z_TIP = Z_STRIP_TOP + GAP       # 40.30
LIPS = [(0.0, 1.0), (2.0, 3.0)] # x ranges from the end face
SCREW_X = 6.5
SCREW_Y = [11.0, 60.0, 105.0, 150.0, 199.0]
# Sealing strip rollers in carriage-top: Ø10 x 20 mm, centre on the low edge of the slanted
# face (x = 118.77), 1.5 mm below the underside, 70.5 mm each side of the centre line.
ROLLER_X, ROLLER_Z, ROLLER_R, ROLLER_L = 118.77, 44.0, 5.0, 20.0
ROLLER_Y = [105.0 - 70.5, 105.0 + 70.5]
# Around each roller and its axle slot (y = 16 to 53 mm) the scraper is shorter.
NOTCHES = [(15.0, 54.0), (156.0, 195.0)]
NOTCH_LEN = 6.4                 # scraper length there, from the end face
CUTTER_R = 2.0                  # end mill radius for the pocket corners
SCRAPER_R = 2.5                 # rounded scraper corners, so they clear the milled ones
# ISO 14581 M3 (Torx countersunk): dk 5.5, k 1.65, 90 deg
DK, K, RECESS, D_CLR = 5.6, 1.65, 0.3, 3.4

def box(x0,y0,z0,x1,y1,z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0,y0,z0),gp_Pnt(x1,y1,z1)).Shape()
def cyl(x,y,z0,r,h): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z0),gp_Dir(0,0,1)),r,h).Shape()
def cone(x,y,z0,r0,r1,h): return BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(x,y,z0),gp_Dir(0,0,1)),r0,r1,h).Shape()
def cut(a,b): return BRepAlgoAPI_Cut(a,b).Shape()
def fuse(a,b): return BRepAlgoAPI_Fuse(a,b).Shape()
def common(a,b): return BRepAlgoAPI_Common(a,b).Shape()
def vol(s):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
def dist(a,b):
    d=BRepExtrema_DistShapeShape(a,b); d.Perform(); return d.Value()

from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRep import BRep_Tool as _BT
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopExp import TopExp

def round_vertical_edges(shape, corners, r):
    """Round the vertical edges that pass through the (x, y) points in corners."""
    f = BRepFilletAPI_MakeFillet(shape); n = 0; seen = set()
    ex = TopExp_Explorer(shape, TopAbs_EDGE)
    while ex.More():
        e = TopoDS.Edge(ex.Current()); ex.Next()
        a = _BT.Pnt_s(TopExp.FirstVertex_s(e)); b = _BT.Pnt_s(TopExp.LastVertex_s(e))
        if abs(a.X()-b.X()) < 1e-6 and abs(a.Y()-b.Y()) < 1e-6 and abs(a.Z()-b.Z()) > 1e-3:
            key = (round(a.X(), 3), round(a.Y(), 3))
            if key not in seen and any(abs(a.X()-x) < 1e-3 and abs(a.Y()-y) < 1e-3 for x, y in corners):
                seen.add(key); f.Add(r, e); n += 1
    f.Build()
    return f.Shape(), n

def outline(x_end, notch_x_end, grow):
    """Plan shape of the scraper (grow = 0) or of the pocket (grow = CLR), as boxes."""
    y0, y1 = P_Y0 + CLR - grow, P_Y1 - CLR + grow
    parts = []; y = y0
    for a, b in NOTCHES:
        parts += [(y, a + grow, x_end), (a + grow, b - grow, notch_x_end)]; y = b - grow
    parts.append((y, y1, x_end))
    return parts

def scraper_plate():
    parts = outline(X0+P_LEN-CLR, X0+NOTCH_LEN, 0.0)
    s = None
    for ya, yb, xe in parts:
        b = box(X0, ya, Z_PLATE_UNDER, xe, yb, Z_TOP_UNDER+P_DEPTH)
        s = b if s is None else fuse(s, b)
    xe = X0+P_LEN-CLR
    corners = [(xe, P_Y0+CLR), (xe, P_Y1-CLR)] + [(xe, y) for a, b in NOTCHES for y in (a, b)]
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    u = ShapeUpgrade_UnifySameDomain(s, True, True, True); u.Build(); s = u.Shape()
    s, n = round_vertical_edges(s, corners, SCRAPER_R)
    assert n == len(corners), n
    return s

def scraper():
    y0,y1 = P_Y0+CLR, P_Y1-CLR
    s = scraper_plate()
    for a,b in LIPS:
        s = fuse(s, box(X0+a, y0, Z_TIP, X0+b, y1, Z_PLATE_UNDER+0.01))
    for y in SCREW_Y:
        x = X0+SCREW_X
        s = cut(s, cyl(x,y,Z_TIP-1,D_CLR/2,20))
        zc = Z_PLATE_UNDER+RECESS             # head face
        s = cut(s, cyl(x,y,Z_TIP-1,DK/2,zc+0.4-(Z_TIP-1)))  # recess + head edge
        s = cut(s, cone(x,y,zc+0.4,DK/2,0.01,DK/2))           # 90 deg countersink
    return s

def pocket_cut():
    p = None
    for ya, yb, xe in outline(X0+P_LEN, X0+NOTCH_LEN+CLR, CLR):
        b = box(X0-1, ya, Z_TOP_UNDER-1, xe, yb, Z_TOP_UNDER+P_DEPTH)
        p = b if p is None else fuse(p, b)
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    u = ShapeUpgrade_UnifySameDomain(p, True, True, True); u.Build(); p = u.Shape()
    xe = X0+P_LEN
    corners = [(xe, P_Y0), (xe, P_Y1)] + [(xe, y) for a, b in NOTCHES for y in (a+CLR, b-CLR)]
    p, n = round_vertical_edges(p, corners, CUTTER_R)
    assert n == len(corners), n
    for y in SCREW_Y:  # tap drill 2.5 mm, 10 mm deep from the pocket ceiling
        p = fuse(p, cyl(X0+SCREW_X, y, Z_TOP_UNDER+P_DEPTH-0.1, 1.25, 10.1))
    return p

def screws():
    out=[]
    for y in SCREW_Y:
        x=X0+SCREW_X; zc=Z_PLATE_UNDER+RECESS
        h=fuse(cyl(x,y,zc,2.75,0.4), cone(x,y,zc+0.4,2.75,1.5,1.25))
        h=fuse(h, cyl(x,y,zc+1.65,1.5,10-1.65))
        out.append(h)
    return out

def rollers():
    """The two top rollers at the start end, as plain cylinders along y."""
    return [BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(ROLLER_X, y-ROLLER_L/2, ROLLER_Z), gp_Dir(0,1,0)),
                                     ROLLER_R, ROLLER_L).Shape() for y in ROLLER_Y]
