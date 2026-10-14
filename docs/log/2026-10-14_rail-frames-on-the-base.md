# 2026-10-14 — The base has mounting frames for the EGR15U rails

**Role(s):** cad, architecture

## Goal

Give the base of the compact stage the mounting frames that the two HIWIN EGR15U418H guide rails
need, so the rails can be put into the assembly with one joint each.

## Work Done

- **The base already had a frame for each rail, but they were hidden and had old names.** They
  were made on 6 October for the older HGR15 rails. They now carry the names that their interfaces
  in the architecture give them: `IF_reference_rail_mount` and `IF_second_rail_mount`. This rename
  was already agreed in the doqs naming rule for ports and frames.
- **All four frames of the base are now visible**, the two rail frames and the two stator frames.
- **The frames fit the EGR15U rail without a change of position.** Each frame sits on the floor of
  the base, at z = 10 mm, on the first screw hole of its rail. X runs along the rail and Z points up.
  The rail frame `IF_mount_bottom` has the same layout. A Fixed joint between the two puts each rail
  from x = 11 mm to x = 429 mm, centred on its row of holes (y = 41 mm and y = 169 mm). This was
  checked by calculation in the FreeCAD window.
- **The architecture now names the EGR15U418H as the guide rail**, in place of the HGR15R, and
  describes the two rail frames.
- **The shape of the base did not change.** Only the names and the visibility changed. The stored
  measurements (fingerprint) of the base are up to date.

## Decisions Made

None. The rail choice was made on 13 October.

## Next Steps

1. Niels puts the two EGR15U418H rails into the assembly, with a Fixed joint between the `XY_Plane`
   of each base frame and the `XY_Plane` of the rail frame `IF_mount_bottom`.
2. Check the screw length for the rail. The interface still says M4 × 16, which was worked out for
   the 15 mm high HGR15 rail. The EGR15U rail is 12.5 mm high, so the screw may need to be shorter
   or longer. Use the HIWIN catalogue values for the EGR15U counterbore.

<details>
<summary>Technical notes</summary>

- Base: `Frame001` relabelled `IF_rail_reference` → `IF_reference_rail_mount`, `Frame` relabelled
  `IF_rail_second` → `IF_second_rail_mount`. Object names stay, so expressions are unchanged:
  x = `RailHoleSketch.Constraints.first_hole_x` (40 mm), y = `reference_rail_y` (169 mm) or
  `second_rail_y` (41 mm), z = `-Pocket001.Offset` (10 mm).
- The floor height was measured: a vertical line at the rail rows cuts the base at z = 0 and
  z = 10 mm.
- Rail file: `modules/stoq/modules/hiwin/modules/egr-rail/cad/parts/EGR15U418H.FCStd`. Its frame
  `IF_mount_bottom` is at (0, 29, 0), turned 90° about Z. Placement of the rail =
  base frame × inverse(rail frame) gives the bounding box (11…429, 161.5…176.5, 10…22.5) for the
  reference rail.
- No joint or assembly file used the old frame names. The rails are not in the assembly now.
- The base was saved from the FreeCAD 1.1.4 window, so its view data stays. The fingerprint was
  written with `freecadcmd` and `cad_fingerprint.write()` after `purgeTouched()`; the `.FCStd`
  hash was the same before and after.
- `bash doqs.sh check` fails only on the assembly and the bottom carriage. Both had changes on disk
  before this work, and their fingerprints are older. The base passes.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  (the tooling folders were left as they are), and the PowerShell rules (all shell work ran in
  bash).

</details>
