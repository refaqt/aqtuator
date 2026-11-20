# 2026-11-20 — Seal strip corner screws are now DIN 7984, with working joints

**Role(s):** cad

## Goal

Niels Bosmans asked to replace the screws that fix the seal strip in the compact stage by
DIN 7984 screws (socket head cap screws with a low head), and to make sure their joints in the
assembly hold them in place.

## Short answer

- **The four corner screws are now DIN 7984 M4 × 10.** They were ISO 7380-2 M4 × 10 (button head
  with collar). They clamp the strip ears, so they are the screws that fix the strip.
- **The two preload screws stay ISO 10642 (countersunk).** Their cone pulls the strip to 270 N
  during fitting, and they come out afterwards. A flat head cannot do that.
- **All four joints work again.** Each one now holds the screw by the circle under its head. The
  screws sit at x = 6 / 434 mm, y = 8 / 202 mm, on top of the strip (z = 40 mm), as before.
- **The new head is 0.6 mm higher** (2.8 mm against 2.2 mm) and smaller across (7 mm against
  10.2 mm). This matters for the open clash with carriage-top and for the scraper. See the open
  questions.

## What changed

- Assembly `compact-stage.FCStd`: the four `corner_screw_*` fasteners have type `DIN7984`.
  One of them was already changed in the open FreeCAD window, but not saved. Its joint had lost
  its edge, so that screw sat 3.5 mm off along x and 1.4 mm too low.
- Joints `Joint046` to `Joint049` (fixed joints, screw to base): the screw side now uses `Edge26`,
  the circle of the head underside (r = 3.1 mm). The old `Edge13` was the collar of the ISO 7380-2
  head. The base side and the offset (strip thickness, head turned over) did not change.
- Bill of materials `MEC-006`: DIN 7984 M4 × 10, A2.
- Architecture note of the seal strip port: DIN 7984, holes 6 mm from the base end (the text
  still said 5 mm), slots 4.5 mm wide and 1 mm long.
- Notes for `strip_corner_hole_d` and in the seal strip build script name DIN 7984.

## Checks

- The assembly solves with no error. All four screws are at their old positions.
- Each screw thread overlaps the Ø3.3 mm tap hole in the base by 38.6 mm³, the same as before.
- Each head touches the strip but does not cut into it. The nearest other part is a magnet strip,
  4.5 mm away.
- The 7 mm head covers the 5.5 mm long slot with 0.75 mm of strip at each slot end, and 1.25 mm
  at each side of the 4.5 mm slot width. The old collar had 1.9 mm at the slot ends.
- The fingerprint was written from the saved file. `doqs check`: all gates pass.

## Open questions

- Carriage-top hangs down to z = 40.5 mm above the screw rows. The new heads reach z = 42.8 mm
  (the old ones 42.2 mm). The end-stop crash study already found that carriage-top hits the
  corner screw heads 6.7 mm before the bumpers. That clash is still open and is now 0.6 mm deeper.
- The brass and TPU scraper design uses the ISO 7380-2 head (Ø10.17 mm, 2.2 mm high). It must be
  checked again with the DIN 7984 head (Ø7 mm, 2.8 mm high).
- Is 0.75 mm of strip under the head at the slot ends enough to hold the pull? A washer
  (ISO 7092, M4) would give a wider bearing face, but it adds about 0.8 mm of height.

<details>
<summary>Technical notes</summary>

- All FreeCAD work went through `execute_code` in the open window, as one undo step. No
  `doqs wrap`.
- The Fasteners workbench renames a screw when its type changes. The labels are now
  `M4x10-Screw020`, `-028`, `-029`, `-030`. The object names (`corner_screw_*`) did not change.
- The joints still use edges, not `IF_` frames, like the other screw joints in this assembly.
- `doqs generate` added copyright lines to 16 licence files in `modules/stoq`. That folder is
  its own repository, so these changes are not part of this branch.
- Mistake rules checked: FreeCAD (only `execute_code`), PowerShell (all shell work in bash),
  tooling (`.agents/` and `doqs/` left as they are).

</details>
