# strip-seal-designer

A web page to design the seal strip: how it bends over the four carriage rollers, the force on
each roller, the stress, the fatigue life, and what the countersunk preload screw does.

**Open it:** <https://refaqt.github.io/aqtuator/strip-seal/> (after the one-time Pages setup
below). No server and no install. It runs in the browser.

**Tool:** plain HTML and JavaScript. The checks need Node 18 or newer, no packages.

```bash
node simulation/cases/strip-seal-designer/check_model.mjs
```

To run the page from a local clone, serve the folder, because browsers block modules opened
straight from disk:

```bash
python3 -m http.server -d simulation/cases/strip-seal-designer 8000
# then open http://localhost:8000
```

Log: [2026-09-28](../../../docs/log/2026-09-28_strip-seal-designer.md).
Earlier cases: [`strip-seal-preload`](../strip-seal-preload/) (the solver this page ports) and
[`strip-seal-fatigue`](../strip-seal-fatigue/) (materials, rainflow and fatigue rules).

## Inputs

| Input | Default | Note |
| --- | --- | --- |
| Material | SS 301 | 301 is Alleima 11R51, measured. 304 fatigue is an estimate range |
| Thickness | 0.15 mm | |
| Width | 186 mm | The widest strip that fits through the carriage. Forces are per mm of width, times this |
| Length between clamps | 1000 mm | Only used for the steel stretch |
| Roller diameter | 10 mm | |
| Distance 1–2 and 3–4 | 36.83 mm | Centre to centre, along the strip. From the CAD, see below |
| Distance 2–3 | 112 mm | Centre to centre. From the CAD |
| Height 2/3 above 1/4 | 2.85 mm | Centre to centre. The strip lift is this plus D plus t, so 13 mm |
| Carriage underside | 13.5 mm | Above the profile. Only drawn, to see if the arch touches it |
| Magnet strip stiffness | 20 N/mm³ | Estimate. See below |
| Magnet pull | 0.005 N/mm² | Estimate |
| Screw travel | 0.5 mm | How far the strip end moves after it lies on the rollers with no pull |

## What the model does

The strip is a thin beam under a pull. The page finds the shape with the lowest energy: bending
energy plus the work of the pull, with the exact curvature. This is `shape()` from
`strip-seal-preload`, ported to JavaScript with a banded solver. `check_model.mjs` compares it
with the Python solver (file `reference.json`) and with the closed form for two point supports.
They agree to three decimals.

Two things are new compared with the Python case:

- **The magnet strips are an elastic bed.** Rollers 1 and 4 press the strip on the magnets. With
  a rigid profile the strip is pinned there at one point, and the force on roller 1 then grows
  without end as the grid gets finer (80 N/mm at 0.1 mm, 160 N/mm at 0.05 mm). The shape was
  right, the force was not. An elastic bed spreads the pinch over about (EI/k)^¼, 2 mm at the
  default, and the force no longer depends on the grid. The stiffness is not measured. It sets
  the force on rollers 1 and 4 and also opens the tightest radius.
- **Screw preload.** The strip is fitted with loose screws and lies over the rollers with no
  pull. A screw travel u must then be taken up by a flatter arch and by stretching the steel:

  `u = extra(0) − extra(T) + L·T / (E·t)`

  The page samples the pull T on a grid, builds the curves u → T and T → arch height, and reads
  the answer off them.

Forces on each roller come from the contact reactions of the solver, split along the line from
the roller centre to the contact point. The vertical forces of the rollers and the magnets add up
to zero, which the check script tests.

Fatigue: rainflow of the bending stress one point sees in one carriage crossing, the pull added
to the mean, Goodman, and the Basquin line through 0.9 Rm at 10³ and the fatigue limit at 2·10⁶,
as in `strip-seal-fatigue`.

## Where the defaults come from

The roller places come from the compact-stage CAD of 2026-10-28 (carriage-bottom and carriage-top,
placed as in the assembly). Rollers 1 and 4 sit in carriage-top, rollers 2 and 3 in
carriage-bottom.

| Size | Value | From |
| --- | --- | --- |
| Roller 1 and 4, along the travel | 92.83 mm from the carriage middle | On the low edge of the slanted faces of carriage-top |
| Roller 2 and 3, along the travel | 56 mm from the carriage middle | On the slope edge of carriage-bottom, 34 mm from its ends |
| Top of rollers 2 and 3 | 13 mm above the top of the base | Carriage-bottom top at 11.5 mm, roller sticks out 1.5 mm |
| Carriage-top ceiling over the strip | 13.5 mm above the top of the base | 2 mm gap between the two carriage halves |
| Strip width | 186 mm | The widest strip through the slope opening of the carriage |

- **The roller heights are an assumption.** The rollers and their axles have no part in CAD yet.
  As in the scraper and roller pocket work, each roller centre is taken 3.5 mm inside its
  carriage half, so each roller sticks out 1.5 mm.
- **The page puts roller 1 and 4 on the strip, with the strip on the base.** The CAD
  assumption puts the top rollers 1.15 mm lower than that. The page cannot show this.
- **The strip length of 1000 mm is the old value.** The clamps have no part in CAD yet. The
  length hardly changes the result: 3.26 mm of screw travel for 54 N at 440 mm, 3.28 mm at
  2000 mm.

## Results at the defaults

301, 0.15 mm, 186 mm wide, 1000 mm between the clamps, magnet stiffness 20 N/mm³:

| Screw travel | Pull | Arch height ¹ | Tightest radius | Highest stress | Roller 1 | Roller 2 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 mm | 0 N | 12.10 mm | 35.5 mm | 391 MPa | 155 N | 11 N |
| 1 mm | 4 N | 10.10 mm | 33.2 mm | 417 MPa | 167 N | 13 N |
| 2 mm | 12 N | 7.54 mm | 30.2 mm | 460 MPa | 179 N | 18 N |
| 3 mm | 35 N | 4.50 mm | 25.9 mm | 537 MPa | 220 N | 29 N |
| 3.27 mm | 54 N | 3.44 mm | 23.8 mm | 584 MPa | 245 N | 38 N |

¹ From a straight edge on the tops of rollers 2 and 3 to the underside of the strip, at its
highest point. Zero when the strip runs flat over the two rollers.

- **The free arch does not fit under carriage-top.** There is only 0.35 mm between the top of
  rollers 2 and 3 and the ceiling of carriage-top. At 54 N the arch wants to rise 3.44 mm. The
  strip will press on the ceiling of carriage-top over the middle of the carriage. To keep the
  arch under 0.35 mm, the pull must be about 1750 N, which is not practical. The model has no
  ceiling, so the shape and forces between rollers 2 and 3 are not real while it touches.
- **About 3.3 mm of screw travel gives the 54 N target** (was about 1 mm with the old layout).
  The higher lift and the thinner strip make the arch take more travel.
- **Rollers 1 and 4 carry about 250 N at 54 N, rollers 2 and 3 about 38 N.** As before, the
  large force comes from the pinch on the magnets: 176 N at 5 N/mm³ and 610 N at 1000 N/mm³.
- **Fatigue life has no limit at 54 N** for 301 at 0.15 mm: 584 MPa (641 MPa with the plate
  factor). The fatigue limit at 0.15 mm, 903 MPa, is an extrapolation below the measured
  0.25 mm. The highest stress is also under the measured 775 MPa at 0.25 mm.

Results for the old layout (26.2 mm, 119 mm, lift 6 mm, 0.25 mm × 150 mm) are in the
[2026-09-28 log](../../../docs/log/2026-09-28_strip-seal-designer.md).

## What the model leaves out

- Friction on the magnets. The pull is taken as equal along the whole strip.
- The carriage near a clamp. The pull is taken as independent of the carriage position.
- Friction on the rollers.
- Measured magnet stiffness and pull. Both are estimates. Measure them, or use the range.
- Measured fatigue data for 304 strip. No maker publishes it.
- The ceiling of carriage-top and the top of carriage-bottom. The strip can pass through both.
- What is under the strip at rollers 1 and 4. The page assumes magnet strips there. In the CAD,
  the top rollers sit over the slot of the base, where nothing supports the strip.

## GitHub Pages setup

Once, by a repository admin: **Settings → Pages → Build and deployment → Source: GitHub
Actions.** After that, every push to `main` that changes this folder runs
[`pages.yml`](../../../.github/workflows/pages.yml), which runs the checks and publishes
`index.html` and `strip_model.js` only.
