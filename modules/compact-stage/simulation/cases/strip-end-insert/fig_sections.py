"""Sections along the travel through the insert (y = YC), for both insert heights."""
from fig_common import *  # noqa: F401,F403

# OUT, top, bot, sc, shapes come from run.py
fig, axs = plt.subplots(2, 3, figsize=(18, 9.5))
for row, variant in enumerate(VARIANTS):
    sh = shapes[variant]
    for col, (label, xe) in enumerate(CARRIAGE_END_X.items()):
        ax = axs[row, col]
        d = xe - X0
        t, s, b = shift(top, d), shift(sc, d), shift(bot, d)
        for shp, c in [(sh['base2'], C['base']), (t, C['top']), (b, C['bot']), (s, C['scraper']),
                       (sh['insert'], C['insert']), (sh['screw'], C['screw'])]:
            draw(ax, poly(shp, (0, YC, 0), (0, 1, 0), 0, 2), c)
        draw(ax, poly(strip(), (0, YC, 0), (0, 1, 0), 0, 2), C['strip'], lw=1.0)
        for a in (t, s, b):
            for p in (sh['insert'], sh['screw']):
                draw(ax, poly(common(a, p), (0, YC, 0), (0, 1, 0), 0, 2), C['clash'])
        ax.axvline(0, color='k', lw=0.6, ls='--')
        ax.set_xlim(-4, 24); ax.set_ylim(36.5, 46); ax.set_aspect('equal'); ax.grid(alpha=.25)
        ax.set_title(f'{variant}: {label}\n(carriage-top end face at x = {xe:g} mm)', fontsize=10)
        ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('z [mm]')
axs[0, 0].set_ylabel('AS DRAWN, insert 1.05 mm proud\nz [mm]')
axs[1, 0].set_ylabel('FLUSH, insert top = strip top\nz [mm]')
note(axs[0, 0], 'red: carriage-top and\nscraper lips hit the insert', (12.5, 40.9), (14, 37.2))
note(axs[1, 0], 'insert sunk in a 1.55 mm groove;\nthe lips pass 0.15 mm over it', (11.6, 40.1), (12.5, 37.2))
for name, c in [('base', C['base']), ('carriage-top', C['top']), ('carriage-bottom', C['bot']), ('scraper', C['scraper']),
                ('seal strip 0.15 mm', C['strip']), ('insert', C['insert']), ('screw M2.5', C['screw']), ('overlap', C['clash'])]:
    axs[0, 2].plot([], [], 's', color=c, mec='k', ms=7, label=name)
axs[0, 2].legend(loc='upper right', fontsize=7)
fig.suptitle(f'Sections through the insert (y = {YC} mm), at the end of the usable travel, at the first damper touch and '
             'in a crash. From the CAD geometry.', fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'sections_insert.png'), dpi=110)
