"""Stress in the seal strip end while the preload screw pulls it.

The cone of the countersunk preload screw pushes the outer edge of the strip hole towards the
strip end. The strip between the hole and the strip end (the bridge) carries the whole pull of
that end. Plane stress, linear triangles, mesh from gmsh (the gmsh.exe that comes with FreeCAD),
solved with scipy. One case per screw position.

Run from the repository root:
    python modules/compact-stage/simulation/cases/strip-seal-fit/strip_end.py
Writes results/strip-seal-fit/strip_end.json and strip_end.png.
"""
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

RES = Path(__file__).resolve().parents[2] / "results" / "strip-seal-fit"
GMSH = os.environ.get("GMSH", r"C:\Program Files\FreeCAD 1.1\bin\gmsh.exe")

E, NU, T = 185000.0, 0.3, 0.15     # EN 1.4310, Alleima 11R51; strip thickness, mm
RP02 = 1975.0                      # MPa, Alleima 11R51
PULL = 270.0                       # N, through one preload screw (the far end has the other)
STRIP_END = 1.0                    # strip end, mm from the base end
D_HOLE = 5.0                       # strip hole
R_CONE = 2.0 + T                   # cone of ISO 10642 M4 at the top of the strip
L, W = 40.0, 80.0                  # model: strip end to the cut, and width around the screw
# Contact half angle of the cone on the hole edge. The cone (4.3 mm) is much smaller than the
# hole (5 mm), so the contact is short. Two values bound it.
ARCS = (15.0, 40.0)
# Screw positions from the base end. 4: as drawn. 4.5: the M4 hole 0.5 mm from the magnet ring
# pocket (ring from 7 mm). 6.5 and 7: the ring cut around the screw; 1.5 and 1 mm of wall stay
# between the
# M4 thread and the slot face at 10 mm.
SCREWS = (4.0, 4.5, 5.5, 6.5, 7.0)


def mesh(xh, h_fine, grow):
    geo = f"""
SetFactory("OpenCASCADE");
Rectangle(1) = {{{STRIP_END}, {-W / 2}, 0, {L}, {W}}};
Disk(2) = {{{xh}, 0, 0, {D_HOLE / 2}, {D_HOLE / 2}}};
BooleanDifference{{ Surface{{1}}; Delete; }}{{ Surface{{2}}; Delete; }}
Field[2] = MathEval; Field[2].F = "{h_fine} + {grow} * Sqrt((x - {xh})^2 + y^2) ^ 1.5";
Background Field = 2;
Mesh.CharacteristicLengthMax = 2;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.ElementOrder = 1;
"""
    with tempfile.TemporaryDirectory() as tmp:
        g, m = Path(tmp) / "m.geo", Path(tmp) / "m.msh"
        g.write_text(geo)
        subprocess.run([GMSH, str(g), "-2", "-format", "msh2", "-o", str(m)],
                       check=True, capture_output=True)
        lines = m.read_text().splitlines()
    i = lines.index("$Nodes")
    n = int(lines[i + 1])
    xy = np.array([[float(v) for v in lines[i + 2 + k].split()[1:3]] for k in range(n)])
    ids = {int(lines[i + 2 + k].split()[0]): k for k in range(n)}
    j = lines.index("$Elements")
    tris = []
    for line in lines[j + 2: j + 2 + int(lines[j + 1])]:
        v = line.split()
        if v[1] == "2":
            tris.append([ids[int(q)] for q in v[-3:]])
    return xy, np.array(tris)


def solve(xs, arc, h_fine=0.005, grow=0.02):
    xh = xs + (D_HOLE / 2 - R_CONE)        # hole off the screw axis, towards the strip middle
    xy, tri = mesh(xh, h_fine, grow)
    n = len(xy)
    Dm = E / (1 - NU ** 2) * np.array([[1, NU, 0], [NU, 1, 0], [0, 0, (1 - NU) / 2]])
    rows, cols, vals, Bs, areas = [], [], [], [], []
    for e in tri:
        x, y = xy[e, 0], xy[e, 1]
        A2 = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])
        if A2 < 0:
            e[[1, 2]] = e[[2, 1]]
            x, y = xy[e, 0], xy[e, 1]
            A2 = -A2
        b = np.array([y[1] - y[2], y[2] - y[0], y[0] - y[1]]) / A2
        c = np.array([x[2] - x[1], x[0] - x[2], x[1] - x[0]]) / A2
        B = np.zeros((3, 6))
        B[0, 0::2], B[1, 1::2], B[2, 0::2], B[2, 1::2] = b, c, c, b
        k = T * A2 / 2 * B.T @ Dm @ B
        dof = np.ravel([[2 * q, 2 * q + 1] for q in e])
        rows += np.repeat(dof, 6).tolist()
        cols += np.tile(dof, 6).tolist()
        vals += k.ravel().tolist()
        Bs.append(B)
        areas.append(A2 / 2)
    K = sp.csr_matrix((vals, (rows, cols)), shape=(2 * n, 2 * n))

    # Load: radial pressure on the hole edge, centred on the side towards the strip end,
    # cosine shaped over +-arc, resultant PULL towards the strip end (-x).
    f = np.zeros(2 * n)
    r = np.hypot(xy[:, 0] - xh, xy[:, 1])
    ang = np.arctan2(xy[:, 1], xy[:, 0] - xh)
    on_hole = np.abs(r - D_HOLE / 2) < 1e-6
    dev = np.abs(np.abs(ang) - math.pi)
    a = math.radians(arc)
    w = np.where(on_hole & (dev < a), np.cos(math.pi / 2 * dev / a), 0.0)
    # weight by the edge length each node carries
    order = np.argsort(ang[on_hole])
    idx = np.where(on_hole)[0][order]
    th = ang[idx]
    seg = np.diff(np.concatenate([th[-1:] - 2 * math.pi, th, th[:1] + 2 * math.pi]))
    ds = (seg[:-1] + seg[1:]) / 2 * D_HOLE / 2
    # radial push, outward from the hole centre
    nx, ny = np.cos(ang[idx]), np.sin(ang[idx])
    fx, fy = w[idx] * ds * nx, w[idx] * ds * ny
    s = PULL / -fx.sum()
    f[2 * idx] += fx * s
    f[2 * idx + 1] += fy * s

    # Support: the cut far from the end is held along x; one node there also along y.
    far = np.where(np.abs(xy[:, 0] - (STRIP_END + L)) < 1e-6)[0]
    fixed = np.concatenate([2 * far, [2 * far[np.argmin(np.abs(xy[far, 1]))] + 1]])
    free = np.setdiff1d(np.arange(2 * n), fixed)
    u = np.zeros(2 * n)
    u[free] = spla.spsolve(K[free][:, free].tocsc(), f[free])

    vm, cen = [], []
    for e, B in zip(tri, Bs):
        dof = np.ravel([[2 * q, 2 * q + 1] for q in e])
        sx, sy, txy = Dm @ (B @ u[dof])
        vm.append(math.sqrt(sx * sx - sx * sy + sy * sy + 3 * txy * txy))
        cen.append(xy[e].mean(axis=0))
    vm, cen = np.array(vm), np.array(cen)
    # Stress away from the contact itself (local crushing under the cone is expected and harmless
    # for a one-time preload); and the free strip end, where the bridge bends.
    pc = np.array([xh - D_HOLE / 2, 0.0])
    away = np.hypot(*(cen - pc).T) > 0.3
    edge = (np.abs(xy[tri, 0] - STRIP_END) < 1e-6).any(axis=1)
    return {
        "screw_x": xs, "arc_deg": arc, "bridge": xh - D_HOLE / 2 - STRIP_END,
        "vm_max_away": float(vm[away].max()), "vm_end_edge": float(vm[edge].max()),
        "vm_max_all": float(vm.max()), "elements": int(len(tri)),
    }, (xy, tri, vm, xh)


def main():
    out, keep = [], {}
    for xs in SCREWS:
        for arc in ARCS:
            r, data = solve(xs, arc)
            out.append(r)
            keep[(xs, arc)] = data
            print(f"screw x {xs:4.1f}  bridge {r['bridge']:.2f} mm  contact +-{arc:.0f} deg: "
                  f"von Mises away from the contact {r['vm_max_away']:6.0f} MPa, "
                  f"at the strip end {r['vm_end_edge']:6.0f} MPa ({r['elements']} elements)")
    (RES / "strip_end.json").write_text(json.dumps({"pull_N": PULL, "Rp02": RP02, "cases": out},
                                                   indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.tri import Triangulation
    fig, axes = plt.subplots(1, len(SCREWS), figsize=(4 * len(SCREWS), 4))
    for ax, xs in zip(axes, SCREWS):
        xy, tri, vm, xh = keep[(xs, ARCS[1])]
        tc = ax.tripcolor(Triangulation(xy[:, 0], xy[:, 1], tri), facecolors=np.minimum(vm, 2500),
                          cmap="viridis", vmin=0, vmax=2500)
        ax.set_xlim(0.5, xh + 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect("equal")
        ax.set_title(f"screw at {xs} mm")
        ax.set_xlabel("x from the base end (mm)")
    fig.colorbar(tc, ax=axes, label="von Mises (MPa), capped at 2500")
    fig.suptitle(f"Strip end under {PULL:.0f} N from the preload screw (contact +-{ARCS[1]:.0f} deg)")
    fig.savefig(RES / "strip_end.png", dpi=120)


if __name__ == "__main__":
    main()
