# brass-tpu-scraper

Sketches and fit checks for the scraper that Niels Bosmans drew on 2026-11-10. Each end of
carriage-top gets a brass block at the front and a printed TPU wiper behind it. The brass keeps a
0.15 mm gap to the seal strip. The TPU presses on the strip with two thin lips.

The case reads the compact-stage CAD files (base, carriage-top, carriage-bottom, the preloaded
seal strip and the assembly with the strip corner screws) and places each part where the assembly
puts it. It builds the new pocket, holes and parts in memory only. It does not need FreeCAD and it
never changes a CAD file. It reuses the readers and drawing helpers of
[`scraper-fit`](../scraper-fit/).

## Running

Run from the repository root:

```bash
git lfs pull --include="modules/compact-stage/cad/**"
pip install cadquery-ocp numpy matplotlib shapely
python modules/compact-stage/simulation/cases/brass-tpu-scraper/run.py
```

The run takes about 1.5 minutes. It stops with `FAILED` if the brass, the TPU, the bolts, the
plungers or the pull screws overlap carriage-top, carriage-bottom, the base, the strip or a top
roller, or if any part passes over a strip corner screw head before the first damper touch.
It writes the results to [`../../results/brass-tpu-scraper/`](../../results/brass-tpu-scraper/).

## Files

| File | What it does |
| --- | --- |
| `design.py` | All sizes, and the 3D shapes of the pocket, the brass, the TPU and the screws |
| `checks.py` | The fit checks and the measured gaps and walls |
| `figs.py` | The figures |
| `run.py` | Runs the checks, writes `fit_checks.json`, then draws all figures |

## What is assumed

- Only the start end is built. The other end is the same, turned 180°.
- The top rollers are Ø10 × 20 mm cylinders that rest on the strip, as in the assembly.
- The corner screw head is the ISO 7380-2 M4 shape from the assembly (Ø10.17 mm, 2.2 mm high).
  The carriage end face stops 4 mm from the base end at the first damper touch, 5 mm at the end
  of the usable travel, and 3 mm past it with the dampers fully pressed (log of the damper
  pockets).
- The spring plunger is drawn as an M4 body, 10 mm long, with a Ø2 pin. The real MISUMI part
  and its length are not chosen yet.
- The TPU lips are drawn free, before they touch the strip. How they bend under the 0.4 mm
  press-in is not modelled.
