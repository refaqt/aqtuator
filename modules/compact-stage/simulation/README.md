# Simulation

Design-time analysis of the compact stage: models that predict how its parts behave before we
build them. Studies that are not about one stage family stay in the repository-wide
[`simulation/`](../../../simulation/) folder.

| Case | Tool | Question |
| --- | --- | --- |
| [`carriage-bottom-deflection`](cases/carriage-bottom-deflection/) | FreeCAD 1.1 (Gmsh, CalculiX) | How much does the bottom carriage bend under a load on its top, and how high is the stress? (Blocks taken as rigid, one load case.) |
| [`scraper-fit`](cases/scraper-fit/) | Python with cadquery-ocp (no FreeCAD) | Does a printed scraper with M3 countersunk screws fit at each end of carriage-top, and how close does it come to the seal strip? |
| [`strip-end-clamp`](cases/strip-end-clamp/) | Python with cadquery-ocp (no FreeCAD) | Can each strip end be held and its pull set from the top only, with nothing above the strip and nothing past the 440 mm length? |

Results summaries belong in `results/<case-slug>/summary.md`. Heavy outputs
(`results/<case>/exports/`) are gitignored.

## Running

Run from the repository root:

```bash
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" modules/compact-stage/simulation/cases/carriage-bottom-deflection/run_fem.py
```

FreeCAD cases run with `freecadcmd`, the FreeCAD program without a window. They read the part file
and never change it. Do not put an analysis inside a part file in `cad/`. Paths in a case are
relative to this module folder, so a case still works if the module moves to its own repository.
