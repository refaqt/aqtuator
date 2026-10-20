# 2026-10-20 — The linear encoder is in the compact stage assembly

**Role(s):** cad, architecture

## Goal

Put the LAMOTION ABS linear encoder into the compact stage. The read head goes on the bottom
carriage, in the pocket that Niels Bosmans added today. The scale and its two end clamps go on
the base. The head must sit at the right distance from the scale, and must not touch anything.

## Work Done

- **The head sits 0.80 mm from the scale.** The LAMOTION data sheet allows 0.8 ± 0.15 mm
  (page 9). With the holes as they were first drawn, the gap was 0.60 mm, which is too small. The
  two screw holes for the head now sit 3.2 mm from the step face of the carriage, not 3.0 mm.
- **The head no longer hits the second guide rail.** The first pocket was 9 mm deep, so the
  16.5 mm wide head hung 7.5 mm below the carriage and overlapped the rail by about 1,400 mm³.
  The pocket is now 16 mm deep. The head bottom stays 1.0 mm above the rail. Nothing in the
  assembly overlaps any more.
- **The head is centred in its pocket along the travel**, with 1 mm of space at each end. The
  holes of the head are not centred on the head (12 mm and 14 mm from its centre), so the hole
  pair sits 1 mm off the middle of the pocket. A formula keeps this true if the pocket length
  changes. Across the travel, the gap to the scale sets the position, and the pocket is open on
  that side.
- **The carriage has a frame for the head**, `IF_readhead_mount`. It sits on the ceiling of the
  head pocket, midway between the two screw holes. It follows the holes and the pocket depth by
  formulas.
- **The base has a frame for the scale**, `IF_scale_mount`. It sits on the inside face of the side
  wall, at the start of the scale, on the centre line of the head. The scale (270 mm) is centred
  on the middle of the travel that the guide blocks allow. Over that whole travel, the head window
  stays between the two clamps.
- **The assembly holds the head, the scale and the clamp pair.** Each one is joined to its frame
  with one fixed joint. Head and scale line up in height and direction. The clamps do not
  overlap the scale.
- **The architecture describes the four new interfaces**: head to carriage, scale to base, head
  to scale (with the gap and its tolerance), and clamps to scale.
- **The scale and the clamps show in the assembly.** At first they were invisible, because the
  parts library had saved both models with every body hidden. The parts library and doqs were
  fixed today, and this repository now uses their newest versions. The positions did not change.

## Decisions Made

- The gap is set by moving the screw holes in the carriage, not by changing the base. The base
  wall is part of the rail design, and the holes were the smaller change.
- The pocket is 16 mm deep, not 16.5 mm. At 16.5 mm its ceiling would be flush with the underside
  of the carriage, and the edge that places the screw holes would disappear. 16 mm still leaves
  1.0 mm above the rail.

## Next Steps

1. Set the gap with a 0.8 mm feeler gauge at assembly. The 3.4 mm holes let the head move 0.2 mm
   each way, which is more than the ±0.15 mm tolerance.
2. Choose the screw length. The screw passes 8.1 mm of carriage under the counterbore. LAMOTION
   asks for more than 8 mm in the head, so an M3 × 18 or longer is needed. Check the length
   against the 16.5 mm width of the head.
3. Two values of the scale frame are typed numbers for now (x = 103 mm, z = 31.75 mm). They
   depend on the carriage. Check them when the carriage or the travel changes.

<details>
<summary>Technical notes</summary>

- Carriage (`carriage-bottom.FCStd`):
  - `Sketch031` constraint 5, 3.0 → 3.2 mm (hole axis to the external edge at x = 17).
  - `Sketch031` symmetric constraint on the external edge removed. New: the start of line 3 lies
    on the external edge, and `readhead_hole_mid_y` (DistanceY from the edge end at y = 53) =
    `Sketch026.Constraints.readhead_pocket_l / 2 - 1 mm` = 18 mm. Sketch fully constrained.
  - `Sketch026` constraint 13 named `readhead_pocket_l` (38 mm). `Pocket015` length 9 → 16 mm.
  - Hole axes now at (20.2, 58) and (20.2, 84); clearance bore from z = 16 to 24.1.
  - New `Frame005`, label `IF_readhead_mount`, `FlatFace` on `XY_Plane001`, now at
    (20.2, 71, 16), axes X = −Y, Y = −X, Z = −Z. Expressions:
    x = `Sketch031.Geometry[0].Center.x`, y = mean of the two hole centres,
    z = `Sketch026.Placement.Base.z + Pocket015.Length`.
- Base (`base.FCStd`): new `Frame004`, label `IF_scale_mount`, `FlatFace` on `XY_Plane001`,
  position (103, 17, 31.75), turned −90° about X. y =
  `(BlockSketch.Constraints.Width - Sketch.Constraints.pocket_w) / 2`. x and z are typed.
- Assembly (`compact-stage.FCStd`): links `AL32B050-30MUL`, `ALZ00270G`, `RUS-ET-A-B`. Joints
  `Fixed_readhead` (carriage `IF_readhead_mount` ↔ head `IF_mount_side`), `Fixed_scale` (base
  `IF_scale_mount` ↔ scale `IF_mount_bottom`), `Fixed_scale_clamps` (scale `IF_mount_bottom` ↔
  clamps `IF_scale_start`). The solver moved the carriage about 0.3 mm along the travel; the
  sliders leave that free.
- Measured after the last solve: gap 0.80 mm. Head `IF_scale` seen from scale `IF_head`:
  (126.6, 0, 0), no rotation. Head to rail `EGR15U418H001`: 1.0 mm. Head to base: 1.2 mm. Head to
  carriage: 0 (on the pocket ceiling). No overlap between the head, the scale or the clamps and
  any other part. Clamps z 24.25…39.25, wall top z = 40.
- Travel limit used for the scale position: each guide block stays on the rail (x 11…429). The
  head centre then runs from x = 129.5 to 346.6 mm. Window ends: 123.6 and 357.1 mm. Clean scale
  between the clamps: 117 to 359 mm.
- The scale and clamp files in `modules/stoq/` had `Visibility = False` on the `App::Part` and on
  every body, so `Part.getShape()` of their links was empty. Fixed in
  [refaqt/stoq#18](https://github.com/refaqt/stoq/pull/18) and, for every headless build, in
  [refaqt/doqs#49](https://github.com/refaqt/doqs/pull/49). The `modules/stoq` pin moves to
  `573f5c4`, and `doqs/` sits on `5de630c`. After the update, the three links give the same
  placements and bounding boxes as before, and the assembly file was not saved again.
- All edits ran in the open FreeCAD 1.1 window through its RPC server. Saved: the three files
  above. Fingerprints written with `cad_fingerprint.write()` in the same window.
  `bash doqs.sh check`: all gates pass.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  (the tooling folders were left as they are), the PowerShell rules (all shell work ran in bash),
  and [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md)
  (the gap of 0.8 ± 0.15 mm was read in the LAMOTION data sheet itself).

</details>
