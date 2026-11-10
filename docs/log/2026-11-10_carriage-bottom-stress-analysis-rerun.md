# 2026-11-10 — The stress analysis of the bottom carriage runs again on the new part

**Role(s):** simulation, cad

## Goal

The stress analysis of the bottom carriage stopped with an error. It could not find the four faces
where the guide blocks sit. The part had changed since 2026-10-20: the guide blocks moved, and the
damper slots and the forcer cooling groove were added. Make the analysis find its faces again, and
run it on the new part.

## Work Done

- **The analysis runs again.** Two sizes in the load case changed with the part. The guide block
  seats are now 35 × 58 mm (they were 35 × 48 mm). The four load edges at the top corners are now
  7 mm long (they were 6 mm). The script itself did not change.
- **The new part is a little softer, and still far from any limit.** 200 N down moves it 0.0044 mm
  at most (was 0.0041 mm, about 9 % more). The highest real stress is 7.5 MPa (was 5.0 MPa).
  Aluminium 6061-T6 yields at about 240 MPa.
- **The highest stress moved** to a sharp inside corner where a side wing meets a front guide block
  seat. A sharp corner makes this number grow a little with a finer mesh, so read it as "below
  10 MPa".
- **The case README now explains how to run it on Linux.** The Linux FreeCAD package may come
  without the CalculiX solver, and the part file must be pulled from Git LFS (large file storage)
  first.

Results: [summary](../../modules/compact-stage/simulation/results/carriage-bottom-deflection/summary.md).

## Open Questions

- **The model holds each whole 35 × 58 mm seat.** If the real block touches only part of a seat,
  the real carriage bends a little more than the model says.
- **The 200 N load at the corners is still a test load.** The magnetic pull of the forcer, about
  963 N, is the next load case to add.

<details>
<summary>Technical notes</summary>

- Error before the fix: `ERROR: found 0 fixed faces at z = 10.0 mm, expected 4. Did the part change?`
- `case.toml`: `[fixed] face_size = [35.0, 58.0]` (was `[35.0, 48.0]`), `[load] edge_length = 7.0`
  (was `6.0`). `face_z`, `edge_z` and the expected counts did not change.
- Faces found: Face2, Face12, Face95, Face125. Load edges: Edge406, Edge433, Edge455, Edge474.
  A fifth down-facing face at z = 10 mm (97 × 62.5 mm) is left out by its size.
- Mesh: 181,867 nodes, 103,174 tetrahedra (was 145,591 and 83,604). No inside-out elements.
- Highest von Mises stress more than 3 mm from a load edge: 7.48 MPa at (191.0, 14.2, 16.5) mm.
  Next ones: about 6.1 MPa next to the load edges, just outside the 3 mm radius.
- Run: `freecadcmd modules/compact-stage/simulation/cases/carriage-bottom-deflection/run_fem.py`,
  FreeCAD 1.1.3, CalculiX 2.23, about 90 s.
- The request said to run `bash setup-fem.sh` first. That file does not exist in the repository.
  CalculiX was installed by hand instead:
  `micromamba create -y -p /opt/calculix -c conda-forge calculix` and a link from
  `/usr/local/bin/ccx`.

</details>
