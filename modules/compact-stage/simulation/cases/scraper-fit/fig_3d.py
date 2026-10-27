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

from raster import render
def rgb(c): return matplotlib.colors.to_rgb(c)
def picture(items, elev, azim, title, path, size=(1400, 900)):
    img = render([(tris(sh), rgb(c)) for sh, c in items], elev, azim, size)
    fig = plt.figure(figsize=(size[0]/150, size[1]/150+0.5)); ax = fig.add_axes([0, 0, 1, size[1]/(size[1]+75)])
    ax.imshow(img); ax.axis('off'); fig.suptitle(title, fontsize=10); fig.savefig(path, dpi=150); plt.close(fig)

# A: one end of the scraper from below and from above
seg = common(sc, box(100, 0, 30, 130, 70, 61))
picture([(seg, '#e8833a')], -40, -125, 'Scraper v2, first 64 mm, from below: two lips, countersunk screw holes, and the cut-out at the roller',
        OUT+'/3d_scraper_from_below.png')
picture([(seg, '#e8833a')], 40, -125, 'Scraper v2, first 64 mm, from above: the flat face that rests on the pocket ceiling',
        OUT+'/3d_scraper_from_above.png')

# B: carriage-top corner with the scraper and the top roller, from below
clipbox = box(95, -1, 30, 140, 58, 61)
items = [(common(top2, clipbox), '#b9c9a8'), (sc_clip := common(sc, clipbox), '#e8833a'), (rol[0], '#1f5fa8')] + \
        [(common(s, clipbox), '#7a5c99') for s in scr[:2]]
picture(items, -40, -125, 'Carriage-top corner at the start end, from below (base, strip and carriage-bottom hidden).\n'
        'Orange: scraper. Blue: top roller in its pocket. Purple: screws. The scraper is shorter where it passes the roller.',
        OUT+'/3d_corner_from_below.png')
