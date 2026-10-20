"""Stress and deflection of the bottom carriage under a load on its top.

Run it with the Python that comes with FreeCAD, from the repository root:

    "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" modules/compact-stage/simulation/cases/carriage-bottom-deflection/run_fem.py

The script only reads the part file. It copies the solid into a new
document, builds the analysis there (material, fixed faces, force, mesh),
runs CalculiX, and writes:

- simulation/results/carriage-bottom-deflection/results.json (committed)
- simulation/results/carriage-bottom-deflection/exports/ (not committed):
  the solid as STEP, the result as VTK to open in FreeCAD or ParaView,
  and the CalculiX files.

Faces and edges are found by their position, not by their FreeCAD name
(Face6, Edge278). Those names change when the part changes.
"""

import functools
import json
import math
import os
import shutil
import sys
import tomllib

import FreeCAD as App
import ObjectsFem
import Part
from femmesh.gmshtools import GmshTools
from feminout.importCcxFrdResults import read_frd_result
from femtools import ccxtools

print = functools.partial(print, flush=True)
CASE = "carriage-bottom-deflection"
TOL = 1e-6


def module_root():
    # Paths are relative to the module folder, so the case still works if
    # the module moves to its own repository. freecadcmd does not set
    # __file__ in every version, so fall back to the working directory,
    # which must then be the repository root.
    here = globals().get("__file__")
    if here:
        return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", ".."))
    return os.path.join(os.getcwd(), "modules", "compact-stage")


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def find_fixed_faces(shape, z, size, expected):
    names = []
    for i, face in enumerate(shape.Faces):
        bb = face.BoundBox
        if abs(bb.ZMin - z) > TOL or abs(bb.ZMax - z) > TOL:
            continue
        if abs(bb.XLength - size[0]) > 1e-3 or abs(bb.YLength - size[1]) > 1e-3:
            continue
        u0, u1, v0, v1 = face.ParameterRange
        normal = face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        if normal.z < -0.999:
            names.append("Face%d" % (i + 1))
    if len(names) != expected:
        fail("found %d fixed faces at z = %s mm, expected %d. Did the part change?"
             % (len(names), z, expected))
    return names


def find_load_edges(shape, z, length, expected):
    names = []
    for i, edge in enumerate(shape.Edges):
        bb = edge.BoundBox
        if abs(bb.ZMin - z) > TOL or abs(bb.ZMax - z) > TOL:
            continue
        if not isinstance(edge.Curve, Part.Line) or abs(edge.Length - length) > TOL:
            continue
        if abs(bb.YMax - bb.YMin) > TOL:  # along x only
            continue
        names.append("Edge%d" % (i + 1))
    if len(names) != expected:
        fail("found %d load edges at z = %s mm, expected %d. Did the part change?"
             % (len(names), z, expected))
    return names


def von_mises(t):
    sxx, syy, szz, sxy, syz, szx = t
    return math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                     + 3.0 * (sxy ** 2 + syz ** 2 + szx ** 2))


def write_vtk(path, nodes, tetra10, disp, stress):
    """Write the result as a legacy VTK file. FreeCAD and ParaView open it."""
    ids = sorted(nodes)
    index = {n: i for i, n in enumerate(ids)}
    with open(path, "w") as f:
        f.write("# vtk DataFile Version 3.0\ncarriage-bottom-deflection\nASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\nPOINTS %d double\n" % len(ids))
        for n in ids:
            v = nodes[n]
            f.write("%.6g %.6g %.6g\n" % (v.x, v.y, v.z))
        f.write("CELLS %d %d\n" % (len(tetra10), 11 * len(tetra10)))
        for e in tetra10.values():
            # The reader turned the CalculiX order into the FreeCAD order.
            # Turn it back: the CalculiX C3D10 order is the VTK order.
            ccx = (e[1], e[0], e[2], e[3], e[4], e[6], e[5], e[8], e[7], e[9])
            f.write("10 " + " ".join(str(index[n]) for n in ccx) + "\n")
        f.write("CELL_TYPES %d\n" % len(tetra10))
        f.write("24\n" * len(tetra10))  # VTK_QUADRATIC_TETRA
        f.write("POINT_DATA %d\nVECTORS Displacement double\n" % len(ids))
        for n in ids:
            v = disp[n]
            f.write("%.6g %.6g %.6g\n" % (v.x, v.y, v.z))
        f.write("SCALARS VonMises double 1\nLOOKUP_TABLE default\n")
        for n in ids:
            f.write("%.6g\n" % stress[n])


def distance_to_segment(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.dot(ab)))
    return (p - (a + ab * t)).Length


def distance_to_edges(point, segments):
    return min(distance_to_segment(point, a, b) for a, b in segments)


def main():
    root = module_root()
    case_dir = os.path.join(root, "simulation", "cases", CASE)
    out_dir = os.path.join(root, "simulation", "results", CASE)
    exports = os.path.join(out_dir, "exports")
    ccx_dir = os.path.join(exports, "ccx")
    shutil.rmtree(ccx_dir, ignore_errors=True)
    os.makedirs(ccx_dir)

    with open(os.path.join(case_dir, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)

    # 1. Copy the solid out of the part file. The part file stays untouched.
    part_path = os.path.join(root, cfg["geometry"]["part_file"])
    part_doc = App.openDocument(part_path, True)  # hidden
    shape = part_doc.getObject(cfg["geometry"]["body"]).Shape.copy()
    App.closeDocument(part_doc.Name)
    if len(shape.Solids) != 1 or not shape.isValid():
        fail("the body is not one valid solid")
    shape.exportStep(os.path.join(exports, "carriage-bottom.step"))

    doc = App.newDocument("carriage_bottom_fem")
    geo = doc.addObject("Part::Feature", "CarriageBottom")
    geo.Shape = shape
    doc.recompute()

    # 2. Analysis, solver, material.
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")
    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "SolverCcxTools")
    solver.AnalysisType = "static"
    solver.GeometricalNonlinearity = "linear"
    analysis.addObject(solver)

    mat = cfg["material"]
    material = ObjectsFem.makeMaterialSolid(doc, "Material")
    card = material.Material
    card["Name"] = mat["card"]
    card["YoungsModulus"] = "%s MPa" % mat["youngs_modulus"]
    card["PoissonRatio"] = str(mat["poisson_ratio"])
    card["Density"] = "%s kg/mm^3" % mat["density"]
    material.Material = card
    analysis.addObject(material)

    # 3. Fixed faces and force.
    fixed_faces = find_fixed_faces(shape, cfg["fixed"]["face_z"], cfg["fixed"]["face_size"],
                                   cfg["fixed"]["expected_faces"])
    fixed = ObjectsFem.makeConstraintFixed(doc, "Fixed")
    fixed.References = [(geo, tuple(fixed_faces))]
    analysis.addObject(fixed)

    load = cfg["load"]
    load_edges = find_load_edges(shape, load["edge_z"], load["edge_length"], load["expected_edges"])
    d = App.Vector(*load["direction"])
    force = ObjectsFem.makeConstraintForce(doc, "Force")
    force.References = [(geo, tuple(load_edges))]
    force.Force = "%s N" % abs(load["force"])
    force.DirectionVector = d * (1 if load["force"] >= 0 else -1)
    analysis.addObject(force)

    # 4. Mesh.
    m = cfg["mesh"]
    mesh = ObjectsFem.makeMeshGmsh(doc, "Mesh")
    mesh.Shape = geo
    mesh.ElementOrder = "2nd"
    mesh.ElementDimension = "3D"
    mesh.CharacteristicLengthMax = "%s mm" % m["length_max"]
    mesh.CharacteristicLengthMin = "%s mm" % m["length_min"]
    mesh.SecondOrderLinear = m["second_order_linear"]
    analysis.addObject(mesh)
    doc.recompute()
    err = GmshTools(mesh).create_mesh()
    if err:
        fail("Gmsh: %s" % err)
    fem_mesh = mesh.FemMesh
    print("mesh: %d nodes, %d tetrahedra" % (fem_mesh.NodeCount, fem_mesh.VolumeCount))

    # 5. Solve.
    fea = ccxtools.FemToolsCcx(analysis, solver)
    fea.update_objects()
    fea.setup_working_dir(ccx_dir)
    fea.setup_ccx()
    msg = fea.check_prerequisites()
    if msg:
        fail("prerequisites: %s" % msg)
    fea.write_inp_file()
    fea.ccx_run()
    frd = os.path.join(ccx_dir, "Mesh.frd")
    if not os.path.isfile(frd) or os.path.getsize(frd) == 0:
        fail("CalculiX gave no results. Read the CalculiX output in %s" % ccx_dir)

    # 6. Numbers. Read the result file directly. Loading it into the
    # document (fea.load_results) takes more than ten minutes without a
    # FreeCAD window, for a few seconds of work here.
    frd_data = read_frd_result(frd)
    nodes = frd_data["Nodes"]
    step = frd_data["Results"][-1]
    disp = step["disp"]
    stress = {n: von_mises(t) for n, t in step["stress"].items()}
    if not disp or not stress:
        fail("the result file holds no displacement or no stress")

    segments = [(e.Vertexes[0].Point, e.Vertexes[1].Point)
                for e in (shape.getElement(n) for n in load_edges)]
    radius = load["stress_exclusion_radius"]
    away = [s for n, s in stress.items() if distance_to_edges(nodes[n], segments) > radius]
    n_max = max(stress, key=stress.get)
    p = nodes[n_max]

    out = {
        "case": CASE,
        "freecad": ".".join(App.Version()[:3]),
        "part_file": cfg["geometry"]["part_file"],
        "load_N": load["force"],
        "fixed_faces": fixed_faces,
        "load_edges": load_edges,
        "mesh": {"nodes": fem_mesh.NodeCount, "tetrahedra": fem_mesh.VolumeCount,
                 "length_max_mm": m["length_max"], "length_min_mm": m["length_min"],
                 "second_order_linear": m["second_order_linear"]},
        "max_displacement_mm": round(max(v.Length for v in disp.values()), 5),
        "max_downward_displacement_mm": round(-min(v.z for v in disp.values()), 5),
        "max_von_mises_MPa": round(stress[n_max], 2),
        "max_von_mises_at_mm": [round(p.x, 1), round(p.y, 1), round(p.z, 1)],
        "max_von_mises_away_from_load_MPa": round(max(away), 2),
        "stress_exclusion_radius_mm": radius,
    }
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    write_vtk(os.path.join(exports, "carriage-bottom-deflection.vtk"),
              nodes, frd_data["Tetra10Elem"], disp, stress)
    # No .FCStd is saved. The CAD check reads every .FCStd on disk, also in
    # ignored folders, and fails on one without a fingerprint.
    App.closeDocument(doc.Name)
    print(json.dumps(out, indent=2))


try:
    main()
except SystemExit:
    raise
except Exception:
    # freecadcmd hides a traceback from a script, so print it here.
    import traceback
    traceback.print_exc()
    sys.exit(1)
