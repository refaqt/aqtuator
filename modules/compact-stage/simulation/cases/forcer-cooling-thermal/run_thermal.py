# SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Temperature and thermal deformation of the compact stage, motor at rated current.

Run it with the Python that comes with FreeCAD, from the repository root,
after build_geometry.py:

    freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/run_thermal.py

It needs numpy, scipy and (for speed) pyamg in the FreeCAD Python. On Linux,
`bash setup-fem.sh` installs them.

Steps:

1. Mesh each body with Gmsh (meshing.py).
2. Sort every outer face of every body: wetted by the water, touching or
   facing another body across a thin gap, on the machine table, or open to
   the air.
3. Build the heat model (fem.py): conduction in each body, contact
   conductance at each joint, air across thin gaps, still-air convection and
   radiation, and the water film in the channel and the block passages.
4. Solve the steady state at the rated current. The water warms up along its
   path, and the copper loss rises with the coil temperature; both are
   solved by repeating the solve until nothing changes.
5. Repeat for each input that is not known (sweeps), and solve the warm-up
   from a cold start.
6. Solve the thermal growth of the whole stage at the steady temperature
   (linear elasticity, same mesh), and read the tilt of carriage-top, the
   change of the air gap, the shift of the read head and the load on the
   guide blocks.

Output:
- simulation/results/forcer-cooling-thermal/thermal.json (committed)
- simulation/results/forcer-cooling-thermal/exports/fields.npz (not committed):
  the meshes and the fields for the web page.
"""

import functools
import json
import math
import os
import sys
import time
import tomllib

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra

print = functools.partial(print, flush=True)
CASE = "forcer-cooling-thermal"
SIGMA = 5.670e-8
T0 = time.time()


def module_root():
    here = globals().get("__file__")
    if here:
        return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", ".."))
    return os.path.join(os.getcwd(), "modules", "compact-stage")


ROOT = module_root()
sys.path.insert(0, os.path.join(ROOT, "simulation", "cases", CASE))
import fem          # noqa: E402
import hydraulics   # noqa: E402
import meshing      # noqa: E402


def log(msg):
    print("[%6.0f s] %s" % (time.time() - T0, msg))
    sys.stdout.flush()


def load():
    with open(os.path.join(ROOT, "simulation", "cases", CASE, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)
    gdir = os.path.join(ROOT, "simulation", "results", CASE, "exports", "geom")
    path = os.path.join(gdir, "geometry.json")
    if not os.path.exists(path):
        raise SystemExit("ERROR: run build_geometry.py first")
    with open(path) as f:
        geom = json.load(f)
    return cfg, geom, gdir


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class Model:
    def __init__(self, cfg, geom, gdir, scale=1.0):
        self.cfg = cfg
        self.geom = geom
        bodies = [b for b in geom["bodies"] if b["name"] != "water"]
        wb = [b for b in geom["bodies"] if b["name"] == "water"][0]
        cfg["_block_box"] = [b for b in bodies if b["name"] == "cooling_block"][0]["bbox"]
        cfg["_block_box"] = [cfg["_block_box"][i] for i in (0, 3, 1, 4, 2, 5)]
        pc = geom["pocket_ceiling"]
        cfg["_pocket_box"] = pc
        zc = pc[4]
        cfg["_channel_box"] = [wb["bbox"][0], wb["bbox"][3], wb["bbox"][1], wb["bbox"][1] + 32.0,
                               zc, zc + cfg["hydraulics"]["channel_d"]]
        self.removed_faces = {}
        self.names, self.mats, self.xyz, self.tets, self.offset = [], [], [], [], []
        n = 0
        for b in bodies + [wb]:
            sc = scale.get(b["name"], scale.get("_default", 1.0)) if isinstance(scale, dict) else scale
            msh, removed = meshing.mesh_body(b["name"], gdir, cfg, scale=sc, log=log)
            if removed:
                self.removed_faces[b["name"]] = removed
            xyz, tets = meshing.read_msh(msh)
            vol, _ = fem.geometry(xyz, tets)
            if (vol <= 0).any():
                raise SystemExit("ERROR: %s has inverted elements" % b["name"])
            err = abs(vol.sum() - b["volume"]) / b["volume"]
            log("mesh %-16s %8d nodes %8d elements, volume error %.2f %%" % (
                b["name"], len(xyz), len(tets), 100 * err))
            if err > (0.03 if b["name"] == "water" else 0.01):
                raise SystemExit("ERROR: the mesh of %s lost %.1f %% of its volume" % (b["name"], 100 * err))
            if b["name"] == "water":
                self.wxyz, self.wtets = xyz, tets
                continue
            self.names.append(b["name"])
            self.mats.append(b["material"])
            self.xyz.append(xyz)
            self.tets.append(tets)
            self.offset.append(n)
            n += len(xyz)
        self.n = n
        self.X = np.concatenate(self.xyz)
        self.index = {nm: i for i, nm in enumerate(self.names)}
        self.faces = [fem.boundary_faces(x, t) for x, t in zip(self.xyz, self.tets)]
        self.surf = [fem.Surface(x, f) for x, f in zip(self.xyz, self.faces)]
        self.wfaces = fem.boundary_faces(self.wxyz, self.wtets)
        self.wsurf = fem.Surface(self.wxyz, self.wfaces)
        self.vol = [fem.geometry(x, t)[0] for x, t in zip(self.xyz, self.tets)]
        self.classify()
        self.water_path()
        self.build()

    # -- face sorting -----------------------------------------------------
    def pair_kind(self, a, b):
        names = {self.names[a], self.names[b]}
        if names == {"carriage_bottom", "forcer"}:
            return "forcer_face"
        if names == {"carriage_bottom", "cooling_block"}:
            return "resin_block"
        if any(x.startswith("rail") for x in names) and any(x.startswith("block") for x in names):
            return "balls"
        return "metal_bolted"

    def classify(self):
        cfg = self.cfg
        gap_max = 1.0
        a = cfg["air"]
        ch = cfg["_channel_box"]
        self.fclass = []
        for i, f in enumerate(self.faces):
            m = len(f["area"])
            kind = np.array(["air"] * m, dtype=object)
            partner = np.full(m, -1)
            gap = np.zeros(m)
            c, nrm = f["centroid"], f["normal"]
            # water
            pw = self.wsurf.project(c)
            wet = (pw["dist"] < 0.15) & (np.einsum("ij,ij->i", nrm, pw["normal"]) < -0.5)
            # other solids
            best = np.full(m, np.inf)
            bb_i = self.X[self.offset[i]:self.offset[i] + len(self.xyz[i])]
            lo, hi = bb_i.min(axis=0) - gap_max, bb_i.max(axis=0) + gap_max
            for j in range(len(self.names)):
                if j == i:
                    continue
                xj = self.xyz[j]
                if (xj.max(axis=0) < lo).any() or (xj.min(axis=0) > hi).any():
                    continue
                near = np.all((c > xj.min(axis=0) - gap_max) & (c < xj.max(axis=0) + gap_max), axis=1)
                if not near.any():
                    continue
                idx = np.where(near)[0]
                pj = self.surf[j].project(c[idx])
                d = pj["signed"]
                ok = (d > -0.05) & (d < gap_max) & (np.einsum("ij,ij->i", nrm[idx], pj["normal"]) < -0.8) \
                    & (pj["dist"] < gap_max + 0.05)
                take = ok & (np.abs(d) < best[idx])
                best[idx[take]] = np.abs(d[take])
                partner[idx[take]] = j
                gap[idx[take]] = np.clip(d[take], 0, None)
            has = partner >= 0
            kind[has & (gap < 0.05)] = "contact"
            kind[has & (gap >= 0.05)] = "gap"
            kind[wet] = "water"
            partner[wet] = -1
            if self.names[i] == "base":
                down = nrm[:, 2] < -0.99
                kind[down & (c[:, 2] < 1e-3)] = "table"
                kind[down & (c[:, 2] > 1e-3) & (c[:, 2] < cfg["contact"]["table_gap"] + 0.01)] = "table_gap"
            zone = np.where((c[:, 2] < ch[5] + 0.01) & (c[:, 2] > ch[4] - 0.01), "channel", "passage")
            # open faces: still air, film by direction; faces under the
            # carriage inside the base walls count as a cavity
            cav = (c[:, 0] > 10) & (c[:, 0] < 430) & (c[:, 1] > 12) & (c[:, 1] < 198) & (c[:, 2] < 40 - 1e-6)
            h = np.where(nrm[:, 2] > 0.7, a["h_up"], np.where(nrm[:, 2] < -0.7, a["h_down"], a["h_side"]))
            h = np.where(cav, a["h_cavity"], h)
            self.fclass.append({"kind": kind, "partner": partner, "gap": gap, "zone": zone,
                                "h_conv": h, "cavity": cav})
            counts = {k: float(f["area"][kind == k].sum()) for k in
                      ("air", "contact", "gap", "water", "table", "table_gap")}
            log("faces %-16s " % self.names[i] + ", ".join("%s %.0f mm2" % (k, v) for k, v in counts.items() if v))

    # -- water path ---------------------------------------------------------
    def water_path(self):
        g = self.geom
        x, t = self.wxyz, self.wtets
        e = np.concatenate([t[:, [a, b]] for a, b in fem.EDGES + [(0, 4), (1, 4), (1, 5), (2, 5), (2, 6),
                                                                  (0, 6), (0, 7), (3, 7), (1, 8), (3, 8),
                                                                  (2, 9), (3, 9)]])
        w = np.linalg.norm(x[e[:, 0]] - x[e[:, 1]], axis=1)
        G = sp.coo_matrix((w, (e[:, 0], e[:, 1])), shape=(len(x), len(x))).tocsr()
        G = G.maximum(G.T)
        pin = np.array(g["fitting_in"])
        pout = np.array(g["fitting_out"])
        di = np.linalg.norm(x - pin, axis=1)
        do = np.linalg.norm(x - pout, axis=1)
        src = np.where(di < di.min() + 0.3)[0]
        dst = np.where(do < do.min() + 0.3)[0]
        s = dijkstra(G, indices=src, min_only=True)
        self.s_water = s
        self.s_total = float(s[dst].mean())
        # s of each wetted face, from the nearest water node
        from scipy.spatial import cKDTree
        tree = cKDTree(x)
        self.wet = []
        for i, f in enumerate(self.faces):
            k = self.fclass[i]["kind"] == "water"
            if not k.any():
                continue
            idx = np.where(k)[0]
            _, nn = tree.query(f["centroid"][idx])
            self.wet.append({"body": i, "faces": idx, "s": s[nn], "zone": self.fclass[i]["zone"][idx]})
        ch_area = sum(self.faces[w["body"]]["area"][w["faces"][w["zone"] == "channel"]].sum() for w in self.wet)
        pa_area = sum(self.faces[w["body"]]["area"][w["faces"][w["zone"] == "passage"]].sum() for w in self.wet)
        self.wet_area = {"channel": float(ch_area), "passage": float(pa_area)}
        log("water path %.0f mm long; wetted area channel %.0f mm2, passages and ports %.0f mm2"
            % (self.s_total, ch_area, pa_area))

    # -- matrices -----------------------------------------------------------
    def build(self):
        n = self.n
        self.K_body = []
        for i in range(len(self.names)):
            K, _ = fem.conduction(self.xyz[i], self.tets[i], np.ones(len(self.tets[i])), self.offset[i], n)
            self.K_body.append(K)
        # links between bodies (unit h = 1 W/(m2 K)), split by joint kind;
        # air gaps carry their own h = k_air / gap
        kinds = ["forcer_face", "resin_block", "balls", "metal_bolted", "air_gap"]
        self.K_link = {k: sp.csr_matrix((n, n)) for k in kinds}
        self.links = []
        k_air = self.cfg["air"]["k"]
        for i, f in enumerate(self.faces):
            fc = self.fclass[i]
            for j in range(len(self.names)):
                sel = (fc["partner"] == j) & np.isin(fc["kind"], ["contact", "gap"])
                if not sel.any():
                    continue
                tri = f["tri"][sel]
                area = f["area"][sel]
                for kind_name, mask in (("contact", fc["kind"][sel] == "contact"),
                                        ("gap", fc["kind"][sel] == "gap")):
                    if not mask.any():
                        continue
                    hface = np.ones(mask.sum()) if kind_name == "contact" else \
                        k_air / (fc["gap"][sel][mask] * 1e-3)
                    w = np.zeros(len(self.xyz[i]))
                    np.add.at(w, tri[mask], (area[mask] * hface)[:, None] * fem.TRI_LUMP[None])
                    nodes = np.where(w > 0)[0]
                    pj = self.surf[j].project(self.xyz[i][nodes])
                    cat = self.pair_kind(i, j) if kind_name == "contact" else "air_gap"
                    # half from each side, so the link is the same both ways
                    K = fem.link_scalar(nodes + self.offset[i], 0.5 * w[nodes] * 1e-6,
                                        pj["nodes"] + self.offset[j], fem.shape_tri(pj["lam"]), 1.0, n)
                    self.K_link[cat] = self.K_link[cat] + K
                    if kind_name == "contact":
                        self.links.append({"a": i, "b": j, "cat": cat, "nodes": nodes, "w": w[nodes],
                                           "mnodes": pj["nodes"], "shape": fem.shape_tri(pj["lam"]),
                                           "normal": pj["normal"]})
        # films: still air, radiation, table, water
        self.films = {}
        for cat in ("conv", "rad", "table", "table_gap", "water_channel", "water_passage"):
            self.films[cat] = []
        for i, f in enumerate(self.faces):
            fc = self.fclass[i]
            air = fc["kind"] == "air"
            self.films["conv"].append((i, np.where(air)[0], fc["h_conv"][air]))
            open_air = air & ~fc["cavity"]
            self.films["rad"].append((i, np.where(open_air)[0], np.ones(open_air.sum())))
            tb = fc["kind"] == "table"
            self.films["table"].append((i, np.where(tb)[0], np.ones(tb.sum())))
            tg = fc["kind"] == "table_gap"
            self.films["table_gap"].append((i, np.where(tg)[0],
                                            self.cfg["air"]["k"] / (f["centroid"][tg, 2] * 1e-3)))
        for w in self.wet:
            for zone in ("channel", "passage"):
                sel = w["zone"] == zone
                self.films["water_" + zone].append((w["body"], w["faces"][sel], np.ones(sel.sum())))
        self.K_film = {}
        for cat, items in self.films.items():
            K = sp.csr_matrix((n, n))
            for i, idx, h in items:
                if len(idx):
                    f = self.faces[i]
                    K = K + fem.film(f["tri"][idx], f["area"][idx], h * 1e-6, self.offset[i], n)
            self.K_film[cat] = K
        # heat source in the forcer
        fi = self.index["forcer"]
        self.V_forcer = float(self.vol[fi].sum())
        self.f_unit_source = fem.source(self.tets[fi], self.vol[fi], np.full(len(self.tets[fi]), 1.0 / self.V_forcer),
                                        self.offset[fi], n)
        # forcer mounting face nodes (touching carriage-bottom)
        f = self.faces[fi]
        sel = self.fclass[fi]["partner"] == self.index["carriage_bottom"]
        sel &= self.fclass[fi]["kind"] == "contact"
        self.forcer_face_nodes = np.unique(f["tri"][sel])
        self.forcer_face_area = float(f["area"][sel].sum())
        wet = self.fclass[fi]["kind"] == "water"
        self.forcer_wet_area = float(f["area"][wet].sum())
        log("matrices built: %d unknowns" % n)

    # -- forcer calibration --------------------------------------------------
    def calibrate_forcer(self, p):
        """Conductivity of the forcer block that gives the data sheet thermal
        resistance.

        The data sheet test holds the mounting face at one temperature. Here
        the whole top face of the forcer (dry and wetted parts) is held at one
        temperature, inside the full model: some heat also leaves through the
        bottom of the forcer, across the air gap to the magnet track, as it
        does in a real test on a motor that sits on its track. The
        conductivity is changed until the hottest point is rth * P above the
        face. Counting the air gap path this way makes the forcer block more
        resistive, so the coil comes out hotter: the safe side."""
        fi = self.index["forcer"]
        xf = self.xyz[fi]
        top = np.unique(self.faces[fi]["tri"][self.faces[fi]["normal"][:, 2] > 0.99])
        top = top[xf[top, 2] > xf[:, 2].max() - 1e-6]
        self.forcer_top_nodes = top
        fix = top + self.offset[fi]
        free = np.setdiff1d(np.arange(self.n), fix)
        q = dict(p, t_air=0.0, t_in=0.0)
        f = self.loads(q, lambda s: np.zeros(len(s)), 1.0)       # 1 W, all sinks at 0
        rth = self.cfg["motor"]["rth"]
        k = 1.85e-3
        T = None
        hist = []
        for it in range(6):
            self.k_forcer = k
            K = self.matrix(p)
            solve = fem.solver(K[free][:, free].tocsr())
            T = solve(f[free], x0=T)
            Tf = np.zeros(self.n)
            Tf[free] = T
            r = float(self.body_T(Tf, fi).max())
            hist.append((k * 1000, r))
            log("forcer conductivity %.3f W/(m K): %.3f K/W" % (k * 1000, r))
            if abs(r / rth - 1) < 2e-3:
                break
            # r is close to a / k; step in log space
            k *= (r / rth) ** 1.05
        self.k_forcer = k
        self.calibration = {"k_W_per_mK": k * 1000, "rth_model": r, "steps": hist,
                            "face_area_mm2": float(self.faces[fi]["area"][
                                (self.faces[fi]["normal"][:, 2] > 0.99) &
                                (self.faces[fi]["centroid"][:, 2] > xf[:, 2].max() - 1e-6)].sum())}
        return k

    # -- steady solve ----------------------------------------------------------
    def conductivities(self, p):
        mats = self.cfg["materials"]
        ks = []
        for nm, mat in zip(self.names, self.mats):
            if mat == "forcer":
                ks.append(self.k_forcer)
            elif mat == "al7075":
                ks.append(p.get("k_al", mats["al7075"]["k"]) / 1000)
            else:
                ks.append(mats[mat]["k"] / 1000)
        return ks

    def matrix(self, p):
        c = self.cfg["contact"]
        K = sum(k * Kb for k, Kb in zip(self.conductivities(p), self.K_body))
        K = K + p.get("forcer_face", c["forcer_face"]) * self.K_link["forcer_face"]
        K = K + p.get("resin_block", c["resin_block"]) * self.K_link["resin_block"]
        K = K + p.get("balls", c["balls"]) * self.K_link["balls"]
        K = K + p.get("metal_bolted", c["metal_bolted"]) * self.K_link["metal_bolted"]
        K = K + self.K_link["air_gap"]
        K = K + self.K_film["conv"] + self.h_rad(p) * self.K_film["rad"]
        K = K + p.get("table", c["table"]) * self.K_film["table"] + self.K_film["table_gap"]
        K = K + p["h_channel"] * self.K_film["water_channel"] + p["h_passage"] * self.K_film["water_passage"]
        return K.tocsr()

    def h_rad(self, p):
        eps = p.get("emissivity", self.cfg["air"]["emissivity_bare"])
        tm = p["t_air"] + 273.15 + 5.0
        return eps * 4 * SIGMA * tm ** 3

    def loads(self, p, Tw_of_s, P):
        n = self.n
        f = P * self.f_unit_source
        for cat, t_sink, scale in (("conv", p["t_air"], 1.0), ("rad", p["t_air"], self.h_rad(p)),
                                   ("table", p["t_air"], p.get("table", self.cfg["contact"]["table"])),
                                   ("table_gap", p["t_air"], 1.0)):
            for i, idx, h in self.films[cat]:
                if len(idx):
                    fc = self.faces[i]
                    f += fem.film_load(fc["tri"][idx], fc["area"][idx], h * scale * 1e-6,
                                       np.full(len(idx), t_sink), self.offset[i], n)
        for w in self.wet:
            fc = self.faces[w["body"]]
            for zone, h in (("channel", p["h_channel"]), ("passage", p["h_passage"])):
                sel = w["zone"] == zone
                if sel.any():
                    idx = w["faces"][sel]
                    f += fem.film_load(fc["tri"][idx], fc["area"][idx], np.full(len(idx), h * 1e-6),
                                       Tw_of_s(w["s"][sel]), self.offset[w["body"]], n)
        return f

    def water_heat(self, T, p, Tw_of_s):
        """Heat into the water from each wetted face, binned along the path."""
        nb = 400
        edges = np.linspace(0, self.s_total * 1.0001, nb + 1)
        q = np.zeros(nb)
        for w in self.wet:
            fc = self.faces[w["body"]]
            for zone, h in (("channel", p["h_channel"]), ("passage", p["h_passage"])):
                sel = w["zone"] == zone
                if not sel.any():
                    continue
                idx = w["faces"][sel]
                tri = fc["tri"][idx] + self.offset[w["body"]]
                tm = T[tri] @ fem.TRI_V
                qf = h * 1e-6 * fc["area"][idx] * (tm - Tw_of_s(w["s"][sel]))
                b = np.clip(np.searchsorted(edges, w["s"][sel]) - 1, 0, nb - 1)
                np.add.at(q, b, qf)
        return edges, q

    def steady(self, p, solve=None, T_init=None, tol=2e-3):
        cfg = self.cfg
        mo = cfg["motor"]
        mdot_c = cfg["water"]["rho"] * p["flow"] / 60000.0 * cfg["water"]["cp"]   # W/K
        if solve is None:
            solve = fem.solver(self.matrix(p))
        edges = np.array([0.0, self.s_total * 1.0001])
        tw = np.array([p["t_in"], p["t_in"]])
        T = T_init
        P = 1.5 * mo["current"] ** 2 * mo["r_ll_25"]
        for it in range(40):
            Tw = lambda s, e=edges.copy(), v=tw.copy(): np.interp(s, e, v)
            T = solve(self.loads(p, Tw, P), x0=T)
            e2, q = self.water_heat(T, p, Tw)
            tw_new = p["t_in"] + np.concatenate([[0.0], np.cumsum(q)]) / mdot_c
            fi = self.index["forcer"]
            Tf = T[self.offset[fi]:self.offset[fi] + len(self.xyz[fi])]
            t_coil = Tf.max()
            r = mo["r_ll_25"] + (mo["r_ll_120"] - mo["r_ll_25"]) * (t_coil - 25.0) / 95.0
            P_new = 1.5 * mo["current"] ** 2 * r
            change = max(np.abs(np.interp(e2, edges, tw) - tw_new).max(), abs(P_new - P) * 0.87)
            edges, tw, P = e2, tw_new, P_new
            if change < tol and it > 1:
                break
        Tw = lambda s, e=edges.copy(), v=tw.copy(): np.interp(s, e, v)
        T = solve(self.loads(p, Tw, P), x0=T)
        return {"T": T, "P": P, "s": edges, "tw": tw, "iterations": it + 1, "Tw": Tw}

    # -- results ------------------------------------------------------------
    def body_T(self, T, i):
        return T[self.offset[i]:self.offset[i] + len(self.xyz[i])]

    def summary(self, res, p):
        T = res["T"]
        out = {"P_loss_W": res["P"], "bodies": {}}
        for i, nm in enumerate(self.names):
            Tb = self.body_T(T, i)
            te = Tb[self.tets[i]] @ fem.TET_V
            out["bodies"][nm] = {"min": float(Tb.min()), "max": float(Tb.max()),
                                 "mean": float((te * self.vol[i]).sum() / self.vol[i].sum())}
        fi = self.index["forcer"]
        out["coil_max"] = out["bodies"]["forcer"]["max"]
        out["coil_mean"] = out["bodies"]["forcer"]["mean"]
        Tf = self.body_T(T, fi)
        # mounting face: the whole top face (dry and wetted), as in the data sheet
        out["forcer_face_mean"] = float(Tf[self.forcer_top_nodes].mean())
        out["forcer_face_max"] = float(Tf[self.forcer_top_nodes].max())
        out["forcer_dry_face_mean"] = float(Tf[self.forcer_face_nodes].mean())
        out["water_out"] = float(res["tw"][-1])
        out["water_rise"] = float(res["tw"][-1] - p["t_in"])
        out["coil_minus_water_in"] = out["coil_max"] - p["t_in"]
        out["iterations"] = res["iterations"]
        # heat balance
        bal = {}
        _, q = self.water_heat(T, p, res["Tw"])
        bal["water"] = float(q.sum())
        hr = self.h_rad(p)
        for cat, scale in (("conv", 1.0), ("rad", hr), ("table", p.get("table", self.cfg["contact"]["table"])),
                           ("table_gap", 1.0)):
            tot = 0.0
            for i, idx, h in self.films[cat]:
                if len(idx):
                    fc = self.faces[i]
                    tri = fc["tri"][idx] + self.offset[i]
                    tot += float((h * scale * 1e-6 * fc["area"][idx] * (T[tri] @ fem.TRI_V - p["t_air"])).sum())
            bal[cat] = tot
        bal["total_out"] = sum(bal.values())
        bal["source"] = res["P"]
        bal["error_pct"] = 100 * (bal["total_out"] - res["P"]) / res["P"]
        out["balance"] = bal
        # cooling block details
        bi = self.index["cooling_block"]
        Tb = self.body_T(T, bi)
        xb = self.xyz[bi]
        y_side = self.geom["placements"]["carriage_bottom001"][1] + 208.0
        out["cooling_block_head_max"] = float(Tb[xb[:, 1] > y_side].max()) if (xb[:, 1] > y_side).any() else None
        out["cooling_block_p99"] = float(np.percentile(Tb, 99))
        return out


# ---------------------------------------------------------------------------
# Thermal growth
# ---------------------------------------------------------------------------

def mechanics(model, T, t_ref, support="free", soft_forcer=False):
    cfg = model.cfg
    mats = cfg["materials"]
    n = model.n
    K = None
    f = np.zeros(3 * n)
    Eb = {}
    for i, (nm, mat) in enumerate(zip(model.names, model.mats)):
        mm = mats[mat]
        ne = len(model.tets[i])
        # variant: the forcer does not hold carriage-bottom (its screws let it slide)
        E = np.full(ne, mm["E"] * (1e-3 if (soft_forcer and mat == "forcer") else 1.0))
        nu = np.full(ne, mm["nu"])
        al = np.full(ne, mm["alpha"])
        Eb[i] = mm["E"]
        dT = model.body_T(T, i) - t_ref
        Ki, fi = fem.elasticity(model.xyz[i], model.tets[i], E, nu, al, dT, model.offset[i], n)
        K = Ki if K is None else K + Ki
        f += fi
    c = cfg["contact"]
    k_ball = c["ball_stiffness_n_per_um"] * 1000.0 / c["ball_contact_area"]     # N/mm3
    for L in model.links:
        a, b = L["a"], L["b"]
        if L["cat"] == "balls":
            k = k_ball
            normal_only = True
        else:
            k = c["tie_factor"] * min(Eb[a], Eb[b]) / 1.0
            normal_only = False
        K = K + fem.link_vector(L["nodes"] + model.offset[a], 0.5 * L["w"], L["mnodes"] + model.offset[b],
                                L["shape"], k, L["normal"], n, normal_only)
    # supports
    bi = model.index["base"]
    fc = model.faces[bi]
    sel = model.fclass[bi]["kind"] == "table"
    bottom = np.unique(fc["tri"][sel]) + model.offset[bi]
    fixed = list(3 * bottom + 2)
    xb = model.X[bottom]
    xm = 0.5 * (model.X[:, 0].min() + model.X[:, 0].max())
    a1 = bottom[np.argmin(np.abs(xb[:, 0] - xm) + np.abs(xb[:, 1] - xb[:, 1].min()))]
    a2 = bottom[np.argmin(np.abs(xb[:, 0] - xm) + np.abs(xb[:, 1] - xb[:, 1].max()))]
    if support == "free":
        fixed += [3 * a1, 3 * a1 + 1, 3 * a2]
    else:
        fixed += list(3 * bottom) + list(3 * bottom + 1)
    fixed = np.unique(np.array(fixed))
    free = np.setdiff1d(np.arange(3 * n), fixed)
    K = K.tocsr()
    Kf = K[free][:, free].tocsr()
    B = fem.rigid_modes(model.X)[free]
    solve = fem.solver(Kf, rigid=B)
    u = np.zeros(3 * n)
    u[free] = solve(f[free], tol=1e-9)
    return u.reshape(n, 3)


def mech_summary(model, u, T, t_ref):
    cfg = model.cfg
    out = {}
    X = model.X
    ci = model.index["carriage_top"]
    sl = slice(model.offset[ci], model.offset[ci] + len(model.xyz[ci]))
    xc = X[sl]
    top = xc[:, 2] > xc[:, 2].max() - 1e-6
    pts = xc[top]
    uz = u[sl][top, 2]
    A = np.c_[np.ones(len(pts)), pts[:, 0] - 220.0, pts[:, 1] - 105.0]
    coef, *_ = np.linalg.lstsq(A, uz, rcond=None)
    resid = uz - A @ coef
    out["top_lift_um"] = float(coef[0] * 1000)
    out["top_pitch_urad"] = float(coef[1] * 1e6)       # slope along x
    out["top_roll_urad"] = float(coef[2] * 1e6)        # slope along y
    out["top_flatness_um"] = float((resid.max() - resid.min()) * 1000)
    out["top_uz_min_um"] = float(uz.min() * 1000)
    out["top_uz_max_um"] = float(uz.max() * 1000)
    ux = u[sl][top, 0]
    uy = u[sl][top, 1]
    out["top_ux_mean_um"] = float(ux.mean() * 1000)
    out["top_uy_mean_um"] = float(uy.mean() * 1000)
    # centre of the top face
    ic = np.argmin(np.linalg.norm(pts[:, :2] - [220.0, 105.0], axis=1))
    out["top_centre_u_um"] = (u[sl][top][ic] * 1000).tolist()
    # air gap between forcer and track
    fi, ti = model.index["forcer"], model.index["track"]
    xf = model.xyz[fi]
    bottom = xf[:, 2] < xf[:, 2].min() + 1e-6
    nodes = np.where(bottom)[0]
    pj = model.surf[ti].project(xf[nodes])
    ut = (u[pj["nodes"] + model.offset[ti]] * fem.shape_tri(pj["lam"])[:, :, None]).sum(axis=1)
    duf = u[nodes + model.offset[fi]]
    dgap = (duf[:, 2] - ut[:, 2]) * 1000
    out["air_gap_change_um"] = {"mean": float(dgap.mean()), "min": float(dgap.min()), "max": float(dgap.max())}
    # read head against the scale
    g = cfg["geometry"]
    cb = model.index["carriage_bottom"]
    base = model.index["base"]

    def at(body, p):
        xb = model.xyz[body]
        k = np.argmin(np.linalg.norm(xb - np.array(p), axis=1))
        return u[k + model.offset[body]], xb[k]
    u_rh, x_rh = at(cb, g["read_head_mount"])
    u_sc, x_sc = at(base, g["scale_point"])
    out["read_head_ux_um"] = float(u_rh[0] * 1000)
    out["scale_ux_um"] = float(u_sc[0] * 1000)
    out["read_head_minus_scale_um"] = float((u_rh[0] - u_sc[0]) * 1000)
    out["table_centre_minus_read_head_ux_um"] = float((out["top_centre_u_um"][0] / 1000 - u_rh[0]) * 1000)
    # guide block loads from the ball springs
    c = cfg["contact"]
    k_ball = c["ball_stiffness_n_per_um"] * 1000.0 / c["ball_contact_area"]
    loads = {}
    for L in model.links:
        if L["cat"] != "balls":
            continue
        a, b = L["a"], L["b"]
        us = u[L["nodes"] + model.offset[a]]
        um = (u[L["mnodes"] + model.offset[b]] * L["shape"][:, :, None]).sum(axis=1)
        dn = np.einsum("ij,ij->i", us - um, L["normal"])
        F = 0.5 * k_ball * L["w"] * dn                            # N, along the master normal
        vec = F[:, None] * L["normal"]
        blk = model.names[a] if model.names[a].startswith("block") else model.names[b]
        sgn = 1.0 if model.names[a].startswith("block") else -1.0
        d = loads.setdefault(blk, {"Fy_pos": 0.0, "Fy_neg": 0.0, "Fz": 0.0, "abs_sum": 0.0})
        vy = sgn * vec[:, 1]
        d["Fy_pos"] += float(vy[vy > 0].sum())
        d["Fy_neg"] += float(vy[vy < 0].sum())
        d["Fz"] += float((sgn * vec[:, 2]).sum())
        d["abs_sum"] += float(np.abs(F).sum())
    out["block_loads_N"] = loads
    # stress in the cooling block
    mats = cfg["materials"]
    bi = model.index["cooling_block"]
    mm = mats["resin"]
    ne = len(model.tets[bi])
    s = fem.stress_centroid(model.xyz[bi], model.tets[bi], np.full(ne, mm["E"]), np.full(ne, mm["nu"]),
                            np.full(ne, mm["alpha"]), model.body_T(T, bi) - t_ref,
                            u[model.offset[bi]:model.offset[bi] + len(model.xyz[bi])])
    vm = fem.von_mises(s)
    out["cooling_block_vm_MPa"] = {"max": float(vm.max()), "p99": float(np.percentile(vm, 99)),
                                   "p95": float(np.percentile(vm, 95))}
    out["u_max_um"] = float(np.linalg.norm(u, axis=1).max() * 1000)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def params(cfg, flow, **kw):
    hc, re_c, v_c = hydraulics.film(cfg, flow, "channel")
    hp, re_p, v_p = hydraulics.film(cfg, flow, "passage")
    p = {"flow": flow, "t_in": cfg["water"]["t_in"], "t_air": cfg["air"]["t_air"],
         "h_channel": hc, "h_passage": hp, "re_channel": re_c, "re_passage": re_p}
    p.update(kw)
    if "h_scale" in kw:
        p["h_channel"] *= kw["h_scale"]
        p["h_passage"] *= kw["h_scale"]
    return p


def main_flow(cfg):
    pumps = cfg["pump"]
    rec = [p for p in pumps if p.get("recommended")][0]
    op = hydraulics.operating_point(cfg, rec)
    return op["q_axes"][0], rec["name"], op


def transient(model, p, t_end=4 * 3600.0):
    cfg = model.cfg
    mats = cfg["materials"]
    n = model.n
    C = None
    for i, mat in enumerate(model.mats):
        if mat == "forcer":
            rc = cfg["motor"]["mass"] / (model.V_forcer * 1e-9) * cfg["motor"]["c_specific"] * 1e-9
        else:
            rc = mats[mat]["rho"] * mats[mat]["c"] * 1e-9
        Ci = fem.capacity(model.tets[i], model.vol[i], np.full(len(model.tets[i]), rc), model.offset[i], n)
        C = Ci if C is None else C + Ci
    K = model.matrix(p)
    mo = cfg["motor"]
    mdot_c = cfg["water"]["rho"] * p["flow"] / 60000.0 * cfg["water"]["cp"]
    T = np.full(n, p["t_air"])
    T[:] = p["t_in"] if abs(p["t_in"] - p["t_air"]) < 1e-9 else p["t_air"]
    edges = np.array([0.0, model.s_total * 1.0001])
    tw = np.array([p["t_in"], p["t_in"]])
    P = 1.5 * mo["current"] ** 2 * mo["r_ll_25"]
    plan = [(5.0, 12), (30.0, 18), (120.0, 25), (600.0, int((t_end - 3600.0) / 600.0))]
    t = 0.0
    hist = []
    fi = model.index["forcer"]

    def record():
        s = {"t": t, "P": P, "water_out": float(tw[-1])}
        for i, nm in enumerate(model.names):
            Tb = model.body_T(T, i)
            s[nm + "_max"] = float(Tb.max())
            s[nm + "_mean"] = float(Tb.mean())
        hist.append(s)
    record()
    for dt, steps in plan:
        A = (C / dt + K).tocsr()
        solve = fem.solver(A)
        for _ in range(steps):
            Tw = lambda s, e=edges.copy(), v=tw.copy(): np.interp(s, e, v)
            b = C @ T / dt + model.loads(p, Tw, P)
            T = solve(b, x0=T)
            t += dt
            e2, q = model.water_heat(T, p, Tw)
            tw = p["t_in"] + np.concatenate([[0.0], np.cumsum(q)]) / mdot_c
            edges = e2
            t_coil = model.body_T(T, fi).max()
            P = 1.5 * mo["current"] ** 2 * (mo["r_ll_25"] + (mo["r_ll_120"] - mo["r_ll_25"]) * (t_coil - 25.0) / 95.0)
            record()
        log("warm-up: %.0f s, coil %.2f C" % (t, hist[-1]["forcer_max"]))
    return hist


def main():
    cfg, geom, gdir = load()
    scale = float(os.environ.get("THERMAL_MESH_SCALE", "1.0"))
    quick = os.environ.get("THERMAL_QUICK", "") == "1"
    out_dir = os.path.join(ROOT, "simulation", "results", CASE)
    model = Model(cfg, geom, gdir, scale=scale)
    flow, pump_name, op = main_flow(cfg)
    model.calibrate_forcer(params(cfg, flow))
    log("main flow %.3f l/min per axis (%s)" % (flow, pump_name))
    t_ref = cfg["air"]["t_air"]

    results = {"flow_main": flow, "pump_main": pump_name, "operating_point": op,
               "mesh": {nm: {"nodes": len(x), "elements": len(t)} for nm, x, t in
                        zip(model.names, model.xyz, model.tets)},
               "mesh_scale": scale, "removed_faces": model.removed_faces,
               "k_forcer": model.k_forcer * 1000, "calibration": model.calibration, "water_path_mm": model.s_total,
               "wetted_area_mm2": model.wet_area, "forcer_face_area_mm2": model.forcer_face_area,
               "forcer_wet_area_mm2": model.forcer_wet_area, "V_forcer_mm3": model.V_forcer}
    face_area = {}
    for i, nm in enumerate(model.names):
        fc = model.fclass[i]
        face_area[nm] = {k: float(model.faces[i]["area"][fc["kind"] == k].sum())
                         for k in ("air", "contact", "gap", "water", "table", "table_gap")}
    results["face_area_mm2"] = face_area

    p_main = params(cfg, flow)
    log("steady state, main case")
    main_res = model.steady(p_main)
    results["main"] = {"params": p_main, **model.summary(main_res, p_main),
                       "water_profile": {"s": main_res["s"][::8].tolist(), "T": main_res["tw"][::8].tolist()}}
    log("coil %.2f C, face %.2f C, water out %.2f C, loss %.1f W, balance %.3f %%" % (
        results["main"]["coil_max"], results["main"]["forcer_face_mean"], results["main"]["water_out"],
        main_res["P"], results["main"]["balance"]["error_pct"]))
    fields = {"T_main": main_res["T"]}

    if scale != 1.0 or quick:
        # mesh check: committed; quick test run: only in the ignored exports folder
        name = "thermal_mesh_s%g.json" % scale if scale != 1.0 else os.path.join("exports", "thermal_quick.json")
        with open(os.path.join(out_dir, name), "w") as f:
            json.dump(results, f, indent=1)
        if scale != 1.0:
            return

    log("thermal growth, main case: coarser mesh for the growth solve")
    mech_scale = {"_default": cfg["mesh"]["mech_scale"], "cooling_block": 1.0, "water": 1.0}
    mech = Model(cfg, geom, gdir, scale=mech_scale)
    # temperatures onto the growth mesh, inside the thermal elements of each part
    Tm = np.zeros(mech.n)
    for i, nm in enumerate(mech.names):
        j = model.index[nm]
        Tm[mech.offset[i]:mech.offset[i] + len(mech.xyz[i])] = fem.interp_tet(
            model.xyz[j], model.tets[j], model.body_T(main_res["T"], j), mech.xyz[i])
    results["mech_mesh"] = {nm: {"nodes": len(x), "elements": len(t)} for nm, x, t in
                            zip(mech.names, mech.xyz, mech.tets)}
    results["mech_removed_faces"] = mech.removed_faces

    def to_thermal(um):
        out = np.zeros((model.n, 3))
        for i, nm in enumerate(model.names):
            j = mech.index[nm]
            out[model.offset[i]:model.offset[i] + len(model.xyz[i])] = fem.interp_tet(
                mech.xyz[j], mech.tets[j], um[mech.offset[j]:mech.offset[j] + len(mech.xyz[j])], model.xyz[i])
        return out
    u = mechanics(mech, Tm, t_ref, "free")
    results["mech_main"] = mech_summary(mech, u, Tm, t_ref)
    fields["u_main"] = to_thermal(u)
    u2 = mechanics(mech, Tm, t_ref, "clamped")
    results["mech_clamped"] = mech_summary(mech, u2, Tm, t_ref)
    fields["u_clamped"] = to_thermal(u2)
    u3 = mechanics(mech, Tm, t_ref, "free", soft_forcer=True)
    results["mech_soft_forcer"] = mech_summary(mech, u3, Tm, t_ref)
    del mech, u, u2, u3
    log("carriage-top lift %.2f um, pitch %.1f urad, roll %.1f urad" % (
        results["mech_main"]["top_lift_um"], results["mech_main"]["top_pitch_urad"],
        results["mech_main"]["top_roll_urad"]))

    if not quick:
        sweeps = []
        c = cfg["contact"]

        def run(label, group, p, keep=None):
            r = model.steady(p, T_init=main_res["T"])
            s = model.summary(r, p)
            s.pop("bodies_full", None)
            sweeps.append({"label": label, "group": group, "params": {k: v for k, v in p.items()
                                                                      if not callable(v)}, **s})
            log("sweep %-34s coil %.2f C, block max %.2f C" % (label, s["coil_max"],
                                                               s["bodies"]["cooling_block"]["max"]))
            if keep:
                fields[keep] = r["T"]
        for q in cfg["water"]["flows_sweep"]:
            run("flow %.2f l/min" % q, "flow", params(cfg, q))
        for ta in cfg["air"]["t_air_sweep"]:
            if ta != cfg["air"]["t_air"]:
                run("air %.0f C" % ta, "air", params(cfg, flow, t_air=ta))
        for key in ("forcer_face", "metal_bolted", "resin_block", "balls", "table"):
            lo, hi = c[key + "_range"]
            run("%s low (%g W/m2K)" % (key, lo), "contact", params(cfg, flow, **{key: lo}))
            run("%s high (%g W/m2K)" % (key, hi), "contact", params(cfg, flow, **{key: hi}))
        run("anodised surfaces", "surface", params(cfg, flow, emissivity=cfg["air"]["emissivity_anodised"]))
        run("water film x 0.5", "water film", params(cfg, flow, h_scale=0.5))
        run("water film x 2", "water film", params(cfg, flow, h_scale=2.0))
        mats = cfg["materials"]
        run("7075 k -10 %", "alloy", params(cfg, flow, k_al=0.9 * mats["al7075"]["k"]))
        for pump in cfg["pump"]:
            opp = hydraulics.operating_point(cfg, pump)
            qa = opp["q_axes"][0]
            run("pump: %s" % pump["name"], "pump", params(cfg, qa))
        results["sweeps"] = sweeps

        log("warm-up from cold")
        results["transient"] = transient(model, p_main)

    np.savez_compressed(os.path.join(out_dir, "exports", "fields.npz"),
                        names=np.array(model.names), offsets=np.array(model.offset),
                        X=model.X, **{"tets_%d" % i: t for i, t in enumerate(model.tets)},
                        **{"tri_%d" % i: f["tri"] for i, f in enumerate(model.faces)},
                        **{"kind_%d" % i: model.fclass[i]["kind"].astype(str) for i in range(len(model.names))},
                        wxyz=model.wxyz, wtri=model.wfaces["tri"], s_water=model.s_water,
                        **fields)
    name = os.path.join("exports", "thermal_quick.json") if quick else "thermal.json"
    with open(os.path.join(out_dir, name), "w") as f:
        json.dump(results, f, indent=1)
    log("Done: %s" % os.path.join(out_dir, name))


if not os.environ.get("THERMAL_NO_MAIN"):
    main()
