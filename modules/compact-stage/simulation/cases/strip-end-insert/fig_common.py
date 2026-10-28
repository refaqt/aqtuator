"""Shared drawing helpers for the strip-end-insert figures."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: F401
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from shapely.geometry import Polygon
from insert import *  # noqa: F401,F403

C = dict(base='#c9ced6', top='#b9c9a8', bot='#9fb7d9', scraper='#e8833a', strip='#222222',
         insert='#c8e600', screw='#ff7a00', magnet='#ff40ff', roller='#1f5fa8', clash='#d62728')


def loops(segs, ax0, ax1, tol=1e-3):
    segs = [[(p[ax0], p[ax1]) for p in s] for s in segs]
    out = []
    while segs:
        cur = segs.pop(0)
        changed = True
        while changed:
            changed = False
            for i, s in enumerate(segs):
                if np.hypot(*np.subtract(s[0], cur[-1])) < tol: cur += s[1:]
                elif np.hypot(*np.subtract(s[-1], cur[-1])) < tol: cur += s[::-1][1:]
                elif np.hypot(*np.subtract(s[-1], cur[0])) < tol: cur = s[:-1] + cur
                elif np.hypot(*np.subtract(s[0], cur[0])) < tol: cur = s[::-1][:-1] + cur
                else: continue
                segs.pop(i); changed = True; break
        if len(cur) > 3: out.append(cur)
    return out


def poly(shape, origin, normal, ax0, ax1):
    g = None
    for l in loops(section(shape, origin, normal, 24), ax0, ax1):
        p = Polygon(l).buffer(0)
        g = p if g is None else g.symmetric_difference(p)
    return g


def draw(ax, g, color, lw=0.6):
    if g is None or g.is_empty:
        return
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type != 'Polygon':
            continue
        verts, codes = [], []
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords); verts += c; codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec='k', lw=lw))


def note(ax, text, xy, xytext, **kw):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=8, arrowprops=dict(arrowstyle='-', lw=0.6, color='k'), **kw)
