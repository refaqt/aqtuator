"""Flat shape of the strip end, before bending, and how the pull is set at fitting."""
import math
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon as MPoly

BEND = (EDGE_R + T / 2) * math.pi / 2      # length of the bend, on the middle of the strip
XB = REC_D + EDGE_R                        # bend starts here, on top
ZC = Z_WALL - EDGE_R


def u(z):
    """Position along the flat strip of a point at height z on the bent tab."""
    return XB - BEND - (ZC - z)


fig, (ax, bx) = plt.subplots(1, 2, figsize=(16, 7.5), gridspec_kw=dict(width_ratios=[1.35, 1]))
# flat strip, x along the strip, y across
x_end = u(TAB_Z_END)
pts = [(60, STRIP_Y[0]), (60, STRIP_Y[1])]
ax.add_patch(Rectangle((FLAT_END_X, STRIP_Y[0]), 60 - FLAT_END_X, STRIP_Y[1] - STRIP_Y[0], fc='#dddddd', ec='k', lw=0.7))
for a, b in TABS:
    ax.add_patch(Rectangle((FLAT_END_X - 0.01, a), XB - FLAT_END_X, b - a, fc='white', ec='none'))
    ax.add_patch(FancyBboxPatch((x_end, a), XB - x_end + 0.5, b - a, boxstyle='round,pad=0,rounding_size=1',
                                fc='#dddddd', ec='k', lw=0.7))
    for y in (a, b):
        ax.plot([FLAT_END_X, RELIEF_X], [y, y], 'k', lw=0.7)
        ax.add_patch(Circle((RELIEF_X, y), 0.75, fc='white', ec='k', lw=0.7))
    for y in screw_ys((a, b)):
        lo, hi = u(SCREW_Z - SLOT_L / 2), u(SCREW_Z + SLOT_L / 2)
        ax.add_patch(FancyBboxPatch((lo, y - SLOT_W / 2), hi - lo, SLOT_W,
                                    boxstyle=f'round,pad=0,rounding_size={SLOT_W / 2 - 0.01}', fc='white', ec='k', lw=0.7))
    ax.add_patch(Circle((u(PULL_HOLE_Z), (a + b) / 2), PULL_HOLE_D / 2, fc='white', ec='k', lw=0.7))
for x in (XB, XB - BEND):
    ax.plot([x, x], [STRIP_Y[0] - 3, STRIP_Y[1] + 3], 'k--', lw=0.5)
ax.text(XB - BEND / 2, STRIP_Y[1] + 14, 'bend R 3, 90°', ha='center', fontsize=8)
ax.text(XB + 13, STRIP_Y[1] + 4, 'lies flat on the end wall', fontsize=8)
ax.text(x_end, STRIP_Y[1] + 4, 'tab: on the end face', fontsize=8)
note(ax, 'slot 3.4 x 8 for M3:\nthe tab slides under the\nloose plate while pulled', (u(SCREW_Z), screw_ys(TABS[1])[0]),
     (-24, 63))
note(ax, 'pull hole Ø3.4,\nbelow the plate', (u(PULL_HOLE_Z), 105), (-24, 145))
note(ax, 'cut 0.5 mm wide,\nends in a Ø1.5 hole\npast the bend', (RELIEF_X, TABS[1][0]), (12, 95))
note(ax, 'strip ends at x = 1\nbeside the tabs', (FLAT_END_X, 65), (12, 36))
note(ax, 'round all corners (R 1)\nand edges, as for the\nrest of the strip', (x_end + 0.3, TABS[2][1] - 1), (12, 185))
ax.set_xlim(x_end - 4, 40); ax.set_ylim(5, 225); ax.set_aspect('equal'); ax.grid(alpha=.2)
ax.set_xlabel('along the strip [mm] (0 = base end face)'); ax.set_ylabel('y across [mm]')
ax.set_title('Strip end, flat, before bending (0.25 mm EN 1.4310). Both ends the same.', fontsize=10)

# fitting the pull: schematic side view, not to scale
bx.set_xlim(0, 100); bx.set_ylim(0, 80); bx.set_aspect('equal'); bx.axis('off')
bx.add_patch(Rectangle((8, 20), 80, 25, fc=C['base'], ec='k', lw=0.7))
bx.plot([8, 8], [45, 34], color=C['strip'], lw=2)
bx.plot([8, 88], [45.4, 45.4], color=C['strip'], lw=2)
bx.add_patch(MPoly([[40, 45.6], [48, 52], [64, 52], [72, 45.6]], fc='none', ec=C['strip'], lw=2))
bx.add_patch(Rectangle((36, 52), 40, 9, fc=C['top'], ec='k', lw=0.7))
bx.text(56, 56, 'carriage in place', ha='center', fontsize=8)
bx.add_patch(Rectangle((5.6, 25), 2.2, 9, fc=C['plate'], ec='k', lw=0.7))
bx.plot([8, 8], [34, 18], color=C['strip'], lw=2)
bx.plot([8, 8], [18, 8], 'k', lw=0.8)
bx.add_patch(Rectangle((4, 2), 8, 6, fc='#666666', ec='k'))
bx.text(14, 4, 'weight or spring scale on a\nbar through the 3 pull holes', fontsize=8, va='center')
bx.annotate('', xy=(56, 45.8), xytext=(56, 51.6), arrowprops=dict(arrowstyle='<->', lw=0.7))
bx.text(77, 47.5, 'arch height:\ncheck it against the\nseal strip designer page', fontsize=8)
bx.text(90, 40, 'other end:\nalready\nclamped', fontsize=8)
steps = ('1. Clamp one end. Tighten its screws.\n'
         '2. Put the carriage in place. Lay the strip on the base.\n'
         '3. At the other end, fit the plates with the screws loose.\n'
         '4. Pull the three tabs down with a set force.\n'
         '5. Check the arch height. Then tighten the screws.')
bx.text(2, 78, steps, fontsize=8.5, va='top')
bx.set_title('How the pull is set at fitting (sketch, not to scale)', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'strip_flat_and_fitting.png'), dpi=110)
