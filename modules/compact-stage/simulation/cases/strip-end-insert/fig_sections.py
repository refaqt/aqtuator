"""Sections along the travel through the insert at the fixed end (y = YC)."""
from fig_common import *  # noqa: F401,F403

# OUT, top, tops, top_st, sc, sc_st, sw, bot, base_fixed, parts come from run.py
fig, axs = plt.subplots(2, 2, figsize=(16, 9.5))
cases = [
    (axs[0, 0], 'first damper touch', top, sc, 'A. Carriage-top and scraper as they are:\nthey pass over the insert (red)'),
    (axs[0, 1], 'first damper touch', top_st, sc_st, 'B. With the corner pockets and the stepped scraper:\nall clear (0.3 mm or more)'),
    (axs[1, 0], 'usable travel end', top_st, sc_st, 'C. Same, at the end of the usable travel'),
    (axs[1, 1], 'dampers fully pressed', top_st, sc_st, 'D. Same, in a crash: the stepped lip hits the insert.\nA 19.5 mm corner pocket and a softer lip would avoid that'),
]
for ax, label, t, s, title in cases:
    d = CARRIAGE_END_X[label] - X0
    t, s, b = shift(t, d), shift(s, d), shift(bot, d)
    for shp, c in [(base_fixed, C['base']), (t, C['top']), (b, C['bot']), (s, C['scraper']),
                   (parts['insert'], C['insert']), (parts['screw'], C['screw'])]:
        draw(ax, poly(shp, (0, YC, 0), (0, 1, 0), 0, 2), c)
    draw(ax, poly(strip(), (0, YC, 0), (0, 1, 0), 0, 2), C['strip'], lw=1.0)
    for a in (t, s):
        draw(ax, poly(common(a, sw), (0, YC, 0), (0, 1, 0), 0, 2), C['clash'])
    sx = poly(sw, (0, YC, 0), (0, 1, 0), 0, 2)
    for g in getattr(sx, 'geoms', [sx]):
        xs_, zs_ = g.exterior.xy
        ax.plot(xs_, zs_, color='0.3', lw=0.6, ls=':')
    ax.axvline(0, color='k', lw=0.6, ls='--')
    ax.set_xlim(-4, 24); ax.set_ylim(37.5, 46); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_title(f'{title}\n(carriage-top end face at x = {CARRIAGE_END_X[label]:g} mm, {label})', fontsize=9.5)
    ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('z [mm]')
note(axs[0, 1], f'corner pocket {CORNER_DEPTH:g} mm deep in carriage-top', (14.5, 41.4), (14, 45.3))
note(axs[0, 1], 'scraper lip behind the insert', (X0 + LIP_BACK_X + CARRIAGE_END_X['first damper touch'] - X0 + 0.5, 40.6),
     (16, 38.2))
note(axs[0, 1], f'insert Ø{INS_D:g}, {Z_WALL - GROOVE_D + INS_H - Z_STRIP:.2f} mm above the strip', (XC + 1.5, 40.7), (-3.5, 38.2))
note(axs[0, 0], 'dotted: the path of the insert\nrelative to the carriage', (2, 40.5), (-3.5, 44.8))
for name, c in [('base', C['base']), ('carriage-top', C['top']), ('carriage-bottom', C['bot']), ('scraper', C['scraper']),
                ('seal strip 0.15 mm', C['strip']), ('insert', C['insert']), ('screw M2', C['screw']), ('overlap', C['clash'])]:
    axs[1, 1].plot([], [], 's', color=c, mec='k', ms=7, label=name)
axs[1, 1].legend(loc='lower right', fontsize=7)
fig.suptitle(f'Fixed end: sections through the insert (y = {YC} mm), from the CAD geometry', fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'sections_insert.png'), dpi=110)
