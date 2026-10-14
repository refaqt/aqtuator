# 2026-10-14 — The bottom carriage has mounting frames for the guide blocks and the forcer

**Role(s):** cad, architecture

## Goal

Give the bottom carriage of the compact stage the mounting frames that the four HIWIN QEH15SA
guide blocks and the Maxwell MK21 forcer need. Then each one can go into the assembly with one
joint.

## Work Done

- **The bottom carriage has five new frames.** One frame for each guide block and one for the
  forcer:

  | Frame | Where | Joins |
  | --- | --- | --- |
  | `IF_block_a_start_mount` | x = 30, y = 11, z = 10 mm | block `IF_mount_top` |
  | `IF_block_b_start_mount` | x = 160, y = 11, z = 10 mm | block `IF_mount_top` |
  | `IF_block_a_end_mount` | x = 30, y = 169, z = 10 mm | block `IF_mount_top` |
  | `IF_block_b_end_mount` | x = 160, y = 169, z = 10 mm | block `IF_mount_top` |
  | `IF_forcer_mount` | x = 95, y = 90, z = 20 mm | forcer `IF_mount_top` |

- **The names do not say which row of blocks runs on the reference rail.** Niels asked for neutral
  names. Row a is at x = 30 mm, row b at x = 160 mm. "Start" is the end with the motor cable slot.
- **Each block frame sits on the floor of its pocket, at the centre of the two screw holes.** Z
  points down, into the block. X runs along the rail, towards the centre of the carriage. With
  this direction, the lubrication unit (E2) of each block points out of the carriage, and the
  block does not touch the carriage. The other direction gives a small overlap.
- **The forcer frame sits on the floor of the forcer pocket, on the middle hole.** Z points down,
  into the forcer. X points away from the cable end. With this direction, the cable stub of the
  forcer comes out at the cable hole that Niels drew.
- **All screw holes line up.** On each frame, the 2 holes of a block and the 6 holes of the forcer
  fall on the holes of the carriage. This was checked by calculation in the FreeCAD window.
- **The frames follow the model.** Their positions are formulas of the carriage sizes and the
  pocket depths. To link them, four sketch sizes got a name. Their values did not change.
- **The architecture has two new interfaces**: a block on the carriage, and the forcer on the
  carriage. It also has the guide block and the forcer as bought parts, and the five connections.
- **The stored measurements (fingerprints) of the carriage and the base are up to date.**

## Open Questions

- **The rows of blocks are 130 mm apart, but the rails in the base are 128 mm apart.** The blocks
  are at x = 30 and x = 160 mm in the carriage. The rails are at y = 41 and y = 169 mm in the base.
  One of the two parts must change before the blocks can sit on the rails. Done later the same
  day: the rails moved to 130 mm apart. See
  [The rails in the base are 130 mm apart](2026-10-14_rails-130-mm-apart.md).
- **The forcer still touches the carriage at its cable stub, by about 720 mm³.** Most of it is at
  the cable hole, near x = 56, y = 14 mm. This was there before the frames were added. The hole or
  the slot must be larger.

## Next Steps

1. Choose the rail spacing, and fix the base or the carriage to match.
2. Make the cable hole clear the cable stub of the forcer.
3. Decide which row of blocks runs on the reference rail. Then add the interface between a block and
   its rail to the architecture.
4. Choose the screw length for the forcer and for the blocks.

<details>
<summary>Technical notes</summary>

- Each frame is a `Part::LocalCoordinateSystem` in the `Part` container, attached `FlatFace` to the
  part's `XY_Plane001`. Rotations: start frames and the forcer frame 180° about (1, 1, 0), so X = +Y
  and Z = −Z; end frames 180° about (1, −1, 0), so X = −Y and Z = −Z.
- Expressions on `AttachmentOffset.Base`:
  - row a x = `Sketch001.Constraints.block_edge_x + Sketch001.Constraints.block_w / 2`;
    row b x = `Sketch.Constraints.w_carrier -` (row a x)
  - start y = `Sketch001.Constraints.block_hole_band / 2`; end y =
    `Sketch.Constraints.l_carrier -` (start y)
  - block z = `Sketch020.Placement.Base.z + Pocket009.Length`
  - forcer x = `Sketch.Constraints.w_carrier / 2`, y = `Sketch.Constraints.l_carrier / 2`,
    z = `Sketch017.Placement.Base.z + Pocket007.Length`
- Named constraints (values unchanged): `Sketch001` 29 `block_hole_band` (22 mm), 30 `block_w`
  (34 mm), 31 `block_edge_x` (13 mm); `Sketch` 9 `l_carrier` (180 mm).
- `Pocket009.Length` sets the block face: a test change to 9 mm moved it, and was undone.
  The forcer x and y assume the hole pattern stays centred on the carriage, as it is now.
- Fit test: the block shape from `QEH15SAZAP+E2.FCStd` and the forcer shape from `MK21.FCStd`
  were placed with frame × inverse(part frame) and intersected with the carriage solid. Blocks:
  0 mm³ (2.1 mm³ the other way round). Forcer: 722 mm³ (2 912 mm³ the other way round).
- The carriage was saved from the FreeCAD 1.1.4 window, with Niels's consent. It held unsaved
  changes by Niels from before this work, and those were saved too.
- The base and the assembly were saved again from the window at 14:42, after the rail frame work.
  The base fingerprint was written again. Its shape did not change. The assembly fingerprint is
  older than the file. That is still open work in the assembly.
- `bash doqs.sh check` fails only on the assembly fingerprint.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  and the PowerShell rules (all shell work ran in bash).

</details>
