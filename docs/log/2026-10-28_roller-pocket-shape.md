# 2026-10-28 — New shape for the roller pockets, with R 3.5 corners

**Role(s):** cad

## Goal

Niels Bosmans asked for a new shape for the sealing strip roller pockets in carriage-bottom and
carriage-top, drawn as a green line on a picture. The corner radii must go down to 3.5 mm. The
roller centre must not move.

## Short answer

- **Each pocket has a narrow part and a wide part.** The narrow part keeps its 21 mm width and
  its 3 mm gap on the inner side. On the end side, the gap to the roller is now 0.5 mm (was 3 mm).
  A wide part, 26 × 7 mm with fully round ends, sits on the end side.
- **All pocket corners are R 3.5 mm** (was 4 mm). The axle slots keep their 8 mm width and R 4 ends.
- **The rollers did not move.** The axle slots and the axle screws did not move either.
- **The wide part is there for the roller corners.** Without it, the R 3.5 corners of the narrow
  part would cut into the roller ends. With 26 mm, the roller keeps 0.46 mm to every pocket wall.
- **The wall to each axle screw hole is now 0.9 mm.** This is the price of the 26 mm width.
- **carriage-top still follows carriage-bottom.** Every new size is read from carriage-bottom.
- All work is on branch `cad/roller-pocket-shape`.

## Work Done

| Size (c = roller centre, across the roller) | Before | Now |
| --- | --- | --- |
| Pocket corner radius | 4 mm | 3.5 mm |
| Narrow part, inner side | c + 8 mm | c + 8 mm |
| Narrow part, end side | c − 8 mm | c − 5.5 mm |
| Wide part | none | 26 × 7 mm, from c − 5.5 to c + 1.5 mm, R 3.5 ends, 11 mm deep |
| Gap roller to pocket wall (smallest) | 0.5 mm | 0.46 mm (roller end corner to the wide part) |
| Wall to the axle screw holes | — | 0.9 mm |
| Wall to the end face (carriage-top) | 4.2 mm | 6.7 mm |

- The width of the wide part is a trade-off. Niels Bosmans chose 26 mm from these options:

  | Width | Roller gap | Screw-hole wall |
  | --- | --- | --- |
  | 24 mm | 0.15 mm | 1.53 mm |
  | 25 mm | 0.34 mm | 1.20 mm |
  | 26 mm | 0.46 mm | 0.90 mm |
  | 27 mm | 0.50 mm | 0.63 mm |

- The width is in the `Params` sheet of carriage-bottom (`roller_lip_w`), with its reason.

### Checks

- Both carriages are one valid solid. All changed and new sketches are fully constrained.
- A comparison with the committed files shows changes only in the roller pocket features, plus
  the new wide-part pockets.
- carriage-bottom: 449 877 → 450 518 mm³. carriage-top: 430 141 → 431 153 mm³. The parts are
  heavier because the narrow part got shorter.
- Every pair of parts in the assembly was checked. Only the two known overlaps with the motor
  cable stub remain.
- Changing `roller_lip_w` in carriage-bottom moved the wide part in carriage-top too.

## Decisions Made

- Niels Bosmans chose: end-side gap 0.5 mm, wide part 7 mm tall with full R 3.5 ends, wide part
  26 mm wide, sharp corners where the narrow part meets the wide part.

## Open Questions

- **0.9 mm of wall next to each axle screw hole is thin.** The hole is threaded. Check it when the
  carriage goes to the machine shop.
- **0.46 mm between a roller end corner and the pocket wall** leaves little room for tolerances.

## Next Steps

1. Look at the pockets in FreeCAD.
2. Merge the branch when the model is accepted.

<details>
<summary>Technical notes</summary>

- carriage-bottom `Sketch013`: `roller_pocket_r` 4 → 3.5 mm. The symmetry of the pocket outline
  about the slope-edge line was replaced by `roller_end_gap_outer` (0.5 mm, line 13 to line 3)
  and a vertical constraint on line 2.
- carriage-bottom `Sketch014` and `Sketch015`: their centre line was placed on the middle of the
  pocket sides. That point moved with the new shape, and the slots moved 0.75 mm. The line now
  sits on the pocket side lines, horizontal, at `roller_centre_y` = `roller_d / 2 +
  roller_end_gap_outer` from the end-side pocket edge. The slots are back at y = 33–41 mm.
- carriage-bottom `Sketch014`: the slot radius was tied to the pocket corner radius (`Equal`). That
  made the slot 7 mm wide. The tie was removed; `axle_slot_r` is now driving at 4 mm.
- carriage-bottom, new `Sketch034` → `Pocket021` at the tip. Four outlines, mirrored by sketch
  constraints. Names: `roller_x`, `roller_y`, `roller_lip_r` (= `roller_pocket_r`),
  `roller_lip_cc` (= `Params.roller_lip_w − 2 r`), `roller_lip_end`. Depth `Pocket004.Length`.
- carriage-top `Sketch005`: `roller_pocket_l` and the symmetry were replaced by `roller_gap_in`,
  `roller_gap_out` and `roller_pocket_half_w`, all read from carriage-bottom.
- carriage-top, new `Sketch009` → `Pocket006`, inserted after `Hole001` and added to
  `MultiTransform`. Sizes from `carriage_bottom#Sketch034`. Depth `carriage_bottom#Pocket004.Length`.
- Roller gaps measured with `distToShape` on Ø10 × 20 mm cylinders, centre 3.5 mm inside each
  part. Walls measured between the solids each feature removes.
- Fingerprints written headless with `freecadcmd.exe` (FreeCAD 1.1.4), carriage-bottom opened
  first. New typed-number notes: `Sketch013.roller_end_gap_outer` and `Sketch014.axle_slot_r`, in
  the same style as the other roller sizes.
- Mistake rules checked: [wrap crashed the open FreeCAD](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)
  (only main-thread calls to the open FreeCAD), the PowerShell rules, the tooling update rule.

</details>
