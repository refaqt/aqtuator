# 2026-10-30 — Radii in the magnet ring split

**Role(s):** cad

## Goal

Niels Bosmans asked to replace the sharp corners of `MagnetRingSplit` in the base with 4 mm radii,
so that the part can be milled.

## Short answer

Done. The four inside corners, where the split meets the pocket wall, are now R4 arcs. A cutter of
8 mm diameter can mill them.

## What changed

- `MagnetRingSplitSketch` has a new named constraint `split_r` = 4 mm.
- The magnet ring is a shelf 3 mm wide (x 7 to 10, and 430 to 433). An R4 arc does not fit in 3 mm.
  So each arc is tangent to the pocket wall and ends on the shelf edge, at 3.87 mm from its centre
  line. The arc circle touches the old split face, so the 5 mm solid zone (`split_y0`, `split_l`)
  did not move. Those two faces are now construction lines.
- The corners at the shelf edge (x 10 and 430) are outside corners. They need no radius.
- Each split is now 5.25 mm long at the shelf edge and 13 mm long at the wall. Each magnet pocket
  is up to 4 mm shorter near the wall, at the split end. Check that the magnets still fit.
- The four arcs add about 7 mm³ of aluminium. The part is valid, and the fingerprint is updated.

## How

The file was changed with `freecadcmd`, because no FreeCAD window was open. A save without the
window writes no view data and no colours. So the view data, colours and thumbnail were copied
back from the previous version of the file. The object names did not change. `doqs check` passes.
