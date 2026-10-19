# 2026-10-19 — The forcer pocket has new clearances, and the forcer touches two short pads

**Role(s):** cad

## Goal

The space around the forcer (the moving coil part of the linear motor) is now 0.5 mm at the sides
and 2 mm at the ends. The pockets for the rail guide blocks are longer, because a block touched the
carriage. Fix what these changes broke, and make three small changes to the bottom carriage:
remove a ledge in the forcer pocket, let the forcer touch its side wall only near its ends, and let
the corner notches end smoothly on the side step.

## Work Done

- **The ledge at both ends of the forcer pocket is gone.** The deeper step of the pocket still used
  the side space (0.5 mm) at its ends. The first step used 2 mm. So a 1.5 mm ledge was left at each
  end. Both steps now use the 2 mm end space, and the end walls are flat from top to bottom.
- **The space above the lower step of the forcer is 1 mm again.** The pocket depth also used the
  side space, so it had dropped to 0.5 mm. The depth now has its own size,
  `pocket_clearance_depth` = 1 mm. The first step is 17 mm deep, the second step 3 mm deeper. The
  forcer mounting face stays at z = 20 mm.
- **The forcer moved 1 mm back toward the cable end.** With the longer pocket, the wall to the
  slanted face at the far end would be 0.75 mm. Now `forcer_shift_y` is 15 mm, and that wall is
  1.11 mm. There are 40 mm of material between the pocket and the cable end of the carriage. The
  holes, the cooling channel and the forcer frame moved with it.
- **The forcer now touches its side wall at two pads of 10 mm.** The wall along the long side of the
  deeper step is cut back between the pads. Each pad touches the forcer over 10 mm, counted from
  the forcer ends. A short contact at each end gives a clearer position than one long wall. The
  corners of the cut have a 3 mm radius, so a 6 mm end mill can make them.
- **The four corner notches now end smoothly on the side step.** The notches were 15 mm wide, and
  the side step is at 17 mm. The 4 mm radius ended on a 2 mm flat and left a very thin edge. The
  notch width now follows the side step, so the radius runs straight into the step wall.
- **The assembly solves.** No guide block touches the carriage. The forcer overlaps only at its
  cable stub, by about 2 270 mm³, because the cable slot does not exist yet.

## Open Questions

- **The far-end wall is only 1.11 mm.** More space at the ends of the pocket, or a larger
  `forcer_shift_y`, makes it thinner than 1 mm.
## Next Steps

1. Draw the cable slot from the forcer pocket to the cable end of the carriage.

<details>
<summary>Technical notes</summary>

- `Sketch017`: `step_start_y` and `step_pocket_l` now use
  `Sketch016.Constraints.pocket_clearance_top_bottom` instead of `pocket_clearance_side`.
- `Sketch016`: new construction line at the origin with the named dimension
  `pocket_clearance_depth` (1 mm). `Pocket006.Length` =
  `Pocket009.Length + 6 mm + Sketch016.Constraints.pocket_clearance_depth`.
- `Sketch016.forcer_shift_y` 16 → 15 mm. `IF_forcer_mount` is now at (104, 105, 20).
- New `Sketch022` and `Pocket011` (last feature, tip). The sketch uses the same attachment as
  `Sketch017`; `Pocket011.Length` = `Pocket007.Length`. Named sizes: `flange_pad_l` (10 mm),
  `relief_left_x`, `relief_w`, `relief_start_y`, `relief_l`, `pocket_corner_r`. All but
  `flange_pad_l` are formulas of `Sketch016`, `Sketch017` and `l_carrier`. The cut runs from
  x = 131.5 to 144.5 mm and y = 52 to 150 mm, z = 17 to 20 mm.
- `Sketch011`: the arc start is no longer tied to the edge at x = 11 mm. New named dimension
  `notch_w` = `Pad001.Length + Sketch010.Constraints.lower_body_step` (17 mm). The other three
  notches follow by symmetry.
- All changed sketches are fully constrained. Pocket ends: y = 40 and 162 mm, z = 0 to 20 mm.
- Carriage and assembly were saved from the FreeCAD window and fingerprinted with
  `cad_fingerprint.write()`. The carriage now has 56 typed-in sizes (53 in the last log):
  `pocket_clearance_top_bottom`, `pocket_clearance_depth` and `flange_pad_l` are new. All are
  named.
- `base.FCStd` was saved in the GUI before this work. Its fingerprint was written again from the open, unchanged document.
- The assembly fingerprint total changed from 2 459 920 to 2 706 788 mm³. Every part volume is the
  same. The new total is the plain sum of the parts.
- `validate_cad.py`: all models pass. Only the old typed-size warnings remain.

</details>
