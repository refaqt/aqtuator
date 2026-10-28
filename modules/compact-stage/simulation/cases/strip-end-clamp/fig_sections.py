"""Sections along the travel at the end x = 0 of the base."""
from fig_common import *  # noqa: F401,F403

# base2, top, sc, st, br, pn, sw come from run.py
XL, ZL = (-13.0, 27.0), (16.0, 50.0)


def panel(ax, y, label, show_rollers=False):
    dx = CARRIAGE_END_X[label] - X0
    parts = [(base2, C['base']), (shift(top, dx), C['top']), (shift(sc, dx), C['scraper'])]
    parts += [(b, C['bar']) for b in br] + [(p, C['pin']) for p in pn] + [(s, C['screw']) for s in sw]
    for s, c in parts:
        draw(ax, poly(s, (0, y, 0), (0, 1, 0), 0, 2), c)
    draw(ax, poly(st, (0, y, 0), (0, 1, 0), 0, 2), C['strip'], lw=1.2)
    if show_rollers:
        for r in roller_cyls(dx):
            draw(ax, poly(r, (0, y, 0), (0, 1, 0), 0, 2), C['roller'])
            draw(ax, poly(common(r, base2), (0, y, 0), (0, 1, 0), 0, 2), C['clash'])
    ax.axvline(0, color='k', lw=0.6, ls='--')
    ax.set_xlim(*XL); ax.set_ylim(*ZL); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('z [mm]')


mid = STEPS[1]
y_pin, y_screw = pin_ys(mid)[1], screw_ys(mid)[0]
fig, axs = plt.subplots(2, 2, figsize=(15, 12))

ax = axs[0, 0]
panel(ax, y_pin, 'usable travel end')
ax.set_title(f'A. Through a pin (y = {y_pin:.0f}), carriage at the end of the usable travel', fontsize=10)
note(ax, 'strip flat on the end wall:\nnothing stands above it', (12, 40.25), (13, 31))
note(ax, 'R 3 edge on the wall top', (8.2, 39.6), (-12.5, 47))
note(ax, 'step milled from the top,\n7 mm long, 16 mm deep,\nopen to the end face', (1, 26), (-12.5, 19))
note(ax, 'bar, aluminium', (2, 33.5), (-12.5, 37))
note(ax, 'tab hangs on a\nØ2 pin in the bar', (6.3, PIN_Z), (13, 23))
note(ax, 'scraper lips 0.15 mm\nabove the strip', (6, 40.6), (13, 46))
note(ax, 'base end face x = 0:\nnothing past it', (0, 18), (-12.5, 29))

ax = axs[0, 1]
panel(ax, y_screw, 'dampers fully pressed')
ax.set_title(f'B. Through a screw (y = {y_screw:.0f}), dampers fully pressed in (carriage 3 mm past the base end)',
             fontsize=10)
note(ax, 'M3 x 16 from the top,\nwith a locking patch.\nTurn it to set the pull', (SCREW_X, 37), (-12.5, 45))
note(ax, 'vertical tapped hole\nin the step floor', (SCREW_X, 20), (8, 18))
note(ax, 'bar moves 4 mm down\nand 2 mm up', (1, BAR_Z[0]), (-12.5, 22))
note(ax, 'carriage-top and scraper\npass over: nothing above\nthe top of the base', (-1, 40.6), (12, 31))

ax = axs[1, 0]
panel(ax, 64.5, 'usable travel end')
ax.set_title('C. Through a damper pocket (y = 64.5): no step, the strip ends flat on top', fontsize=10)
note(ax, 'strip ends at x = 1\nand covers the\ndamper pocket', (5, 40.2), (12, 31))
note(ax, 'damper pocket\n(no change)', (6, 25), (12, 20))
note(ax, '3 mm wall:\nno change', (1.5, 30), (-12.5, 22))

ax = axs[1, 1]
panel(ax, ROLLER_Y[0], 'dampers fully pressed', show_rollers=True)
ax.set_title(f'D. Through a top roller (y = {ROLLER_Y[0]}), dampers fully pressed: the roller hits the end wall',
             fontsize=10)
note(ax, 'roller Ø10 reaches 1 mm\nbelow the wall top (red).\nNot caused by the clamp:\nthe roller sits 1.25 mm below\nthe strip everywhere.\nRaise the rollers 1.25 mm.',
     (8.5, 39.5), (11, 19))

for a in (axs[0, 0], axs[1, 1]):
    for name, c in [('base', C['base']), ('carriage-top', C['top']), ('scraper', C['scraper']),
                    ('seal strip', C['strip']), ('bar', C['bar']), ('pin', C['pin']), ('screw', C['screw'])]:
        a.plot([], [], 's', color=c, mec='k', ms=7, label=name)
axs[1, 1].plot([], [], 's', color=C['roller'], mec='k', ms=7, label='top roller')
axs[1, 1].plot([], [], 's', color=C['clash'], mec='k', ms=7, label='overlap')
axs[0, 0].legend(loc='lower right', fontsize=7)
axs[1, 1].legend(loc='upper right', fontsize=7)
fig.suptitle('Strip end clamp, version 2: everything from the top. Sections along the travel (from the CAD geometry)',
             fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'sections_along_travel.png'), dpi=110)
