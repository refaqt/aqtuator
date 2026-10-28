# 2026-10-28 — Seal strip page updated to the current roller places

**Role(s):** engineering, simulation, software

## Goal

Niels Bosmans asked to update the seal strip design page with the current roller places from
the CAD, the current strip width, and a strip 0.15 mm thick.

## Short answer

- **The page now starts with the current layout.** Rollers 1–2 are 36.83 mm apart, rollers 2–3
  are 112 mm apart, and rollers 2 and 3 lift the strip 13 mm (was 6 mm). The strip is 0.15 mm
  thick and 186 mm wide.
- **The free arch does not fit under the top carriage.** Only 0.35 mm of room is left above
  rollers 2 and 3. At 54 N the strip wants to rise 3.4 mm. So the strip will press on the
  ceiling of the top carriage over the middle of the carriage. The page shows this in red.
- **About 3.3 mm of screw travel gives 54 N** (was about 1 mm).
- **At 54 N, rollers 1 and 4 carry about 250 N, rollers 2 and 3 about 38 N.**
- **No fatigue limit is reached at 54 N.** The highest stress is 584 MPa. The thinner strip
  bends with less stress.
- **The solver no longer stops at very high pulls.** It failed at about 5600 N with the new
  layout. Normal pulls gave the same results before and after the fix.

## Work Done

- Read the roller places from carriage-bottom and carriage-top, placed as in the assembly.
- Set the new defaults in the page and in the model. Updated the case README with the new
  results and where each number comes from.

Full table: [case README](../../simulation/cases/strip-seal-designer/README.md#results-at-the-defaults).

## Decisions Made

No design decision.

## Open Questions

- **How should the strip pass between the two carriage halves?** The gap is 2 mm, and the strip
  arch is much higher than the room above the rollers. Options: lower rollers 2 and 3, a higher
  ceiling in the top carriage, or accept that the strip slides on the ceiling.
- **What holds the strip down at rollers 1 and 4?** The page assumes magnet strips under the
  strip there. In the CAD, the top rollers sit over the slot of the base, where nothing supports
  the strip.
- **How high do the rollers sit?** The rollers and axles have no part yet. This work assumes
  each roller sticks out 1.5 mm from its carriage half, as in earlier CAD work. With that
  assumption, the top rollers sit 1.15 mm lower than the strip on the base.

## Next Steps

- [ ] Choose how the strip passes between the carriage halves.
- [ ] Draw the rollers and axles, so their height is known.
- [ ] If the strip may touch the top carriage, add that ceiling to the model.

<details>
<summary>Technical notes</summary>

- Geometry read from the `.FCStd` files with `cadquery-ocp`, no FreeCAD. Placements from the
  assembly: carriage-bottom at (301.603, 1, 24) mm turned 90°, carriage-top at
  (211.603, 105, 40.5) mm.
- Top rollers (carriage-top `Pocket003`, `Pocket006`): x = 118.77 and 304.44 mm. Bottom rollers
  (carriage-bottom `Sketch013` `roller_y` = 34 mm): x = 155.60 and 267.60 mm. So a = 36.833 mm,
  b = 112 mm.
- Heights: base top z = 40, carriage-bottom top z = 51.5, carriage-top ceiling z = 53.5.
  Roller centres 3.5 mm inside each part: bottom z = 48, top z = 44. Bottom roller top
  z = 53, so lift = 13 mm and dz = 13 − D − t = 2.85 mm. Carriage underside input 13.5 mm.
- Strip width 186 mm: the slope opening of the carriage, as in the scraper-fit case.
- `boundedQP()` in `strip_model.js`: after 200 steps that change every wrong set at once, it
  changes only the worst one per step. Before 200 steps it works as before, so all old results
  stay the same. It cycled at 30 N/mm in the screw curve.
- `node simulation/cases/strip-seal-designer/check_model.mjs`: all checks pass. The page was
  loaded in Chromium: no errors, 54.3 N at 3.27 mm.
- Length between clamps stays 1000 mm; the clamps have no geometry. 440 mm gives 3.26 mm for
  54 N, 2000 mm gives 3.28 mm.
- Mistake rules checked: the fatigue mistake (the 903 MPa limit at 0.15 mm is marked as an
  extrapolation), the page mistakes (no server, no cached model), the tooling update rule.

</details>
