# 2026-10-22 — Roller pockets back on the slope edge, and thicker walls at the read head

**Role(s):** cad

## Goal

Fix three problems in the bottom carriage that came from moving the guide blocks 20 mm closer
together:

- The centre of each sealing strip roller must sit on the edge where the sloped carriage end
  starts. The roller pockets had moved 10 mm away from that edge.
- The roller pockets must not cut into the counterbores of the block screws, and the slope must
  not cut into the forcer pocket.
- The wall between the read head insertion pocket and the guide block pocket was only 1 mm thick.

## Short answer

- **The roller pockets are centred on the slope edge again**, at 34 mm from each carriage end. A
  formula now keeps them there if the slope changes.
- **The slope is longer and less steep.** It runs 34 mm (was 30 mm) and starts 15.5 mm high at the
  carriage end (was 14 mm). The angle is now about 19°, down from 24°.
- **Nothing cuts into anything.** The roller pockets keep 2.3 mm to the block screw counterbores.
  The slope keeps 0.75 mm of material above the forcer pocket (0.68 mm before).
- **The axle slots are on the inner side of each roller pocket now**, away from the counterbores.
  The countersunk screw that pushes each axle against the slot wall moved with them.
- **The read head moved 2 mm towards the start end.** Both walls around its pockets are now
  3 mm (were 1 mm and 5 mm). The encoder scale moved 2 mm with it.
- All work is on branch `cad/guide-blocks-10-mm-closer`, not yet committed.

## Work Done

### Slope and roller pockets

| | Before | Now |
| --- | --- | --- |
| Slope length, from the carriage end | 30 mm | 34 mm |
| Slope height at the carriage end | 14 mm | 15.5 mm |
| Roller pocket centre, from the carriage end | 40 mm | 34 mm (on the slope edge) |
| Roller pocket to block screw counterbore | 7.8 mm | 2.3 mm |
| Axle slot to block screw counterbore | 8.0 mm | 8.0 mm |
| Slope to forcer pocket (thinnest material) | 0.68 mm | 0.75 mm |
| Slope to motor cable pocket | 5.5 mm | 6.7 mm |
| Slope to damper nut slots | 5.0 mm | 6.5 mm |

- Raising the low end of the slope is what keeps the forcer pocket closed. A longer slope with the
  old 14 mm start would cut into it.
- In the assembly, the low end of the slope is at base z = 39.5 mm. The sealing strip lies on the
  base top at z = 40 mm, so the slope still lifts the strip from below.
- The axle of each roller lies on the pocket centre line. Before, the axle slot ran towards the
  carriage end and a screw on that side pushed the axle towards the centre. Now the slot runs
  towards the carriage centre, and the screw pushes the axle towards the end. The layout is the
  same, mirrored.

### Read head

- The read head pocket now keeps 3.0 mm to the start block pocket, and its insertion pocket keeps
  3.0 mm to the end block pocket.
- The read head keeps 6.45 mm to the nearest guide block.
- The scale now starts at x = 97.3 mm (was 95.3 mm). The read window still keeps 2.8 mm of clean
  scale at each end of the 220 mm usable travel.

### Motor cable path

- After this work, Niels Bosmans reshaped one bend of the motor cable path at the start end of the
  carriage in FreeCAD. The bend had grown 10 mm in radius when the blocks moved. It now has a
  short straight piece. The sketch is fully constrained, and the carriage stays one valid solid.

### Checks

- The carriage is one valid solid with no errors. All changed sketches are fully constrained.
- A comparison with the file saved before this work shows changes only at the slopes, the roller
  pockets, the axle slots and screw holes, and the read head pockets.
- Every pair of parts in the assembly was checked. Only the two known overlaps remain (damper
  "a, start" with the motor cable stub, and the cable stub with the bottom carriage).
- The travel did not change: 220 mm usable, 236 mm at full damper press.

## Decisions Made

- Niels Bosmans chose: slope edge at 34 mm with the low end at 15.5 mm, roller pocket centre on
  the edge, axle slots on the inner side, and equal 3 mm walls at the read head.

## Open Questions

- **0.75 mm of material between the slope and the forcer pocket is thin.** It was 0.68 mm before
  this change, so it is not new. Check it in the next stress case of the bottom carriage.
- The roller and axle sizes are not in the architecture yet. The rollers have no part and no
  interface to the sealing strip.

## Next Steps

1. Look at the roller pockets, axle slots and slope in FreeCAD.
2. Commit the work on the branch when the model is accepted.

<details>
<summary>Technical notes</summary>

- `Sketch003`: constraint 4 named `slope_l`, 30 → 34 mm in 1 mm steps; `h_block` 14 → 15.5 mm.
- `Sketch013`: `block_access_y` renamed `roller_y`, stepped 40 → 34 mm, then set to
  `Sketch003.Constraints.slope_l`.
- `Sketch014`: the distance of 1 mm from the pocket centre line now holds slot line 0 (inner
  side), not line 1. Slots at y = 33–41 and 139–147 mm.
- `Sketch015`: new external reference to `Sketch014` `Edge1` (the slot edge next to the axle);
  the tangent of the axle circle moved to it. The circle-to-circle distance of 0.5 mm became a
  signed vertical distance of 3 mm (same position, no second solution). The angle of the
  countersink line is 135° (was 45°). The old reference to `Sketch014` `Edge3` is unused and left
  in place. Holes at x = 20.5, 46.5, 161.5, 187.5 mm, y = 37 and 143 mm.
- First try of the slot step deleted the wrong external references in `Sketch015` and was undone
  as one step. `delExternal()` removed the whole `Pocket005` group, not one edge.
- `Sketch026`: constraint 15 named `readhead_wall_start`, 5 → 3 mm. `IF_readhead_mount` at
  y = 79 mm. Carriage volume 449 777 → 450 059 mm³.
- base: `Params.scale_start_x` 95.3 → 97.3 mm.
- Assembly: the solver moved the carriage about 102 mm along the rails. All moving parts were
  shifted back together, so the carriage stays at base x = 301.603 mm.
- Motor cable path: `Sketch024` 22 → 26 elements, 51 → 63 constraints, edited by hand.
  `Pocket013` 12 771 → 13 149 mm³. `Sketch025` follows. Carriage volume after the edit
  449 877 mm³. Files recomputed, saved and fingerprinted again after the edit.
- Walls measured with `distToShape` between the solids each feature removes.
- `doqs.sh check`: all gates passed; one known warning (TA17-7 has no `IF_stop`).
- Mistake rules checked: PowerShell rules (bash only), the tooling update rule, and the wrap
  mistake (no background calls to FreeCAD).

</details>
