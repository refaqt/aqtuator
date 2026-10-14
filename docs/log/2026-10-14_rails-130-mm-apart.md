# 2026-10-14 — The rails in the base are 130 mm apart

**Role(s):** cad, architecture

## Goal

Make the rails in the base match the rows of guide blocks in the bottom carriage. The blocks are
130 mm apart, and the rails were 128 mm apart.

## Work Done

- **The rails are now at y = 40 mm and y = 170 mm, 130 mm apart.** They stay centred on the base
  (y = 105 mm), under the magnet tracks. Before, they were at 41 and 169 mm. The screw holes and
  the two rail frames moved with them.
- **The alignment tabs moved with the rails.** Each rail again lies against its tabs, with no
  overlap. The tab depth is now a formula of the rail position, so the tabs follow the rails if
  they move again.
- **The pocket between the side walls is now 166 mm wide, up from 164 mm.** With the rails 1 mm
  further out, the 34 mm wide blocks touched the walls. Now each block has 1 mm of space again. Each
  wall is now 22 mm thick, down from 23 mm. Niels chose this.
- **In the assembly, nothing overlaps the base.** The rails, the blocks and the magnet tracks were
  checked after the assembly was solved again.
- **The architecture has the new rail positions**, and the rail spacing of 130 mm as a number.
- **The stored measurements (fingerprint) of the base are up to date.** The base is 25 200 mm³
  smaller: 2 mm more pocket width, over 30 mm of height and 420 mm of length.

## Open Questions

- **The carriage sides now touch the base walls, with 0 mm of space.** The lower body of the
  carriage is 166 mm wide (carriage x = 12 to 178 mm), the same as the pocket. Niels will make it
  narrower. Done later the same day: see
  [The lower body of the bottom carriage is 2 mm narrower](2026-10-14_narrower-lower-body-of-the-bottom-carriage.md).
- **The carriage edge sits right on the top of the base walls, with 0 mm of space.** The outer
  strip of the carriage (carriage x = 0 to 8 mm, and 182 to 190 mm) is at z = 40 mm, the top of the
  walls. This was already so before this change. It comes from the lower QEH15SA blocks. Done
  later the same day: see [The bottom carriage clears the top of the base](2026-10-14_carriage-clears-the-top-of-the-base.md).

## Next Steps

1. Make the lower body of the carriage narrower, so the sides clear the walls.
2. Raise the outer strip of the carriage, or lower the walls, so the carriage clears the top of the
   base.
3. Save the assembly and write its fingerprint again.

<details>
<summary>Technical notes</summary>

- `RailHoleSketch`: `reference_rail_y` 169 → 170 mm, `second_rail_y` 41 → 40 mm.
- `Sketch` (the pocket between the walls): constraint 11 is now named `pocket_w`, 164 → 166 mm.
- `Sketch001` (the floor with the tabs): new expressions
  - `second_rail_tab_depth` = `RailHoleSketch.Constraints.second_rail_y - 15 mm / 2 - (BlockSketch.Constraints.Width - Sketch.Constraints.pocket_w) / 2`
  - `ref_tab_left_depth` = `(BlockSketch.Constraints.Width + Sketch.Constraints.pocket_w) / 2 - (RailHoleSketch.Constraints.reference_rail_y + 15 mm / 2)`
  - `ref_tab_right_depth` = `Constraints.ref_tab_left_depth`
  - 15 mm is the width of the EGR15 rail, from the HIWIN catalogue. The value is 10.5 mm, as before.
- Checks in the FreeCAD window, after `Assembly.solve()`: no common volume between the base and any
  part. Smallest distance from each block to the base: 1.000 mm. Rails touch the floor and the tabs
  (0 mm, on purpose).
- Carriage check: carriage-bottom placed on the blocks by calculation (carriage x → base y, block
  face at base z = 34 mm). Contacts at base y = 22 mm (z = 24…34 mm) and at z = 40 mm
  (y = 10…18 mm). No common volume.
- The base was saved from the FreeCAD 1.1.4 window. The assembly was solved again in memory, but
  not saved. It holds Niels's unsaved work.
- `bash doqs.sh check` fails only on the assembly fingerprint.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  and the PowerShell rules (all shell work ran in bash).

</details>
