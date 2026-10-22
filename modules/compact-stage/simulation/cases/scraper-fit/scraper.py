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
Z_STRIP_TOP = 40.25 # 0.25 mm strip on the base top at z = 40
# pocket in carriage-top
P_LEN, P_Y0, P_Y1, P_DEPTH = 10.0, 6.0, 204.0, 4.5
# scraper
CLR = 0.2                       # side play in the pocket (y and x inner end)
PLATE_T = 3.5                   # plate: z 41.5 .. 45.0
Z_PLATE_UNDER = Z_TOP_UNDER + P_DEPTH - PLATE_T   # 41.5
GAP = 0.15                      # lip tip above the strip
Z_TIP = Z_STRIP_TOP + GAP       # 40.40
LIPS = [(0.0, 1.0), (2.0, 3.0)] # x ranges from the end face
SCREW_X = 6.5
SCREW_Y = [13.0, 59.0, 105.0, 151.0, 197.0]
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

def scraper():
    y0,y1 = P_Y0+CLR, P_Y1-CLR
    s = box(X0, y0, Z_PLATE_UNDER, X0+P_LEN-CLR, y1, Z_TOP_UNDER+P_DEPTH)
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
    p = box(X0-1, P_Y0, Z_TOP_UNDER-1, X0+P_LEN, P_Y1, Z_TOP_UNDER+P_DEPTH)
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
