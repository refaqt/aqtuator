# CAD

FreeCAD models of the machine and the actuator. Nothing here yet — the project has so far been
measurement and control; mechanical design of the actuator is the next phase. First-order concept
sizing is in
[`simulation/cases/short-stroke-actuator-concepts`](../simulation/cases/short-stroke-actuator-concepts/).

**FreeCAD v1.1**, built-in Assembly workbench. Read
[`doqs/docs/decisions/2026-06-24_freecad-master-sketches-body.md`](../doqs/docs/decisions/2026-06-24_freecad-master-sketches-body.md)
before starting top-down design, and
[`doqs/skills/freecad/SKILL.md`](../doqs/skills/freecad/SKILL.md) when something misbehaves.

| Folder | Contents |
| --- | --- |
| `assemblies/` | Assembly documents linking module parts by relative path |
| `parts/` | One folder per part, each with its own `exports/` |
| `exports/` | STEP/STL of this module's assembly |
| `params/` | Parameter sets — `default.csv` plus override files |

`.FCStd`, `.step`, `.stp`, `.stl` and `.3mf` are tracked with Git LFS (see `.gitattributes`).
Measurement data is **not** — it lives on Google Drive, which is what keeps LFS usage inside the
free tier.

**Never edit `.FCStd` files directly.** After changing parameters, run `cad/sync_params.py` inside
FreeCAD.
