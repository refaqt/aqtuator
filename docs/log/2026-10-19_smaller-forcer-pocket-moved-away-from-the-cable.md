# 2026-10-19 — The forcer pocket is smaller and sits 16 mm away from the cable end

**Role(s):** cad, architecture

## Goal

Make the pocket for the forcer (the moving coil part of the linear motor) in the bottom carriage
as small as possible. It must not touch the forcer, and it must be possible to mill it. Then move
the pocket away from the cable end of the carriage, to make room for a cable slot. The pocket must
keep at least 1 mm of material to the slanted faces at the ends of the carriage.

## Work Done

- **The pocket now follows the real outline of the forcer.** The forcer body is 86 × 118 mm, and its
  top step is 76 mm wide. The pocket has 1 mm of space on every side. The old pocket had between
  0.5 mm and 10 mm.
- **The old sketch had a forcer outline in the wrong place.** It was 4 mm off along the travel,
  because the forcer body is not centred on its hole pattern. The new pocket uses the true
  position: 63 mm from the middle hole to the cable end, and 55 mm to the other end.
- **The corners have a radius of 3 mm, so a 6 mm end mill can cut them.** The forcer corners are
  sharp. At each corner the space is 0.17 mm. The pocket is 20 mm deep at its deepest, so the
  end mill needs about 21 mm of reach.
- **The pocket is in two steps.** The first step is 88 × 120 mm and 17 mm deep. The second step is
  78 × 120 mm and 3 mm deeper. The mounting face of the forcer stays at z = 20 mm.
- **The first step is now 1 mm deeper, at 17 mm instead of 16 mm.** Before, the lower step of the
  forcer touched the pocket ceiling with 0 mm of space. Then the forcer could rest on that face and
  not on its mounting face. Now that face has 1 mm of space as well.
- **The extra bump on one side of the second step is gone.** It gave 4 mm of air over the lower step
  of the forcer, but the forcer did not need it.
- **The forcer, its six holes, the cooling channel and the forcer frame moved 16 mm away from the
  cable end.** One size sets this: `forcer_shift_y` in the pocket sketch.
- **16 mm is close to the limit.** The thinnest wall to the slanted face at the far end is now
  1.11 mm. A move of 16.3 mm would give exactly 1 mm.
- **There is now 42 mm of material between the pocket and the cable end of the carriage.** Before,
  there was 25 mm. The cable slot can go there.
- **The cooling channel now sits 4 mm inside the forcer face at both ends.** Before, one end of the
  channel lay on the edge of the forcer face. Then the forcer could not close the channel there.
- **All forcer sizes are named, and the other sketches follow them.** The second step, the six
  holes, the cooling channel and the forcer frame all use formulas from the pocket sketch. All four
  sketches are fully constrained.
- **The assembly solves.** The forcer does not overlap the carriage with its body. It still overlaps
  at the cable stub, by about 2 380 mm³, because the cable slot does not exist yet. The forcer does
  not touch the magnet tracks or the base.
- **The architecture says where the forcer pocket is now.**

## Open Questions

- **The forcer now sits 16 mm off the centre of the carriage.** Does this change the usable stroke
  at one end of the magnet tracks?
- **A space of 0.17 mm at the corners is small.** If the real forcer corners are sharp and the
  pocket is a little too small, the forcer will not go in. A larger corner relief, or 1.5 mm of
  space on each side, would give more margin.
- **The six screw holes are still 4.5 mm.** The screw length is not chosen yet.

## Next Steps

1. Draw the cable slot from the forcer pocket to the cable end of the carriage.
2. Check the stroke with the forcer in its new place.

<details>
<summary>Technical notes</summary>

- `Sketch016` (first step, from the bottom) was rebuilt. Named sizes: `forcer_shift_y` 16,
  `forcer_w` 86, `forcer_l` 118, `forcer_step_w` 76, `forcer_hole_to_cable_side` 46,
  `forcer_hole_to_cable_end` 63, `pocket_clearance` 1, `pocket_corner_r` 3. The forcer outline and
  the step line are construction geometry. Links to the carriage outline were replaced by
  `Sketch.Constraints.w_carrier` and `l_carrier` formulas.
- `Pocket006.Length` = `Pocket009.Length + 6 mm + Sketch016.Constraints.pocket_clearance` (17 mm).
  `Pocket007.Length` follows by its old formula (3 mm). `Pocket006.Profile` now takes the whole
  sketch, because the old edge names no longer existed.
- `Sketch017` (second step) was rebuilt with formulas from `Sketch016`. It is now attached to the
  body `XY_Plane`, offset by `Pocket006.Length` and turned 180° about X, instead of to a pocket face.
- `Sketch018` (six holes) was rebuilt: centre at `w_carrier / 2`, `l_carrier / 2 + forcer_shift_y`,
  `hole_row_spacing` 50, `hole_pitch` 35. Old stale external edges were removed.
- `Sketch019` (cooling channel): now attached to `XY_Plane`, offset by
  `Pocket006.Length + Pocket007.Length`. `channel_top`, `channel_bottom` and `channel_end_y` are
  formulas: forcer start + 4 mm (47 mm), forcer end − 4 mm (157 mm), forcer end − 34 mm (127 mm).
- `Frame004` (`IF_forcer_mount`): y = `l_carrier / 2 + Sketch016.Constraints.forcer_shift_y`.
  Now at (99, 106, 20).
- Pocket outline: first step x 52–140, y 42–162 mm; second step x 52–130, y 42–162 mm.
- Fit check by calculation, forcer placed on `Frame004`: body overlap 0 mm³, smallest space
  0.172 mm (corners). Cable stub overlap 2 383 mm³. Wall to the far slanted face 1.114 mm, at the
  pocket end wall y = 162 mm.
- Carriage volume: 457 133 → 488 611 mm³.
- Assembly after `solve()`: forcer to carriage 2 383 mm³ (cable stub only), forcer to magnet tracks
  and base 0 mm³.
- The carriage and the assembly were saved from the FreeCAD 1.1 window, with Niels's consent.
  Both fingerprints were written again after the save.
- `bash doqs.sh check`: all gates passed. The carriage still has 55 typed-in sizes that are not
  linked to a parameter. That is a warning, not a failure.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
