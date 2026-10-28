"""End view: the end face x = 0 of the base, seen from outside, with the three clamps."""
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Circle

# base2, st, pl, sw come from run.py
fig, ax = plt.subplots(figsize=(15, 5.6))
# hidden: the pockets behind the face (section 5 mm in), dashed
for s in section(base2, (5, 0, 0), (1, 0, 0), 24):
    ax.plot([p[1] for p in s], [p[2] for p in s], color='0.45', lw=0.6, ls='--')
draw(ax, poly(base2, (0.01, 0, 0), (1, 0, 0), 1, 2), C['base'])
draw(ax, poly(base2, (2.31, 0, 0), (1, 0, 0), 1, 2), '#aeb4bd')     # recess floors
draw(ax, poly(st, (REC_D - T / 2, 0, 0), (1, 0, 0), 1, 2), C['strip'])  # the tabs
for a, b in TABS:                                                   # the bend, seen end on
    ax.fill_between([a, b], Z_WALL - EDGE_R - 0.1, Z_WALL + T, color=C['strip'])
for p in pl:
    draw(ax, poly(p, (REC_D - T - 0.5, 0, 0), (1, 0, 0), 1, 2), C['plate'])
for tab in TABS:
    for y in screw_ys(tab):
        ax.add_patch(Circle((y, SCREW_Z), 2.75, fc=C['screw'], ec='k', lw=0.6))
ax.fill_between([STRIP_Y[0], STRIP_Y[1]], Z_WALL, Z_WALL + 0.9, color=C['strip'])
ax.set_xlim(-3, 213); ax.set_ylim(-2, 47); ax.set_aspect('equal'); ax.grid(alpha=.2)
ax.set_xlabel('y across the stage [mm]'); ax.set_ylabel('z [mm]')
note(ax, 'strip on top (drawn thicker)', (100, 40.5), (95, 45))
note(ax, 'clamp plate', (105, 29), (95, 5))
note(ax, 'tab with pull hole,\nbelow the plate', ((TABS[1][0] + TABS[1][1]) / 2, PULL_HOLE_Z), (60, 3))
note(ax, 'recess 2.3 mm deep', (TABS[0][0] + 1, 12), (2, 3))
note(ax, 'damper pocket\n(dashed: behind the face)', (64.5, 20), (52, 28))
note(ax, 'half-round pocket:\nwall only 4 mm', (23, 34), (0, 43))
for tab in TABS:
    a, b = recess_y(tab)
    ax.annotate('', xy=(a, 8.6), xytext=(b, 8.6), arrowprops=dict(arrowstyle='<->', lw=0.6))
    ax.text((a + b) / 2, 7.2, f'{b - a:.0f}', ha='center', fontsize=8)
ax.set_title('End face of the base, seen from outside (x = 0). Three tabs and three clamp plates sit where the end wall '
             'is 10 mm thick.', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'end_view.png'), dpi=110)
