# 2026-10-07 — The motor stators are in the compact-stage assembly

**Role(s):** cad, architecture

## Goal

Put the two Maxwell MK2-180 stators (the magnet tracks of the linear motor) into the compact-stage
assembly. Fix each one to the base with one joint between two mounting frames.

## Work Done

- **Each MK2 stator in the parts library now has a mounting frame.** It sits on the first mounting
  hole at the N end of the stator, on its bottom face. This was added in stoq
  ([refaqt/stoq#10](https://github.com/refaqt/stoq/pull/10), merged), and aqtuator now uses that
  stoq version.
- **The base has two mounting frames for the stators.** They sit on the first motor hole of each
  stator, on the centre line of the base, on the floor. Their positions are formulas of the motor
  hole sketch and the hole pattern, so they move when the holes move. The second frame is 180 mm
  after the first.
- **Two MK2-180 stators are in the assembly, each with a fixed joint.** All 12 stator holes line up
  with the 12 motor holes in the base. The two stators touch at their slanted ends, with no
  overlap. They lie flat on the floor, 13.5 mm from each rail.
- **The stators and their interface to the base are now in the stage architecture.**
- **The hole spacing in the Maxwell data sheet is wrong.** The drawing says "A x 120". The holes
  are 60 mm apart, as Niels confirmed. The stoq parts table is corrected in
  [refaqt/stoq#11](https://github.com/refaqt/stoq/pull/11), not yet merged.

## Decisions Made

- **Both stators point the same way, N end towards the start of the base.** This keeps the magnet
  pattern continuous across the joint, and the slanted ends fit into each other.

## Next Steps

1. Merge [refaqt/stoq#11](https://github.com/refaqt/stoq/pull/11), then move aqtuator to that stoq
   version. Until then, the FreeCAD window may open the stators hidden (see the technical notes).
2. Model the locating pin holes for the stators.
3. Choose the screws for the stators.

<details>
<summary>Technical notes</summary>

- Base: new frames `Frame002` (`IF_first_stator_mount`) and `Frame003` (`IF_second_stator_mount`)
  in the `Part` container, attached `FlatFace` to the `XY_Plane` of the part origin, like the rail
  frames. Expressions:
  - x = `BlockSketch.Constraints.Length / 2 - Sketch002.Constraints.first_motor_hole_offset`
    (70 mm); the second adds `LinearPattern.Occurrences / 2 * LinearPattern.Offset` (250 mm).
  - y = `BlockSketch.Constraints.Width / 2` (105 mm); z = `-Pocket001.Offset` (10 mm).
- `MotorHoleSketch` (`Sketch002`): constraint 5 is now named `motor_hole_row_offset` (74 / 2) and
  constraint 6 `first_motor_hole_offset` (30 + 2 × 60). The values did not change.
- Assembly: links `MK2_180` and `MK2_181` to `Part` in
  `modules/stoq/modules/maxwell/modules/mk2-stator/cad/parts/MK2-180.FCStd`. Joints `Joint006` and
  `Joint007` are `Fixed`, between the `XY_Plane` of each base frame and the `XY_Plane` of the stator
  frame `IF_mount_bottom`. No offsets. After moving both stators away, the solver put them back on
  the same placements.
- The stator frame has its Z axis along the stator's +Y axis, so the links stand at +90° about X.
- stoq moved from `bf9eec5` to `14fe9b1`.
- The stator files at `14fe9b1` have no view data, so the FreeCAD window opens them with everything
  hidden, and the stators do not show in the assembly. A headless open is fine, so the fingerprint
  measures them. [refaqt/stoq#11](https://github.com/refaqt/stoq/pull/11) adds the view data.
- The base and the assembly were saved from the FreeCAD 1.1.4 window. A save without the window
  drops `GuiDocument.xml`, and with it the colours of the base. This was tested on a copy.
- Fingerprints were written with `freecadcmd` and `cad_fingerprint.write()` after `purgeTouched()`.
  The documents were closed without saving, and the `.FCStd` hashes stayed the same.
- `bash doqs.sh check` passes. The interface check finds the SysML ports, `okh.toml` and the frames
  in agreement. 29 warnings about typed-in sizes remain. They were there before.
- `modules/stoq` still has local changes to two HIWIN part files. They were there before this work
  and are not part of this commit.
- The uncommitted change in the assembly from before this work was discarded, as Niels asked.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  (the tooling folders were left as they are), and the PowerShell rules (all shell work ran in
  bash).

</details>
