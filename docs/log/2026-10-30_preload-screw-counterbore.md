# 2026-10-30 — Counterbore for the seal strip preload screws

**Role(s):** cad

## Goal

The ISO 10642 M4 preload screws at the seal strip ends could not go down: the screw cone rested on
the floor of the strip pocket. Niels Bosmans asked for a counterbore in the base, as wide as the
hole in the seal strip, and as deep as the head of the countersunk screw.

## Short answer

Done. The base has a new pocket, `PreloadCounterbore`: Ø5 mm, 2.48 mm deep from the strip pocket
floor, on the axis of each preload screw. The screw can now go down 0.49 mm before its cone sits on
the edge of the counterbore. The strip needs only about 0.02 mm of pull at each end for 270 N, so
this is enough room.

## What changed

- `Params` in the base has two new rows: `preload_counterbore_d` = 5 mm (the same as
  `strip_preload_hole_d`) and `preload_counterbore_depth` = 2.48 mm (head height k of ISO 10642
  M4, from the Fasteners workbench).
- `PreloadCounterboreSketch` sits on the strip pocket floor (z = 39.85). Its two circles are on the
  preload screw axes (`Sketch007` `preload_screw_x`, half the base width). Every size is linked.
- The counterbore is on the screw axis, not on the strip hole. The strip hole is 0.35 mm off the
  axis, towards the strip middle. So the cone meets the strip edge first (2.15 mm from the axis),
  and the base edge only at 2.5 mm.
- The thread of the M4 hole now starts 2.48 mm lower. 12.5 mm of the 15 mm hole is left.
- The wall between the counterbore and the magnet pockets is 1.4 mm.

## Checks

- In the assembly, the head of each preload screw does not touch the base when it is lowered by
  up to 0.49 mm. At 0.6 mm it does: the cone sits on the Ø5 edge.
- The screws in the assembly did not move. They still show the strip in its preloaded state.
- The head cannot sink fully: it is 8 mm wide, and the counterbore is 5 mm. A full sink needs a
  counterbore of at least 8 mm, or a countersink.
- The change was made in the open FreeCAD window, as one undo step. `doqs check` passes.
