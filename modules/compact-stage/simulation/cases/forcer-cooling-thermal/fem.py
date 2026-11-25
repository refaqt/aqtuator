# SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite element tools for the thermal model: 10-node tetrahedra.

Everything here is plain numpy and scipy. pyamg (algebraic multigrid) makes the
solves fast; without it, scipy's direct solver is used.

Units: mm, W, N, MPa, s, K. A conductivity k in W/(m K) becomes k / 1000 in
W/(mm K). A film coefficient h in W/(m2 K) becomes h / 1e6 in W/(mm2 K).

Node order of a tetrahedron (CalculiX order): corners 0..3, then the edge
nodes 0-1, 1-2, 2-0, 0-3, 1-3, 2-3. The edges are straight, so the map from
the reference element is affine and each element has one Jacobian.
"""

import math
from itertools import combinations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.spatial import cKDTree

try:
    import pyamg
except ImportError:  # the direct solver still works, only slower
    pyamg = None

EDGES = [(0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)]
EDGE_NODE = {}
for _k, (_a, _b) in enumerate(EDGES):
    EDGE_NODE[(_a, _b)] = 4 + _k
    EDGE_NODE[(_b, _a)] = 4 + _k
FACES = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3)]
OPPOSITE = [3, 2, 0, 1]


# ---------------------------------------------------------------------------
# Reference integrals, exact, from the barycentric monomial formula
# ---------------------------------------------------------------------------

def _poly_tet():
    """Each P2 shape function as {exponents of (L0, L1, L2, L3): coefficient}."""
    polys = []
    for i in range(4):
        e2 = [0, 0, 0, 0]
        e2[i] = 2
        e1 = [0, 0, 0, 0]
        e1[i] = 1
        polys.append({tuple(e2): 2.0, tuple(e1): -1.0})
    for a, b in EDGES:
        e = [0, 0, 0, 0]
        e[a] += 1
        e[b] += 1
        polys.append({tuple(e): 4.0})
    return polys


def _poly_tri():
    polys = []
    for i in range(3):
        e2 = [0, 0, 0]
        e2[i] = 2
        e1 = [0, 0, 0]
        e1[i] = 1
        polys.append({tuple(e2): 2.0, tuple(e1): -1.0})
    for a, b in ((0, 1), (1, 2), (2, 0)):
        e = [0, 0, 0]
        e[a] += 1
        e[b] += 1
        polys.append({tuple(e): 4.0})
    return polys


def _int_mono(exps, dim):
    """Integral of a barycentric monomial over the simplex, divided by its size."""
    num = 1.0
    for e in exps:
        num *= math.factorial(e)
    return math.factorial(dim) * num / math.factorial(sum(exps) + dim)


def _ref_mass(polys, dim):
    n = len(polys)
    m = np.zeros((n, n))
    v = np.zeros(n)
    for i in range(n):
        for ea, ca in polys[i].items():
            v[i] += ca * _int_mono(ea, dim)
            for j in range(n):
                for eb, cb in polys[j].items():
                    m[i, j] += ca * cb * _int_mono(tuple(x + y for x, y in zip(ea, eb)), dim)
    return m, v


TET_M, TET_V = _ref_mass(_poly_tet(), 3)       # int N N^T dV / V, int N dV / V
TRI_M, TRI_V = _ref_mass(_poly_tri(), 2)       # int N N^T dA / A, int N dA / A
TRI_LUMP = np.array([1 / 12, 1 / 12, 1 / 12, 1 / 4, 1 / 4, 1 / 4])  # area share per node

# 4-point Gauss rule for the tetrahedron (exact to degree 2)
_A, _B = 0.5854101966249685, 0.1381966011250105
GP = np.array([[_A, _B, _B, _B], [_B, _A, _B, _B], [_B, _B, _A, _B], [_B, _B, _B, _A]])
GW = np.full(4, 0.25)


def shape_tet(L):
    """P2 shape values (10) at barycentric point L (4)."""
    n = [L[i] * (2 * L[i] - 1) for i in range(4)]
    n += [4 * L[a] * L[b] for a, b in EDGES]
    return np.array(n)


def dshape_tet(L):
    """d N / d L (10 x 4) at barycentric point L."""
    d = np.zeros((10, 4))
    for i in range(4):
        d[i, i] = 4 * L[i] - 1
    for k, (a, b) in enumerate(EDGES):
        d[4 + k, a] = 4 * L[b]
        d[4 + k, b] = 4 * L[a]
    return d


def shape_tri(l):
    """P2 shape values of a 6-node triangle at barycentrics l (..., 3)."""
    l0, l1, l2 = l[..., 0], l[..., 1], l[..., 2]
    return np.stack([l0 * (2 * l0 - 1), l1 * (2 * l1 - 1), l2 * (2 * l2 - 1),
                     4 * l0 * l1, 4 * l1 * l2, 4 * l2 * l0], axis=-1)


GP_N = np.array([shape_tet(g) for g in GP])          # (4, 10)
GP_DN = np.array([dshape_tet(g) for g in GP])        # (4, 10, 4)


def geometry(xyz, tets):
    """Volume (n) and barycentric gradients (n, 4, 3) of each element."""
    p = xyz[tets[:, :4]]
    J = np.stack([p[:, 1] - p[:, 0], p[:, 2] - p[:, 0], p[:, 3] - p[:, 0]], axis=2)
    det = np.linalg.det(J)
    inv = np.linalg.inv(J)                      # rows: grad xi, grad eta, grad zeta
    g = np.empty((len(tets), 4, 3))
    g[:, 1:] = inv
    g[:, 0] = -inv.sum(axis=1)
    return det / 6.0, g


# ---------------------------------------------------------------------------
# Surfaces
# ---------------------------------------------------------------------------

def boundary_faces(xyz, tets):
    """Faces used by only one element: (m, 6) node ids, outward, with geometry."""
    loc = []
    for f, opp in zip(FACES, OPPOSITE):
        a, b, c = f
        loc.append([a, b, c, EDGE_NODE[(a, b)], EDGE_NODE[(b, c)], EDGE_NODE[(c, a)], opp])
    loc = np.array(loc)
    allf = tets[:, loc[:, :6]].reshape(-1, 6)            # (4n, 6)
    opp = tets[:, loc[:, 6]].reshape(-1)
    elem = np.repeat(np.arange(len(tets)), 4)
    key = np.sort(allf[:, :3], axis=1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    once = cnt[inv.ravel()] == 1
    f = allf[once]
    opp = opp[once]
    elem = elem[once]
    p0, p1, p2 = xyz[f[:, 0]], xyz[f[:, 1]], xyz[f[:, 2]]
    n = np.cross(p1 - p0, p2 - p0)
    cen = (p0 + p1 + p2) / 3.0
    flip = np.einsum("ij,ij->i", n, cen - xyz[opp]) < 0
    f[flip] = f[flip][:, [0, 2, 1, 5, 4, 3]]
    n[flip] *= -1
    area = 0.5 * np.linalg.norm(n, axis=1)
    return {"tri": f, "elem": elem, "normal": n / (2 * area[:, None]), "area": area,
            "centroid": cen}


class Surface:
    """Closest point on a body surface (straight 6-node triangles)."""

    def __init__(self, xyz, faces):
        self.xyz = xyz
        self.f = faces
        self.tree = cKDTree(faces["centroid"])

    def project(self, pts, k=12):
        f = self.f
        k = min(k, len(f["area"]))
        _, idx = self.tree.query(pts, k=k)
        if k == 1:
            idx = idx[:, None]
        tri = f["tri"][idx]                                 # (n, k, 6)
        p0 = self.xyz[tri[..., 0]]
        e1 = self.xyz[tri[..., 1]] - p0
        e2 = self.xyz[tri[..., 2]] - p0
        v = pts[:, None, :] - p0
        d00 = np.einsum("nki,nki->nk", e1, e1)
        d01 = np.einsum("nki,nki->nk", e1, e2)
        d11 = np.einsum("nki,nki->nk", e2, e2)
        d20 = np.einsum("nki,nki->nk", v, e1)
        d21 = np.einsum("nki,nki->nk", v, e2)
        den = d00 * d11 - d01 * d01
        l1 = (d11 * d20 - d01 * d21) / den
        l2 = (d00 * d21 - d01 * d20) / den
        lam = np.stack([1 - l1 - l2, l1, l2], axis=-1)
        lc = np.clip(lam, 0, None)
        lc /= lc.sum(axis=-1, keepdims=True)
        q = p0 + lc[..., 1:2] * e1 + lc[..., 2:3] * e2
        dist = np.linalg.norm(pts[:, None, :] - q, axis=-1)
        best = np.argmin(dist, axis=1)
        r = np.arange(len(pts))
        fid = idx[r, best]
        nrm = f["normal"][fid]
        signed = np.einsum("ni,ni->n", pts - q[r, best], nrm)
        return {"face": fid, "lam": lc[r, best], "dist": dist[r, best], "signed": signed,
                "normal": nrm, "nodes": f["tri"][fid]}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _coo(rows, cols, vals, n):
    return sp.coo_matrix((vals.ravel(), (rows.ravel(), cols.ravel())), shape=(n, n)).tocsr()


def conduction(xyz, tets, k_elem, offset, n):
    """Conduction matrix of one body. k_elem in W/(mm K) per element."""
    vol, g = geometry(xyz, tets)
    ke = np.zeros((len(tets), 10, 10))
    for q in range(4):
        G = np.einsum("ia,nab->nib", GP_DN[q], g)             # (n, 10, 3)
        ke += GW[q] * np.einsum("nib,njb->nij", G, G)
    ke *= (k_elem * vol)[:, None, None]
    t = tets + offset
    rows = np.repeat(t[:, :, None], 10, axis=2)
    cols = np.repeat(t[:, None, :], 10, axis=1)
    return _coo(rows, cols, ke, n), vol


def capacity(tets, vol, rc_elem, offset, n):
    """Heat capacity matrix of one body. rc_elem in J/(mm3 K)."""
    me = (rc_elem * vol)[:, None, None] * TET_M[None]
    t = tets + offset
    rows = np.repeat(t[:, :, None], 10, axis=2)
    cols = np.repeat(t[:, None, :], 10, axis=1)
    return _coo(rows, cols, me, n)


def source(tets, vol, q_elem, offset, n):
    """Load vector of a heat source q_elem in W/mm3."""
    f = np.zeros(n)
    np.add.at(f, tets + offset, (q_elem * vol)[:, None] * TET_V[None])
    return f


def film(tri, area, h, offset, n):
    """Film matrix and the unit load (times the sink temperature later).
    h in W/(mm2 K) per face. Returns K and the per-face load vectors basis."""
    me = (h * area)[:, None, None] * TRI_M[None]
    t = tri + offset
    rows = np.repeat(t[:, :, None], 6, axis=2)
    cols = np.repeat(t[:, None, :], 6, axis=1)
    return _coo(rows, cols, me, n)


def film_load(tri, area, h, t_sink, offset, n):
    f = np.zeros(n)
    np.add.at(f, tri + offset, (h * area * t_sink)[:, None] * TRI_V[None])
    return f


def link_scalar(slave, weight, master_nodes, shape, h, n):
    """Conductance between slave nodes and points on a master surface.
    Each pair adds h * a * (T_s - sum N_j T_j)^2 / 2 to the energy."""
    c = h * weight                                        # (m,)
    idx = np.concatenate([slave[:, None], master_nodes], axis=1)   # (m, 7)
    vec = np.concatenate([np.ones((len(slave), 1)), -shape], axis=1)
    ke = c[:, None, None] * vec[:, :, None] * vec[:, None, :]
    rows = np.repeat(idx[:, :, None], 7, axis=2)
    cols = np.repeat(idx[:, None, :], 7, axis=1)
    return _coo(rows, cols, ke, n)


def solver(A, rigid=None, tol=1e-8):
    """A function that solves A x = b.

    The matrix is first scaled by its diagonal (D A D, D = diag(A)^-1/2). The
    parts are joined by links that are much weaker than the conduction inside
    each part; without the scaling the multigrid method converges very slowly."""
    A = A.tocsr()
    d = 1.0 / np.sqrt(A.diagonal())
    Dm = sp.diags(d)
    As = (Dm @ A @ Dm).tocsr()
    if pyamg is not None:
        if rigid is None:
            ml = pyamg.smoothed_aggregation_solver(As, max_coarse=2000)
        else:
            ml = pyamg.smoothed_aggregation_solver(As, B=rigid / d[:, None], max_coarse=3000)
        state = {"lu": None}

        def solve(b, x0=None, tol=tol):
            bs = d * b
            if state["lu"] is not None:
                return d * state["lu"].solve(bs)
            res = []
            y0 = None if x0 is None else x0 / d
            y = ml.solve(bs, x0=y0, tol=tol, accel="cg", maxiter=1500, residuals=res)
            rel = np.linalg.norm(bs - As @ y) / max(np.linalg.norm(bs), 1e-300)
            if rel > 1e-5 or not np.isfinite(y).all():
                # Multigrid stalled: fall back to a direct solve.
                state["lu"] = spla.splu(As.tocsc())
                return d * state["lu"].solve(bs)
            return d * y
        return solve
    lu = spla.splu(As.tocsc())
    return lambda b, x0=None, tol=None: d * lu.solve(d * b)


# ---------------------------------------------------------------------------
# Elasticity
# ---------------------------------------------------------------------------

def iso_c(E, nu):
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    C = np.zeros((6, 6))
    C[:3, :3] = lam
    C[np.arange(3), np.arange(3)] += 2 * mu
    C[np.arange(3, 6), np.arange(3, 6)] = mu
    return C


def _bmat(G):
    """Strain-displacement matrices (n, 6, 30) from shape gradients (n, 10, 3).
    Strain order: xx, yy, zz, xy, yz, zx (engineering shear)."""
    n = G.shape[0]
    B = np.zeros((n, 6, 30))
    gx, gy, gz = G[:, :, 0], G[:, :, 1], G[:, :, 2]
    B[:, 0, 0::3] = gx
    B[:, 1, 1::3] = gy
    B[:, 2, 2::3] = gz
    B[:, 3, 0::3] = gy
    B[:, 3, 1::3] = gx
    B[:, 4, 1::3] = gz
    B[:, 4, 2::3] = gy
    B[:, 5, 0::3] = gz
    B[:, 5, 2::3] = gx
    return B


def elasticity(xyz, tets, E, nu, alpha, dT_nodes, offset, n, chunk=40000):
    """Stiffness matrix and thermal load of one body (3 DOF per node).
    E, nu, alpha per element; dT_nodes: temperature rise at each node of the body."""
    vol, g = geometry(xyz, tets)
    K = None
    f = np.zeros(3 * n)
    dof = 3 * (tets + offset)[:, :, None] + np.arange(3)[None, None, :]
    dof = dof.reshape(len(tets), 30)
    for s in range(0, len(tets), chunk):
        e = slice(s, s + chunk)
        m = len(vol[e])
        lam = (E[e] * nu[e] / ((1 + nu[e]) * (1 - 2 * nu[e])))
        mu = E[e] / (2 * (1 + nu[e]))
        C = np.zeros((m, 6, 6))
        C[:, :3, :3] = lam[:, None, None]
        for i in range(3):
            C[:, i, i] += 2 * mu
            C[:, 3 + i, 3 + i] = mu
        ke = np.zeros((m, 30, 30))
        fe = np.zeros((m, 30))
        for q in range(4):
            G = np.einsum("ia,nab->nib", GP_DN[q], g[e])
            B = _bmat(G)
            CB = np.einsum("nij,njk->nik", C, B)
            ke += GW[q] * np.einsum("nji,njk->nik", B, CB)
            dT = dT_nodes[tets[e]] @ GP_N[q]
            eps = np.zeros((m, 6))
            eps[:, :3] = (alpha[e] * dT)[:, None]
            fe += GW[q] * np.einsum("nji,nj->ni", CB, eps)
        ke *= vol[e][:, None, None]
        fe *= vol[e][:, None]
        d = dof[e]
        rows = np.repeat(d[:, :, None], 30, axis=2)
        cols = np.repeat(d[:, None, :], 30, axis=1)
        Kc = _coo(rows, cols, ke, 3 * n)
        K = Kc if K is None else K + Kc
        np.add.at(f, d, fe)
    return K, f


def stress_centroid(xyz, tets, E, nu, alpha, dT_nodes, u_nodes):
    """Stress (n, 6) at the centroid of each element, in MPa."""
    vol, g = geometry(xyz, tets)
    Lc = np.full(4, 0.25)
    G = np.einsum("ia,nab->nib", dshape_tet(Lc), g)
    B = _bmat(G)
    ue = u_nodes[tets].reshape(len(tets), 30)
    eps = np.einsum("nij,nj->ni", B, ue)
    dT = dT_nodes[tets] @ shape_tet(Lc)
    eps[:, :3] -= (alpha * dT)[:, None]
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    tr = eps[:, :3].sum(axis=1)
    s = np.empty_like(eps)
    s[:, :3] = lam[:, None] * tr[:, None] + 2 * mu[:, None] * eps[:, :3]
    s[:, 3:] = mu[:, None] * eps[:, 3:]
    return s


def von_mises(s):
    return np.sqrt(0.5 * ((s[:, 0] - s[:, 1]) ** 2 + (s[:, 1] - s[:, 2]) ** 2 +
                          (s[:, 2] - s[:, 0]) ** 2) + 3 * (s[:, 3] ** 2 + s[:, 4] ** 2 + s[:, 5] ** 2))


def link_vector(slave, weight, master_nodes, shape, k, normal, n, normal_only):
    """Penalty springs that tie slave nodes to points on a master surface.
    normal_only: only the motion along the master face normal is tied, so the
    faces can slide (used for the balls between rail and guide block)."""
    m = len(slave)
    idx = np.concatenate([slave[:, None], master_nodes], axis=1)       # (m, 7)
    w = np.concatenate([np.ones((m, 1)), -shape], axis=1)               # (m, 7)
    if normal_only:
        P = normal[:, :, None] * normal[:, None, :]
    else:
        P = np.broadcast_to(np.eye(3), (m, 3, 3))
    c = k * weight
    ke = c[:, None, None, None, None] * w[:, :, None, None, None] * w[:, None, :, None, None] \
        * P[:, None, None, :, :]                                        # (m, 7, 7, 3, 3)
    ke = ke.transpose(0, 1, 3, 2, 4).reshape(m, 21, 21)
    dof = (3 * idx[:, :, None] + np.arange(3)).reshape(m, 21)
    rows = np.repeat(dof[:, :, None], 21, axis=2)
    cols = np.repeat(dof[:, None, :], 21, axis=1)
    return _coo(rows, cols, ke, 3 * n)


def rigid_modes(xyz):
    n = len(xyz)
    B = np.zeros((3 * n, 6))
    c = xyz - xyz.mean(axis=0)
    for i in range(3):
        B[i::3, i] = 1.0
    B[0::3, 3], B[1::3, 3] = -c[:, 1], c[:, 0]
    B[1::3, 4], B[2::3, 4] = -c[:, 2], c[:, 1]
    B[0::3, 5], B[2::3, 5] = c[:, 2], -c[:, 0]
    return B
