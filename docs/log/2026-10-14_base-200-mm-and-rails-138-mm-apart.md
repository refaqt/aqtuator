# 2026-10-14 — The base is 200 mm wide, and the rails are 138 mm apart

**Role(s):** cad, architecture

## Goal

Make the base of the compact stage narrower: 200 mm instead of 210 mm. Give the guide blocks more
room across the stage: each rail moves 4 mm outward, and the pocket between the side walls grows
by 4 mm on each side. The bottom carriage grows with the rails, so it is 2 mm narrower than the
base.

## Work Done

- **The base is 200 mm wide, down from 210 mm.** The pocket between the side walls is 174 mm
  wide, up from 166 mm. Each side wall is now 13 mm thick, down from 22 mm. The base is about
  276 800 mm³ smaller.
- **The rails are at y = 31 mm and y = 169 mm, 138 mm apart.** Before, they were 130 mm apart.
  They stay centred on the base (y = 100 mm), and so do the magnet tracks. The screw holes, the
  rail frames and the alignment tabs moved with the rails. The tabs are still 10.5 mm deep.
- **The bottom carriage is 198 mm wide, up from 190 mm.** The rows of guide blocks are now at
  x = 30 mm and x = 168 mm, 138 mm apart. The block pockets, the screw holes, the counterbores and
  the lower body grew with the carriage. The lower body is now 172 mm wide (x = 13 to 185 mm).
- **The forcer stays in the middle of the carriage, at x = 99 mm.** The forcer pocket, its six
  holes, the channel in `Sketch019`, and the cable hole and cable slot all moved
  4 mm with it. The forcer pocket still has the same size.
- **Some sketches held frozen copies of edges.** These copies did not move when the carriage
  became wider, so the model broke. They now point at the outline of the carriage, or at the
  forcer pocket sketch. The next change of width will not break them. The cable channel position
  is now a formula: 20.2 mm left of the carriage centre.
- **All spaces are the same as before.** With the carriage on the guide blocks:
  - each block has 1 mm of space to the base wall;
  - each side of the lower body has 1 mm of space to the base wall;
  - the outer strip of the carriage is 0.5 mm above the top of the walls;
  - the blocks do not overlap the rails, and the rails do not overlap the base.
- **The assembly was solved again and saved.** Nothing overlaps the base.
- **The architecture has the new rail positions**, the rail spacing of 138 mm, the pocket width
  of 174 mm and the new position of block row b.
- **The stored measurements (fingerprints) of the base, the carriage and the assembly are up to
  date.** All repository checks pass.

## Open Questions

- **In the assembly, each guide block overlaps the carriage by about 2 mm³.** A check that places
  the blocks on the carriage frames by calculation finds no overlap. An earlier log found the same
  2.1 mm³ with the block turned the other way round. So the block joints in the assembly may use
  the other direction. This was there before this change.
- **The forcer still overlaps the carriage at its cable stub, by about 722 mm³.** This was there
  before this change.

## Next Steps

1. Check the direction of the block joints in the assembly.
2. Make the cable hole clear the cable stub of the forcer.

<details>
<summary>Technical notes</summary>

- Base: `BlockSketch.Width` 210 → 200 mm, `Sketch.pocket_w` 166 → 174 mm,
  `RailHoleSketch.second_rail_y` 40 → 31 mm, `reference_rail_y` 170 → 169 mm. Pocket, motor holes,
  stator frames and tab depths follow by symmetry or formula. Volume 1 596 780 → 1 319 983 mm³.
- Carriage: `Sketch.w_carrier` 190 → 198 mm. Volume 416 420 → 450 820 mm³. Forcer pocket
  (`Pocket006`) still removes 193 096.64 mm³.
- Frozen external edges replaced by links to `Sketch` (the carriage outline, `Edge1`–`Edge4`):
  `Sketch011` and `Sketch012` (2 each), `Sketch014` (2), `Sketch015` (4, plus `Sketch014` `Edge3`
  for the tangent line), `Sketch016` (4, it had no live links at all), `Sketch018` (4).
  `Sketch017`: the frozen, defining line at x = 48.5 mm (left side of the step profile) replaced by
  a defining link to `Sketch016` `Edge5`. The constraints kept their meaning. The volume did not
  change before the width change.
- `Sketch019`: `channel_x` = `Sketch.Constraints.w_carrier / 2 - 20.2 mm` (78.8 mm).
- Frames: block rows a/b at x = 30 / 168 mm, forcer at x = 99 mm (all by formula).
- Fit check by calculation: carriage placed on the base with carriage x → base y + 1 mm, carriage
  y → base −x, z + 24 mm. Blocks on the carriage frames. Results: carriage to base 0.500 mm, block
  to base 1.000 mm, block and rail common volume 0, rail and base common volume 0.
- Assembly after `Assembly.solve()`: no common volume with the base. Blocks to carriage 2.07 mm³
  each, forcer to carriage 722.06 mm³, forcer to magnet tracks 0.
- The assembly file was already changed on disk when this work started. The open document had no
  unsaved changes, so it held the same state. Base, carriage and assembly were saved from the
  FreeCAD 1.1.4 window.
- `bash doqs.sh check`: all gates passed.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  and the PowerShell rules (all shell work ran in bash).

</details>
