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
| Thickness | 0.25 mm | |
| Width | 150 mm | Forces are per mm of width, times this |
| Length between clamps | 1000 mm | Only used for the steel stretch |
| Roller diameter | 10 mm | |
| Distance 1–2 and 3–4 | 26.2 mm | Centre to centre, along the strip |
| Distance 2–3 | 119 mm | Centre to centre |
| Height 2/3 above 1/4 | −4.25 mm | Centre to centre. Negative: 2/3 sit lower. The strip lift is this plus D plus t, so 6 mm |
| Carriage underside | 15.75 mm | Above the profile. Only drawn, to see if the arch touches it |
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

## Results at the defaults

301, 0.25 mm, 150 mm wide, 1000 mm between the clamps, magnet stiffness 20 N/mm³:

| Screw travel | Pull | Arch height ¹ | Tightest radius | Highest stress | Roller 1 | Roller 2 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 mm | 0 N | 8.85 mm | 39.7 mm | 583 MPa | 371 N | 46 N |
| 0.5 mm | 17 N | 7.30 mm | 37.8 mm | 612 MPa | 397 N | 55 N |
| 1.0 mm | 51 N | 5.42 mm | 35.3 mm | 657 MPa | 437 N | 70 N |
| 1.25 mm | 87 N | 4.30 mm | 33.5 mm | 692 MPa | 470 N | 83 N |
| 1.5 mm | 169 N | 2.99 mm | 31.0 mm | 750 MPa | 529 N | 110 N |
| 1.75 mm | 439 N | 1.58 mm | 26.7 mm | 877 MPa | 656 N | 190 N |

¹ From a straight edge on the tops of rollers 2 and 3 to the underside of the strip, at its
highest point. Zero when the strip runs flat over the two rollers.

- **About 1 mm of screw travel gives the 54 N target.** The strip length hardly matters: 1.03 mm
  at 500 mm and 1.04 mm at 2000 mm. The arch takes almost all the travel, the steel stretch very
  little.
- **Past about 1.3 mm the pull rises fast,** because the arch is nearly flat and the steel has to
  stretch. The screw travel must stop well before that.
- **The arch height is a good gauge.** Near 54 N it drops about 0.4 mm per 10 N. A depth gauge
  on a straight edge across the tops of rollers 2 and 3 can read that.
- **The arch comes close to the carriage.** At zero pull its top is 14.98 mm above the profile,
  0.77 mm under the carriage underside.
- **Rollers 1 and 4 carry the most force, and it comes from the pinch, not the pull.** At 54 N it
  is 310 N at 5 N/mm³, 440 N at 20 N/mm³ and 1140 N at 1000 N/mm³. Rollers 2 and 3 carry about
  70 N.
- **Fatigue life has no limit at 54 N** for 301 at 0.25 mm (660 MPa against 775 MPa). With the
  plate factor it is about 725 MPa, still under.

## What the model leaves out

- Friction on the magnets. The pull is taken as equal along the whole strip.
- The carriage near a clamp. The pull is taken as independent of the carriage position.
- Friction on the rollers.
- Measured magnet stiffness and pull. Both are estimates. Measure them, or use the range.
- Measured fatigue data for 304 strip. No maker publishes it.

## GitHub Pages setup

Once, by a repository admin: **Settings → Pages → Build and deployment → Source: GitHub
Actions.** After that, every push to `main` that changes this folder runs
[`pages.yml`](../../../.github/workflows/pages.yml), which runs the checks and publishes
`index.html` and `strip_model.js` only.
