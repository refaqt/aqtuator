# strip-end-clamp

Builds the clamp that holds each end of the seal strip (version 2), and checks that it fits
beside the scraper, the carriage and the end stop dampers. The strip lies flat over the end wall
of the base and bends down into three steps milled from the top. In each step, the tab hangs on
the pins of a bar, and two vertical screws pull the bar down. Turning the screws sets the pull.
Everything is reached and machined from the top. Nothing stands above the top of the base, and
nothing sticks out past its end.

The case reads the compact-stage CAD files and places each part where the assembly puts it. It
does not need FreeCAD and it never changes a CAD file. The steps in the base, the strip, the
bars, the pins and the screws exist in memory only. It reuses the readers and the scraper of
[`scraper-fit`](../scraper-fit/).

## Running

Run from the repository root:

```bash
git lfs pull --include="modules/compact-stage/cad/**"
pip install cadquery-ocp numpy matplotlib shapely
python modules/compact-stage/simulation/cases/strip-end-clamp/run.py
```

The script stops with `FAILED` if a step or a hole breaks into a hollow part of the base, if two
of the new parts overlap, if anything sticks out past the end or above the top of the base, if
the bar has no room to move, or if the carriage or the scraper hits the strip or the clamp. It
also reports how far the top rollers reach into the base and the strip. Those numbers do not stop the script, because the rollers are a known open point.
It writes the figures to [`../../results/strip-end-clamp/`](../../results/strip-end-clamp/).

## Files

| File | What it does |
| --- | --- |
| `run.py` | Runs the fit checks, then draws all figures |
| `clamp.py` | All sizes of the steps, the strip end, the bars, the pins and the screws, and the 3D shapes |
| `fig_common.py` | Colours and drawing helpers shared by the figures |
| `fig_sections.py`, `fig_top_view.py`, `fig_strip.py` | The figures |

## What is assumed

- Only the end at x = 0 is built. The end at x = 440 mm is the same, mirrored. The base is the
  same at both ends.
- The seal strip is 0.25 mm thick and 186 mm wide (y = 12 to 198 mm), as in `scraper-fit`. The
  strip lies flat on the base. The case does not model how the rollers bend it.
- The carriage positions come from the log of the damper pockets: the end face of carriage-top is
  5 mm from the base end at the end of the usable travel, and 3 mm past it with the dampers fully
  pressed in.
- The screws are ISO 4762 M3 × 16 with a thread locking patch. The pins are ISO 8734 dowels,
  2 × 4 mm. The bar is drawn at its nominal height; in use it moves with the pull.
