# Simulation

Design-time analysis of the compact stage: models that predict how its parts behave before we
build them. Studies that are not about one stage family stay in the repository-wide
[`simulation/`](../../../simulation/) folder.

| Case | Tool | Question |
| --- | --- | --- |
| [`carriage-bottom-deflection`](cases/carriage-bottom-deflection/) | FreeCAD 1.1 (Gmsh, CalculiX) | How much does the bottom carriage bend under a load on its top, and how high is the stress? (Blocks taken as rigid, one load case.) |
| [`end-stop-crash`](cases/end-stop-crash/) | FreeCAD 1.1 (Gmsh, CalculiX), numpy | What does a crash into the end stops at 2 m/s and full motor force do to the base, the guide blocks, the read head and the screw joints, for payloads up to 20 kg and a second stage on top? |
| [`scraper-fit`](cases/scraper-fit/) | Python with cadquery-ocp (no FreeCAD) | Does a printed scraper with M3 countersunk screws fit at each end of carriage-top, and how close does it come to the seal strip? |
| [`strip-pull`](cases/strip-pull/) | Python and Node | How far must the strip ends move for a given pull, and how hard does a 0.15 mm strip press on carriage-top? |
| [`strip-end-insert`](cases/strip-end-insert/) | Python with cadquery-ocp (no FreeCAD) and scipy | Does the corner insert concept for the strip ends fit the base and the carriage (with corner pockets and a spring end), and how does its pull spread across the strip? |
| [`strip-seal-fit`](cases/strip-seal-fit/) | Node | How far must seal strip rollers 2 and 3 go down, and which pull keeps the strip off both carriage halves with an infinite fatigue life? |

Results summaries belong in `results/<case-slug>/summary.md`. Heavy outputs
(`results/<case>/exports/`) are gitignored.

## Running

Run from the repository root:

```bash
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" modules/compact-stage/simulation/cases/carriage-bottom-deflection/run_fem.py
```

On Linux and in the cloud environment, run `bash setup-fem.sh` from the repository root once. It
installs FreeCAD 1.1 with Gmsh and CalculiX, and puts `freecadcmd`, `gmsh` and `ccx` on the path.
Then use `freecadcmd` in place of the Windows path.

FreeCAD cases run with `freecadcmd`, the FreeCAD program without a window. They read the part file
and never change it. Do not put an analysis inside a part file in `cad/`. Paths in a case are
relative to this module folder, so a case still works if the module moves to its own repository.
