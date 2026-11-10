"""3D stress fields of the base for the results web page.

Run it with the Python that comes with FreeCAD, from the repository root:

    freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/export_web_fem.py

It uses the mesh, the supports and the loads of run_fem.py (the same
functions, read from that file), and runs:

- "pocket" and "band": the same elastic-plastic load ramps as run_fem.py, up
  to the highest force any case of the study reaches. It keeps the full
  field of every load step on the outer surface of the base: displacement,
  von Mises stress and plastic strain. It also prints the sum of the support
  reactions, to check that the supports carry the whole load.
- "mesh check": the pocket load at 5 kN, elastic, on a coarse, the normal and
  a fine mesh. The peak stress and the wall deflection should not change much.

Output:
- simulation/cases/end-stop-crash-results/fem_fields.js (committed): one plain
  script for the web page (window.FEM_FIELDS).
- simulation/results/end-stop-crash/exports/web-fem/ (not committed): the work
  files of CalculiX.

It takes about 30 minutes on four cores.
"""

import base64
import copy
import functools
import json
import math
import os
import shutil
import sys
import time
import tomllib

import numpy as np

print = functools.partial(print, flush=True)

HERE = os.path.dirname(os.path.abspath(globals().get("__file__", os.path.join(
    os.getcwd(), "modules", "compact-stage", "simulation", "cases", "end-stop-crash", "x"))))
MODULE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(MODULE, "..", ".."))
WEB = os.path.join(REPO, "simulation", "cases", "end-stop-crash-results")

# Highest forces the page must show. The largest force of the study on the
# pocket walls is 46.7 kN in total (spread, second stage); the largest metal
# hit is 43 kN (overspeed trip, second stage).
POCKET_MAX = 48000.0
BAND_MAX = 64000.0
STEPS = 16
# EXPORT_ONLY=ramps or mesh runs one part. EXPORT_SMOKE=1 is a fast test run on a coarse mesh.
SMOKE = os.environ.get("EXPORT_SMOKE") == "1"
if SMOKE:
    STEPS = 2


def load_run_fem():
    """The functions of run_fem.py, without running its main()."""
    path = os.path.join(HERE, "run_fem.py")
    with open(path) as f:
        src = f.read()
    head, tail = src.rsplit("\nmain()", 1)
    if tail.strip():
        raise SystemExit("run_fem.py changed: it no longer ends with main()")
    ns = {"__file__": path, "__name__": "run_fem"}
    exec(compile(head, path, "exec"), ns)
    return ns


R = load_run_fem()


def build_mesh(cfg, work):
    os.makedirs(work, exist_ok=True)
    step = R["export_step"](MODULE, cfg, work)
    msh = R["mesh"](step, cfg, work)
    ids, xyz, tets = R["read_msh"](msh)
    tets = R["to_ccx_order"](ids, xyz, tets)
    mesh_inp = os.path.join(work, "mesh.inp")
    R["write_mesh_inp"](mesh_inp, ids, xyz, tets)
    return ids, xyz, tets, mesh_inp


def load_sets(cfg, ids, xyz, tets):
    """Supports and load faces: the same rules as in run_fem.py main()."""
    TOL = R["TOL"]
    g = cfg["geometry"]
    pos = {int(n): k for k, n in enumerate(ids)}
    fixed = [int(n) for n, p in zip(ids, xyz) if abs(p[2]) < TOL and (p[1] <= 40 + TOL or p[1] >= 170 - TOL)]
    bfaces = R["boundary_faces"](tets)
    r = 0.5 * cfg["fem"]["pocket_disc_diameter"]
    xp = g["pocket_back_x"]

    def on_pocket(c, centre):
        if np.any(np.abs(c[:, 0] - xp) > 1e-4):
            return False
        return any(math.hypot(centre[1] - yb, centre[2] - g["bumper_z"]) <= r for yb in g["bumper_y"])

    xw = g["end_wall_inner_x"]
    z0, z1 = g["metal_band_z"]

    def on_band(c, centre):
        return bool(np.all(np.abs(c[:, 0] - xw) < 1e-4) and z0 - 1e-4 <= c[:, 2].min()
                    and c[:, 2].max() <= z1 + 1e-4)

    pocket_faces, pocket_area = R["select_faces"](bfaces, tets, pos, xyz, on_pocket)
    band_faces, band_area = R["select_faces"](bfaces, tets, pos, xyz, on_band)

    def face_nodes(faces):
        s = set()
        for e, fnum in faces:
            for i in R["FACE_CORNERS"][fnum]:
                s.add(int(tets[e][i]))
        return s

    region = [int(n) for n, p in zip(ids, xyz) if p[0] < 60 and p[2] > 5]
    return {"pos": pos, "fixed": fixed, "bfaces": bfaces, "region": region,
            "pocket": (pocket_faces, pocket_area, face_nodes(pocket_faces)),
            "band": (band_faces, band_area, face_nodes(band_faces))}


def add_reaction_print(job_path):
    with open(job_path) as f:
        txt = f.read()
    txt = txt.replace("*END STEP", "*NODE PRINT, NSET=FIX, TOTALS=ONLY\nRF\n*END STEP")
    with open(job_path, "w") as f:
        f.write(txt)


def read_reactions(dat_path):
    """Sum of the support reactions per load step: [(time, fx, fy, fz)]."""
    out = []
    with open(dat_path) as f:
        lines = f.read().split("\n")
    for k, line in enumerate(lines):
        if line.strip().startswith("total force") and "time" in line:
            t = float(line.split("time")[-1].split()[0])
            vals = [v for v in lines[k + 1:k + 4] if v.strip()][0].split()
            out.append((t, float(vals[0]), float(vals[1]), float(vals[2])))
    return out


def q16(values):
    """Values as unsigned 16 bit integers, with the range to scale them back."""
    v = np.asarray(values, dtype=float)
    lo = float(v.min())
    hi = float(v.max())
    span = hi - lo if hi > lo else 1.0
    q = np.round((v - lo) / span * 65535.0).astype("<u2")
    return {"lo": lo, "hi": hi, "b64": base64.b64encode(q.tobytes()).decode("ascii")}


def surface(tets, bfaces, pos, xyz):
    """Corner triangles of the outer surface, and the node ids they use."""
    tris = []
    for e, fnum in bfaces:
        tris.append([int(tets[e][i]) for i in R["FACE_CORNERS"][fnum]])
    nodes = sorted({n for t in tris for n in t})
    local = {n: k for k, n in enumerate(nodes)}
    tri_idx = np.array([[local[n] for n in t] for t in tris], dtype="<u4")
    pts = np.array([xyz[pos[n]] for n in nodes])
    return nodes, tri_idx, pts


def ramp(cfg, name, sets, mesh_inp, work, f_max, surf_nodes):
    mat = cfg["material_base"]
    faces, area, load_nodes = sets[name]
    job = os.path.join(work, name + ".inp")
    R["write_static_job"](job, mesh_inp, mat, sets["fixed"], faces, area, f_max, STEPS)
    add_reaction_print(job)
    t0 = time.time()
    print("   job %s: %d load faces, %.0f mm2, ramp to %.0f N" % (name, len(faces), area, f_max))
    R["run_ccx"](name, work, allow_stop=True)
    print("   solved in %.0f min" % ((time.time() - t0) / 60))
    blocks = R["read_frd"](os.path.join(work, name + ".frd"))
    disp = [(t, b) for t, n, b in blocks if n == "DISP"]
    stress = [(t, b) for t, n, b in blocks if n == "STRESS"]
    peeq = [(t, b) for t, n, b in blocks if n == "PE"]
    reac = read_reactions(os.path.join(work, name + ".dat"))
    vm_fn = R["von_mises"]
    steps = []
    for (t, d), (_, s), (_, p) in zip(disp, stress, peeq):
        force = f_max * t
        u = np.array([d[n][:3] for n in surf_nodes])
        vm = np.array([vm_fn(s[n]) for n in surf_nodes])
        pe = np.array([p[n][0] for n in surf_nodes])
        ux_load = float(np.mean([-d[n][0] for n in load_nodes]))
        reg_vm = max(vm_fn(s[n]) for n in sets["region"])
        reg_pe = max(p[n][0] for n in sets["region"])
        rf = min(reac, key=lambda r: abs(r[0] - t)) if reac else (t, float("nan"), 0.0, 0.0)
        steps.append({
            "force": force,
            "load_displacement": ux_load,
            "von_mises_max_region": reg_vm,
            "peeq_max_region": reg_pe,
            "reaction": [rf[1], rf[2], rf[3]],
            "ux": q16(u[:, 0]), "uy": q16(u[:, 1]), "uz": q16(u[:, 2]),
            "vm": q16(vm), "pe": q16(pe),
        })
        print("   %8.0f N: wall %.4f mm, %.0f MPa, plastic %.5f, reaction x %.0f N"
              % (force, ux_load, reg_vm, reg_pe, rf[1]))
    return {"area": area, "f_max": f_max, "force_reached": steps[-1]["force"] if steps else 0.0,
            "steps": steps}


def mesh_check(cfg, base_work):
    """Pocket load at 5 kN, elastic, on three meshes."""
    out = []
    for factor, label in ((2.0, "coarse"), (1.0, "normal"), (0.6, "fine")):
        c = copy.deepcopy(cfg)
        for k in ("mesh_fine", "mesh_mid"):
            c["fem"][k] = cfg["fem"][k] * factor
        work = os.path.join(base_work, "mesh-" + label)
        shutil.rmtree(work, ignore_errors=True)
        ids, xyz, tets, mesh_inp = build_mesh(c, work)
        sets = load_sets(c, ids, xyz, tets)
        faces, area, load_nodes = sets["pocket"]
        mat = dict(c["material_base"])
        job = os.path.join(work, "lin.inp")
        with open(job, "w") as f:
            f.write("*INCLUDE, INPUT=mesh.inp\n*NSET, NSET=FIX\n")
            fx = sets["fixed"]
            for k in range(0, len(fx), 12):
                f.write(", ".join(str(n) for n in fx[k:k + 12]) + "\n")
            f.write("*MATERIAL, NAME=AL\n*ELASTIC\n%g, %g\n*SOLID SECTION, ELSET=EALL, MATERIAL=AL\n"
                    % (mat["youngs_modulus"], mat["poisson_ratio"]))
            f.write("*BOUNDARY\nFIX, 1, 3\n*STEP\n*STATIC\n*DLOAD\n")
            f.write(R["dload_lines"](faces, 5000.0 / area))
            f.write("*NODE FILE\nU\n*EL FILE\nS\n*NODE PRINT, NSET=FIX, TOTALS=ONLY\nRF\n*END STEP\n")
        t0 = time.time()
        R["run_ccx"]("lin", work)
        blocks = R["read_frd"](os.path.join(work, "lin.frd"))
        d = [b for t, n, b in blocks if n == "DISP"][-1]
        s = [b for t, n, b in blocks if n == "STRESS"][-1]
        ux = float(np.mean([-d[n][0] for n in load_nodes]))
        vm = max(R["von_mises"](s[n]) for n in sets["region"])
        # The stress one element away from the sharp edges: the 99.5th percentile
        # of the region shows whether the peak is a local corner effect.
        vms = np.array([R["von_mises"](s[n]) for n in sets["region"]])
        reac = read_reactions(os.path.join(work, "lin.dat"))
        row = {"mesh": label, "size_at_pocket_mm": c["fem"]["mesh_fine"], "nodes": int(len(ids)),
               "elements": int(len(tets)), "wall_displacement_mm": ux, "von_mises_max": vm,
               "von_mises_p995": float(np.percentile(vms, 99.5)),
               "reaction_x": reac[-1][1] if reac else None, "minutes": (time.time() - t0) / 60}
        print("   mesh %-6s %6d nodes: wall %.4f mm, peak %.1f MPa, 99.5 %% %.1f MPa, reaction %.0f N"
              % (label, row["nodes"], ux, vm, row["von_mises_p995"], row["reaction_x"] or 0))
        out.append(row)
    return out


def main():
    with open(os.path.join(HERE, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)
    work = os.path.join(MODULE, "simulation", "results", "end-stop-crash", "exports", "web-fem")
    only = os.environ.get("EXPORT_ONLY", "all")
    if SMOKE:
        for k in ("mesh_fine", "mesh_mid", "mesh_coarse"):
            cfg["fem"][k] *= 3.0
        work += "-smoke"
    os.makedirs(work, exist_ok=True)
    out_path = os.path.join(work, "fem_fields.json")
    data = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            data = json.load(f)

    if only in ("all", "ramps"):
        print("1. Mesh the base (same settings as run_fem.py)")
        ids, xyz, tets, mesh_inp = build_mesh(cfg, os.path.join(work, "main"))
        sets = load_sets(cfg, ids, xyz, tets)
        nodes, tris, pts = surface(tets, sets["bfaces"], sets["pos"], xyz)
        print("   %d nodes, %d elements, surface %d nodes, %d triangles"
              % (len(ids), len(tets), len(nodes), len(tris)))
        local = {n: k for k, n in enumerate(nodes)}

        def node_flags(node_set):
            fl = np.zeros(len(nodes), dtype="u1")
            for n in node_set:
                if n in local:
                    fl[local[n]] = 1
            return fl

        flags = (node_flags(sets["pocket"][2]) * 1 + node_flags(sets["band"][2]) * 2
                 + node_flags(sets["fixed"]) * 4).astype("u1")
        data["mesh"] = {"nodes": int(len(ids)), "elements": int(len(tets)),
                        "surface_nodes": len(nodes), "surface_triangles": int(len(tris)),
                        "fixed_nodes": len(sets["fixed"])}
        data["surface"] = {
            "x": q16(pts[:, 0]), "y": q16(pts[:, 1]), "z": q16(pts[:, 2]),
            "tris": base64.b64encode(tris.astype("<u4").tobytes()).decode("ascii"),
            "flags": base64.b64encode(flags.tobytes()).decode("ascii"),
        }
        data["material"] = cfg["material_base"]
        print("2. Load ramps")
        data["pocket"] = ramp(cfg, "pocket", sets, mesh_inp, os.path.join(work, "main"), POCKET_MAX, nodes)
        data["band"] = ramp(cfg, "band", sets, mesh_inp, os.path.join(work, "main"), BAND_MAX, nodes)
        with open(out_path, "w") as f:
            json.dump(data, f)

    if only in ("all", "mesh"):
        print("3. Mesh check")
        data["mesh_check"] = mesh_check(cfg, work)
        with open(out_path, "w") as f:
            json.dump(data, f)

    if "surface" in data and "mesh_check" in data and not SMOKE:
        os.makedirs(WEB, exist_ok=True)
        js = os.path.join(WEB, "fem_fields.js")
        with open(js, "w") as f:
            f.write("// Made by modules/compact-stage/simulation/cases/end-stop-crash/export_web_fem.py."
                    " Do not edit.\n")
            f.write("window.FEM_FIELDS = ")
            json.dump(data, f, separators=(",", ":"))
            f.write(";\n")
        print("Done: %s (%.1f MB)" % (js, os.path.getsize(js) / 1e6))


main()
