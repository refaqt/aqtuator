"""Top view of the base end at x = 0, with the strip lifted away, and with the strip fitted."""
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Circle

# base2, st, br, pn, sw come from run.py
fig, axs = plt.subplots(1, 2, figsize=(15, 9.5))
for ax, with_strip in zip(axs, (False, True)):
    for s in section(base2, (0, 0, 30), (0, 0, 1), 24):          # pockets below the top, dashed
        ax.plot([p[0] for p in s], [p[1] for p in s], color='0.45', lw=0.6, ls='--')
    draw(ax, poly(base2, (0, 0, 39.9), (0, 0, 1), 0, 1), C['base'])
    for b in br:
        draw(ax, poly(b, (0, 0, BAR_Z[1] - 0.1), (0, 0, 1), 0, 1), C['bar'])
    for s in STEPS:
        for y in screw_ys(s):
            ax.add_patch(Circle((SCREW_X, y), HEAD_D / 2, fc=C['screw'], ec='k', lw=0.6))
    if with_strip:
        draw(ax, poly(st, (0, 0, Z_WALL + T / 2), (0, 0, 1), 0, 1), '#5a5a5a')
        for s in STEPS:
            a, b = tab_y(s)
            ax.fill_between([STEP_X - T, STEP_X + EDGE_R], a, b, color=C['strip'])
    else:
        for s in STEPS:
            a, b = tab_y(s)
            ax.fill_between([STEP_X - T, STEP_X], a, b, color=C['strip'])
            for y in pin_ys(s):
                ax.plot([STEP_X - 0.6, STEP_X], [y, y], color=C['pin'], lw=3)
    ax.axvline(0, color='k', lw=0.6, ls='--')
    ax.set_xlim(-14, 30); ax.set_ylim(-2, 212); ax.set_aspect('equal'); ax.grid(alpha=.2)
    ax.set_xlabel('x along the travel [mm]'); ax.set_ylabel('y across [mm]')
ax = axs[0]
ax.set_title('A. Base end from above, strip tabs shown in place,\nflat strip left out', fontsize=10)
s = STEPS[1]
note(ax, 'bar with 3 pins', (1, 105), (-13.5, 110))
note(ax, 'screw M3,\nfrom the top', (SCREW_X, screw_ys(s)[0]), (-13.5, 88))
note(ax, 'tab on the wall face', (STEP_X, 120), (12, 125))
note(ax, 'damper pocket\n(dashed: below the top)', (6, 64.5), (12, 64))
note(ax, 'half-round pocket', (6, 23), (12, 14))
for st_ in STEPS:
    note(ax, f'step {st_[1] - st_[0]:.1f} mm wide', (6, (st_[0] + st_[1]) / 2 + 4), (12, (st_[0] + st_[1]) / 2 + 2))
note(ax, 'R 3 edge on the wall top', (8.5, 128), (12, 140))
ax = axs[1]
ax.set_title('B. With the strip fitted (grey). The bars and screws stay open\nfrom the top: move the carriage away to reach them',
             fontsize=10)
note(ax, 'strip ends at x = 1\nbeside the steps', (1.2, 64.5), (-13.5, 75))
note(ax, 'cut beside each tab,\nends in a Ø1.5 hole', (RELIEF_X, tab_y(STEPS[1])[0]), (14, 70))
note(ax, 'chips the scraper pushes\nfall out of the open steps', (0.5, 40), (-13.5, 20))
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'top_view.png'), dpi=110)
