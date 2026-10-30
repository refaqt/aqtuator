# 2026-10-30 — Seal strip: corner slots, corner screws 1 mm in, and the flat strip

**Role(s):** cad

## Goal

Niels Bosmans asked for three changes to the seal strip:

1. The four ISO 7380-2 M4 corner screws clamp the strip. While the preload screws pull it, the
   strip must slide a little under them. So the four corner holes become slots: the same
   diameter, 1 mm long centre to centre. Then the preload can be adjusted a bit more.
2. Move the four corner screws and their holes 1 mm inward along X (the travel).
3. Put the flat strip, as cut from the sheet, in the design, parametric. The assembly keeps
   showing the bent strip.

## Short answer

- **Corner slots:** 4.5 mm wide, 1 mm centre to centre, 5.5 mm long, along X, centred on the
  screw. The strip can slide 0.5 mm each way. It needs only about 0.02 mm of pull at each end for
  270 N.
- **Corner screws at 6 mm from the base ends** (were 5 mm). The base holes, the screws in the
  assembly and the strip slots moved together.
- **The flat strip is 441.95 mm long**, 3.95 mm longer than the bent strip seen from above.
  The strip climbs about 12 mm over rollers 2 and 3 and comes back down. That adds 3.98 mm. The
  270 N pull stretches the strip by 0.02 mm, so the strip as cut is that much shorter. The holes
  near the ends hardly move: slot centres 5.000 mm and preload holes 5.850 mm from the strip end,
  against 5 and 5.85 mm on the bent strip.
- The flat strip is a Body with fully constrained sketches. Every size comes from the parameter
  sheet.

## What changed

### Parameters

- New parameter `strip_corner_slot_l` = 1 mm in `cad/params/default.csv`. `strip_corner_hole_d`
  (4.5 mm) is now the slot width. `params-table.csv` is generated again.

### Base

- `Sketch007`: the four corner holes were placed by a Ø8 construction circle 1 mm from the
  pocket end. That distance is replaced by a named constraint, `corner_screw_x` = 6 mm from the
  base end, like `preload_screw_x`. The other three holes follow by symmetry.
- Walls: inside the strip pocket, the nearest other edge is 5 mm from the hole axis (the ear
  edge). Below the pocket floor, no edge is within 6 mm of the axis. The M4 tap hole is Ø3.3.

### Seal strip file

The file now holds two Part containers:

| Part | What it is | In the assembly |
| --- | --- | --- |
| `sealing-strip` | The strip as it lies in the assembly: bent over the rollers, pulled, carriage in the middle | Yes, the only one linked |
| `sealing-strip-flat` | The strip as cut: flat at z = 0, its middle at the middle of the base | No |

`sealing-strip-flat` holds `FlatBody`:

- `FlatOutline`: two ends, two body sides and four ears (straight side, R3.8 arc, 45° step), as
  in the strip pocket of the base with the 0.2 mm edge gap. 16 elements, 0 degrees of freedom.
- `FlatPad`: `strip_t`.
- `FlatHolesSketch` with `FlatHoles` (through all): the four slots and the two preload holes.
  18 elements, 0 degrees of freedom.

The build script writes the sizes it reads from the base to the sheet (`strip_base_l`,
`strip_pocket_y0/1`, `strip_ear_*`, `strip_corner_screw_y0/1`, `strip_screw_y_mid`). It also
writes three values it computes from the bent shape and the pull:

| Sheet value | Value | How |
| --- | --- | --- |
| `strip_flat_l` | 441.953 mm | strip length as cut |
| `strip_flat_corner_x` | 4.9997 mm | slot centre from the strip end |
| `strip_flat_preload_x` | 5.8497 mm | preload hole centre from the strip end |

How: a point of the flat strip lies as far from the strip middle as it does along the bent
centre line, divided by 1 + ε. ε = 270 N / (185 GPa × 185.6 mm × 0.15 mm) = 5.2 × 10⁻⁵. The
stretch is taken as the same along the whole strip. Beyond the preload holes there is no pull,
which changes less than 0.001 mm.

### Assembly

- The four corner screws moved from x = 5 / 435 to 6 / 434 mm.

## Checks

- Both new sketches are fully constrained, with no conflicting or redundant constraints.
- The flat strip is one valid solid. Its outline area, less the 3.953 mm of extra length, is the
  outline area of the bent strip: 81 738.575 against 81 738.578 mm².
- Parametric: with `strip_corner_slot_l` = 2 mm, the flat slots grew to 2 mm. Set back to 1 mm.
- In the assembly, the strip does not touch any of the six screws. The rollers touch the strip as
  before. Screws and base holes line up again: each corner screw overlaps the Ø3.3 tap hole by
  38.6 mm³, its thread.
- The strip still keeps 2.55 mm of material between each slot and the edge of the ear.
- The ISO 7380-2 M4 collar is 9.4 mm wide (Fasteners workbench model). It covers the whole
  5.5 mm slot, with at least 1.9 mm of strip under the collar at the slot ends.
- The volume FreeCAD reports for the bent strip is 0.3 % too high. Its faces are right: the side
  face of the bent part is its centre line length × 0.15 mm. Only the volume number of the curved
  faces is off. So the bent shape is right.
- `doqs check`: all gates pass. No dimension in the strip file is a typed number.

## Open questions

- The corner screw heads now sit 1 mm closer to carriage-top at the ends of the travel. This was
  already an open point: carriage-top and the scraper are still to be adapted.

<details>
<summary>Technical notes</summary>

- When FreeCAD was connected again, no document was open. Before that, the assembly window had
  unsaved changes; they are not in the file. The assembly was opened again from the file and
  changed only for the four screws.
- The FreeCAD tools were not loaded in this session after the restart. All FreeCAD work went
  through the same RPC call that the add-on tool uses (`execute_code` on `127.0.0.1:9875`, main
  thread), never `doqs wrap`.
- One slow check (a face-by-face wall measurement) passed the 90 s limit of the add-on. It
  finished on its own, and the change it made was checked afterwards.
- Mistake rules checked: FreeCAD (only `execute_code`), PowerShell (all shell work in bash),
  tooling (`.agents/` and `doqs/` left as they are).

</details>
