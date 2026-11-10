"""Stress and plastic deformation of the base end wall in a crash.

Run it with the Python that comes with FreeCAD, from the repository root:

    freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/run_fem.py

On Windows: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" and the same
path. Gmsh and CalculiX (ccx) must be on the PATH, or in the FreeCAD bin
folder. On Linux, `bash setup-fem.sh` installs them.

The script only reads the part file. It exports the base as STEP, meshes it
with Gmsh (second order tetrahedra, straight middle nodes), writes the
CalculiX input itself, and runs three jobs:

- "pocket": pressure on the back faces of the two bumper pockets at the start
  end. This is the force of the two TA17-7 bumpers.
- "band": pressure on the inner face of the end wall, where the end face of
  carriage-bottom hits it when the bumpers are pressed in fully.
- "modes": the first natural frequencies, to check that a static load is a
  fair model of the impact.

"pocket" and "band" load and unload the wall in steps, up to each force level
in case.toml. After each unload, the lasting dent and the plastic strain are
read. The material is elastic-plastic (Rp0.2 to Rm, isotropic hardening).

Output:
- simulation/results/end-stop-crash/fem.json (committed)
- simulation/results/end-stop-crash/exports/fem/ (not committed): STEP, mesh,
  CalculiX input and result files.
"""

import functools
import json
import math
import os
import shutil
import subprocess
import sys
import tomllib

import numpy as np

print = functools.partial(print, flush=True)
CASE = "end-stop-crash"
TOL = 1e-6


def module_root():
    here = globals().get("__file__")
    if here:
        return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", ".."))
    return os.path.join(os.getcwd(), "modules", "compact-stage")


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def find_tool(name):
    path = shutil.which(name)
    if path:
        return path
    for cand in (os.path.join(os.path.dirname(sys.executable), name),
                 os.path.join(os.path.dirname(sys.executable), name + ".exe")):
        if os.path.exists(cand):
            return cand
    fail("%s not found. On Linux run: bash setup-fem.sh" % name)


# ---------------------------------------------------------------------------
# Geometry and mesh
# ---------------------------------------------------------------------------

def export_step(root, cfg, out):
    import FreeCAD as App
    part = os.path.join(root, cfg["geometry"]["base_part"])
    doc = App.openDocument(part, True)
    shape = doc.getObject("Body").Shape.copy()
    App.closeDocument(doc.Name)
    if len(shape.Solids) != 1 or not shape.isValid():
        fail("the base body is not one valid solid")
    bb = shape.BoundBox
    if abs(bb.XLength - 440) > 1e-3 or abs(bb.YLength - 210) > 1e-3 or abs(bb.ZLength - 40) > 1e-3:
        fail("the base is not 440 x 210 x 40 mm any more. Check the case inputs.")
    # The faces this case loads must still be there: the pocket back faces at
    # x = 3 and the end wall inner face at x = 10.
    g = cfg["geometry"]
    found_pocket = 0
    found_wall = 0
    for f in shape.Faces:
        fb = f.BoundBox
        if abs(fb.XMin - g["pocket_back_x"]) < TOL and abs(fb.XMax - g["pocket_back_x"]) < TOL:
            found_pocket += 1
        if abs(fb.XMin - g["end_wall_inner_x"]) < TOL and abs(fb.XMax - g["end_wall_inner_x"]) < TOL:
            found_wall += 1
    if found_pocket != 2 or found_wall < 1:
        fail("found %d pocket back faces and %d end wall faces, expected 2 and 1. "
             "Did the base change?" % (found_pocket, found_wall))
    # Keep only the start end. The crash loads that end, and the base is held
    # on its bottom strips along the whole length, so the far half carries
    # nothing. It also leaves out the threaded holes at the far end, where
    # Gmsh cannot mesh one of the hole faces.
    import Part
    cut = cfg["fem"]["cut_x"]
    shape = shape.common(Part.makeBox(cut, 210.0, 40.0))
    if len(shape.Solids) != 1:
        fail("the cut base is not one solid")
    step = os.path.join(out, "base.step")
    shape.exportStep(step)
    return step


def mesh(step, cfg, out):
    m = cfg["fem"]
    y = cfg["geometry"]["bumper_y"]
    geo = os.path.join(out, "base.geo")
    msh = os.path.join(out, "base.msh")
    fields = []
    lines = [
        'SetFactory("OpenCASCADE");',
        'Merge "%s";' % os.path.basename(step),
        "Mesh.MeshSizeFromPoints = 0;",
        "Mesh.MeshSizeFromCurvature = 0;",
        "Mesh.MeshSizeExtendFromBoundary = 0;",
        "Mesh.MeshSizeMax = %g;" % m["mesh_coarse"],
        "Mesh.MeshSizeMin = %g;" % (0.5 * m["mesh_fine"]),
    ]
    n = 1
    for yc in y:  # fine boxes around the two pockets of the start end
        lines += [
            "Field[%d] = Box;" % n,
            "Field[%d].VIn = %g;" % (n, m["mesh_fine"]),
            "Field[%d].VOut = %g;" % (n, m["mesh_coarse"]),
            "Field[%d].XMin = -1; Field[%d].XMax = 8;" % (n, n),
            "Field[%d].YMin = %g; Field[%d].YMax = %g;" % (n, yc - 14, n, yc + 14),
            "Field[%d].ZMin = 16; Field[%d].ZMax = 41;" % (n, n),
            "Field[%d].Thickness = 4;" % n,
        ]
        fields.append(n)
        n += 1
    lines += [
        "Field[%d] = Box;" % n,
        "Field[%d].VIn = %g;" % (n, m["mesh_mid"]),
        "Field[%d].VOut = %g;" % (n, m["mesh_coarse"]),
        "Field[%d].XMin = -1; Field[%d].XMax = 14;" % (n, n),
        "Field[%d].YMin = -1; Field[%d].YMax = 211;" % (n, n),
        "Field[%d].ZMin = 8; Field[%d].ZMax = 41;" % (n, n),
        "Field[%d].Thickness = 12;" % n,
    ]
    fields.append(n)
    n += 1
    lines += [
        "Field[%d] = Min;" % n,
        "Field[%d].FieldsList = {%s};" % (n, ", ".join(str(f) for f in fields)),
        "Background Field = %d;" % n,
        "Mesh.Algorithm3D = 1;",
        "Geometry.OCCFixDegenerated = 1;",
        "Geometry.OCCFixSmallEdges = 1;",
        "Geometry.OCCFixSmallFaces = 1;",
        "Mesh.ElementOrder = 2;",
        "Mesh.SecondOrderLinear = 1;",
        "Mesh.Optimize = 1;",
        "Mesh.MshFileVersion = 2.2;",
        "Mesh 3;",
        'Save "%s";' % os.path.basename(msh),
    ]
    with open(geo, "w") as f:
        f.write("\n".join(lines) + "\n")
    gmsh = find_tool("gmsh")
    r = subprocess.run([gmsh, os.path.basename(geo), "-nt", str(os.cpu_count() or 1), "-v", "2", "-"],
                       cwd=out, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(msh):
        print(r.stdout[-3000:], r.stderr[-3000:])
        fail("gmsh failed")
    return msh


def read_msh(path):
    """Nodes and 10-node tetrahedra from a Gmsh 2.2 ASCII file."""
    with open(path) as f:
        lines = f.read().split("\n")
    i = lines.index("$Nodes")
    nn = int(lines[i + 1])
    ids = np.empty(nn, dtype=np.int64)
    xyz = np.empty((nn, 3))
    for k in range(nn):
        p = lines[i + 2 + k].split()
        ids[k] = int(p[0])
        xyz[k] = (float(p[1]), float(p[2]), float(p[3]))
    i = lines.index("$Elements")
    ne = int(lines[i + 1])
    tets = []
    for k in range(ne):
        p = lines[i + 2 + k].split()
        if p[1] == "11":
            ntag = int(p[2])
            tets.append([int(v) for v in p[3 + ntag:3 + ntag + 10]])
    if not tets:
        fail("no 10-node tetrahedra in the mesh")
    return ids, xyz, np.array(tets, dtype=np.int64)


def to_ccx_order(ids, xyz, tets):
    """Put the middle nodes in CalculiX C3D10 order, found by position.

    C3D10: corners 1-4, then the middle nodes of edges 1-2, 2-3, 3-1, 1-4,
    2-4, 3-4. Gmsh uses a different order for the last nodes, so each middle
    node is matched to the middle of its edge. That does not depend on any
    numbering convention.
    """
    pos = {n: k for k, n in enumerate(ids)}
    out = np.empty_like(tets)
    edges = [(0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)]
    for e, t in enumerate(tets):
        corners = t[:4]
        mids = t[4:]
        mxyz = np.array([xyz[pos[n]] for n in mids])
        out[e, :4] = corners
        for j, (a, b) in enumerate(edges):
            target = 0.5 * (xyz[pos[corners[a]]] + xyz[pos[corners[b]]])
            d = np.linalg.norm(mxyz - target, axis=1)
            k = int(np.argmin(d))
            if d[k] > 1e-6:
                fail("a middle node is not on its edge (element %d)" % e)
            out[e, 4 + j] = mids[k]
        # Positive volume, or CalculiX stops.
        p = [xyz[pos[n]] for n in corners]
        if np.dot(np.cross(p[1] - p[0], p[2] - p[0]), p[3] - p[0]) <= 0:
            fail("element %d is inside out" % e)
    return out


# C3D10 faces by corner index (CalculiX manual, element face numbering).
FACE_CORNERS = {1: (0, 1, 2), 2: (0, 3, 1), 3: (1, 3, 2), 4: (2, 3, 0)}


def boundary_faces(tets):
    count = {}
    for e, t in enumerate(tets):
        for fnum, c in FACE_CORNERS.items():
            key = tuple(sorted(int(t[i]) for i in c))
            count.setdefault(key, []).append((e, fnum))
    return [v[0] for v in count.values() if len(v) == 1]


def face_geometry(face, tets, pos, xyz):
    e, fnum = face
    c = [xyz[pos[int(tets[e][i])]] for i in FACE_CORNERS[fnum]]
    centre = (c[0] + c[1] + c[2]) / 3.0
    area = 0.5 * np.linalg.norm(np.cross(c[1] - c[0], c[2] - c[0]))
    return np.array(c), centre, area


def select_faces(bfaces, tets, pos, xyz, test):
    sel = []
    area = 0.0
    for f in bfaces:
        c, centre, a = face_geometry(f, tets, pos, xyz)
        if test(c, centre):
            sel.append(f)
            area += a
    return sel, area


# ---------------------------------------------------------------------------
# CalculiX input
# ---------------------------------------------------------------------------

def write_mesh_inp(path, ids, xyz, tets):
    with open(path, "w") as f:
        f.write("*NODE, NSET=NALL\n")
        for n, p in zip(ids, xyz):
            f.write("%d, %.6f, %.6f, %.6f\n" % (n, p[0], p[1], p[2]))
        f.write("*ELEMENT, TYPE=C3D10, ELSET=EALL\n")
        for e, t in enumerate(tets):
            f.write("%d, %s\n" % (e + 1, ", ".join(str(int(v)) for v in t)))


def material_block(mat):
    eps_y = 0.0
    return (
        "*MATERIAL, NAME=AL7075\n"
        "*ELASTIC\n%g, %g\n"
        "*PLASTIC\n%g, %g\n%g, %g\n"
        "*DENSITY\n%g\n"
        "*SOLID SECTION, ELSET=EALL, MATERIAL=AL7075\n"
        % (mat["youngs_modulus"], mat["poisson_ratio"], mat["rp02"], eps_y,
           mat["rm"], mat["plastic_strain_at_rm"], mat["density"] * 1e-3)
    )  # density in t/mm3 for N, mm, s


def dload_lines(faces, pressure):
    return "".join("%d, P%d, %.6f\n" % (e + 1, fnum, pressure) for e, fnum in faces)


def write_static_job(path, mesh_file, mat, fixed_nodes, faces, area, f_max, n_inc):
    """One step: the load rises from zero to f_max. Every increment is saved."""
    with open(path, "w") as f:
        f.write("*INCLUDE, INPUT=%s\n" % os.path.basename(mesh_file))
        f.write("*NSET, NSET=FIX\n")
        for k in range(0, len(fixed_nodes), 12):
            f.write(", ".join(str(int(n)) for n in fixed_nodes[k:k + 12]) + "\n")
        f.write(material_block(mat))
        f.write("*BOUNDARY\nFIX, 1, 3\n")
        f.write("*STEP, NLGEOM, INC=400\n*STATIC\n%g, 1.0, 1e-4, %g\n" % (1.0 / n_inc, 1.0 / n_inc))
        f.write("*DLOAD\n")
        f.write(dload_lines(faces, f_max / area))
        f.write("*NODE FILE\nU\n*EL FILE\nS, PEEQ\n*END STEP\n")


def write_modes_job(path, mesh_file, mat, fixed_nodes):
    with open(path, "w") as f:
        f.write("*INCLUDE, INPUT=%s\n" % os.path.basename(mesh_file))
        f.write("*NSET, NSET=FIX\n")
        for k in range(0, len(fixed_nodes), 12):
            f.write(", ".join(str(int(n)) for n in fixed_nodes[k:k + 12]) + "\n")
        f.write(material_block(mat))
        f.write("*BOUNDARY\nFIX, 1, 3\n")
        f.write("*STEP\n*FREQUENCY\n12\n*NODE FILE\nU\n*END STEP\n")


def run_ccx(job, cwd, allow_stop=False):
    ccx = find_tool("ccx")
    env = dict(os.environ)
    env.setdefault("OMP_NUM_THREADS", str(os.cpu_count() or 1))
    env.setdefault("CCX_NPROC_EQUATION_SOLVER", str(os.cpu_count() or 1))
    r = subprocess.run([ccx, "-i", job], cwd=cwd, capture_output=True, text=True, env=env)
    log = os.path.join(cwd, job + ".log")
    with open(log, "w") as f:
        f.write(r.stdout)
        f.write(r.stderr)
    stopped = "increment size smaller than minimum" in r.stdout or "too many cutbacks" in r.stdout
    if allow_stop and stopped:
        return r.stdout
    if r.returncode != 0 or "*ERROR" in r.stdout:
        print(r.stdout[-3000:])
        fail("CalculiX failed on job %s, see %s" % (job, log))
    return r.stdout


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def read_frd(path):
    """All result blocks of a CalculiX .frd file, in order.

    Returns a list of (time, name, {node: values}).
    """
    blocks = []
    time = None
    with open(path) as f:
        cur = None
        for line in f:
            if line.startswith("  100C"):
                time = float(line[12:24])
            elif line.startswith(" -4"):
                name = line.split()[1]
                cur = (time, name, {})
            elif line.startswith(" -1") and cur is not None:
                node = int(line[3:13])
                vals = [float(line[13 + 12 * k:25 + 12 * k]) for k in range((len(line.rstrip()) - 13) // 12)]
                cur[2][node] = vals
            elif line.startswith(" -3") and cur is not None:
                blocks.append(cur)
                cur = None
    return blocks


def von_mises(s):
    sxx, syy, szz, sxy, syz, szx = s[:6]
    return math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                     + 3.0 * (sxy ** 2 + syz ** 2 + szx ** 2))


def summarise_static(frd, f_max, levels, load_nodes, region_nodes):
    """Force-displacement curve, peak stress and plastic strain.

    The load rises in one step. At each force level the values are read off
    the curve. The lasting dent after the load is gone is the displacement
    minus the elastic spring-back F / k, with k the first, elastic slope.
    That holds as long as the wall does not yield again in the other
    direction while it springs back, which a single push does not cause.
    """
    blocks = read_frd(frd)
    disp = [(t, b) for t, n, b in blocks if n == "DISP"]
    stress = [(t, b) for t, n, b in blocks if n == "STRESS"]
    peeq = [(t, b) for t, n, b in blocks if n == "PE"]
    load_nodes = list(load_nodes)
    curve = [{"force": 0.0, "displacement": 0.0, "von_mises_max": 0.0, "peeq_max": 0.0}]
    for (t, d), (_, s), (_, p) in zip(disp, stress, peeq):
        ux = float(np.mean([-d[n][0] for n in load_nodes if n in d]))
        smax = max(von_mises(s[n]) for n in region_nodes if n in s)
        pmax = max(p[n][0] for n in region_nodes if n in p)
        curve.append({"force": f_max * t, "displacement": ux, "von_mises_max": smax, "peeq_max": pmax})
    reached = curve[-1]["force"]
    if reached < 0.999 * f_max:
        # The wall gave way (no more equilibrium): it collapses plastically.
        print("   NOTE: the job stopped at %.0f N of %.0f N. The wall collapses." % (reached, f_max))
    F = np.array([c["force"] for c in curve])
    k_el = curve[1]["displacement"] and curve[1]["force"] / curve[1]["displacement"]
    per_level = []
    for level in [v for v in levels if v <= reached + 1e-6]:
        d = float(np.interp(level, F, [c["displacement"] for c in curve]))
        per_level.append({
            "force": level,
            "displacement_at_peak": d,
            "von_mises_max_at_peak": float(np.interp(level, F, [c["von_mises_max"] for c in curve])),
            "peeq_max": float(np.interp(level, F, [c["peeq_max"] for c in curve])),
            "lasting_dent": max(0.0, d - level / k_el),
        })
    return curve, per_level, k_el


def main():
    root = module_root()
    case_dir = os.path.join(root, "simulation", "cases", CASE)
    out_dir = os.path.join(root, "simulation", "results", CASE)
    work = os.path.join(out_dir, "exports", "fem")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    with open(os.path.join(case_dir, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)
    g = cfg["geometry"]
    mat = cfg["material_base"]

    print("1. Export the base and mesh it")
    step = export_step(root, cfg, work)
    msh = mesh(step, cfg, work)
    ids, xyz, tets = read_msh(msh)
    tets = to_ccx_order(ids, xyz, tets)
    pos = {int(n): k for k, n in enumerate(ids)}
    print("   %d nodes, %d elements" % (len(ids), len(tets)))
    mesh_inp = os.path.join(work, "mesh.inp")
    write_mesh_inp(mesh_inp, ids, xyz, tets)

    # Fixed: the two bottom strips that touch the machine table (the middle
    # of the bottom face has a 0.5 mm recess).
    fixed = [int(n) for n, p in zip(ids, xyz) if abs(p[2]) < TOL and (p[1] <= 40 + TOL or p[1] >= 170 - TOL)]
    if len(fixed) < 100:
        fail("too few fixed nodes on the bottom strips")
    bfaces = boundary_faces(tets)

    # Pocket back faces: a disc around each bumper axis.
    r = 0.5 * cfg["fem"]["pocket_disc_diameter"]
    xp = g["pocket_back_x"]

    def on_pocket(c, centre):
        if np.any(np.abs(c[:, 0] - xp) > 1e-4):
            return False
        return any(math.hypot(centre[1] - yb, centre[2] - g["bumper_z"]) <= r for yb in g["bumper_y"])

    pocket_faces, pocket_area = select_faces(bfaces, tets, pos, xyz, on_pocket)

    # End wall band: inner face x = 10, at the height of carriage-bottom.
    xw = g["end_wall_inner_x"]
    z0, z1 = g["metal_band_z"]

    def on_band(c, centre):
        return bool(np.all(np.abs(c[:, 0] - xw) < 1e-4) and z0 - 1e-4 <= c[:, 2].min()
                    and c[:, 2].max() <= z1 + 1e-4)

    band_faces, band_area = select_faces(bfaces, tets, pos, xyz, on_band)
    print("   pocket area %.0f mm2, band area %.0f mm2" % (pocket_area, band_area))
    if pocket_area < 0.8 * 2 * math.pi * r * r * 0.9 or band_area < 1000:
        fail("the load faces are smaller than expected")

    def face_nodes(faces):
        s = set()
        for e, fnum in faces:
            for i in FACE_CORNERS[fnum]:
                s.add(int(tets[e][i]))
        return s

    pocket_nodes = face_nodes(pocket_faces)
    band_nodes = face_nodes(band_faces)
    # Stress is read in the end region, away from the fixed bottom edges.
    region = [int(n) for n, p in zip(ids, xyz) if p[0] < 60 and p[2] > 5]

    results = {"mesh": {"nodes": int(len(ids)), "elements": int(len(tets))},
               "material": mat, "load_area": {"pocket": pocket_area, "band": band_area}}

    jobs = [("pocket", pocket_faces, pocket_area, pocket_nodes, cfg["fem"]["pocket_force_levels"]),
            ("band", band_faces, band_area, band_nodes, cfg["fem"]["band_force_levels"])]
    for name, faces, area, nodes, levels in jobs:
        print("2. Job %s: %d load faces, levels %s N" % (name, len(faces), levels))
        f_max = max(levels)
        write_static_job(os.path.join(work, name + ".inp"), mesh_inp, mat, fixed, faces, area,
                         f_max, cfg["fem"]["increments"])
        run_ccx(name, work, allow_stop=True)
        curve, per_level, k_el = summarise_static(os.path.join(work, name + ".frd"), f_max, levels,
                                                  nodes, region)
        results[name] = {"levels": per_level, "curve": curve, "elastic_stiffness_n_per_mm": k_el,
                         "force_reached": curve[-1]["force"]}
        print("   elastic stiffness %.0f N/mm" % k_el)
        for lv in per_level:
            print("   %8.0f N: %.4f mm, %.0f MPa, plastic strain %.4f, lasting dent %.4f mm"
                  % (lv["force"], lv["displacement_at_peak"], lv["von_mises_max_at_peak"],
                     lv["peeq_max"], lv["lasting_dent"]))

    print("3. Job modes")
    write_modes_job(os.path.join(work, "modes.inp"), mesh_inp, mat, fixed)
    run_ccx("modes", work)
    freqs = []
    with open(os.path.join(work, "modes.dat")) as f:
        txt = f.read().split("\n")
    for k, line in enumerate(txt):
        if "E I G E N V A L U E   O U T P U T" in line:
            for row in txt[k + 6:k + 6 + 12]:
                p = row.split()
                if len(p) >= 4:
                    freqs.append(float(p[3]))
            break
    results["modes_hz"] = freqs
    print("   first frequencies (Hz): %s" % ", ".join("%.0f" % v for v in freqs[:6]))

    with open(os.path.join(out_dir, "fem.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("Done: %s" % os.path.join(out_dir, "fem.json"))


main()
