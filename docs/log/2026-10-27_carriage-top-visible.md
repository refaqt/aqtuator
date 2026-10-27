# 2026-10-27 — The top carriage is visible in the assembly

**Role(s):** cad

## Goal

The top carriage was hidden in the compact-stage assembly. Niels Bosmans made it visible in
FreeCAD and saved the part and the assembly. The pull request did not pass the checks. Make it
pass.

## Short answer

- **The checks pass again.** The two saved files no longer matched their recorded measurements,
  because FreeCAD saved them by hand. The measurements are now written again from the saved files.
- **No shape changed.** No volume, no position and no part changed. Only some bounding boxes moved
  by less than 1 mm, from rounding in the measurement.

## Work Done

- New measurement records (fingerprints) for the top carriage and the compact-stage assembly.

## Next Steps

1. After you save a CAD file by hand, write its fingerprint again before you open a pull request.

<details>
<summary>Technical notes</summary>

- `validate_cad.py` failed: `carriage-top.FCStd` and `compact-stage.FCStd` "changed since its
  fingerprint was written". Neither part has a `build_model.py`.
- FreeCAD was not running with its RPC server, so the fingerprints were written headless with
  `freecadcmd.exe` (FreeCAD 1.1.4) and `cad_fingerprint.write(doc, params={})`. The files were
  opened and measured only, never saved.
- When the assembly is opened alone in FreeCADCmd, the link `carriage_bottom001` is not restored
  ("Link not restored"). The fingerprint then misses the bottom carriage and records
  `saved: false`. Opening `carriage-bottom.FCStd` first restores the link. The assembly fingerprint
  was written that way.
- Assembly diff: only the bounding boxes of the four TA17-7 dampers (by less than 1 mm) and of
  `carriage_bottom001` (0.0006 mm). Top carriage diff: only the bounding boxes of five sketches,
  by less than 0.03 mm. No volume or centre of mass changed.
- `doqs check`: all gates passed. On Windows it needs `PYTHONIOENCODING=utf-8`, or
  `validate_names.py` crashes on an arrow character.
- Mistake rules checked: [wrap crashed the open FreeCAD](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)
  (no `doqs wrap`, nothing sent to an open window), the PowerShell rules (all shell work in bash).

</details>
