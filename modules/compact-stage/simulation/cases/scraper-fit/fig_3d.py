import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','results','scraper-fit')
os.makedirs(OUT,exist_ok=True)
from render import *
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def tris(shape):
    BRepMesh_IncrementalMesh(shape,0.05,False,0.3,True)
    ex=TopExp_Explorer(shape,TopAbs_FACE); out=[]
    while ex.More():
        f=TopoDS.Face(ex.Current()); loc=TopLoc_Location()
        t=BRep_Tool.Triangulation_s(f,loc)
        if t is not None:
            tr=loc.Transformation(); rev=f.Orientation()==TopAbs_REVERSED
            P=[t.Node(i).Transformed(tr) for i in range(1,t.NbNodes()+1)]
            P=[(p.X(),p.Y(),p.Z()) for p in P]
            for i in range(1,t.NbTriangles()+1):
                a,b,c=t.Triangle(i).Get()
                tri=[P[a-1],P[b-1],P[c-1]]
                out.append(tri[::-1] if rev else tri)
        ex.Next()
    return np.array(out)
def shade(T,color,light=(0.3,-0.5,-0.8)):
    n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12
    L=np.array(light)/np.linalg.norm(light); k=0.45+0.55*np.abs(n@L)
    c=np.array(matplotlib.colors.to_rgb(color)); return np.clip(c[None]*k[:,None],0,1)
def show(ax,items,elev,azim,lims):
    for s,c,a in items:
        T=tris(s); pc=Poly3DCollection(T,facecolors=shade(T,c),edgecolors='none',alpha=a); ax.add_collection3d(pc)
    (x0,x1),(y0,y1),(z0,z1)=lims
    ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0))
    ax.view_init(elev,azim); ax.set_xlabel('x');ax.set_ylabel('y');ax.set_zlabel('z')

# A: one end of the scraper from below, and from above
seg=common(sc,box(100,0,30,130,62,61))
fig=plt.figure(figsize=(13,6))
for k,(el,az,t) in enumerate([(-35,-60,'from below: the two lips and the countersunk screw holes'),(35,-60,'from above: the flat face that rests on the pocket ceiling')]):
    ax=fig.add_subplot(1,2,k+1,projection='3d')
    show(ax,[(seg,'#e8833a',1)],el,az,((104,120),(5,62),(39,47)))
    ax.set_axis_off(); ax.set_title('Scraper, first 55 mm, '+t,fontsize=9)
fig.suptitle('Printed scraper (one part per carriage end, 197.6 x 9.8 x 4.6 mm)',fontsize=11)
fig.tight_layout(); fig.savefig(OUT+'/3d_scraper_from_below.png',dpi=150)

# B: cut-away of the carriage corner from below: x 100..140, y 0..45
clipbox=box(95,-1,30,140,45,61)
items=[(common(top2,clipbox),'#b9c9a8',1),(common(bot,clipbox),'#9fb7d9',1),(common(sc,clipbox),'#e8833a',1)]+[(common(s,clipbox),'#7a5c99',1) for s in scr[:1]]
fig=plt.figure(figsize=(11,8)); ax=fig.add_subplot(111,projection='3d')
show(ax,items,-30,-50,((100,140),(0,45),(30,61))); ax.set_axis_off()
ax.set_title('Carriage corner at the start end, seen from below (base and strip hidden).\nThe scraper sits in a pocket in carriage-top; carriage-bottom (blue) starts 5 mm behind it.',fontsize=10)
fig.tight_layout(); fig.savefig(OUT+'/3d_corner_from_below.png',dpi=150)
