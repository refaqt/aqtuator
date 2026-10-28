"""Plane stress model of the whole strip: how the pull of the four corner inserts spreads across
the 186 mm width. Linear elastic, bilinear elements of 1 mm.

Almost all the travel of the inserts goes into flattening the arch over the carriage, not into
stretching the steel. So the arch is modelled as a soft band across the strip, between the two
bottom rollers (112 mm long), stiff across the width and in shear but soft along the travel. Its
stiffness along the travel comes from the strip model (strip-pull case): near 125 N, 0.1 mm of
travel changes the pull by 50 to 100 N, so about 750 N/mm for the whole width.
The insert holes are rigid and pulled outwards. No friction, no magnets."""
import os, json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from matplotlib.path import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from insert import XC, YC, HOLE_D, STRIP_END_X, STRIP_Y0, EAR_Y, EAR_X1, EAR_X2, T

E, NU, G = 185000.0, 0.3, 185000.0 / 2.6
PULL, W_STRIP, LEN = 125.0, 186.0, 440.0
K_ARCH, L_ARCH = 750.0, 112.0                     # N/mm for the whole width; band length
E_BAND = K_ARCH / W_STRIP * L_ARCH / T            # soft along the travel
YM, h = 105.0, 1.0
XE = LEN - STRIP_END_X                            # the far strip end
# The band: between the bottom rollers, carriage-top end face at 5 mm (end of the usable travel)
# or centred. Bottom rollers 49 mm and 161 mm from the carriage-top end face.
CASES = {'carriage at the end of the travel': 5.0 + 49.0, 'carriage in the middle': LEN / 2 - L_ARCH / 2}
ear = [(STRIP_END_X, EAR_Y), (EAR_X1, EAR_Y), (EAR_X2, STRIP_Y0)]
ear2 = [(LEN - x, y) for x, y in ear[::-1]]
pts = ear + ear2 + [(x, 2 * YM - y) for x, y in ear2[::-1]] + [(x, 2 * YM - y) for x, y in ear[::-1]]
outline = Path(pts)
holes = [(XC, YC), (XC, 2 * YM - YC), (LEN - XC, YC), (LEN - XC, 2 * YM - YC)]
xs = np.arange(STRIP_END_X, XE + h / 2, h); ys = np.arange(EAR_Y, 2 * YM - EAR_Y + h / 2, h)
nx, ny = len(xs), len(ys)
els, cen = [], []
for i in range(nx - 1):
    for j in range(ny - 1):
        c = (xs[i] + h / 2, ys[j] + h / 2)
        if outline.contains_point(c) and all(np.hypot(c[0] - a, c[1] - b) > HOLE_D / 2 for a, b in holes):
            els.append((i * ny + j, (i + 1) * ny + j, (i + 1) * ny + j + 1, i * ny + j + 1)); cen.append(c)
els, cen = np.array(els), np.array(cen)
X = np.repeat(xs, ny); Y = np.tile(ys, nx)
used = np.unique(els)


def dmat(ex):
    ey = E
    nxy = NU * ex / E                              # keeps the matrix symmetric
    d = 1 - nxy * NU
    return np.array([[ex / d, NU * ex / d, 0], [NU * ex / d, ey / d, 0], [0, 0, G]])


g = 1 / np.sqrt(3); gp = [(-g, -g), (g, -g), (g, g), (-g, g)]


def bmat(xi, eta):
    dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)],
                          [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]]) * (2 / h)
    B = np.zeros((3, 8)); B[0, 0::2] = dN[0]; B[1, 1::2] = dN[1]; B[2, 0::2] = dN[1]; B[2, 1::2] = dN[0]
    return B


D_steel, D_band = dmat(E), dmat(E_BAND)
K_s = sum(bmat(*p).T @ D_steel @ bmat(*p) for p in gp) * T * (h / 2) ** 2
K_b = sum(bmat(*p).T @ D_band @ bmat(*p) for p in gp) * T * (h / 2) ** 2
dofs = np.stack([np.stack([2 * els[:, k], 2 * els[:, k] + 1], 1) for k in range(4)], 1).reshape(-1, 8)
r = np.repeat(dofs, 8, 1).ravel(); c = np.tile(dofs, 8).ravel()
rim = {}
for a, b in holes:
    rim[(a, b)] = used[np.hypot(X[used] - a, Y[used] - b) <= HOLE_D / 2 + 0.75]
res = {'avg_MPa': PULL / (W_STRIP * T), 'E_band_MPa': E_BAND, 'cases': {}}
fig, axs = plt.subplots(1, 2, figsize=(16, 6.2))
for (label, x0), ax in zip(CASES.items(), axs):
    band = (cen[:, 0] > x0) & (cen[:, 0] < x0 + L_ARCH)
    vals = np.where(band[:, None], K_b.ravel()[None, :], K_s.ravel()[None, :]).ravel()
    K = coo_matrix((vals, (r, c)), shape=(2 * nx * ny,) * 2).tocsr()
    fix = {}
    for (a, b), nodes in rim.items():
        for n in nodes:
            fix[2 * n] = -0.5 if a < LEN / 2 else 0.5
            fix[2 * n + 1] = 0.0
    act = np.zeros(2 * nx * ny, bool); act[2 * used] = act[2 * used + 1] = True
    fd = np.array(sorted(fix)); fv = np.array([fix[k] for k in fd])
    free = np.where(act)[0]; free = free[~np.isin(free, fd)]
    u = np.zeros(2 * nx * ny); u[fd] = fv
    u[free] = spsolve(K[free][:, free], -K[free][:, fd] @ fv)
    Rx = (K @ u)[0::2]
    force = abs(sum(Rx[n] for (a, b), nodes in rim.items() if a < LEN / 2 for n in nodes))
    u *= PULL / force
    S = np.array([(D_band if bd else D_steel) @ bmat(0, 0) @ u[d] for d, bd in zip(dofs, band)])
    avg = res['avg_MPa']
    out = {'travel_both_ends_mm': float(PULL / force), 'cuts': {}}
    for xc_, col in zip([15, 30, x0 + 1, x0 + L_ARCH / 2, x0 + L_ARCH - 1],
                        plt.cm.viridis(np.linspace(0, 0.9, 5))):
        colx = cen[np.argmin(abs(cen[:, 0] - xc_)), 0]
        m = np.isclose(cen[:, 0], colx) & (cen[:, 1] > STRIP_Y0) & (cen[:, 1] < 2 * YM - STRIP_Y0)
        sx = S[m, 0]
        out['cuts'][f'{colx:.1f}'] = dict(centre=float(sx[np.argmin(abs(cen[m, 1] - YM))] / avg),
                                          max=float(sx.max() / avg), min=float(sx.min() / avg))
        name = 'arch' if x0 < xc_ < x0 + L_ARCH else 'strip'
        ax.plot(cen[m, 1], sx / avg, color=col, label=f'x = {colx:.0f} mm ({name})')
    out['syy_min_MPa'] = float(S[cen[:, 0] > 9, 1].min())
    res['cases'][label] = out
    ax.axhline(1, color='k', lw=0.8, ls='--'); ax.axhline(0, color='k', lw=0.5)
    ax.set_ylim(-0.5, 9); ax.grid(alpha=.3); ax.legend(fontsize=8)
    ax.set_xlabel('y across the strip [mm]'); ax.set_ylabel('pull stress / average pull stress')
    ax.set_title(f'{label}: arch between x = {x0:.0f} and {x0 + L_ARCH:.0f} mm', fontsize=10)
fig.suptitle(f'How the pull of four corner inserts spreads across the 0.15 mm strip at {PULL:.0f} N '
             f'(average {res["avg_MPa"]:.1f} MPa). The arch over the carriage is a soft band.', fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'membrane.png'), dpi=110)
with open(os.path.join(OUT, 'membrane.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('membrane:', json.dumps(res['cases'], indent=0))
