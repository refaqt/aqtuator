"""The drawing of Niels Bosmans laid over the CAD, at the scale measured on it, with the modelled
insert, groove and magnets. Carriage at the first damper touch, as in the drawing."""
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Circle
from PIL import Image

# OUT, top, bot, shapes come from run.py
IMG = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..',
                                    'docs', 'log', 'images', '2026-10-28-03.png'))
S, X0I, Y0I = 3.44, 265.0, 57.6          # pixels per mm, and the pixel of the base corner
im = Image.open(IMG).convert('RGB')
W, H = im.size
fig, axs = plt.subplots(1, 2, figsize=(16, 9))
for ax, alpha in zip(axs, (0.75, 0.0)):
    if alpha:
        ax.imshow(im, extent=(-X0I / S, (W - X0I) / S, (H - Y0I) / S, -Y0I / S), alpha=alpha)
    d = CARRIAGE_END_X['first damper touch'] - X0
    base2 = shapes['flush']['base2']
    for shp, c, z in [(base2, 'k', 39.95), (base2, '0.45', 38.0)]:
        for sgm in section(shp, (0, 0, z), (0, 0, 1), 24):
            ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color=c, lw=0.8, ls='-' if z > 39 else '--')
    for sgm in section(shift(top, d), (0, 0, 40.6), (0, 0, 1), 24):
        ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color='#2a7a2a', lw=0.8)
    for sgm in section(shift(top, d), (0, 0, 44.0), (0, 0, 1), 24):
        ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color='#2a7a2a', lw=0.6, ls=':')
    draw(ax, poly(strip(), (0, 0, Z_WALL + T / 2), (0, 0, 1), 0, 1), (0.2, 0.8, 0.9, 0.25), lw=0.8)
    draw(ax, poly(shapes['flush']['insert'], (0, 0, Z_WALL - 0.5), (0, 0, 1), 0, 1), C['insert'])
    ax.add_patch(Circle((XC, YC), DK / 2, fc=C['screw'], ec='k', lw=0.6))
    for x, y in MAGNETS:
        ax.add_patch(Circle((x, y), MAG_D / 2, fc=C['magnet'], ec='k', lw=0.6, alpha=0.8))
    ax.set_xlim(-3, 45); ax.set_ylim(95, -3); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('x from the base end [mm]'); ax.set_ylabel('y from the base side [mm]')
axs[0].set_title('A. The drawing laid over the CAD (3.44 pixels per mm).\nBlack: base top. Green: carriage-top at the first damper touch.', fontsize=10)
axs[1].set_title('B. The modelled parts: strip (blue), insert and groove (dashed),\nscrew head, magnets (Ø6 assumed)', fontsize=10)
ax = axs[1]
note(ax, 'insert Ø7.5, flats 6 mm apart,\nscrew M2.5 countersunk', (XC + 2, YC + 2), (18, 28))
note(ax, 'groove 6.1 mm wide, milled\nfrom the top; 0.75 mm wall to\nthe half-round pocket', (15, 16.3), (24, 8))
note(ax, 'strip ear, out to 6.5 mm\nfrom the base side', (8, 7.2), (14, 1.5))
note(ax, 'magnets in pockets', (5.8, 42), (14, 46))
note(ax, 'damper pocket', (6, 64), (14, 64))
note(ax, 'half-round pocket', (8, 26), (14, 36))
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'overlay.png'), dpi=110)
