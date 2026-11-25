# SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Write the data of the thermal results page.

Run it with the Python that comes with FreeCAD, from the repository root,
after run_thermal.py:

    freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/export_web.py

It writes two files into simulation/cases/forcer-cooling-thermal-results/ at
the repository root:

- thermal_data.js: every number of the page (results, sweeps, warm-up,
  pump and flow, materials, inputs, checks).
- thermal_fields.js: a light surface mesh of each body for the 3D views, with
  the temperature, the thermal growth and the boundary condition of each
  point.

The 3D surfaces are new, coarse surface meshes of the same STEP files. Each
point takes its values from the closest point of the solver mesh.
"""

import base64
import functools
import json
import os
import subprocess
import sys
import tomllib

import numpy as np

print = functools.partial(print, flush=True)
CASE = "forcer-cooling-thermal"


def module_root():
    here = globals().get("__file__")
    if here:
        return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", ".."))
    return os.path.join(os.getcwd(), "modules", "compact-stage")


ROOT = module_root()
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "simulation", "cases", CASE))
import fem          # noqa: E402
import hydraulics   # noqa: E402
import meshing      # noqa: E402

KINDS = ["air", "contact", "gap", "water", "table", "table_gap", "cavity"]


def q16(values):
    v = np.asarray(values, dtype=float)
    lo, hi = float(v.min()), float(v.max())
    span = hi - lo if hi > lo else 1.0
    q = np.round((v - lo) / span * 65535.0).astype("<u2")
    return {"lo": lo, "hi": hi, "b64": base64.b64encode(q.tobytes()).decode("ascii")}


def b64(arr, dtype):
    return base64.b64encode(np.asarray(arr, dtype=dtype).tobytes()).decode("ascii")


def display_mesh(body, gdir, size, fine_boxes):
    """A coarse triangle mesh of the body surface (Gmsh, first order)."""
    out = os.path.join(gdir, "display")
    os.makedirs(out, exist_ok=True)
    step = os.path.join(gdir, body + "_defeatured.step")
    if not os.path.exists(step):
        step = os.path.join(gdir, body + ".step")
    geo = os.path.join(out, body + ".geo")
    msh = os.path.join(out, body + ".msh")
    lines = ['SetFactory("OpenCASCADE");', 'Merge "%s";' % step,
             "Mesh.MeshSizeFromPoints = 0;", "Mesh.MeshSizeFromCurvature = 8;",
             "Mesh.MeshSizeExtendFromBoundary = 0;",
             "Mesh.MeshSizeMax = %g;" % size, "Mesh.MeshSizeMin = 0.3;"]
    ids = []
    for i, (vin, b) in enumerate(fine_boxes):
        n = i + 1
        lines += ["Field[%d] = Box;" % n, "Field[%d].VIn = %g; Field[%d].VOut = %g;" % (n, vin, n, size),
                  "Field[%d].XMin = %g; Field[%d].XMax = %g;" % (n, b[0], n, b[1]),
                  "Field[%d].YMin = %g; Field[%d].YMax = %g;" % (n, b[2], n, b[3]),
                  "Field[%d].ZMin = %g; Field[%d].ZMax = %g;" % (n, b[4], n, b[5]),
                  "Field[%d].Thickness = 2;" % n]
        ids.append(n)
    if ids:
        lines += ["Field[%d] = Min;" % (len(ids) + 1),
                  "Field[%d].FieldsList = {%s};" % (len(ids) + 1, ",".join(map(str, ids))),
                  "Background Field = %d;" % (len(ids) + 1)]
    lines += ["Mesh.Algorithm = 6;", "Mesh.MshFileVersion = 2.2;", "Mesh 2;", 'Save "%s";' % msh]
    with open(geo, "w") as f:
        f.write("\n".join(lines) + "\n")
    r = subprocess.run([meshing.find_tool("gmsh"), geo, "-v", "1", "-"], capture_output=True, text=True)
    if not os.path.exists(msh):
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("ERROR: display mesh of %s failed" % body)
    with open(msh) as fh:
        txt = fh.read()
    a = txt.index("$Nodes") + 6
    blk = txt[a:txt.index("$EndNodes")].split("\n", 2)
    arr = np.array(blk[2].split(), dtype=float).reshape(int(blk[1]), 4)
    ids = arr[:, 0].astype(int)
    xyz = arr[:, 1:]
    pos = np.full(ids.max() + 1, -1)
    pos[ids] = np.arange(len(ids))
    tris = []
    for ln in txt[txt.index("$Elements") + 9:txt.index("$EndElements")].strip().split("\n")[1:]:
        p = ln.split()
        if p[1] == "2":
            nt = int(p[2])
            tris.append([int(x) for x in p[3 + nt:6 + nt]])
    tris = pos[np.array(tris)]
    used = np.unique(tris)
    remap = np.full(len(xyz), -1)
    remap[used] = np.arange(len(used))
    return xyz[used], remap[tris]


def main():
    with open(os.path.join(ROOT, "simulation", "cases", CASE, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)
    with open(os.path.join(ROOT, "simulation", "cases", CASE, "print_materials.toml"), "rb") as f:
        mats = tomllib.load(f)["material"]
    res_dir = os.path.join(ROOT, "simulation", "results", CASE)
    gdir = os.path.join(res_dir, "exports", "geom")
    with open(os.path.join(res_dir, "thermal.json")) as f:
        R = json.load(f)
    with open(os.path.join(gdir, "geometry.json")) as f:
        geom = json.load(f)
    mesh_check = None
    p = os.path.join(res_dir, "thermal_mesh_s0.75.json")
    if os.path.exists(p):
        with open(p) as f:
            mesh_check = json.load(f)
    Fz = np.load(os.path.join(res_dir, "exports", "fields.npz"), allow_pickle=False)
    names = [str(x) for x in Fz["names"]]
    offsets = Fz["offsets"]
    X = Fz["X"]

    # -- surfaces for the 3D view -------------------------------------------------
    wb = [b for b in geom["bodies"] if b["name"] == "water"][0]["bbox"]
    ch_box = [wb[0] - 2, wb[3] + 2, wb[1] - 2, wb[1] + 34, geom["pocket_ceiling"][4] - 1,
              geom["pocket_ceiling"][4] + 3]
    bl = [b for b in geom["bodies"] if b["name"] == "cooling_block"][0]["bbox"]
    bl_box = [bl[0] - 1, bl[3] + 1, bl[1] - 1, bl[4] + 1, bl[2] - 1, bl[5] + 1]
    out_bodies = []
    allx, allT, allu, allk, allb, alltri = [], [], [], [], [], []
    nbase = 0
    T = Fz["T_main"]
    U = Fz["u_main"] if "u_main" in Fz else np.zeros((len(X), 3))
    UC = Fz["u_clamped"] if "u_clamped" in Fz else np.zeros((len(X), 3))
    for i, nm in enumerate(names + ["water"]):
        size = {"base": 6.0, "carriage_top": 4.0, "carriage_bottom": 3.0, "forcer": 3.0, "track": 6.0,
                "cooling_block": 0.8, "water": 0.6}.get(nm, 3.0)
        boxes = [(0.8, ch_box), (0.8, bl_box)] if nm in ("carriage_bottom", "forcer") else []
        dx, dt = display_mesh(nm, gdir, size, boxes)
        if nm == "water":
            Tv = np.full(len(dx), np.nan)
            uv = np.zeros((len(dx), 3))
            uc = uv
            kind = np.full(len(dx), KINDS.index("water"))
            s_w = Fz["s_water"]
            from scipy.spatial import cKDTree
            _, nn = cKDTree(Fz["wxyz"]).query(dx)
            sv = s_w[nn]
        else:
            xb = X[offsets[i]:offsets[i] + (offsets[i + 1] if i + 1 < len(names) else len(X)) - offsets[i]]
            tri = Fz["tri_%d" % i]
            kind_f = Fz["kind_%d" % i]
            faces = {"tri": tri}
            p0, p1, p2 = xb[tri[:, 0]], xb[tri[:, 1]], xb[tri[:, 2]]
            n = np.cross(p1 - p0, p2 - p0)
            a = 0.5 * np.linalg.norm(n, axis=1)
            faces.update({"normal": n / (2 * a[:, None]), "area": a, "centroid": (p0 + p1 + p2) / 3})
            surf = fem.Surface(xb, faces)
            pj = surf.project(dx)
            N = fem.shape_tri(pj["lam"])
            g = pj["nodes"] + offsets[i]
            Tv = (T[g] * N).sum(axis=1)
            uv = (U[g] * N[:, :, None]).sum(axis=1)
            uc = (UC[g] * N[:, :, None]).sum(axis=1)
            kf = kind_f[pj["face"]]
            cen = faces["centroid"][pj["face"]]
            cav = (cen[:, 0] > 10) & (cen[:, 0] < 430) & (cen[:, 1] > 12) & (cen[:, 1] < 198) & (cen[:, 2] < 40 - 1e-6)
            kind = np.array([KINDS.index(k) for k in kf])
            kind[(kf == "air") & cav] = KINDS.index("cavity")
            sv = np.full(len(dx), -1.0)
        out_bodies.append({"name": nm, "n": len(dx), "ntri": len(dt), "first": nbase})
        allx.append(dx)
        allT.append(Tv)
        allu.append(np.c_[uv, uc])
        allk.append(kind)
        allb.append(np.full(len(dx), len(out_bodies) - 1))
        alltri.append(dt + nbase)
        nbase += len(dx)
        print("display %-16s %6d points %6d triangles" % (nm, len(dx), len(dt)))
    P = np.concatenate(allx)
    Tall = np.concatenate(allT)
    Tfill = np.where(np.isnan(Tall), np.nanmin(Tall), Tall)
    Uall = np.concatenate(allu)
    fields = {
        "bodies": out_bodies,
        "n": int(len(P)),
        "x": q16(P[:, 0]), "y": q16(P[:, 1]), "z": q16(P[:, 2]),
        "T": q16(Tfill),
        "ux": q16(Uall[:, 0] * 1000), "uy": q16(Uall[:, 1] * 1000), "uz": q16(Uall[:, 2] * 1000),
        "cux": q16(Uall[:, 3] * 1000), "cuy": q16(Uall[:, 4] * 1000), "cuz": q16(Uall[:, 5] * 1000),
        "kind": b64(np.concatenate(allk), "<u1"),
        "body": b64(np.concatenate(allb), "<u1"),
        "tris": b64(np.concatenate(alltri), "<u4"),
        "kinds": KINDS,
    }
    rdir = os.path.join(REPO, "simulation", "cases", "forcer-cooling-thermal-results")
    os.makedirs(rdir, exist_ok=True)
    with open(os.path.join(rdir, "thermal_fields.js"), "w") as f:
        f.write("// Made by modules/compact-stage/simulation/cases/forcer-cooling-thermal/export_web.py. Do not edit.\n")
        f.write("window.THERMAL_FIELDS = " + json.dumps(fields, separators=(",", ":")) + ";\n")

    # -- numbers ----------------------------------------------------------------
    hy = {"pumps": [], "branch": [], "system": hydraulics.system_curve(cfg, list(np.linspace(0, 4.5, 46)))}
    for q in np.linspace(0.05, 1.2, 47):
        dp, parts = hydraulics.axis_branch(cfg, float(q), detail=True)
        hc, rec, _ = hydraulics.film(cfg, float(q), "channel")
        hp, rep, _ = hydraulics.film(cfg, float(q), "passage")
        hy["branch"].append({"q": float(q), "dp_bar": dp / 1e5, "parts": parts, "h_channel": hc, "h_passage": hp,
                             "re_channel": rec, "re_passage": rep})
    for pump in cfg["pump"]:
        op = hydraulics.operating_point(cfg, pump)
        op_nv = hydraulics.operating_point(cfg, pump, spindle_valve=False)
        L = [cfg["hydraulics"]["hose_length"]] * cfg["hydraulics"]["n_axes"]
        L[-1] = 3000.0
        op_long = hydraulics.operating_point(cfg, pump, hose_lengths=L)
        curve = []
        if pump["kind"] == "centrifugal":
            for q in np.linspace(0, pump["q_max"], 31):
                curve.append({"q": float(q), "p_bar": hydraulics.pump_pressure(pump, float(q)) / 1e5})
        else:
            curve = [{"q": pump["q_lpm"], "p_bar": 0.0}, {"q": pump["q_lpm"], "p_bar": pump["relief_bar"]}]
        heat = cfg["hydraulics"]["n_axes"] * R["main"]["P_loss_W"] + cfg["hydraulics"]["spindle_heat_w"]
        hy["pumps"].append({**{k: v for k, v in pump.items()}, "op": op, "op_no_valve": op_nv,
                            "op_one_long_hose": op_long, "curve": curve, "heat_w": heat})
    dp_main, parts_main = hydraulics.axis_branch(cfg, R["flow_main"], detail=True)
    hy["main_parts"] = parts_main
    hy["main_dp_bar"] = dp_main / 1e5

    # materials against the cooling block temperature
    tb = R["main"]["bodies"]["cooling_block"]["max"]
    hot = [s for s in R.get("sweeps", []) if s["group"] in ("air", "contact", "water film", "pump", "flow")]
    tb_worst = max([tb] + [s["bodies"]["cooling_block"]["max"] for s in hot if s["group"] != "flow"])
    mat_out = []
    for m in mats:
        lim = m["hdt_045"]
        margin = lim - tb
        margin_worst = lim - tb_worst
        verdict = "ok" if margin_worst >= 20 else ("warn" if margin_worst >= 5 else "bad")
        mat_out.append({**m, "margin": margin, "margin_worst": margin_worst, "verdict": verdict})

    data = {"results": R, "hydraulics": hy, "materials": mat_out, "block_max": tb, "block_max_worst": tb_worst,
            "inputs": cfg, "geometry": geom, "mesh_check": mesh_check}
    # checks
    m = R["main"]
    mo = cfg["motor"]
    checks = {}
    checks["balance_pct"] = m["balance"]["error_pct"]
    mdc = cfg["water"]["rho"] * R["flow_main"] / 60000 * cfg["water"]["cp"]
    checks["water_rise_hand"] = m["balance"]["water"] / mdc
    checks["water_rise_model"] = m["water_rise"]
    r = mo["r_ll_25"] + (mo["r_ll_120"] - mo["r_ll_25"]) * (m["coil_max"] - 25) / 95
    checks["loss_hand"] = 1.5 * mo["current"] ** 2 * r
    checks["loss_model"] = m["P_loss_W"]
    checks["coil_face_hand"] = mo["rth"] * m["P_loss_W"]
    checks["coil_face_model"] = m["coil_max"] - m["forcer_face_mean"]
    hc = R["main"]["params"]["h_channel"]
    A = R["wetted_area_mm2"]["channel"] * 1e-6
    checks["film_dT_hand"] = m["balance"]["water"] / (hc * A)
    if mesh_check:
        checks["mesh"] = {"coil_fine": m["coil_max"], "coil_coarse": mesh_check["main"]["coil_max"],
                          "block_fine": m["bodies"]["cooling_block"]["max"],
                          "block_coarse": mesh_check["main"]["bodies"]["cooling_block"]["max"],
                          "nodes_fine": sum(v["nodes"] for v in R["mesh"].values()),
                          "nodes_coarse": sum(v["nodes"] for v in mesh_check["mesh"].values())}
    data["checks"] = checks
    with open(os.path.join(rdir, "thermal_data.js"), "w") as f:
        f.write("// Made by modules/compact-stage/simulation/cases/forcer-cooling-thermal/export_web.py. Do not edit.\n")
        f.write("window.THERMAL_DATA = " + json.dumps(data, separators=(",", ":"), default=float) + ";\n")
    print("Done: %s" % rdir)


main()
