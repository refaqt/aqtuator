# 2026-10-22 — The slanted faces of carriage-top now follow carriage-bottom

**Role(s):** cad

## Goal

The slanted faces under carriage-top had a different angle from the slanted ends of
carriage-bottom. Make them the same, and link them, so a change in carriage-bottom moves
carriage-top too.

## Work Done

- **Why they were different.** carriage-top was drawn when the bottom slope was 30 mm long and
  13.5 mm high. On 2026-10-22 the bottom slope changed to 34 mm long and 12 mm high (about 19°).
  carriage-top kept the old angle (about 24°).
- **The two slanted faces are now parallel.** carriage-top reads the slope length, the slope
  height and the carriage length from carriage-bottom. Its slanted face sits 2 mm above the
  slanted face of carriage-bottom, measured straight up. That is the same 2 mm gap as over the
  middle, where the sealing strip runs.
- **The opening under carriage-top changed a little.** Its flat ceiling is now 112 mm long (was
  120 mm), the same as the flat top of carriage-bottom. At the underside, the opening is now
  185.7 mm long (was 177.8 mm). It ends 2.8 mm past each end of carriage-bottom.
- **The assembly is checked.** The two halves do not overlap. carriage-top does not touch the
  base, the dampers, the forcer or any other part. It still keeps 0.5 mm to the base.
- **The link also works without the FreeCAD window.** FreeCAD opens carriage-bottom by itself
  when it opens carriage-top. carriage-bottom must stay in its folder next to carriage-top.

## Open Questions

- **The gap along the slope is 1.9 mm at a right angle to the faces.** It is 2 mm when measured
  straight up. Check that this is enough for the sealing strip and the rollers.

<details>
<summary>Technical notes</summary>

- carriage-top `Sketch001` (the pocket under the part), three constraints now named and driven
  from the other document:
  - `slope_l = carriage_bottom#Sketch003.Constraints.slope_l` (34 mm)
  - `slope_rise = carriage_bottom#Pad.Length - carriage_bottom#Sketch003.Constraints.h_block`
    (12 mm)
  - `ceiling_l = carriage_bottom#Sketch.Constraints.l_carrier - 2 * .Constraints.slope_l` (112 mm)
- The 13 mm ceiling height still comes from the typed 6.5 mm distance to the top face. It was not
  linked in this change.
- The file stores the link with a relative path: `../carriage-bottom/carriage-bottom.FCStd`.
- In the assembly, the slanted faces of both parts have the normal (±0.3328, 0, ∓0.9430).
- carriage-top and compact-stage were saved and fingerprinted again. `doqs check` passes. On
  Windows it needs `PYTHONIOENCODING=utf-8`, or the name check stops on a console character. That
  is the same on `main`.

</details>
