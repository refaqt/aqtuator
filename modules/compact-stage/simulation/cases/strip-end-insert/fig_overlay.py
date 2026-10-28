"""The drawing of Niels Bosmans laid over the CAD, at the scale measured on it, with the modelled
parts of the fixed end. Carriage at the first damper touch, as in the drawing."""
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Circle, Rectangle
from PIL import Image

# OUT, top_st, sc_st, base_fixed, parts come from run.py
IMG = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..',
                                    'docs', 'log', 'images', '2026-10-28-03.png'))
S, X0I, Y0I = 3.44, 265.0, 57.6          # pixels per mm, and the pixel of the base corner
im = Image.open(IMG).convert('RGB')
W, H = im.size
d = CARRIAGE_END_X['first damper touch'] - X0
fig, axs = plt.subplots(1, 2, figsize=(16, 9))
for ax, show_img in zip(axs, (True, False)):
    if show_img:
        ax.imshow(im, extent=(-X0I / S, (W - X0I) / S, (H - Y0I) / S, -Y0I / S), alpha=0.75)
    for sgm in section(base_fixed, (0, 0, 39.95), (0, 0, 1), 24):
        ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color='k', lw=0.8)
    for sgm in section(base_fixed, (0, 0, 38.0), (0, 0, 1), 24):
        ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color='0.45', lw=0.6, ls='--')
    for sgm in section(shift(top_st, d), (0, 0, 40.6), (0, 0, 1), 24):
        ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color='#2a7a2a', lw=0.8)
    draw(ax, poly(strip(), (0, 0, Z_WALL + T / 2), (0, 0, 1), 0, 1), (0.2, 0.8, 0.9, 0.25), lw=0.8)
    draw(ax, poly(shift(sc_st, d), (0, 0, Z_TIP + 0.05), (0, 0, 1), 0, 1), (0.91, 0.51, 0.23, 0.6), lw=0.6)
    draw(ax, poly(parts['insert'], (0, 0, Z_WALL - 0.2), (0, 0, 1), 0, 1), C['insert'])
    ax.add_patch(Circle((XC, YC), DK / 2, fc=C['screw'], ec='k', lw=0.6))
    for x, y in MAGNETS:
        ax.add_patch(Circle((x, y), MAG_D / 2, fc=C['magnet'], ec='k', lw=0.6, alpha=0.8))
    ax.add_patch(Circle((11.6, 13.2), 3.75, fc='none', ec='k', lw=1.0, ls='--'))
    ax.set_xlim(-3, 45); ax.set_ylim(95, -3); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('x from the base end [mm]'); ax.set_ylabel('y from the base side [mm]')
axs[0].set_title('A. The drawing laid over the CAD (3.44 pixels per mm).\nBlack: base top. Green: carriage-top at the first damper touch.', fontsize=10)
axs[1].set_title('B. The modelled fixed end: strip (blue), insert and screw, stepped\nscraper lips (orange), magnets. Dashed circle: insert as drawn.', fontsize=10)
ax = axs[1]
note(ax, f'insert Ø{INS_D:g}, M2 countersunk screw,\nmoved over the strip ear', (XC + 1.5, YC + 1.5), (18, 4))
note(ax, 'insert as drawn (Ø7.5)', (13, 16.5), (18, 22))
note(ax, 'scraper lip behind the insert', (X0 + LIP_BACK_X + d + 0.5, 7), (26, 12))
note(ax, 'strip rises towards the carriage\nslope here: no lip possible', (20, 14), (26, 30))
note(ax, 'magnets in pockets', (5.8, 42), (14, 46))
note(ax, 'damper pocket', (6, 64), (14, 64))
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'overlay.png'), dpi=110)
