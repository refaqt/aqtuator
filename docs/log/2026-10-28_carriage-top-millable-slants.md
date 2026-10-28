# 2026-10-28 — The slanted edges of the top carriage can be milled

**Role(s):** cad

## Goal

Niels Bosmans changed the top carriage in FreeCAD. The slanted edges had inside corners that a
milling cutter cannot make. Commit the change, and make the checks pass.

## Short answer

- **The slanted edges can now be milled.** The sharp inside corners are gone.
- **The outside size did not change.** The part is about 4.7 cm³ lighter (434.8 → 430.1 cm³).
- **The checks pass.** The fingerprint was written again from the saved file.

## Work Done

- New fingerprint for the top carriage.

## Next Steps

1. Check that the assembly still fits, and that the top carriage does not touch other parts.

<details>
<summary>Technical notes</summary>

- `validate_cad.py` failed: `carriage-top.FCStd` "changed since its fingerprint was written". The
  part has no `build_model.py`.
- Fingerprint written headless with `freecadcmd.exe` (FreeCAD 1.1.4) and
  `cad_fingerprint.write(doc, params={})`. The file was opened and measured only, never saved.
- Body diff: volume 434847 → 430141 mm³, area 106811 → 107766 mm², faces 172 → 178,
  edges 472 → 490. Bounding box unchanged. Centre of mass z 13.397 → 13.412 mm.
- The assembly fingerprint did not need a new write. `doqs check`: all validators passed (with
  `PYTHONIOENCODING=utf-8`).
- Mistake rules checked: [wrap crashed the open FreeCAD](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)
  (nothing sent to an open window), the PowerShell rules (all shell work in bash).

</details>
