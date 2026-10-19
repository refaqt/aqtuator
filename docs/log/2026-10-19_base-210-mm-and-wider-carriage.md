# 2026-10-19 — The base is 210 mm wide, and the bottom carriage is 208 mm wide

**Role(s):** cad, architecture

## Goal

Make the base 210 mm wide instead of 200 mm. The pocket for the rails and the motor grows by 2 mm.
The side walls take the rest. In the bottom carriage, the lower body (the part that goes into the
base pocket) grows by 2 mm. This gives material between the outer counterbores of the block screws
and the side of the lower body. The slanted end faces must reach 5 mm over each base wall, so the
seal strip has enough overhang. The shoulders take the rest of the extra width.

## Work Done

- **The base is 210 mm wide, up from 200 mm.** The pocket between the side walls is 176 mm wide,
  up from 174 mm. Each side wall is now 17 mm thick, up from 13 mm. The base is about
  151 000 mm³ larger.
- **The rails stay 138 mm apart, centred on the base.** They are now at y = 36 mm and y = 174 mm.
  The screw holes, the rail frames and the alignment tabs moved with them. The tabs are now
  11.5 mm deep, up from 10.5 mm. The motor holes and the stator frames stay centred, at y = 105 mm.
- **The bottom carriage is 208 mm wide, up from 198 mm.** It is still 1 mm inside the base on each
  side.
- **The lower body is 174 mm wide, up from 172 mm** (x = 17 to 191 mm). It still has 1 mm of space
  to each base wall.
- **The outer counterbores now have 1 mm of material to the side of the lower body.** Before, the
  edge of the counterbore lay exactly on the side of the lower body.
- **The slanted end faces reach 5 mm over each base wall, up from 4 mm.** They run from x = 11 to
  197 mm in the carriage (186 mm wide).
- **Each shoulder is 11 mm wide, up from 8 mm.** The notches and small chamfers at the ends of the
  shoulders moved with them.
- **The guide blocks stay centred.** The rows of blocks are at x = 35 mm and x = 173 mm. The block
  pockets, screw holes, counterbores, and the pockets and small holes over the blocks moved 5 mm
  with them. The forcer and its pocket stay in the middle, at x = 104 mm.
- **The block rows now follow a formula.** Their position comes from the carriage width and the
  rail spacing of 138 mm. The pockets over the blocks (`Sketch013`) now follow the block rows.
  Before, they followed the shoulder.
- **All spaces were checked by calculation in the assembly:**
  - each block has 2 mm of space to the base wall (before: 1 mm);
  - each side of the lower body has 1 mm of space to the base wall;
  - the outer strip of the carriage is 0.5 mm above the top of the walls;
  - the blocks do not overlap the rails, and the rails do not overlap the base.
- **The architecture has the new rail positions, block rows, pocket width and base width.**
- **The stored measurements (fingerprints) of the base, the carriage and the assembly are up to
  date.**

## Open Questions

- **The base is now 210 mm wide. This is exactly the limit in the stage requirements** (at most
  210 mm). There is no margin left for parts that stick out at the sides.
- **`Sketch015` (the small holes over the blocks) has two solutions.** A hole circle sits 0.5 mm
  from a pocket edge, and the solver can put it on either side. A jump of 3 mm made it flip, so the
  change was made in 1 mm steps. A clear distance from the block centre would be safer.
- **The two known overlaps did not change.** Each block overlaps the carriage by 2.07 mm³, and the
  forcer cable stub overlaps the carriage by about 2 383 mm³.

## Next Steps

1. Give the holes in `Sketch015` a size that has only one solution.
2. Draw the cable slot from the forcer pocket to the cable end of the carriage.

<details>
<summary>Technical notes</summary>

- Base: `BlockSketch.Width` 200 → 210 mm, `Sketch.pocket_w` 174 → 176 mm,
  `RailHoleSketch.second_rail_y` 31 → 36 mm, `reference_rail_y` 169 → 174 mm. Pocket, motor
  holes, stator frames (y = 105 mm) and tab depths follow by symmetry or formula.
  Volume 1 319 983 → 1 470 963 mm³.
- Carriage: `Sketch.w_carrier` 198 → 208 mm. `Pad001.Length` (shoulder) 8 → 11 mm.
  `Sketch010.lower_body_step` 5 → 6 mm (measured from the shoulder face: 5 mm overhang + 1 mm
  space). `Sketch001.block_edge_x` = `(Sketch.Constraints.w_carrier - 138 mm - .Constraints.block_w) / 2`
  (18 mm).
- `Sketch013`: the distance of 10 mm from the shoulder edge (constraint 99) was replaced by
  `block_pocket_x` = `Sketch001.Constraints.block_edge_x + 5 mm` (23 mm), measured from the origin.
  `Sketch014` and `Sketch015` follow `Sketch013`.
- The first try (one step from 198 to 208 mm) flipped the holes in `Sketch015` to x = 24.5 and
  38.5 mm. It was undone. The change was then made in ten steps of 1 mm. Holes now at x = 20.5,
  46.5, 161.5 and 187.5 mm.
- All carriage sketches are fully constrained. Volume 488 611 → 507 222 mm³.
- Frames: blocks a/b at x = 35 / 173 mm, forcer at (104, 106, 20).
- Assembly after `Assembly.solve()`: carriage at base y = 1 to 209 mm. Lower body y = 18 to 192
  (walls at 17 / 193). Slanted faces y = 12 to 198. Blocks at y = 19 to 53 and 157 to 191, 2.0 mm
  to the base. Carriage to base 0.5 mm, common volume 0. Forcer to base and magnet tracks 0 mm³.
- The open documents matched the saved files before the work (fingerprint volumes within rounding).
  Base, carriage and assembly were saved from the FreeCAD 1.1 window, then fingerprinted with
  `cad_fingerprint.write()`. The carriage now has 53 typed-in sizes, down from 55.
- Also added the missing index line for the 2026-10-19 forcer pocket log.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
