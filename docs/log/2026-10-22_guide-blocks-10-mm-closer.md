# 2026-10-22 — Guide blocks 10 mm closer together, and the travel check

**Role(s):** cad, engineering

## Goal

Move the four guide blocks of the compact stage 10 mm closer together, 5 mm at each end of the
bottom carriage. Then check two things with the end stop dampers in place: is the travel that the
stage needs reached before the dampers touch the end walls of the base, and can the dampers press
in fully without the guide blocks running off the rails?

## Short answer

- **The blocks are 10 mm closer together, on branch `cad/guide-blocks-10-mm-closer`.** Each block
  now sticks out 5.45 mm past the carriage end, down from 10.45 mm.
- **The dampers can now press in fully.** At full press, each block still has 2.55 mm of rail left
  under it. Before this change, the blocks ran off the rails after about 4.5 mm of the 7 mm damper
  stroke. The motor cable stub keeps 4.0 mm to the end wall at full press.
- **The travel that the stage needs is not reached.** The length rule STG-03 asks for at least
  220 mm of travel at 440 mm length and 60 mm height. The dampers touch the walls after 208 mm.
  With 1 mm of safety at each end, the usable travel is 206 mm. That is 14 mm short. Moving the
  blocks does not change this: the dampers and the carriage length decide it.
- **The encoder read head moved 5 mm too.** Its pocket, its cable slot and the motor cable path
  were drawn with a 5 mm wall to the block pockets, so they follow the blocks. The read head still
  reads the clean part of the scale over the whole usable travel.

## Work Done

### What moved in the bottom carriage

- The block screw holes, counterbores and block pockets moved 5 mm towards the carriage centre at
  each end. The four block mounting frames moved with them (y = 16 mm and 164 mm, from 11 mm and
  169 mm).
- The pockets and the small holes over the blocks moved with the blocks. Before, they were tied to
  the edge of the sloped carriage end, so they would have stayed behind. They now follow the block
  holes.
- The read head pocket, its two screw holes, the cable slot from the read head and the motor cable
  path moved or changed shape with the block pockets. They keep their 5 mm wall to the block
  pockets. Two curves of the motor cable path are now 5 mm larger in radius, and the curve of the
  read head cable slot moved 2.8 mm. Please look at these two curves once.
- The carriage is one valid solid with no recompute errors. Its volume went from 467 850 mm³ to
  458 246 mm³, because the block pockets are 5 mm longer.

### Collisions in the assembly

Every pair of parts was checked for overlap. Only two overlaps remain, and both were there before
this change:

- the damper at "a, start" and the motor cable stub (303 mm³), see
  [the damper log](2026-10-22_end-stop-dampers.md);
- the motor cable stub and the bottom carriage (1 267 mm³, the same as before).

The read head now has 8.45 mm of space to the nearest block.

### Travel

Measured in the assembly. The base end walls are 420 mm apart. The bottom carriage is 180 mm long,
and each damper sticks out 16 mm.

| | Before (blocks 10.45 mm out) | Now (blocks 5.45 mm out) |
| --- | --- | --- |
| Travel until the first damper touch | 208 mm | 208 mm |
| Usable travel, 1 mm before each damper | 206 mm | 206 mm |
| Travel with the dampers fully pressed in | 222 mm | 222 mm |
| Travel until the blocks reach the rail ends | 217.1 mm | 227.1 mm |
| Rail left under each block at full press | −2.45 mm (off the rail) | **2.55 mm** |
| Space from the motor cable stub to the end wall at full press | 4.0 mm | 4.0 mm |
| Length rule STG-03 (at least 220 mm usable) | not met | **not met, 14 mm short** |

### Encoder

- The read window is now 7.15 mm to 23.55 mm ahead of the carriage centre, 5 mm closer to it than
  before.
- Over the usable travel, the window stays between x = 124.15 mm and 346.55 mm. The clean part of
  the scale runs from x = 117 mm to 359 mm, so it fits with at least 7 mm to spare.
- At full damper press at the end walls, the window goes 0.85 mm past the clean part at one end.
  It stays on the scale. This only happens in a crash.

## Decisions Made

- The read head pocket and the cable paths follow the blocks, as the model was drawn. The other
  choice was to keep them in place. Then the 5 mm walls between the block pockets and these
  pockets would disappear.

## Open Questions

- **How do we reach 220 mm of travel?** The study of
  [2026-10-21](2026-10-21_space-for-end-bumpers.md) found one way: sink the dampers 7 mm into
  pockets in the carriage ends, and move the blocks 10 mm in at each end (20 mm in total). That
  gives 220 mm, with no margin. Another way is a longer base, but the length rule then asks for
  more travel too.
- The carriage tilts more easily with the blocks closer together: about 13 % less tilt
  stiffness, from the study. Check this against STG-06 and STG-13.
- The damper at "a, start" still collides with the motor cable stub.
- The stress case of the bottom carriage should run again, with the blocks in their new places.

## Next Steps

1. Decide how to reach 220 mm of travel.
2. Look at the two changed curves of the cable paths in the carriage.
3. Decide on the cable stub collision.

<details>
<summary>Technical notes</summary>

- carriage-bottom: `Sketch001.block_hole_band` 22 → 32 mm, in 1 mm steps (the small holes in
  `Sketch015` flipped on a large jump before). The holes in `Sketch015` stayed at x = 20.5, 46.5,
  161.5 and 187.5 mm.
- `Sketch013`: the two symmetric constraints on the external edge of the sloped end (`Pocket003`
  edge at y = 30 mm) were replaced by a new construction line with
  `block_access_y` = `Sketch001.Constraints.block_hole_band / 2 + 19 mm`. `Sketch014` and
  `Sketch015` follow `Sketch013`.
- Followed by external geometry, unchanged constraints: `Sketch020`, `Sketch021` (blocks),
  `Sketch023` (5 mm from the block pocket end), `Sketch024`, `Sketch026` (5 mm from the block
  pocket end), `Sketch029`, `Sketch030`, `Sketch031`. Read head frame `IF_readhead_mount` now at
  y = 76 mm.
- Assembly: `Assembly.solve()` moved the carriage 0.2 to 0.4 mm along the rails each time. All
  moving parts were then shifted back together, so the carriage stays at base x = 301.603 mm.
- Travel in base coordinates: damper faces at x = 105.603 and 317.603 mm, walls at 10 and 430 mm,
  so 95.603 + 112.397 = 208.0 mm. Blocks x = 116.154 to 307.052 mm, rails x = 11 to 429 mm.
  Motor stub ends at x = 306.603 mm.
- Encoder window from the log of 2026-10-20 (12.15 to 28.55 mm ahead of the centre), minus 5 mm.
  Carriage centre range over the usable travel: x = 117.0 to 323.0 mm.
- Work done in the open FreeCAD 1.1 window with the add-on's main-thread call only, not the
  background call (see [the wrap mistake](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)).
  Fingerprints written with `cad_fingerprint.write()` after saving. `doqs.sh check`: all gates
  passed. `validate_names.py` crashes when the Windows console cannot print an arrow; it passes
  with `PYTHONIOENCODING=utf-8`.
- SysML: block frame positions in `BlockMountInterface_v1` updated to y = 16 and 164 mm.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash),
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md) (tooling
  folders left as they are), and the wrap mistake (no background calls to FreeCAD).

</details>
