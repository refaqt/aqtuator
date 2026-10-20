# 2026-10-20 — The stress analysis of the bottom carriage runs, as its own simulation case

**Role(s):** simulation

## Goal

Niels set up a stress analysis (a finite element analysis) of the bottom carriage in FreeCAD. Gmsh
made a mesh, but the CalculiX solver did not run. Two questions: does the analysis belong in the
part file, and how do we get results?

## Work Done

- **The analysis now lives in its own case, not in the part file.** A script reads the part file,
  copies the solid, and builds the analysis in a new document. The part file stays geometry only.
  A mesh inside a part file makes the file much larger in Git and breaks the geometry check. The
  load, the material and the mesh size are in a text file that a reviewer can read.
- **The solver failed because of inside-out elements.** Gmsh moves the middle node of each element
  edge onto curved faces. Near small holes and rounded edges, that folded a few elements over, and
  CalculiX stopped. Keeping the middle nodes straight fixes it. We tested both ways: with straight
  middle nodes the solver runs on the coarse and the fine mesh. With curved middle nodes it fails
  on both.
- **The first results:** 200 N down on the four corner edges of the top moves the carriage
  0.0041 mm at most. The highest stress away from the load edges is 5 MPa.
- **You can look at the result in colour.** The script writes a VTK file (a common format for
  mesh results) that FreeCAD and ParaView open.
- **The script finds faces by position and size, not by name.** FreeCAD names like `Face6` change
  when the part changes. If the part changes so much that the script cannot find the four block
  faces and the four load edges, it stops and says so.

## Open Questions

- **The 200 N load at the corners is a test load.** The load that matters most is probably the
  magnetic pull of the MK21 forcer, about 963 N. That value is from the parts list and is not yet
  checked against the data sheet.
- **The analysis is still open, unsaved, in the FreeCAD window** that holds the part file. Close it
  without saving, so the part file stays clean.

<details>
<summary>Technical notes</summary>

- Case: `modules/compact-stage/simulation/cases/carriage-bottom-deflection/` (`case.toml`, `run_fem.py`, `README.md`).
- Results: `modules/compact-stage/simulation/results/carriage-bottom-deflection/` (`summary.md`, `results.json`).
  `exports/` holds the STEP, the result as VTK and the CalculiX files, and is gitignored.
- No `.FCStd` is saved in `exports/`. `validate_cad.py` scans every `.FCStd` on disk, also in
  gitignored folders, and fails on one without a fingerprint.
- FreeCAD 1.1 cannot open `Mesh.frd` on its own: `importCcxFrdResults.insert` calls
  `setupPipeline` with no analysis and fails on `None.getObjectsOfType`. The VTK file
  (quadratic tetrahedra, `Displacement` and `VonMises` per node) opens as a `Fem::FemPostPipeline`.
- Run: `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" modules/compact-stage/simulation/cases/carriage-bottom-deflection/run_fem.py`,
  about two minutes. FreeCAD 1.1.4.
- Fix: `FemMeshGmsh.SecondOrderLinear = True`. CalculiX error: `*ERROR in e_c3d: nonpositive jacobian`.
- Mesh test: 2–20 mm straight gives 0.0036 mm and solves. 0.5–5 mm curved fails in elements 59849
  and 97107. 0.5–5 mm straight gives 0.0041 mm (case default).
- The script reads `Mesh.frd` with `read_frd_result` and works out von Mises itself.
  `FemToolsCcx.load_results()` took more than ten minutes in `freecadcmd` and was dropped.
- Fixed faces: down-facing planar faces at z = 10 mm with a 35 × 48 mm bounding box. A fifth
  down-facing face at z = 10 mm exists (1225 mm²) and is left out.
- Load edges: straight edges along x, 6 mm long, at z = 27.5 mm.

</details>
