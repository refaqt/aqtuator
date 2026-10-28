"""Shared drawing helpers for the strip end clamp figures."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: F401
from shapely.geometry import Polygon
from clamp import *  # noqa: F401,F403
from render import loops, draw  # scraper-fit helpers

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results',
                                    'strip-end-clamp'))
os.makedirs(OUT, exist_ok=True)

C = dict(base='#c9ced6', top='#b9c9a8', scraper='#e8833a', strip='#222222', bar='#8fb3c9', pin='#e0c040',
         screw='#7a5c99', roller='#1f5fa8', clash='#d62728')


def poly(shape, origin, normal, ax0, ax1):
    """The section of a shape as one shapely geometry (holes kept)."""
    g = None
    for l in loops(section(shape, origin, normal, 24), ax0, ax1):
        p = Polygon(l).buffer(0)
        g = p if g is None else g.symmetric_difference(p)
    return g


def note(ax, text, xy, xytext, **kw):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=8,
                arrowprops=dict(arrowstyle='-', lw=0.6, color='k'), **kw)
