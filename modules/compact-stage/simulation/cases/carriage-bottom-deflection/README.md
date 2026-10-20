# carriage-bottom-deflection

How much does the bottom carriage of the compact stage bend, and how high is the stress, when a
force pushes down on its top? This is a finite element analysis (a stress calculation on a mesh of
small elements) in FreeCAD, solved with CalculiX.

**Tool:** FreeCAD 1.1 with its own Python, Gmsh and CalculiX. All three come with the FreeCAD
installer. Nothing else to install.

```bash
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" modules/compact-stage/simulation/cases/carriage-bottom-deflection/run_fem.py
```

Run it from the repository root. It takes about two minutes. The numbers go to
[`results.json`](../../results/carriage-bottom-deflection/results.json).

**To see the colours:** open
`modules/compact-stage/simulation/results/carriage-bottom-deflection/exports/carriage-bottom-deflection.vtk` in FreeCAD
(File, Open) or in ParaView. It holds the movement (`Displacement`) and the stress (`VonMises`, in
MPa) at every node. The `exports/` folder is not in Git. Run the script once to make it.

The script saves no `.FCStd` file. The CAD check reads every `.FCStd` file on disk, also in ignored
folders, and fails on one without a fingerprint. FreeCAD 1.1 also cannot open the CalculiX result
file (`Mesh.frd`) on its own, so the VTK file is the way to look at the result.

## Why the analysis is not in the part file

The part file holds the shape and nothing else. This case reads the part file, copies the solid
into a new document, and builds the analysis there. That keeps four things right:

- **The part file stays small and clean.** A mesh and a result add tens of megabytes to the file
  in Git, at every save.
- **The geometry check stays happy.** A mesh object in a part file breaks the fingerprint, the
  record of the shape that the checks compare against.
- **The analysis is text.** The load, the material and the mesh size are in
  [`case.toml`](case.toml). A reviewer can read and compare them. A setting inside an `.FCStd`
  file cannot be compared in a pull request.
- **It runs again after every change to the part.** The script finds the faces and edges by their
  position and size, not by FreeCAD names like `Face6`. Those names change when the part changes.
  If the part changes so much that the script cannot find exactly the expected faces, it stops and
  says so.

There is no separate STEP export step. The script reads the `.FCStd` file straight away, so the
analysis can never use an old export. It still writes a STEP file of the exact solid it used, next
to the results.

## Inputs

All inputs are in [`case.toml`](case.toml).

| Input | Value | Note |
| --- | --- | --- |
| Material | 6061-T6, E = 69 GPa, ν = 0.33 | Stand-in until the alloy is chosen |
| Fixed | The four flat faces at z = 10 mm where the QEH15SA blocks sit | Fully fixed. The real blocks give a little |
| Force | 200 N down in total | Spread over four 6 mm edges on the top face, at y = 10 mm and y = 170 mm, at both ends in x |
| Mesh | Second order tetrahedra, 0.5 to 5 mm | Straight middle nodes, see below |

## What went wrong in the first setup

The first setup was inside the part file. Gmsh made a mesh, but CalculiX stopped with
"nonpositive jacobian" in about ten elements. That means those elements were turned inside out.

- **The cause: curved middle nodes.** A second order element has a node in the middle of each
  edge. Gmsh moves that node onto curved faces. In a small element near a hole or a rounded edge,
  that move can fold the element over. `second_order_linear = true` keeps the middle nodes on the
  straight edge. With that one setting, even the first coarse mesh (2 to 20 mm) solves. The fine
  mesh with curved middle nodes still fails in two elements.
- **The mesh size is for accuracy, not for the error.** The coarse mesh gives 0.0036 mm of
  deflection, the 0.5 to 5 mm mesh gives 0.0041 mm. That is 11 % apart, so this case uses the
  finer mesh.

## Limits of this model

- **The stress right at a load edge is not real.** A force on a line has no area, so the
  calculated stress there grows without limit as the mesh gets finer. The results give two peaks:
  the peak everywhere, and the peak more than 3 mm away from the load edges. Use the second one.
- **The blocks are rigid.** The real QEH15SA blocks and rails give a little. The real deflection is
  a bit larger.
- **One load case.** The magnetic pull of the forcer, the cutting force and the motor force are not
  in it yet. Add them as new load cases when the numbers are known.

Results: [`results/carriage-bottom-deflection/summary.md`](../../results/carriage-bottom-deflection/summary.md).
