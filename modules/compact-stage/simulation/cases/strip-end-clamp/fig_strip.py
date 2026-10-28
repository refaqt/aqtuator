"""Flat shape of the strip end before bending, and how the pull is set and released."""
import math
from fig_common import *  # noqa: F401,F403
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

BEND = (EDGE_R + T / 2) * math.pi / 2      # length of the bend, on the middle of the strip
XB = STEP_X + EDGE_R                       # the bend starts here, on top
ZC = Z_WALL - EDGE_R


def u(z):
    """Position along the flat strip of a point at height z on the bent tab."""
    return XB - BEND - (ZC - z)


fig, (ax, bx) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw=dict(width_ratios=[1.0, 1.25]))
x_end = u(TAB_Z_END)
ax.add_patch(Rectangle((FLAT_END_X, STRIP_Y[0]), 40 - FLAT_END_X, STRIP_Y[1] - STRIP_Y[0], fc='#dddddd', ec='k', lw=0.7))
for s in STEPS:
    a, b = tab_y(s)
    ax.add_patch(Rectangle((FLAT_END_X - 0.01, a), XB - FLAT_END_X, b - a, fc='white', ec='none'))
    ax.add_patch(FancyBboxPatch((x_end, a), XB - x_end + 0.5, b - a, boxstyle='round,pad=0,rounding_size=1',
                                fc='#dddddd', ec='k', lw=0.7))
    for y in (a, b):
        ax.plot([FLAT_END_X, RELIEF_X], [y, y], 'k', lw=0.7)
        ax.add_patch(Circle((RELIEF_X, y), 0.75, fc='white', ec='k', lw=0.7))
    for y in pin_ys(s):
        ax.add_patch(Circle((u(PIN_Z), y), TAB_HOLE_D / 2, fc='white', ec='k', lw=0.7))
for x in (XB, XB - BEND):
    ax.plot([x, x], [STRIP_Y[0] - 3, STRIP_Y[1] + 3], 'k--', lw=0.5)
ax.text(XB - BEND / 2, STRIP_Y[1] + 9, 'bend R 3, 90°', ha='center', fontsize=8)
ax.text(XB + 8, STRIP_Y[1] + 14, 'lies flat\non the end wall', fontsize=8)
ax.text(x_end - 13, STRIP_Y[1] + 4, 'tab, on the wall face', fontsize=8)
note(ax, 'Ø2.1 holes for the pins:\nthe pull is about 8 N per hole', (u(PIN_Z), pin_ys(STEPS[1])[1]), (-15, 140))
note(ax, 'cut 0.5 mm wide,\nends in a Ø1.5 hole\npast the bend', (RELIEF_X, tab_y(STEPS[1])[0]), (16, 95))
note(ax, 'strip ends at x = 1\nbeside the tabs', (FLAT_END_X, 65), (16, 50))
note(ax, 'round all corners (R 1)\nand edges, as for the\nrest of the strip', (x_end + 0.3, tab_y(STEPS[2])[1] - 1), (16, 185))
ax.set_xlim(-16, 40); ax.set_ylim(5, 222); ax.set_aspect('equal'); ax.grid(alpha=.2)
ax.set_xlabel('along the strip [mm] (0 = base end face)'); ax.set_ylabel('y across [mm]')
ax.set_title('Strip end, flat, before bending (0.25 mm EN 1.4310).\nBoth ends the same.', fontsize=10)

bx.axis('off')
bx.set_title('Fitting, setting the pull, and taking the strip out (only from the top)', fontsize=10)
steps = (
    'Fitting\n'
    '  1. Move the carriage to the middle. Lay the strip on the base. The tabs are bent before fitting.\n'
    '  2. At each end, hook each tab on the pins of its bar. Drop the bar into its step.\n'
    '  3. Put in the two screws of each bar. Turn them until the heads just touch the bar.\n\n'
    'Setting the pull\n'
    '  4. Turn all screws of one end in equal steps. M3 has a 0.5 mm pitch, so a quarter turn\n'
    '      moves the bar 0.125 mm down. That is about 15 N more pull near 54 N.\n'
    '  5. Check the arch height under the carriage against the seal strip designer page.\n'
    '      Stop when it is right.\n\n'
    'Taking the strip out\n'
    '  6. Move the carriage to the other end. Loosen the screws of the free end from the top.\n'
    '      The strip goes slack.\n'
    '  7. Lift the bars out, unhook the tabs, and lift the strip away.\n\n'
    'Why the pin holes are safe\n'
    '  The strip lies flat between the wall and the bar, so it cannot buckle.\n'
    '  The pull is low: about 8 N per Ø2 pin, or about 16 MPa on the hole edge.\n'
    '  The holes are in the static part of the strip. No roller runs there.\n\n'
    'Option: a set force instead of a set travel\n'
    '  Put a small coil spring under each screw head. Tighten until the spring has a marked length.\n'
    '  The spring then sets the pull, and the bar follows changes in length and temperature.')
bx.text(0.0, 1.0, steps, fontsize=9, va='top', transform=bx.transAxes)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'strip_flat_and_fitting.png'), dpi=110)
