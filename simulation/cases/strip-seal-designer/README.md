# strip-seal-designer

A web page to design the seal strip: how it bends over the four carriage rollers and through the
channel between the two carriage halves, the force on each roller, the friction on the carriage,
the stress, the fatigue life, and what the countersunk preload screw does.

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

Logs: [2026-09-28](../../../docs/log/2026-09-28_strip-seal-designer.md),
[2026-10-28](../../../docs/log/2026-10-28_strip-seal-designer-current-layout.md).
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
| Height 2/3 above 1/4 | 1.85 mm | Centre to centre. The strip lift is this plus D plus t, so 12 mm |
| Strip runs between the carriage halves | on | Off: a free strip, as before 2026-10-28 |
| Roller stick-out | 0.5 mm | How far each roller sticks out of its carriage half |
| Slope of the halves | 19.44° | 12 mm over 34 mm, the same on both halves |
| Carriage-top ceiling | 13.5 mm | Above the profile |
| Flat ceiling starts | 8.45 mm | Outside rollers 2 and 3. Between there and roller 1 the ceiling is the slope |
| Plastic strip on the ceiling | 0.5 mm | Thickness. 0 means bare aluminium |
| Width of the plastic strip | 10 mm | Along the strip, centred between rollers 2 and 3. 0 means bare aluminium |
| Plastic | PTFE | PTFE, UHMW-PE, POM-C or PA6. Sets the friction, see below |
| Magnet strip stiffness | 20 N/mm³ | Estimate. See below |
| Magnet pull | 0.005 N/mm² | Estimate |
| Screw travel | 0.03 mm | How far the strip end moves after it lies on the rollers with no pull |

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

Walls can be added as obstacles (`opts.walls`), for example the faces of the two carriage halves
around the strip. Their forces on the strip come back in `wallF`. The page does not use them yet.
The [`strip-pull`](../../../modules/compact-stage/simulation/cases/strip-pull/) case does.

The option `stick23` sets the stick-out of rollers 2 and 3 alone, for rollers that go down while
carriage-bottom stays. Below zero, the roller sits under the flat top of carriage-bottom. Without
it, both halves use `stick`. The page does not use it. The
[`strip-seal-fit`](../../../modules/compact-stage/simulation/cases/strip-seal-fit/) case does.

Forces on each roller come from the contact reactions of the solver, split along the line from
the roller centre to the contact point. The vertical forces of the rollers, the magnets and the
carriage add up to zero, which the check script tests.

**The carriage channel.** Between rollers 1 and 4 the strip runs between the two carriage halves.
The top of carriage-bottom (its slope, then its flat top) is a floor. The underside of
carriage-top (its slope, then its flat ceiling) is a ceiling. The plastic strip is a short pad
on that flat ceiling, in the middle between rollers 2 and 3. It hangs down by its thickness and
pushes the strip down there. Beside the pad the ceiling is bare aluminium. The strip
may touch them but not pass through them, in the same way as it touches the rollers. The force
of each surface on the strip is along the surface normal.

**Friction.** The rollers roll and add no friction. Where the strip touches a carriage surface,
it slides when the carriage moves. The friction is the friction coefficient times the normal
force, added over all the contacts and both sides of the carriage. The page gives a range from
the range of the coefficient.

| Surface | Friction on steel, dry | Source |
| --- | --- | --- |
| PTFE, unfilled | 0.05–0.20 | [Engineering ToolBox](https://engineeringtoolbox.com/friction-coefficients-d_778.html), PTFE on steel, clean and dry |
| UHMW-PE (TIVAR 1000) | 0.15–0.30 | [mcam data sheet](https://mcam.com/mam/51243/Bronymec-PE-TIVAR%C2%AE%201000%20UHMW-PE%20colors_en_US.pdf), ISO 7148-2 (0.12 by QTM 55007) |
| POM-C (Acetron C) | 0.30–0.45 | [mcam data sheet](https://www.mcam.com/mam/54384/GEP-Acetron%E2%84%A2%20C%20Sterra%E2%84%A2%20POM-C%20_en_US.pdf), ISO 7148-2 (0.25 by QTM 55007) |
| PA6 (Ertalon 6 SA) | 0.40–0.60 | [mcam data sheet](https://mcam.com/mam/51011/Bronymec-GEP-Ertalon%C2%AE%206%20SA%20PA6_en_US.pdf), ISO 7148-2 |
| Bare aluminium (the slopes) | 0.47 | [Engineering ToolBox](https://engineeringtoolbox.com/friction-coefficients-d_778.html), aluminium on mild steel, kinetic |

The mcam values come from a pin-on-disk test at 3 MPa and 0.33 m/s. The strip presses on the
plastic far more lightly than that, so the real value can differ. Measure it before you rely on
it.

**The solver.** The contact solver changes every wrong contact at once. That is fast, but in
the narrow channel it can go round in a circle. Then a slower method takes over. It moves only
as far as the first new contact and lets go of one contact at a time, so it always ends. A
solve takes up to about a second.

Fatigue: rainflow of the bending stress one point sees in one carriage crossing, the pull added
to the mean, Goodman, and the Basquin line through 0.9 Rm at 10³ and the fatigue limit at 2·10⁶,
as in `strip-seal-fatigue`.

## Where the defaults come from

The roller places come from the compact-stage CAD of 2026-10-28 (carriage-bottom and carriage-top,
placed as in the assembly). Rollers 1 and 4 sit in carriage-top, rollers 2 and 3 in
carriage-bottom.

| Size | Value | From |
| --- | --- | --- |
| Roller 1 and 4, along the travel | 92.83 mm from the carriage middle | On the low edge of the slope of carriage-top |
| Roller 2 and 3, along the travel | 56 mm from the carriage middle | On the high edge of the slope of carriage-bottom, 34 mm from its ends |
| Roller stick-out | 0.5 mm | Niels Bosmans, 2026-10-28. The rollers have no part in CAD yet |
| Top of rollers 2 and 3 | 12 mm above the top of the base | Carriage-bottom top at 11.5 mm, plus 0.5 mm |
| Slopes | 19.44°, 2 mm apart vertically | Both halves, measured in the CAD |
| Carriage-top ceiling | 13.5 mm above the top of the base | Flat from 8.45 mm outside rollers 2 and 3. There the slope stops with a 3 mm step |
| Strip width | 186 mm | The widest strip through the slope opening of the carriage |

- **The page puts rollers 1 and 4 on the strip, with the strip on the base.** In the CAD their
  bottom is at the top of the base, so 0.15 mm (one strip thickness) lower. The page cannot show
  this.
- **The plastic strip is 0.5 mm thick and 10 mm wide here as an example.** Both are inputs. It
  leaves 0.85 mm of room above rollers 2 and 3. A pad thicker than 1.85 mm leaves less room than
  the strip thickness above carriage-bottom, so it clamps the strip.
- **The strip length of 1000 mm is the old value.** The clamps have no part in CAD yet. It hardly
  matters for the pull: 0.024 mm of screw travel for 54 N at 440 mm, 0.040 mm at 2000 mm.

## Results at the defaults

301, 0.15 mm, 186 mm wide, 1000 mm between the clamps, magnet stiffness 20 N/mm³, a PTFE pad of
0.5 mm × 10 mm on the ceiling:

| Pull | Screw travel | Tightest radius | Highest stress | Roller 1 | Roller 2 | Normal force on the pad | Normal force on bare carriage-top | Normal force on carriage-bottom | Friction, PTFE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 N | 0 mm | 24.5 mm | 566 MPa | 229 N | 23 N | 2 N | 18 N | 26 N | 21.0–21.3 N |
| 20 N | 0.010 mm | 24.2 mm | 575 MPa | 237 N | 29 N | 3 N | 15 N | 20 N | 16.3–16.8 N |
| 54 N | 0.027 mm | 23.5 mm | 591 MPa | 250 N | 41 N | 4 N | 9 N | 8 N | 8.5–9.1 N |
| 100 N | 0.064 mm | 22.1 mm | 631 MPa | 278 N | 55 N | 6 N | 2 N | 0 N | 1.0–1.9 N |
| 200 N | 0.187 mm | 18.7 mm | 751 MPa | 342 N | 90 N | 4 N | 0 N | 0 N | 0.2–0.9 N |
| 400 N | 0.325 mm | 15.2 mm | 924 MPa | 472 N | 158 N | 0 N | 0 N | 0 N | 0.0 N |

Friction at 54 N, by plastic: PTFE 8.5–9.1 N, UHMW-PE 8.9–9.5 N, POM-C 9.5–10.1 N, PA6
9.9–10.8 N. The plastic matters little, because most of the friction is steel on aluminium.

- **A 0.5 mm pad does not keep the strip off the aluminium.** The arch between rollers 2 and 3
  wants to rise about 11 mm, and the ceiling stops it at 1.35 mm. At 54 N the strip touches the
  pad at its two edges, and also the bare ceiling about 18 mm in from rollers 2 and 3
  (9 N), and carriage-bottom (8 N).
- **A thicker pad takes over the ceiling contact.** At 54 N, with a 10 mm wide pad, the bare
  ceiling carries 9 N at 0.5 mm, 4 N at 1 mm, 2 N at 1.25 mm and nothing from 1.5 mm. Then the
  PTFE friction is 4.8 to 6.4 N. From about 1.8 mm the pad starts to pinch the strip on carriage-bottom.
- **The width of the pad matters less than its thickness.** At 54 N and 0.5 mm, the friction is
  8.6 to 9.2 N at 5 mm wide, 8.0 to 8.7 N at 20 mm and 5.4 to 6.9 N at 40 mm. With no pad it is
  10.5 N.
- **The screw sets the pull with very little travel.** 54 N needs only 0.027 mm, and 0.33 mm
  gives 400 N. The channel holds the strip, so tightening the screw mostly stretches the steel.
  The arch can not be the gauge for the pull, because it stays on the ceiling. Set the pull
  another way, for example with a spring or a force gauge at the clamp.
- **Rollers 1 and 4 carry about 250 N at 54 N, rollers 2 and 3 about 41 N.** The force on rollers
  1 and 4 comes from the pinch on the magnets: 175 N at 5 N/mm³ and 670 N at 1000 N/mm³.
- **Fatigue life has no limit at 54 N** for 301 at 0.15 mm: 591 MPa (650 MPa with the plate
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
- How friction on the carriage changes the pull along the strip. The pull is taken as the same
  on both sides of the carriage.
- The roller pockets in the carriage surfaces. The strip is wide, so the surfaces next to the
  pockets hold it.
- What is under the strip at rollers 1 and 4. The page assumes magnet strips there. In the CAD,
  the top rollers sit over the slot of the base, where nothing supports the strip.

## GitHub Pages setup

Once, by a repository admin: **Settings → Pages → Build and deployment → Source: GitHub
Actions.** After that, every push to `main` that changes this folder runs
[`pages.yml`](../../../.github/workflows/pages.yml), which runs the checks and publishes
`index.html` and `strip_model.js` only.
