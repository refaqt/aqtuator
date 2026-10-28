"""Top view of the base end at x = 0 with the insert, and the scraper lips seen from below."""
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Circle, Rectangle

# base2, sc, parts come from run.py
fig, axs = plt.subplots(1, 2, figsize=(15, 8.5))
ax = axs[0]
for s in section(base2, (0, 0, 38.5), (0, 0, 1), 24):            # groove and pockets, dashed
    ax.plot([p[0] for p in s], [p[1] for p in s], color='0.45', lw=0.6, ls='--')
draw(ax, poly(base2, (0, 0, 39.95), (0, 0, 1), 0, 1), C['base'])
draw(ax, poly(parts['strip'], (0, 0, Z_WALL + T / 2), (0, 0, 1), 0, 1), '#5a5a5a')
draw(ax, poly(parts['insert'], (0, 0, Z_STRIP + 0.5), (0, 0, 1), 0, 1), C['insert'])
ax.add_patch(Circle((screw_x(), Y_C), DK / 2, fc=C['screw'], ec='k', lw=0.6))
for y in ROLLER_Y:                                               # top roller lanes
    ax.add_patch(Rectangle((-3, y - ROLLER_L / 2), 33, ROLLER_L, fc='none', ec=C['roller'], ls=':', lw=1))
ax.axvline(0, color='k', lw=0.6, ls='--')
ax.set_xlim(-14, 30); ax.set_ylim(-2, 212); ax.set_aspect('equal'); ax.grid(alpha=.2)
ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('y across [mm]')
ax.set_title('A. Base end from above with the strip fitted (grey).\nOne insert on the centre line', fontsize=10)
note(ax, 'insert flange Ø9 and\nM2.5 screw head', (5, Y_C + 3), (-13.5, 125))
note(ax, 'groove under the strip\n(dashed)', (8.5, Y_C - 4), (-13.5, 85))
note(ax, 'top roller lanes (dotted):\nno insert there', (10, ROLLER_Y[0]), (12, 12))
note(ax, 'damper pocket (dashed)', (6, 64.5), (12, 64))
note(ax, 'pull spreads from one\ninsert into a 186 mm strip', (14, 150), (12, 150))

ax = axs[1]
draw(ax, poly(sc, (0, 0, Z_TIP + 0.05), (0, 0, 1), 0, 1), C['scraper'])
ax.set_xlim(X0 - 3, X0 + 18); ax.set_ylim(80, 130); ax.set_aspect('equal'); ax.grid(alpha=.2)
ax.set_xlabel('x from the carriage-top end face [mm]'); ax.set_ylabel('y across [mm]')
ax.set_xticks([X0 + v for v in range(0, 18, 2)]); ax.set_xticklabels([str(v) for v in range(0, 18, 2)])
ax.set_title('B. Scraper lips seen from below, near the insert.\nThey step back 6.5 mm over 14 mm of width', fontsize=10)
note(ax, 'lips at the carriage end', (X0 + 1.5, 90), (X0 + 4, 84))
note(ax, 'lips stepped back', (X0 + 7, Y_C), (X0 + 11, 112))
note(ax, 'side lips close the step', (X0 + 4, NOTCH_Y[0] - 0.5), (X0 + 11, 92))
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'top_view.png'), dpi=110)
