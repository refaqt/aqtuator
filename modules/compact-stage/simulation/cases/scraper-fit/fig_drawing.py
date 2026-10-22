import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','results','scraper-fit')
os.makedirs(OUT,exist_ok=True)
from scraper import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon as Poly
L=P_LEN-CLR; W=(P_Y1-P_Y0)-2*CLR; T=PLATE_T; H=Z_PLATE_UNDER-Z_TIP   # 9.8, 197.6, 3.5, 1.1
Y0=P_Y0+CLR
fig=plt.figure(figsize=(14,9))
gs=fig.add_gridspec(2,2,width_ratios=[5,1],height_ratios=[1,1.1])
c='#e8833a'
def dim(ax,p0,p1,text,off=(0,0),fs=8):
    ax.annotate('',p0,p1,arrowprops=dict(arrowstyle='<->',lw=.7)); ax.text((p0[0]+p1[0])/2+off[0],(p0[1]+p1[1])/2+off[1],text,ha='center',va='center',fontsize=fs,bbox=dict(fc='w',ec='none',pad=.5))
# bottom view (looking up at the lips): horizontal = y, vertical = x from end face
ax=fig.add_subplot(gs[0,0])
ax.add_patch(Rectangle((0,0),W,L,fc='#f6c9a6',ec='k'))
for a,b in LIPS: ax.add_patch(Rectangle((0,a),W,b-a,fc=c,ec='k',lw=.6))
for y in SCREW_Y:
    ax.add_patch(Circle((y-Y0,SCREW_X),DK/2,fc='w',ec='k',lw=.6)); ax.add_patch(Circle((y-Y0,SCREW_X),D_CLR/2,fc='#ddd',ec='k',lw=.6))
ax.set_xlim(-8,W+8); ax.set_ylim(-9,L+6); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Bottom view (side that faces the strip). Dark bands = lips. Lip 1 is on the carriage end side (bottom edge here).',fontsize=9)
dim(ax,(0,-3),(W,-3),f'{W:.1f}')
pos=[y-Y0 for y in SCREW_Y]
for p0,p1 in zip([0]+pos,pos): dim(ax,(p0,-6.5),(p1,-6.5),f'{p1-p0:.1f}',fs=7)
dim(ax,(W+3,0),(W+3,L),f'{L:.1f}',off=(2.5,0)); dim(ax,(-3,0),(-3,SCREW_X),f'{SCREW_X}',off=(-2.5,0))
ax.text(W/2,L+3,f'5 x countersunk hole for M3 ISO 14581 (Torx): through hole {D_CLR} mm, 90 deg countersink to {DK} mm, head sits {RECESS} mm below the plate face',ha='center',fontsize=8)
ax.text(-7,-1,'carriage\nend side',fontsize=7,va='center',ha='right')
# side view = section through a screw, x-z, scaled up
ax=fig.add_subplot(gs[1,0]); s=6
from render import section_poly, draw, sc
g=section_poly(sc,(0,SCREW_Y[2],0),(0,1,0),0,2)
from shapely.affinity import translate
draw(ax,translate(g,-X0,-Z_TIP),c,lw=.8)
ax.axhline(-GAP,color='#555',lw=3); ax.text(L+0.3,-GAP-0.15,'strip top (0.15 mm below the lips)',va='center',fontsize=8)
ax.axhline(H+T,color='g',lw=.8,ls='--'); ax.text(L+0.3,H+T,'pocket ceiling in carriage-top',va='center',fontsize=8)
ax.axhline(H+T-P_DEPTH,color='g',lw=.8,ls=':'); ax.text(L+0.3,H+T-P_DEPTH+0.12,'underside of carriage-top',va='center',fontsize=8)
dim(ax,(-0.6,0),(-0.6,H+T),f'{H+T:.1f}',off=(-0.5,0)); dim(ax,(-1.6,H),(-1.6,H+T),f'{T}',off=(-0.45,0))
for a,b in LIPS: dim(ax,(a,-0.45),(b,-0.45),f'{b-a:.1f}',fs=7)
dim(ax,(LIPS[0][1],-0.45),(LIPS[1][0],-0.45),'1.0',fs=7); dim(ax,(LIPS[1][1]+0.1,0),(LIPS[1][1]+0.1,H),f'{H:.1f}',off=(0.5,0),fs=7)
dim(ax,(0,H+T+0.5),(SCREW_X,H+T+0.5),f'{SCREW_X}',fs=7); dim(ax,(0,H+T+1.1),(L,H+T+1.1),f'{L:.1f}',fs=7)
ax.set_xlim(-3,L+9); ax.set_ylim(-1,H+T+1.6); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Side view, cut through a screw hole (scale about 6:1). Left = carriage end.',fontsize=9)
# front view: y-z, small
ax=fig.add_subplot(gs[:,1]); ax.axis('off')
ax.text(0,1,"""Scraper, compact stage
Two per stage, one at each end
(the same part, turned 180 deg).

Material: iglidur i180 or
PETG with PTFE. No carbon
or glass fibre.

Print flat, ceiling face
on the bed, lips up.
Layer 0.12 to 0.16 mm.
Ironing on the lip tips.

Screws: 5 x M3x10
ISO 14581 (Torx, countersunk),
steel or A2 stainless.
Thread in carriage-top:
M3, tap drill 2.5 mm,
10 mm deep from the
pocket ceiling.

Pocket in carriage-top:
10.0 x 198.0 x 4.5 mm,
open at the end face,
y = 6 to 204 mm.

Gap lip to strip: 0.15 mm
(set with shim foil
between plate and ceiling).""",va='top',fontsize=8.5,family='monospace',transform=ax.transAxes)
fig.tight_layout(); fig.savefig(OUT+'/drawing_scraper.png',dpi=150)
