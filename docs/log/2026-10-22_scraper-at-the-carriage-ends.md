# 2026-10-22 — A printed scraper at each end of the carriage

**Role(s):** cad, engineering

## Goal

Design the scrapers that keep chips off the steel seal strip, where the strip comes out under
the carriage. Print them on a Bambu Lab or Prusa printer. Hold them with M3 countersunk screws
that screw up into the underside of carriage-top. Check that they fit.

## Short answer

- **The scraper fits, with no collision.** It sits in a new pocket, 10 mm long, 198 mm wide and
  4.5 mm deep, cut up into the underside of carriage-top at each end. The pocket is open at the
  end face.
- **One part, 197.6 x 9.8 x 4.6 mm, used at both ends.** At the other end it is turned 180°.
- **Five M3x10 countersunk screws (ISO 14581, Torx head) per scraper**, 46 mm apart. About
  6.8 mm of each screw goes into the aluminium.
- **Two lips with a 1 mm groove between them.** Both lips stop 0.15 mm above the strip. They do
  not touch it, so there is no friction and no wear in normal use.
- **Material:** iglidur i180 or PETG with PTFE. No carbon or glass fibre, because the fibres
  scratch steel.
- **Risk: the sealing clamps.** At the ends of the travel, the scraper passes over the end walls
  of the base, where the sealing clamps hold the strip. Nothing there may stand higher than the
  lips. The clamp is not designed yet.

![Section through the middle screw](../../modules/compact-stage/simulation/results/scraper-fit/section-A-A_y105.png)

## Work Done

### Space at the carriage end

- Carriage-top reaches 15 mm past each end of carriage-bottom. Its underside is only 0.5 mm above
  the base, and so only 0.25 mm above the strip. There is no room for a scraper under it. So the
  scraper sits in a pocket cut up into carriage-top.
- The end of carriage-top is solid over the first 12.2 mm, for the full width. After that, the
  slope opening starts. The pocket takes 10 mm and leaves 2.2 mm of aluminium to the opening.
- The strip lies flat on the base under the lips. Behind them, it starts to lift towards the
  slope of carriage-bottom. The point where it lifts is between 3 mm before and 0.5 mm after the
  inner end of the pocket. It depends on how tight the strip bends. That is why both lips are at the outer end of the scraper: they stay 3 to 7 mm
  ahead of the point where the strip lifts.

### Shape

| Part of the scraper | Size |
| --- | --- |
| Plate | 3.5 mm thick, rests flat on the pocket ceiling |
| Lip 1, at the end face | 1.0 mm thick, 1.1 mm high |
| Groove | 1.0 mm wide, open at both sides |
| Lip 2 | 1.0 mm thick, 1.1 mm high |
| Gap from the lips to the strip | 0.15 mm |
| Screw holes | 3.4 mm, 90° countersink to 5.6 mm, at 6.5 mm from the end face |
| Thread in carriage-top | M3, tap drill 2.5 mm, 10 mm deep from the pocket ceiling |

### Two changes to the advice of earlier today

- **No snowplough shape.** A slanted lip pushes chips sideways only when it is slanted by about
  20° or more. Over a 186 mm wide strip, that needs far more than the 10 mm of length that is
  free. So the lips run straight across. The groove is open at both sides, so coolant can leave.
- **No lip that presses on the strip.** In this height a printed lip can only be about 1 mm high.
  A lip that short does not bend. If it pressed on the strip, a rough estimate gives more than
  10 N per mm of width, which is far too much. So the lips keep a small gap. If a lip that touches
  is needed later, it must be soft (TPU) and a separate part.

### Checks

All parts were placed as in the compact-stage assembly and checked for overlap. The scraper does
not overlap carriage-top (with the new pocket), carriage-bottom or the base. It keeps 5.6 mm to
carriage-bottom and 0.4 mm to the base walls beside the strip. Details:
[results](../../modules/compact-stage/simulation/results/scraper-fit/summary.md).

## Decisions Made

No decision yet. The design is a proposal. The pocket and the five threaded holes are not in the
carriage-top CAD file yet.

## Open Questions

- **The sealing clamps must not hit the scrapers.** At the usable end of the travel, the end face
  of carriage-top is about 5 mm from the base end. With the dampers fully pressed in, it is 3 mm
  past the base end. So the scraper passes over the end wall, where the clamp sits. Either the
  clamp stays lower than the lips (less than 0.15 mm above the strip), or it holds the strip on
  the end face of the base, or it sits in a recess.
- **How wide is the strip?** The checks assume 186 mm, the widest strip that fits. The scraper
  covers y = 6.2 to 203.8 mm, so it covers any strip that fits.
- **Can the 0.15 mm gap be held?** A printed part is accurate to about 0.1 mm in height. Set the
  gap at fitting with a feeler gauge, and with shim foil between the plate and the pocket ceiling
  if the lips sit too high. Print the scraper flat, with the ceiling face on the bed and the lips
  up, and use ironing on the lip tips.
- **Are the magnet strips there?** If the magnets hold the strip less flat than assumed, the lips
  may touch. The plastic then wears in by itself. Check the strip for a track after the first run.

## Next Steps

- [ ] Add the pocket and the five M3 threaded holes to carriage-top in FreeCAD, at both ends.
- [ ] Add the scraper as a part in CAD, and add it and the 10 screws to the parts list.
- [ ] Design the sealing clamp so it stays out of the path of the scrapers.
- [ ] Print one scraper in PETG with PTFE and check the gap on the real strip.

<details>
<summary>Technical notes</summary>

- Case: `modules/compact-stage/simulation/cases/scraper-fit/`. It reads the `.FCStd` files as zip
  files with the `cadquery-ocp` package, not with FreeCAD, because FreeCAD is not installed in the
  cloud session. It places the parts with the `Placement` of each link in the compact-stage
  assembly. carriage-top at x = 106.6 to 316.6 mm, z = 40.5 to 60 mm. carriage-bottom at
  x = 121.6 to 301.6 mm.
- The sealing strip part has no shape in its file. The case uses a box y = 12 to 198 mm,
  z = 40 to 40.25 mm.
- Pocket (start end, assembly coordinates): x = 106.6 to 116.6, y = 6 to 204, z = 40.5 to 45.0.
  Scraper: x = 106.6 to 116.4, y = 6.2 to 203.8, z = 40.40 to 45.0. Screws at x = 113.1,
  y = 13, 59, 105, 151, 197.
- ISO 14581 M3: head 5.5 mm, head height 1.65 mm. The screw model is simplified.
- Strip lift point: estimated with a circular bend of R 35 to 60 mm onto the 19.4° slope of
  carriage-bottom. R 35 mm is the tightest radius from the seal strip designer page; R 60 mm is
  a gentler bend. Lift point at x = 117.1 and 112.8 mm.
- Lip stiffness estimate: cantilever 1.15 mm long, 1 mm thick, PETG at about 2 GPa (typical
  value, not from a data sheet), bent 0.3 mm: about 44 N per mm of width.
- Travel ends from the
  [damper pocket log](2026-10-22_damper-pockets-in-the-end-walls.md): carriage-top sticks out 3 mm
  past the base end at full damper press; damper stroke 7 mm; 1 mm safety.
- Mistake rules checked: the fatigue mistake (no material value given as fact without a data
  sheet), and the PowerShell rules (all shell work ran in bash).

</details>
