# 2026-10-28 — Seal strip page updated to the current carriage, with the channel and friction

**Role(s):** engineering, simulation, software

## Goal

Niels Bosmans asked to update the seal strip design page with the current roller places from
the CAD, the current strip width, and a strip 0.15 mm thick. After the first results he asked to
add the ceiling of carriage-top to the model, with a plastic strip on it, and the friction from
this contact for several plastics. The rollers stick out only 0.5 mm from each carriage half.

## Short answer

- **The page now models the real path of the strip.** The strip runs in a 2 mm channel between
  the two carriage halves, over the slopes and under the flat ceiling. Rollers 1–2 are 36.83 mm
  apart, rollers 2–3 112 mm. Rollers 2 and 3 lift the strip 12 mm. The strip is 0.15 mm thick
  and 186 mm wide.
- **The strip lies against the plastic strip on the ceiling at every useful pull.** With 0.5 mm
  of plastic, it presses on it with about 29 N at 54 N.
- **The friction on the carriage is small with PTFE: 2 to 7 N at 54 N.** UHMW-PE gives 5 to
  10 N, POM-C 10 to 14 N, PA6 12 to 18 N. With no pull it is higher (11 to 16 N with PTFE),
  because the strip then also presses on the bottom carriage.
- **A thinner plastic strip presses less.** At 54 N the normal force is 20 N at 0.25 mm, 29 N at
  0.5 mm, 73 N at 1 mm.
- **The screw now sets the pull with almost no travel.** 0.03 mm gives 54 N, and 0.27 mm gives
  400 N. The channel holds the strip, so tightening the screw mostly stretches the steel. The arch
  height can no longer be the gauge for the pull.
- **No fatigue limit is reached at 54 N.** The highest stress is 586 MPa.
- **The contact solver is now robust.** It stopped in some cases with the new layout. A slower
  method now takes over when the fast one goes round in a circle.

## Work Done

- Read the roller places and the shape of both carriage surfaces from carriage-bottom and
  carriage-top, placed as in the assembly.
- Added the channel to the model: the slopes and the flat top of carriage-bottom, the slope and
  the flat ceiling of carriage-top, and a plastic strip of a chosen thickness on the ceiling.
- Added the friction on the carriage, with friction values from data sheets for four plastics.
  The page shows it in a new tile and in the force table.
- Updated the case README with the new inputs, the sources and the results.

Full tables: [case README](../../simulation/cases/strip-seal-designer/README.md#results-at-the-defaults).

## Decisions Made

No design decision. The 0.5 mm plastic strip and PTFE are only the starting values on the page.

## Open Questions

- **How should the pull be set and checked?** 54 N needs only 0.03 mm of screw travel, which is
  too little to set by turning a screw. A spring or a force gauge at the clamp may be needed.
- **Which plastic, and how thick?** PTFE gives the lowest friction. A thinner strip presses less.
  The friction values come from tests at much higher pressure, so measure them on a sample.
- **What holds the strip down at rollers 1 and 4?** The page assumes magnet strips under the
  strip there. In the CAD, the top rollers sit over the slot of the base.

## Next Steps

- [ ] Choose the plastic and its thickness, and draw it in carriage-top.
- [ ] Choose how to set the pull: screw, spring or force gauge.
- [ ] Measure the friction of the strip on a plastic sample.
- [ ] Draw the rollers and axles in CAD.

<details>
<summary>Technical notes</summary>

- Geometry read from the `.FCStd` files with `cadquery-ocp`, no FreeCAD. Placements from the
  assembly: carriage-bottom at (301.603, 1, 24) mm turned 90°, carriage-top at
  (211.603, 105, 40.5) mm.
- Top rollers (carriage-top `Pocket003`, `Pocket006`): x = 118.77 and 304.44 mm. Bottom rollers
  (carriage-bottom `Sketch013` `roller_y` = 34 mm): x = 155.60 and 267.60 mm. So a = 36.833 mm,
  b = 112 mm.
- Surfaces, sampled across y = 13 to 197 mm: carriage-top underside z = 40.5 + 0.353 (x − 118.77)
  from x = 118.77 to 147.15, then a step to the flat ceiling at z = 53.5. Carriage-bottom top
  z = 51.5 − 0.353 (155.6 − x) up to x = 155.6, then flat at 51.5. Base top z = 40. Slope
  12/34 = 19.44°.
- Roller stick-out 0.5 mm: roller 2 top z = 52, so lift = 12 mm and dz = 12 − D − t = 1.85 mm.
- `strip_model.js`: `channel(p)` gives the ceiling and floor heights; `shape()` adds them as
  bounds (owners 4 carriage-top bare, 5 liner, 6 carriage-bottom) and returns `carriageForces`
  with the normal force; `carriageFriction()` sums mu × N × width. `LINERS` and `MU_ALU` hold
  the friction values and sources.
- `boundedQP()`: 200 steps of the old all-at-once active set method, then `boundedQPSafe()`, a
  primal active set method with a step length. It keeps a bound that its release would put
  straight back (a rounding effect), and its force tolerance is 1e-12 times the largest diagonal
  of the matrix.
- Contact forces on a 0.05 mm grid: 29.0 N on the plastic and 2.4 N on carriage-bottom, against
  28.9 N and 1.9 N on the 0.1 mm grid.
- `node simulation/cases/strip-seal-designer/check_model.mjs`: all checks pass, with new checks
  that the strip stays in the channel and that the forces add up to zero. The page was loaded in
  Chromium with no errors.
- Friction sources: Engineering ToolBox (PTFE on steel 0.05–0.2; aluminium on mild steel 0.47
  kinetic); mcam data sheets, ISO 7148-2 pin-on-disk at 3 MPa and 0.33 m/s: TIVAR 1000 0.15–0.30,
  Acetron C POM-C 0.3–0.45, Ertalon 6 SA PA6 0.4–0.6.
- Mistake rules checked: the fatigue mistake (no material value without a source; the 903 MPa
  limit at 0.15 mm is marked as an extrapolation), the page mistakes (no server, no cached model),
  the tooling update rule.

</details>
