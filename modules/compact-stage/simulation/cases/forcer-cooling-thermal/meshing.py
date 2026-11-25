# SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Mesh each body of the thermal model on its own with Gmsh.

Each body gets its own mesh. The bodies are joined later, in the solver, at
the faces where they touch. This is more robust than one shared mesh, because
Gmsh does not have to cut all parts against each other.

The mesh is second order (10-node tetrahedra) with straight edges. The size is
small at the water channel, the ports and the cooling block, and larger far
from the forcer.

If Gmsh cannot mesh a body, it names the face that fails. Then that face is
removed from the solid (FreeCAD defeaturing: the faces next to it grow over
the gap), and the body is meshed again. This happens for a few small corner
faces in carriage-top. Each removed face is written to the log.
"""

import os
import re
import shutil
import subprocess
import sys

import numpy as np

# Gmsh 10-node tetrahedron order: 0-1, 1-2, 2-0, 3-0, 3-2, 3-1 (edge nodes 4..9).
# This module uses the CalculiX order: 0-1, 1-2, 2-0, 0-3, 1-3, 2-3.
GMSH_TO_CCX = [0, 1, 2, 3, 4, 5, 6, 7, 9, 8]


def find_tool(name):
    path = shutil.which(name)
    if path:
        return path
    for cand in (os.path.join(os.path.dirname(sys.executable), name),
                 os.path.join(os.path.dirname(sys.executable), name + ".exe")):
        if os.path.exists(cand):
            return cand
    raise SystemExit("ERROR: %s not found. On Linux run: bash setup-fem.sh" % name)


def size_fields(body, cfg):
    """Gmsh size fields for one body: list of (size inside, box, ramp width)."""
    m = cfg["mesh"]
    f, mid = m["size_fine"], m["size_mid"]
    ch = cfg["_channel_box"]      # x0, x1, y0, y1, z0, z1 of the channel
    pk = cfg["_pocket_box"]       # forcer pocket ceiling: x0, x1, y0, y1, z
    bl = cfg["_block_box"]        # cooling block: x0, x1, y0, y1, z0, z1
    boxes = []
    if body == "carriage_bottom":
        boxes.append((f, [ch[0] - 1.5, ch[1] + 1.5, ch[2] - 1.5, ch[3] + 1.5, ch[4] - 0.5, ch[5] + 1.6], 2.0))
        boxes.append((f * 1.2, [bl[0] - 0.5, bl[1] + 0.5, bl[2] - 0.5, bl[3] + 0.5, bl[4] - 0.5, bl[5] + 0.5], 2.0))
        boxes.append((mid, [pk[0] - 3, pk[1] + 3, pk[2] - 3, pk[3] + 3, pk[4] - 4, pk[4] + 8], 5.0))
    if body == "forcer":
        boxes.append((f * 1.3, [ch[0] - 1.5, ch[1] + 1.5, ch[2] - 1.5, ch[3] + 1.5, ch[4] - 0.8, ch[4] + 0.5], 3.0))
    return boxes


def global_size(body, cfg):
    m = cfg["mesh"]
    return {"water": m["size_fine"], "cooling_block": m["size_fine"] * 1.2,
            "base": m["size_base"], "carriage_bottom": m["size_coarse"],
            "carriage_top": m["size_coarse"], "forcer": m["size_coarse"],
            "track": m["size_coarse"]}.get(body, m["size_coarse"] * 0.65)


def write_geo(path, step, msh, body, cfg, scale=1.0, alg2d=6):
    gmax = global_size(body, cfg) * scale
    lines = [
        'SetFactory("OpenCASCADE");',
        "Geometry.OCCFixDegenerated = 1;",
        "Geometry.OCCFixSmallEdges = 1;",
        "Geometry.OCCFixSmallFaces = 1;",
        'Merge "%s";' % os.path.basename(step),
        "Mesh.MeshSizeFromPoints = 0;",
        "Mesh.MeshSizeFromCurvature = 0;",
        "Mesh.MeshSizeExtendFromBoundary = 0;",
        "Mesh.MeshSizeMax = %g;" % gmax,
        "Mesh.MeshSizeMin = %g;" % (0.4 * cfg["mesh"]["size_fine"] * scale),
    ]
    ids = []
    for i, (vin, b, th) in enumerate(size_fields(body, cfg)):
        n = i + 1
        lines += ["Field[%d] = Box;" % n,
                  "Field[%d].VIn = %g; Field[%d].VOut = %g;" % (n, vin * scale, n, gmax),
                  "Field[%d].XMin = %g; Field[%d].XMax = %g;" % (n, b[0], n, b[1]),
                  "Field[%d].YMin = %g; Field[%d].YMax = %g;" % (n, b[2], n, b[3]),
                  "Field[%d].ZMin = %g; Field[%d].ZMax = %g;" % (n, b[4], n, b[5]),
                  "Field[%d].Thickness = %g;" % (n, th)]
        ids.append(n)
    if ids:
        n = len(ids) + 1
        lines += ["Field[%d] = Min;" % n,
                  "Field[%d].FieldsList = {%s};" % (n, ", ".join(str(i) for i in ids)),
                  "Background Field = %d;" % n]
    lines += ["Mesh.Algorithm = %d;" % alg2d, "Mesh.Algorithm3D = 1;", "Mesh.ElementOrder = 2;",
              "Mesh.SecondOrderLinear = 1;", "Mesh.Optimize = 1;", "Mesh.MshFileVersion = 2.2;",
              "Mesh 3;", 'Save "%s";' % os.path.basename(msh)]
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def mesh_body(body, folder, cfg, scale=1.0, log=print, max_fixes=6):
    """Mesh one body. Returns the path of the .msh file and the removed faces."""
    import Part
    step = os.path.join(folder, body + ".step")
    tag = "" if scale == 1.0 else "_s%g" % scale
    msh = os.path.join(folder, body + tag + ".msh")
    geo = os.path.join(folder, body + tag + ".geo")
    gmsh = find_tool("gmsh")
    removed = []
    work_step = step
    algs = [6, 5, 1]
    a = 0
    for attempt in range(max_fixes + len(algs)):
        write_geo(geo, work_step, msh, body, cfg, scale, algs[a])
        if os.path.exists(msh):
            os.remove(msh)
        r = subprocess.run([gmsh, os.path.basename(geo), "-nt", "1", "-v", "2", "-"],
                           cwd=folder, capture_output=True, text=True)
        text = r.stdout + r.stderr
        ok = os.path.exists(msh) and "Error" not in text
        if ok:
            return msh, removed
        hit = re.search(r"on surface (\d+)", text) or re.search(r"periodic surface (\d+)", text)
        if not hit:
            print(text[-3000:])
            raise SystemExit("ERROR: gmsh failed on %s" % body)
        face = int(hit.group(1))
        shape = Part.read(work_step)
        bad = shape.Faces[face - 1]
        if isinstance(bad.Surface, Part.Plane):
            # A flat face: try another surface mesh method first.
            a += 1
            if a >= len(algs):
                raise SystemExit("ERROR: gmsh fails on flat face %d of %s" % (face, body))
            log("  %s: gmsh failed on flat face %d; trying surface method %d" % (body, face, algs[a]))
            continue
        log("  %s: gmsh failed on face %d (%s, %.2f mm2); removing it" % (
            body, face, type(bad.Surface).__name__, bad.Area))
        removed.append({"face": face, "type": type(bad.Surface).__name__, "area": bad.Area,
                        "bbox": [bad.BoundBox.XMin, bad.BoundBox.YMin, bad.BoundBox.ZMin,
                                 bad.BoundBox.XMax, bad.BoundBox.YMax, bad.BoundBox.ZMax]})
        fixed = shape.defeaturing([bad])
        if not fixed.isValid() or len(fixed.Solids) != 1 or len(fixed.Faces) >= len(shape.Faces):
            raise SystemExit("ERROR: could not remove face %d of %s" % (face, body))
        work_step = os.path.join(folder, body + "_defeatured.step")
        fixed.exportStep(work_step)
    raise SystemExit("ERROR: %s still fails after %d tries" % (body, max_fixes + len(algs)))


def read_msh(path):
    """Nodes (N x 3) and 10-node tetrahedra (CalculiX order, 0-based) from Gmsh 2.2 ASCII."""
    with open(path) as fh:
        txt = fh.read()
    a = txt.index("$Nodes") + len("$Nodes")
    b = txt.index("$EndNodes")
    block = txt[a:b].split("\n", 2)
    n = int(block[1])
    arr = np.array(block[2].split(), dtype=float).reshape(n, 4)
    ids = arr[:, 0].astype(np.int64)
    xyz = arr[:, 1:]
    a = txt.index("$Elements") + len("$Elements")
    b = txt.index("$EndElements")
    lines = txt[a:b].strip().split("\n")[1:]
    tets = []
    for ln in lines:
        p = ln.split()
        if p[1] == "11":
            ntag = int(p[2])
            tets.append([int(x) for x in p[3 + ntag:3 + ntag + 10]])
    tets = np.array(tets, dtype=np.int64)
    pos = np.full(ids.max() + 1, -1, dtype=np.int64)
    pos[ids] = np.arange(len(ids))
    tets = pos[tets][:, GMSH_TO_CCX]
    used = np.unique(tets)
    remap = np.full(len(ids), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return xyz[used], remap[tets]
