# 2026-10-30 — Slots for the seal strip corner screws

**Role(s):** cad

## Goal

The four ISO 7380-2 M4 corner screws clamp the seal strip to the base. While the preload screws
pull the strip, the strip must slide a little under the corner screws. Niels Bosmans asked to make
the four corner holes slots: the same diameter, 1 mm long centre to centre. Then the preload can be
adjusted a bit more. The two preload holes stay as they are.

## Short answer

Done. Each corner hole is now a slot along X (the travel): 4.5 mm wide, 1 mm centre to centre,
5.5 mm long overall. It is centred on the screw, so the strip can slide 0.5 mm each way. The
strip needs only about 0.02 mm of pull at each end for 270 N, so this is much more than the pull
needs.

## What changed

- New parameter `strip_corner_slot_l` = 1 mm in `cad/params/default.csv`. `strip_corner_hole_d`
  (4.5 mm) is now the slot width. `params-table.csv` is generated again.
- `sealing-strip/build_model.py` cuts each corner slot as two Ø4.5 circles 1 mm apart, with the
  part between them.
- `sealing-strip.FCStd` is rebuilt in the open FreeCAD window and saved, with a new fingerprint.

## Checks

- The strip is one valid solid. The slot at the corner screw (5, 8) runs from x = 2.25 to 7.75 mm
  and from y = 5.75 to 10.25 mm.
- In the assembly, the strip does not overlap any of the six screws.
- The assembly file is not saved by this work: it had unsaved changes in the open FreeCAD window
  before it started. It links the strip file, so it shows the new slots when it is opened.
- The collar of the ISO 7380-2 M4 screw is 9.4 mm wide (Fasteners workbench model). It still
  covers the whole 5.5 mm slot, with at least 1.9 mm of strip under the collar at the slot ends.
- `doqs check` passes for this change.
