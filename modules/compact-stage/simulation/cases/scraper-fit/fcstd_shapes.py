"""Read the part shapes straight out of the FreeCAD files, without FreeCAD.

A .FCStd file is a zip with a Document.xml and one BREP file per shape. This module unzips the
compact-stage files into a work folder and places each part where the assembly puts it.
"""
import os, tempfile, zipfile
import xml.etree.ElementTree as ET
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from OCP.gp import gp_Trsf, gp_Quaternion, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def props(path):
    r=ET.parse(path).getroot(); out={}
    od={o.get('name'):o for o in r.find('ObjectData')}
    for n,o in od.items():
        d={}
        for p in o.iter('Property'):
            for c in p:
                d[p.get('name')]=c.attrib; break
        out[n]=d
    return out
def shape(part,obj='Body'):
    P=props(f'{part}/Document.xml')
    f=P[obj]['Shape']['file']
    s=TopoDS_Shape(); BRepTools.Read_s(s,f'{part}/{f}',BRep_Builder())
    return s
def trsf(pl):
    t=gp_Trsf(); t.SetRotation(gp_Quaternion(*[float(pl[k]) for k in ('Q0','Q1','Q2','Q3')]))
    t2=gp_Trsf(); t2.SetTranslation(gp_Vec(*[float(pl[k]) for k in ('Px','Py','Pz')]))
    return t2.Multiplied(t)
def move(s,pl): return BRepBuilderAPI_Transform(s,trsf(pl),True).Shape()
def bbox(s):
    b=Bnd_Box(); BRepBndLib.Add_s(s,b); a,c=b.CornerMin(),b.CornerMax(); return [round(v,3) for v in (a.X(),a.Y(),a.Z(),c.X(),c.Y(),c.Z())]
MODULE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
WORK = tempfile.mkdtemp(prefix='scraper-fit-')
for name, rel in [('asm', 'cad/assemblies/compact-stage/compact-stage.FCStd')] + [
        (p, f'cad/parts/{p}/{p}.FCStd') for p in ('base', 'carriage-top', 'carriage-bottom')]:
    path = os.path.join(MODULE, rel)
    if open(path, 'rb').read(4) != b'PK\x03\x04':
        raise SystemExit(f'{rel} is not a FreeCAD file. Run: git lfs pull')
    zipfile.ZipFile(path).extractall(os.path.join(WORK, name))
os.chdir(WORK)
A=props('asm/Document.xml')
def placed(part,link):
    s=shape(part)
    P=props(f'{part}/Document.xml')
    s=move(s,P['Part']['Placement']) if 'Part' in P else s
    return move(s,A[link]['Placement'])
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_UniformAbscissa
from OCP.TopoDS import TopoDS
def section(s,origin,normal,n=40):
    sec=BRepAlgoAPI_Section(s,gp_Pln(gp_Pnt(*origin),gp_Dir(*normal))); sec.Build()
    ex=TopExp_Explorer(sec.Shape(),TopAbs_EDGE); segs=[]
    while ex.More():
        c=BRepAdaptor_Curve(TopoDS.Edge(ex.Current()))
        a,b=c.FirstParameter(),c.LastParameter()
        pts=[c.Value(a+(b-a)*i/n) for i in range(n+1)]
        segs.append([(p.X(),p.Y(),p.Z()) for p in pts]); ex.Next()
    return segs
