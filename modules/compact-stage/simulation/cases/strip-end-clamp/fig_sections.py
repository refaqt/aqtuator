"""Sections along the travel through the insert (y = 105), and a detail of the insert."""
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Rectangle

# base2, top, top_long, sc, parts come from run.py
Y = Y_C


def draw_parts(ax, d, top_shape, clash=True):
    t, s = shift(top_shape, d), shift(sc, d)
    for shp, c in [(base2, C['base']), (t, C['top']), (s, C['scraper']), (parts['nut'], C['nut']),
                   (parts['insert'], C['insert']), (parts['screw'], C['screw'])]:
        draw(ax, poly(shp, (0, Y, 0), (0, 1, 0), 0, 2), c)
    draw(ax, poly(parts['strip'], (0, Y, 0), (0, 1, 0), 0, 2), C['strip'], lw=1.2)
    if clash:
        for a in (t, s):
            for b in (parts['insert'], parts['screw']):
                draw(ax, poly(common(a, b), (0, Y, 0), (0, 1, 0), 0, 2), C['clash'])
    ax.axvline(0, color='k', lw=0.6, ls='--')
    ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('z [mm]')


fig, axs = plt.subplots(2, 2, figsize=(16, 11.5))
ax = axs[0, 0]
draw_parts(ax, CARRIAGE_END_X['first damper touch'] - X0, top)
ax.set_xlim(-6, 24); ax.set_ylim(34, 50)
ax.set_title('A. Through the insert (y = 105), carriage at the first damper touch.\nThe lips step back behind the insert.',
             fontsize=10)
note(ax, 'insert, flange Ø9 x 1 mm\non top of the strip', (6, Z_STRIP + 0.8), (-5.5, 47.5))
note(ax, 'M2.5 countersunk screw,\nstraight down', (screw_x(), 39), (13, 36))
note(ax, 'square nut in a groove\nmilled from the top', (3, 38.5), (-5.5, 35))
note(ax, 'lips stepped back', (X0 + LIP_BACK[0][0] + CARRIAGE_END_X['first damper touch'] - X0 + 0.5, 40.5), (12, 46))
note(ax, 'strip 0.15 mm', (16, Z_STRIP), (17, 42.5))

ax = axs[0, 1]
d = CARRIAGE_END_X['dampers fully pressed'] - X0
draw_parts(ax, d, top)
lp = poly(shift(long_pocket_cut(), d), (0, Y, 0), (0, 1, 0), 0, 2)
for g in getattr(lp, 'geoms', [lp]):
    xs, zs = g.exterior.xy
    ax.plot(xs, zs, 'k--', lw=0.8)
ax.set_xlim(-6, 24); ax.set_ylim(34, 50)
ax.set_title('B. Same section, dampers fully pressed in (a crash).\nRed: carriage-top and scraper lips hit the insert.',
             fontsize=10)
note(ax, f'longer pocket in carriage-top\n(dashed, {POCKET_LONG:.0f} mm) clears it', (10, 44.5), (11, 47.5))
note(ax, 'the printed lips would hit\nthe flange in a crash', (4, 40.8), (8, 36))

ax = axs[1, 0]
xs = screw_x()
for shp, c in [(base2, C['base']), (parts['nut'], C['nut']), (parts['insert'], C['insert']), (parts['screw'], C['screw'])]:
    draw(ax, poly(shp, (0, Y, 0), (0, 1, 0), 0, 2), c)
draw(ax, poly(parts['strip'], (0, Y, 0), (0, 1, 0), 0, 2), C['strip'], lw=1.2)
loose_ins = poly(insert(TRAVEL), (0, Y, 0), (0, 1, 0), 0, 2)
for g in getattr(loose_ins, 'geoms', [loose_ins]):
    x_, z_ = g.exterior.xy
    ax.plot(x_, z_, color=C['insert'], lw=1.2, ls='--')
ax.axvline(X_C, color='k', lw=0.5, ls=':')
ax.axvline(xs, color=C['screw'], lw=0.5, ls=':')
ax.set_xlim(-1, 12); ax.set_ylim(35.5, 42.5); ax.set_aspect('equal'); ax.grid(alpha=.25)
ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('z [mm]')
ax.set_title(f'C. The insert, enlarged. Insert axis x = {X_C}, screw axis x = {xs:.1f}.\n'
             f'Dashed: the insert before the screw pulls ({TRAVEL} mm further in)', fontsize=10)
note(ax, f'countersink {ECC} mm off the insert axis.\nInserts made with other offsets\ntune the pull',
     (xs - 1.5, Z_STRIP + 0.7), (6.5, 41.6))
note(ax, 'M6 x 0.5 thread clamps the strip\nbetween flange and nut', (X_C - 3, Z_WALL), (-0.8, 36.0))
note(ax, 'groove floor; nut floats\n0.2 mm above it', (8.5, GROOVE_FLOOR), (8.0, 36.0))

ax = axs[1, 1]
ax.axis('off')
txt = (
    'How it works\n'
    '  1. Before fitting, clamp each strip end between an insert and its nut.\n'
    '  2. Lay the strip. Drop each nut into its groove: the flat sides stop it from turning.\n'
    '  3. Put in the countersunk screw. Its hole in the base is a little nearer the stage middle\n'
    '      than the countersink. As the head goes down, its cone pulls the insert, and the strip,\n'
    f'      towards the base end until the countersink is centred: {TRAVEL} mm at each end.\n\n'
    'What the base needs (all from the top)\n'
    f'  A groove {GROOVE_W} mm wide, {Z_WALL - GROOVE_FLOOR:.1f} mm deep, from x = {GROOVE_X0} mm to the inside face.\n'
    '  One M2.5 tapped hole, drilled straight down into its floor.\n\n'
    'What the carriage needs\n'
    '  The scraper lips step back to 6.5 mm behind the carriage end, 14 mm wide around the insert.\n'
    '  For a crash, a longer pocket in carriage-top at the insert (15 mm instead of 10 mm),\n'
    '  and the lips moved back into it. Without that, a full crash breaks the printed lips.\n\n'
    'What stays visible\n'
    '  Only the screw head and the flange. No pocket is open: the strip and the flange cover the\n'
    '  groove, so chips cannot fall in, and users cannot reach the mechanism.')
ax.text(0, 1, txt, va='top', fontsize=9.5, transform=ax.transAxes)
for a in (axs[0, 0],):
    for name, c in [('base', C['base']), ('carriage-top', C['top']), ('scraper', C['scraper']),
                    ('seal strip 0.15 mm', C['strip']), ('insert', C['insert']), ('nut', C['nut']),
                    ('screw', C['screw']), ('overlap', C['clash'])]:
        a.plot([], [], 's', color=c, mec='k', ms=7, label=name)
    a.legend(loc='lower right', fontsize=7)
fig.suptitle('Strip end clamp, version 3: an insert pulled by a countersunk screw (from the CAD geometry)', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'sections_insert.png'), dpi=110)
