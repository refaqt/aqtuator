"""Sections along the travel at the end x = 0 of the base."""
from fig_common import *  # noqa: F401,F403

# base2, top, sc, st, pl, sw come from run.py
XL, ZL = (-13.0, 27.0), (8.0, 50.0)


def panel(ax, y, label, show_rollers=False):
    dx = CARRIAGE_END_X[label] - X0
    parts = [(base2, C['base']), (shift(top, dx), C['top']), (shift(sc, dx), C['scraper'])]
    parts += [(p, C['plate']) for p in pl] + [(s, C['screw']) for s in sw]
    for s, c in parts:
        draw(ax, poly(s, (0, y, 0), (0, 1, 0), 0, 2), c)
    g = poly(st, (0, y, 0), (0, 1, 0), 0, 2)
    draw(ax, g, C['strip'], lw=1.2)
    if show_rollers:
        for r in roller_cyls(dx):
            draw(ax, poly(r, (0, y, 0), (0, 1, 0), 0, 2), C['roller'])
            draw(ax, poly(common(r, base2), (0, y, 0), (0, 1, 0), 0, 2), C['clash'])
    ax.axvline(0, color='k', lw=0.6, ls='--')
    ax.set_xlim(*XL); ax.set_ylim(*ZL); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('z [mm]')


fig, axs = plt.subplots(2, 2, figsize=(15, 13))
y_screw = screw_ys(TABS[1])[0]

ax = axs[0, 0]
panel(ax, y_screw, 'usable travel end')
ax.set_title(f'A. Through a clamp screw (y = {y_screw:.1f}), carriage at the end of the usable travel', fontsize=10)
note(ax, 'strip 0.25 mm, flat on the\nend wall: nothing stands\nabove it', (8, 40.25), (12, 30))
note(ax, 'R 3 edge at the\nrecess floor', (3.3, 39.4), (-12.5, 45))
note(ax, 'recess 2.3 mm deep\nin the end face', (1.2, 11), (-12.5, 9.5))
note(ax, 'clamp plate\n2 mm, 1.4301', (0.9, 29), (-12.5, 33))
note(ax, 'M3x8 ISO 14581\nflush', (0.3, SCREW_Z - 1), (-12.5, 19))
note(ax, 'tab bent 90°,\nslot for the screw', (2.15, 34), (-12.5, 38.5))
note(ax, 'scraper lips\n0.15 mm above\nthe strip', (6, 40.6), (14, 46))
note(ax, 'carriage-top', (20, 55), (20, 48))
note(ax, 'base end face x = 0:\nnothing past it, the base\nstays 440 mm long', (0, 14), (12, 14))

ax = axs[0, 1]
panel(ax, y_screw, 'dampers fully pressed')
ax.set_title('B. Same section, dampers fully pressed in (carriage 3 mm past the base end)', fontsize=10)
note(ax, 'carriage-top and scraper pass\nover the clamp: nothing stands\nabove the top of the strip', (-1.5, 40.6), (8, 30))
note(ax, 'chips the scraper pushes\nfall off the end here', (-0.2, 39), (-12.5, 25))

ax = axs[1, 0]
panel(ax, 64.5, 'usable travel end')
ax.set_title('C. Through a damper pocket (y = 64.5): no tab, the strip ends flat on top', fontsize=10)
note(ax, 'strip ends at x = 1\nand covers the\ndamper pocket', (5, 40.2), (12, 30))
note(ax, 'damper pocket\n(no change)', (6, 25), (12, 18))
note(ax, '3 mm wall:\nno recess here', (1.5, 30), (-12.5, 20))

ax = axs[1, 1]
panel(ax, ROLLER_Y[0], 'dampers fully pressed', show_rollers=True)
ax.set_title(f'D. Through a top roller (y = {ROLLER_Y[0]}), dampers fully pressed: the roller hits the end wall',
             fontsize=10)
note(ax, 'roller Ø10 reaches 1 mm\nbelow the wall top (red).\nNot new: the roller sits 1.25 mm\nbelow the strip everywhere.\nRaise the rollers 1.25 mm.', (7, 39.5),
     (10, 24))

for a in axs.flat:
    for name, c in [('base', C['base']), ('carriage-top', C['top']), ('scraper', C['scraper']),
                    ('seal strip', C['strip']), ('clamp plate', C['plate']), ('screw', C['screw'])]:
        a.plot([], [], 's', color=c, mec='k', ms=7, label=name)
axs[1, 1].plot([], [], 's', color=C['roller'], mec='k', ms=7, label='top roller')
axs[1, 1].plot([], [], 's', color=C['clash'], mec='k', ms=7, label='overlap')
axs[0, 0].legend(loc='lower right', fontsize=7)
axs[1, 1].legend(loc='upper right', fontsize=7)
fig.suptitle('Strip end clamp at each base end: sections along the travel (sketch from the CAD geometry)', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'sections_along_travel.png'), dpi=110)
