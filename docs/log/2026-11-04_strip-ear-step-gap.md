# 2026-11-04 — Seal strip: room at the 45° steps of the ears

**Role(s):** cad

## Goal

Niels Bosmans showed a corner of the seal strip in the base. The strip must slide along X in its
corner slots to set the preload. At the 45° step of each ear, the strip had almost no room to the
pocket wall. Make enough room there. Change only the strip, not the base.

## Short answer

- **The problem:** the corner slots let the strip slide 0.5 mm each way. At the 45° steps the
  strip kept only the normal 0.2 mm edge gap, square to the step. Along X that is only 0.28 mm.
  So when the strip slid towards its middle, the step and the ear arc next to it hit the base
  before the end of the slot.
- **The fix:** the 45° steps and the ear arcs of the strip now sit half a slot length (0.5 mm)
  further towards the strip ends. The gap at each step is now 0.55 mm square to the step, or
  0.78 mm along X. At the full slide of 0.5 mm, 0.2 mm is still left, the same as along the
  sides.
- The shift follows the slot length. A longer slot later moves the steps by itself.
- The base is not changed. The width of the strip, the slots and the holes are not changed.

## What changed

- `cad/parts/sealing-strip/build_model.py`: the bent strip in the assembly and the flat strip as
  cut both take the shift. In the flat strip it is an expression on the parameter sheet
  (`strip_corner_slot_l / 2`), so there is no new parameter.
- `cad/params/default.csv`: the description of `strip_corner_slot_l` now says that the ear steps
  follow it.
- `sealing-strip.FCStd` and its fingerprint are built again.

## Checks

- The strip, moved −0.5, 0 and +0.5 mm along X, does not overlap the base (0 mm³). At ±0.8 mm it
  does (0.04 mm³). So the check finds a collision, and the strip collides only past the slot ends.
- Gap at all four steps: 0.554 mm square to the step. Smallest gap from the strip outline to the
  base: 0.2 mm, at the sides, as before.
- Material between a slot and the moved step: 2.50 mm (was about 2.85 mm). To the outer ear side
  it stays 2.55 mm. To the strip end it stays 2.25 mm.
- Both flat strip sketches are fully constrained, with no conflicting or redundant constraints.
  Both strip shapes are one valid solid.
- Parametric: with `strip_corner_slot_l` = 2 mm, the flat strip steps moved 0.5 mm more. The file
  was not saved with that value.
- `doqs check`: all gates pass.

## Open questions

- None for the strip. The steps of the base pocket are unchanged.

<details>
<summary>Technical notes</summary>

- The first rebuild ran inside the open FreeCAD window, through the add-on's `execute_code` call.
  It failed: inside the build transaction, a document recompute did not recompute the parameter
  sheet, so reading `strip_edge_gap` failed. The transaction was aborted, but left the open strip
  document with an empty sheet. That open copy was not saved. The file was then built headless
  with `freecadcmd`, which worked.
- Headless `freecadcmd cad/parts/sealing-strip/build_model.py` built nothing and printed no
  error. Running the same file through `exec()` with `__file__` set did build and save.
- The new fingerprint has an empty `params` block, because the module has no `cad/params.csv`
  (the build reads `cad/params/default.csv` itself). The old fingerprint listed the parameters.
  `doqs check` accepts both.
- `validate_names.py` crashes on the Windows console code page (an arrow character), also on
  `main`. With `PYTHONIOENCODING=utf-8` all gates pass.
- Mistake rules checked: FreeCAD (only `execute_code`, no `doqs wrap`), PowerShell (all shell work
  in bash), tooling (`.agents/` and `doqs/` left as they are).

</details>
