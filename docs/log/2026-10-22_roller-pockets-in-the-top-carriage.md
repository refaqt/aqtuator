# 2026-10-22 — Roller pockets in the top carriage, linked to the bottom carriage

**Role(s):** cad

## Goal

Add pockets for the sealing strip rollers to carriage-top, at the low end of its slanted faces.
The pockets, the axle slots and the axle screws must have the same sizes as in carriage-bottom.
The sizes must be linked, so a change in carriage-bottom also changes carriage-top.

## Short answer

- **carriage-top now has four roller pockets.** Each roller is centred on the edge where the
  slanted face meets the underside, 92.8 mm from the middle of the part. The pockets cut up
  from the underside.
- **Every size comes from carriage-bottom.** That includes the pocket size, the corner radius,
  the pocket depth, the axle slot, the screw positions and the screw holes. A test change in
  carriage-bottom moved carriage-top with it.
- **The axle slots point inward, the same as in carriage-bottom.** Each slot starts 1 mm on the
  end side of the roller centre and runs 8 mm towards the middle of the part. The screws sit on
  the inner side of the axle and push it towards the end.
- **The gap between a top roller and the bottom carriage is only 0.32 mm.** The sealing strip
  must pass through this gap. See the open questions.
- All work is on branch `cad/carriage-top-roller-pockets`.

## Work Done

### Sizes, the same as carriage-bottom

| | Size |
| --- | --- |
| Roller (length × diameter) | 20 × 10 mm |
| Pocket (gap 0.5 mm at the roller ends, 3 mm along the roller) | 21 × 16 mm, corner radius 4 mm, 11 mm deep |
| Axle slot | 8 mm wide, 37 mm long, 4.5 mm deep |
| Axle screw holes | Ø3.4 mm, 8 mm deep, two per pocket, 13 mm each side of the roller middle, 3 mm from the axle |
| Roller position across the width | 70.5 mm from the centre line |

### How the link works

- carriage-bottom got names on the sizes that carriage-top reads. Four of them are new
  measuring dimensions that do not drive the sketch: the roller position across the width, the
  half length of the axle slot, the slot radius, and the screw distance along the axle. No size
  changed, and the volume of carriage-bottom stayed the same.
- carriage-top reads each of these sizes from carriage-bottom. The position along the length
  follows the low end of the slanted face, so the rollers move if the slope changes.
- One corner is drawn. A mirror feature copies it to the other three corners.

### Checks

- carriage-top is one valid solid. All new sketches are fully constrained.
- The new cuts keep 7.5 mm to the guide block pockets, 11.4 mm to the other underside pockets,
  14.5 mm to the counterbored holes, and 4.2 mm of wall to each end face. The screw holes end
  6 mm below the top face.
- In the assembly, a top roller sticks out 1.5 mm below carriage-top. It keeps 0.32 mm to the
  slanted face of carriage-bottom and 7.5 mm to the base.
- For comparison, a bottom roller keeps 0.19 mm to carriage-top.
- Every pair of parts in the assembly was checked. Only the two known overlaps remain, both with
  the motor cable stub.
- The files were saved and fingerprinted again. All repository checks pass.

## Decisions Made

- Niels Bosmans chose: the same sizes as carriage-bottom, linked, and the axle slots towards the
  inside of carriage-top.

## Open Questions

- **The gaps at the rollers are small.** A top roller keeps 0.32 mm to carriage-bottom, and a
  bottom roller keeps 0.19 mm to carriage-top. The sealing strip runs through these gaps. The
  strip part has no solid yet, so its thickness could not be checked. Check the strip thickness
  against these gaps.
- The rollers and axles have no part of their own yet.

<details>
<summary>Technical notes</summary>

- carriage-bottom, names added: `Sketch013` `roller_pocket_r`, `roller_d`, `roller_side_gap`,
  `roller_end_gap`, `roller_l`; `Sketch014` `axle_offset`; `Sketch015` `axle_screw_dy`.
  Reference (non-driving) constraints added: `Sketch013.roller_offset` (70.5 mm),
  `Sketch014.axle_slot_half` (14.5 mm), `Sketch014.axle_slot_r` (4 mm),
  `Sketch015.axle_screw_dx` (13 mm). Volume 449 877 mm³ before and after.
- carriage-top, new features: `Sketch005` → `Pocket003` (depth `carriage_bottom#Pocket004.Length`),
  `Sketch006` → `Pocket004` (depth `carriage_bottom#Pocket005.Length`), `Sketch007` → `Hole001`
  (`Diameter`, `Depth`, `DrillPointAngle` from `carriage_bottom#Hole001`; sketch offset
  `-Pocket004.Length`), then `MultiTransform` with mirrors on the YZ and XZ planes.
- The three sketches are attached like `Sketch002` (XY plane, reversed). Each has an external
  reference to `Sketch001` `Edge1`; a vertical point-to-point constraint puts the roller centre
  on its end point.
- Removed volume 15 493.6 mm³ (4 × 3873.4). carriage-top volume 434 846.7 mm³.
- Link test: `roller_end_gap` 3 → 4 mm and `Hole001.Depth` 8 → 9 mm in carriage-bottom moved
  the carriage-top pocket and holes; the test was undone, not saved.
- Clearances measured with `distToShape` on Ø10 × 20 mm cylinders at the axle positions.
- `doqs.sh check` (`PYTHONIOENCODING=utf-8`): all gates passed. Typed-number warnings are the
  same as before; none of them is a new carriage-top feature.
- Mistake rules checked: no background calls to FreeCAD, PowerShell rules (bash only), the
  tooling update rule.

</details>
