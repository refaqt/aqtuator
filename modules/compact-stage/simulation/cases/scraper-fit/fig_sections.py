import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','results','scraper-fit')
os.makedirs(OUT,exist_ok=True)
from render import *
# 1) Section at y = 105 (plane across the width): x-z view, through the middle screw
fig,axs=plt.subplots(2,1,figsize=(11,9))
sec_plot(axs[0],(0,105,0),(0,1,0),0,2,(100,160),(36,62),'Section A-A at y = 105 mm (centre of the carriage, through the middle screw), side view x-z. The strip is drawn flat; in reality it climbs the slope of carriage-bottom.')
sec_plot(axs[1],(0,105,0),(0,1,0),0,2,(104.5,120.5),(39.6,46.0),'Section A-A, detail: lips, gap and screw')
a=axs[1]
kw=dict(arrowprops=dict(arrowstyle='->',lw=.7),fontsize=8)
a.annotate('end face of\ncarriage-top',(106.6,43.5),(104.7,44.6),**kw)
a.annotate('lip 1: chip lip\n1.0 mm thick',(107.1,40.7),(104.7,41.6),**kw)
a.annotate('groove\n1.0 mm',(108.5,41.3),(108.0,42.6),**kw)
a.annotate('lip 2',(109.3,40.9),(110.0,40.95),**kw)
a.annotate('gap 0.15 mm',(109.0,40.32),(110.6,39.75),**kw)
a.annotate('screw head 1.55 mm\nabove the strip',(113,41.8),(111.6,40.75),**kw)
a.annotate('pocket in carriage-top:\n10 mm long, 4.5 mm deep',(110.6,45.0),(115.2,45.55),**kw)
a.annotate('aluminium wall 2.2 mm\nto the slope opening',(117.7,40.6),(117.6,41.9),**kw)
a.text(104.7,40.05,'strip, simplified flat (z = 40 to 40.25)',fontsize=7,color='w')
a.set_xlabel('x [mm] (travel direction)'); a.set_ylabel('z [mm]')
axs[0].legend(loc='upper right',fontsize=8)
fig.tight_layout(); fig.savefig(OUT+'/section-A-A_y105.png',dpi=150)

# 2) Section at x = X0+0.5 (through lip 1) and x = X0+6.5 (through screws): y-z view
fig,axs=plt.subplots(3,1,figsize=(13,9))
sec_plot(axs[0],(X0+6.5,0,0),(1,0,0),1,2,(-2,212),(36,62),'Section B-B at x = 6.5 mm from the end face (through the five screws), front view y-z')
sec_plot(axs[1],(X0+6.5,0,0),(1,0,0),1,2,(0,30),(39.6,47),'Section B-B, detail at the side: base wall, strip edge, scraper, screw')
sec_plot(axs[2],(X0+0.5,0,0),(1,0,0),1,2,(0,30),(39.6,47),'Section C-C at x = 0.5 mm from the end face (through lip 1), detail at the side')
for a in axs: a.set_xlabel('y [mm] (across the stage)'); a.set_ylabel('z [mm]')
axs[1].annotate('strip edge (strip 186 mm wide assumed)',(12,40.25),(18,40.9),arrowprops=dict(arrowstyle='->'),fontsize=8)
axs[0].legend(loc='upper center',bbox_to_anchor=(0.5,-0.32),fontsize=8,ncol=5)
fig.tight_layout(); fig.savefig(OUT+'/section-B-B_C-C_x.png',dpi=150)

# 3) Section at y = 34.5 (through a top roller): x-z view
fig,axs=plt.subplots(2,1,figsize=(11,9))
y=ROLLER_Y[0]
sec_plot(axs[0],(0,y,0),(0,1,0),0,2,(100,160),(36,62),f'Section D-D at y = {y} mm (through a top roller), side view x-z. The strip is drawn flat; the roller presses it down.')
sec_plot(axs[1],(0,y,0),(0,1,0),0,2,(104.5,125.5),(38.4,50),'Section D-D, detail: the scraper is shorter here and keeps 0.77 mm to the roller')
a=axs[1]; kw=dict(arrowprops=dict(arrowstyle='->',lw=.7),fontsize=8)
a.annotate('roller pocket in carriage-top',(124,49),(119.8,49.3),**kw)
a.annotate('roller bottom z = 39.0 mm:\n1.5 mm below carriage-top,\n1.0 mm below the base top',(118.77,39.0),(119.6,46.6),**kw)
a.annotate('scraper ends 6.4 mm\nfrom the end face',(113.0,43),(107.3,46.6),**kw)
a.set_xlabel('x [mm] (travel direction)'); a.set_ylabel('z [mm]')
axs[0].legend(loc='upper right',fontsize=8)
fig.tight_layout(); fig.savefig(OUT+'/section-D-D_y34.5_roller.png',dpi=150)
