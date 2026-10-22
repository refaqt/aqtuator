import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scraper import *

top=placed('carriage-top','carriage_top'); bot=placed('carriage-bottom','carriage_bottom001'); base=placed('base','base')
top2=cut(top,pocket_cut()); sc=scraper(); scr=screws(); rol=rollers()
strip=box(0,12,40,440,198,40.25)
PARTS=[('base',base,'#c9ced6'),('carriage-bottom',bot,'#9fb7d9'),('carriage-top (with new pocket)',top2,'#b9c9a8'),
       ('seal strip 0.25 mm',strip,'#555555'),('scraper',sc,'#e8833a')]+[('M3x10 ISO 14581',s,'#7a5c99') for s in scr]+[('top roller 10 x 20 mm',r,'#1f5fa8') for r in rol]

def loops(segs,ax0,ax1,tol=1e-3):
    segs=[[(p[ax0],p[ax1]) for p in s] for s in segs]
    out=[]
    while segs:
        cur=segs.pop(0)
        changed=True
        while changed:
            changed=False
            for i,s in enumerate(segs):
                if np.hypot(*np.subtract(s[0],cur[-1]))<tol: cur+=s[1:]
                elif np.hypot(*np.subtract(s[-1],cur[-1]))<tol: cur+=s[::-1][1:]
                elif np.hypot(*np.subtract(s[-1],cur[0]))<tol: cur=s[:-1]+cur
                elif np.hypot(*np.subtract(s[0],cur[0]))<tol: cur=s[::-1][:-1]+cur
                else: continue
                segs.pop(i); changed=True; break
        if len(cur)>3: out.append(cur)
    return out

def section_poly(shape,origin,normal,ax0,ax1):
    ls=loops(section(shape,origin,normal,24),ax0,ax1)
    g=None
    for l in ls:
        p=Polygon(l).buffer(0)
        g=p if g is None else g.symmetric_difference(p)
    return g

def draw(ax,g,color,lw=0.6):
    if g is None or g.is_empty: return
    for p in getattr(g,'geoms',[g]):
        if p.geom_type!='Polygon': continue
        verts=[];codes=[]
        for ring in [p.exterior]+list(p.interiors):
            c=list(ring.coords); verts+=c; codes+=[Path.MOVETO]+[Path.LINETO]*(len(c)-2)+[Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts,codes),fc=color,ec='k',lw=lw))

def sec_plot(ax,origin,normal,ax0,ax1,xlim,ylim,title,labels=True):
    used=set()
    for name,s,c in PARTS:
        g=section_poly(s,origin,normal,ax0,ax1)
        if g is not None and not g.is_empty and g.intersects(Polygon([(xlim[0],ylim[0]),(xlim[1],ylim[0]),(xlim[1],ylim[1]),(xlim[0],ylim[1])])):
            draw(ax,g,c)
            if name not in used: ax.plot([],[],'s',color=c,label=name,ms=8,mec='k'); used.add(name)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=.3)
    ax.set_title(title,fontsize=10)
