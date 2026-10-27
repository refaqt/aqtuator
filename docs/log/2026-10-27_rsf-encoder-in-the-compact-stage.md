# 2026-10-27 — The RSF MC 15 encoder replaces the LAMOTION encoder in the compact stage

**Role(s):** cad, architecture

## Goal

Replace the LAMOTION ABS encoder in the compact stage with the RSF MC 15 encoder: the AK MC 15 B
read head and the MC 15 MK steel tape with a 220 mm measuring length. The RSF tape needs no end
clamps, so the LAMOTION clamps go too. Niels Bosmans asked for this. All interfaces must match,
and no parts may touch.

## Short answer

- **The RSF head fits the existing pocket in the bottom carriage.** It has the same 26 mm hole
  pitch, the same 3 mm from the holes to the scanning face, and the same 1 mm offset of the holes
  along the head. Only the two screw holes moved, by 0.2 mm.
- **The air gap is 0.55 mm**, as RSF asks (0.55 ± 0.25 mm, RSF drawing D1158017-04). The head and
  the tape are on the same line, with no sideways offset and no angle.
- **No part touches the encoder** at the present position or at either end of the travel. The
  closest parts: the bottom carriage 0.55 mm from the tape, the base 1.0 mm from the head, the
  guide blocks 1.55 mm from the tape, and the second rail 4.15 mm from the head.
- **The travel is 2 mm longer than the measuring length.** Between the two damper contacts the
  carriage moves 222 mm. The sensor then runs 1 mm past each end of the 220 mm measuring length.
  With the dampers fully pressed, it runs 8 mm past. The limit switches must stop the carriage
  inside the measuring length. Nothing in the CAD changes for this.

## Work Done

- **Bottom carriage:** the two M3 holes for the head are now 3.0 mm from the step face, not
  3.2 mm. The scanning face of the head is then flush with the step face, and the gap is 0.55 mm.
  The pocket (38 × 16 mm) and the counterbores did not change.
- **The head holes are threads.** The RSF head has M3 threads through its full 13.5 mm. The screws
  still go down through the carriage into the head. An M3 × 16 screw gives about 7.9 mm of
  thread.
- **The head sits higher.** It is 13.5 mm tall, against 16.5 mm for LAMOTION, and it stays fully
  inside the 16 mm pocket. Its sensor line is at z = 34 mm. The tape moved up with it, from a
  centre at z = 31.75 mm to 34 mm. The tape lies from z = 30 to 38 mm, under the top of the wall
  at 40 mm.
- **The cable points to the same end as before.** With the cable the other way, the head would
  cut 72 mm³ into the bottom carriage.
- **Base:** the scale frame `IF_scale_mount` is turned 180°, so the tape runs towards −X, the same
  way as the head. Its two values are now in the `Params` sheet of the base: `scale_start_x` =
  351 mm and the new `scale_centre_z` = 34 mm. The tape lies from x = 111 to 351 mm, centred on
  the path of the sensor.
- **Assembly:** the three LAMOTION parts and their three joints are gone. The RSF head and tape
  are in, each with one fixed joint.
- **Architecture:** the head mount, the scale mount and the head-to-scale interfaces are now
  version 2, with the RSF numbers. The clamp interface and the clamp part are gone.
- **Bill of materials:** two new rows, `SW-002` (head) and `SW-003` (tape). The LAMOTION parts were
  never in the bill of materials.

## Decisions Made

- The gap is set by the screw holes in the carriage, as for LAMOTION. The 3.4 mm holes let the
  head move 0.2 mm each way. Set the gap with the 0.55 mm gap foil that comes with the head.
- The measuring length is centred on the travel between the damper contacts, not on the travel
  of the guide blocks. The dampers now set the end of the travel.

## Next Steps

1. Set the limit switches so the carriage stays inside the 220 mm measuring length. Or order a
   longer tape, if the full 222 mm must be measured. Closed on 27 October 2026. The stage now
   uses the 240 mm tape, which covers the full travel. The limit switches no longer need to stop
   the carriage inside the measuring length. See
   [the 240 mm tape log](2026-10-27_rsf-ml240-tape.md).
2. Ask RSF for the ID number of the head with a 0.5 m cable (still open from the library work).
3. The sealing strip and the two sealing clamps have no geometry yet, so the collision check
   could not include them. Check them when they are drawn.

<details>
<summary>Technical notes</summary>

- `carriage-bottom.FCStd`: `Sketch031` constraint 5, 3.2 → 3.0 mm, now named
  `readhead_hole_inset`. Hole axes at (20.0, 66) and (20.0, 92). `IF_readhead_mount` follows by
  its expressions: (20.0, 79, 16). There is solid material on both sides of the clearance holes
  and the 5 mm counterbores.
- `base.FCStd`: `Params.scale_start_x` 97.3 → 351 mm. New alias `Params.scale_centre_z` = 34 mm.
  `Frame004` (`IF_scale_mount`): z expression `Params.scale_centre_z`, offset turned 180° about its
  own Z. Global result: (351, 17, 34), X = −X, Z = +Y.
- `compact-stage.FCStd`: links `AK-MC15-B-0.5M-SUBD15` (to the App::Part of the RSF head file) and
  `MB-MC15-MK-ML220`. `Fixed_readhead`: carriage `IF_readhead_mount` ↔ head `IF_mount_top`, with
  `Offset2` = 180° about Z. `Fixed_scale`: base `IF_scale_mount` ↔ scale `IF_mount_bottom`.
  `Fixed_scale_clamps` deleted. The first solve used stale joint placements; after
  `updateJCSPlacements()` the solve was right. The solver moved the carriage group 17.13 mm along
  the travel; all twelve moving parts were moved back to their earlier positions.
- Measured after the solve: head `IF_scale` (223.403, 17.45, 34) seen from scale `IF_ml_start`:
  (118.397, 0, 0), no rotation. Gap 0.550 mm. Damper contacts at +119.397 and −102.603 mm from the
  present position. Sensor path x = 120.8 … 342.8; measuring length x = 121.8 … 341.8.
- Collision check: `common().Volume` for every pair of links, at the present position and with
  the moving parts shifted to both damper contacts. No overlap anywhere. The sealing strip and
  clamps link to empty App::Parts.
- The compact stage has no `cad/params.csv`, so `cad_sync_params.sync_active()` does not apply.
  `bash doqs.sh generate` ran after the bill of materials change.
- All edits ran in the open FreeCAD 1.1 window through its RPC server. Saved: the three files
  above. Fingerprints written with `cad_fingerprint.write()` in the same window.
- The `modules/stoq` working copy shows changed HIWIN and Maxwell files dated 14 October. They are
  not part of this work and were left as they are.
- Mistake rules checked: [wrap crashed the open FreeCAD](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)
  (no `doqs wrap`), the PowerShell rules (all shell work in bash),
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md) (tooling
  folders left as they are), and [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md)
  (gap, offsets and angles read in the RSF drawing itself).

</details>
