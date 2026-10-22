# 2026-10-22 — Damper pockets in the end walls, and the guide blocks 20 mm closer

**Role(s):** cad, engineering, architecture

## Goal

Reach the 220 mm of travel that the length rule STG-03 asks for. Each end stop damper gets a
pocket, 7 mm deep, in the end wall of the base, milled from the top with inside corners of at least
R4 mm. The guide blocks move another 10 mm closer together, so the dampers can still press in
fully without the blocks running off the rails.

## Short answer

- **The stage now has 220 mm of usable travel. STG-03 is met, with no margin.** The dampers touch
  the pocket floors after 222 mm. With 1 mm of safety at each end, 220 mm is usable.
- **The dampers can press in fully.** At full press, each guide block still has 0.55 mm of rail
  under it. The motor cable stub runs into the "a, start" pocket and keeps 4.0 mm to its back
  face.
- **The guide blocks are now 20 mm closer together than at the start of the day.** Each block
  sticks out 0.45 mm past the carriage end.
- **The encoder scale moved 7.7 mm.** The read head moved 5 mm again with the blocks. The scale
  now starts at x = 95.3 mm, so the read window runs on the middle of the clean part of the
  scale, with 2.8 mm to spare at each end of the travel.
- **Risk: the wall behind each pocket is only 3 mm thick.** A rough estimate gives 115 to 175 MPa
  of bending stress at a 2 m/s impact. The base material is not chosen yet. This needs a stress
  case before the base is ordered.
- All work is on branch `cad/guide-blocks-10-mm-closer`, not yet merged.

## Work Done

### Damper pockets in the base

- Four open slots, one in front of each damper, cut down from the top of the base:
  - 7 mm deep into the 10 mm end wall, so 3 mm of wall stays;
  - 24 mm wide, centred on the damper axis. The damper grows to 22 mm across when fully pressed
    (ACE manual, page 3), so 1 mm stays on each side;
  - inside corners R4 mm, for an 8 mm cutter;
  - floor at z = 17.5 mm, 1 mm below the bulge of a fully pressed damper. The pocket is 22.5 mm
    deep from the top face.
- The base has a new `Params` sheet with the pocket sizes, the damper positions and the scale
  start. Every new size reads from it.
- Four new frames mark the back face of each pocket on the damper axis.

### Guide blocks another 5 mm in at each end

- The block holes, block pockets and the pockets and small holes over the blocks moved 5 mm in at
  each end, as in the first move. The block frames are now at y = 21 mm and 159 mm.
- The read head pocket, its cable slot and the motor cable path followed again with their 5 mm
  wall. The read head cable slot failed to solve for one 1 mm step, then solved again. Its curve
  is now shorter, because the read head moved towards it.
- The carriage is one valid solid with no errors. A comparison with the last commit shows only
  clean 5 mm shifts.

### Travel

Measured in the assembly. The pocket back faces are 434 mm apart.

| | Blocks 10 mm closer, no pockets | Now |
| --- | --- | --- |
| Travel until the first damper touch | 208 mm | 222 mm |
| Usable travel, 1 mm before each damper | 206 mm | **220 mm** |
| Travel with the dampers fully pressed in | 222 mm | 236 mm |
| Travel until the blocks reach the rail ends | 227.1 mm | 237.1 mm |
| Rail left under each block at full press | 2.55 mm | 0.55 mm |
| Space from the cable stub to the wall or pocket at full press | 4.0 mm | 4.0 mm |
| Length rule STG-03 (at least 220 mm usable) | not met | **met, no margin** |

At full press, the bottom carriage comes within 2 mm of the end wall. The top carriage passes over
the wall and sticks out 3 mm past the base end.

### Collisions

Every pair of parts was checked. Only the two known overlaps remain: the damper at "a, start" with
the motor cable stub (303 mm³), and the cable stub with the bottom carriage (1 267 mm³). The read
head keeps 7.9 mm to the nearest block.

### The 3 mm wall behind each damper

- One damper pushes with about 1.31 kN at a 2 m/s impact. That is half of the 2.62 kN for two
  dampers from [the study of 2026-10-21](2026-10-21_space-for-end-bumpers.md).
- Seen as a beam 24 mm long, fixed at both sides, the wall gets 115 MPa if its full height of
  22.5 mm carries the load. It gets about 175 MPa if only 15 mm of height carries it.
- A common aluminium alloy may hold that, but it must be checked against the data sheet of the
  chosen material. In a crash, when a damper presses in fully, the force is much higher.

## Decisions Made

- The blocks moved 10 mm more, not less. Niels Bosmans confirmed this and the pocket floor height.
- The scale is now centred on the path of the read window, not on the travel of the blocks.

## Open Questions

- **Is the 3 mm wall strong enough?** Run a stress case of the base end wall, and choose the base
  material.
- **0.55 mm of rail at full press is very little.** Any assembly error can put a block past the
  rail end in a crash.
- **The sealing strip and its clamps lie on the top of the end walls, where the pockets now
  open.** The clamps have no geometry yet. They must leave the pockets free, or bridge them.
- **The top carriage sticks out 3 mm past the base at full press.** Check that nothing is mounted
  there.
- The carriage tilts more easily: with the blocks 20 mm closer, the study expects about 26 % less
  tilt stiffness. Check STG-06 and STG-13.
- The damper at "a, start" still collides with the motor cable stub.
- The damper file in the parts library has no frame for its impact face. Add `IF_stop` there.

## Next Steps

1. Run a stress case of the base end wall, and choose the base material.
2. Draw the sealing clamps around the pockets.
3. Decide on the cable stub collision.
4. Add `IF_stop` to the TA17-7 file in the parts library.

<details>
<summary>Technical notes</summary>

- carriage-bottom: `Sketch001.block_hole_band` 32 → 42 mm in 1 mm steps. `Sketch030` showed an
  error at 37 mm only. `Sketch015` holes stayed at x = 20.5, 46.5, 161.5 and 187.5 mm.
  `IF_readhead_mount` at y = 81 mm. Volume 458 246 → 449 777 mm³.
- base: `Sketch` constraint 4 named `end_wall_t` (10 mm). New `Params` sheet: `damper_pocket_depth`
  7 mm, `damper_pocket_w` 24 mm, `damper_pocket_r` 4 mm, `damper_pocket_floor_z` 17.5 mm,
  `damper_y_a` 64.5 mm, `damper_y_b` 145.5 mm, `damper_axis_z` 29.5 mm, `scale_start_x` 95.3 mm.
  `damper_y_*` and `damper_axis_z` copy the damper frames of carriage-bottom in the assembly,
  because the base cannot read the carriage file.
- base: `DamperPocketSketch` (fully constrained, on the XY plane at `Block.Length`) and
  `DamperPocket` (length `Block.Length - Params.damper_pocket_floor_z`). The slots run 2 mm past
  the wall face into the empty cavity. Each slot removes 3 625.5 mm³.
- base frames `IF_damper_a_start_stop` and `IF_damper_b_start_stop` at x = 437 mm, z towards −x;
  `IF_damper_a_end_stop` and `IF_damper_b_end_stop` at x = 3 mm, z towards +x; all at
  z = 29.5 mm. `IF_scale_mount` x now reads `Params.scale_start_x`.
- Assembly: the solver moved the carriage 0.42 mm along the rails. All moving parts were shifted
  back together, so the carriage stays at base x = 301.603 mm.
- Travel in base coordinates: damper faces at x = 105.603 and 317.603 mm, pocket back faces at 3
  and 437 mm: 102.603 + 119.397 = 222.0 mm. Blocks x = 121.154 to 302.052 mm, rails x = 11 to
  429 mm. Stub x up to 306.603 mm, y = 61.95 to 70.45 mm, z = 27.8 to 36.3 mm, inside the
  "a, start" pocket (y = 52.5 to 76.5 mm, floor 17.5 mm).
- Encoder: window = head centre −5.9 to +10.5 mm (log of 2026-10-20). Head centre now 8 mm ahead
  of the carriage centre. Over the usable travel the window runs from x = 112.1 to 348.5 mm. Clean
  scale x = 109.3 to 351.3 mm. Clamps x = 77.3 to 383.3 mm.
- SysML: new `DamperStopInterface_v1`, four ports on `Base`, port `stop` on `EndStopDamper`, four
  `connect`s. Block frame text y = 21 and 159 mm; scale frame text now names
  `Params.scale_start_x`.
- `doqs.sh check`: all gates passed. One interface warning: TA17-7 has no `IF_stop`.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash),
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md), and
  [the wrap mistake](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md) (no background calls
  to FreeCAD).

</details>
