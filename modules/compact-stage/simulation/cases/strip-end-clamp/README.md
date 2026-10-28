# strip-end-clamp

Builds the clamp that holds each end of the seal strip (version 3), checks that it fits beside
the scraper, the carriage and the end stop dampers, and runs the strip model for the 0.15 mm
strip in the real carriage.

The clamp is one insert per strip end. The insert clamps the strip between its flange on top and
a square nut below. The nut slides in a groove milled from the top into the end wall of the base,
and its flat sides stop it from turning. A countersunk screw goes straight down into the groove
floor. Its hole sits a little nearer the stage middle than the countersink in the insert, so the
cone of the head pulls the insert, and the strip, towards the base end.

The case reads the compact-stage CAD files and places each part where the assembly puts it. It
does not need FreeCAD and it never changes a CAD file. The groove, the strip, the insert, the nut
and the screw exist in memory only. It reuses the readers and the scraper of
[`scraper-fit`](../scraper-fit/), and the strip solver of the
[seal strip designer page](../../../../../simulation/cases/strip-seal-designer/).

## Running

Run from the repository root:

```bash
git lfs pull --include="modules/compact-stage/cad/**"
pip install cadquery-ocp numpy matplotlib shapely
python modules/compact-stage/simulation/cases/strip-end-clamp/run.py
```

It needs Node 18 or newer for the strip model. The run takes about one minute.

The script stops with `FAILED` if the groove or the hole breaks into a hollow part of the base, if
two of the new parts overlap, if anything sticks out past the end of the base, or if the scraper or
carriage-top hits the clamp before the dampers start to press in. With the dampers fully pressed
in, it only reports the overlaps, and it checks that a longer pocket in carriage-top clears them.

## Files

| File | What it does |
| --- | --- |
| `run.py` | Runs the fit checks and the strip model, then draws all figures |
| `clamp.py` | All sizes of the groove, the insert, the nut, the screw and the stepped scraper lips, and the 3D shapes |
| `strip_pull.mjs` | The strip model: bow, force on carriage-top, and travel against pull |
| `fig_common.py` | Colours and drawing helpers shared by the figures |
| `fig_sections.py`, `fig_top_view.py`, `fig_strip_model.py` | The figures |

## What is assumed

- Only the end at x = 0 is built. The end at x = 440 mm is the same, mirrored.
- The seal strip is 0.15 mm thick and 186 mm wide (y = 12 to 198 mm), and 430 mm long between the
  two inserts.
- The carriage positions come from the log of the damper pockets: the end face of carriage-top is
  5 mm from the base end at the end of the usable travel, 4 mm at the first damper touch, and 3 mm
  past it with the dampers fully pressed in.
- The screw is ISO 14581 M2.5 × 8. The insert has an M6 × 0.5 thread and a Ø9 × 1 mm flange.
- The strip model uses the carriage faces at y = 105 mm. It takes the bottom rollers as standing
  1.5 mm proud of carriage-bottom, the same as the top rollers below carriage-top. It takes the top
  rollers as raised, so they just touch the strip. Neither roller is in the CAD yet.
- The magnet strips are the estimates of the designer page: 20 N/mm³ and 0.005 N/mm².
