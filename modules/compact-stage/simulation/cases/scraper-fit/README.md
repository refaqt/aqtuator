# scraper-fit

Builds the printed scraper that sits at each end of carriage-top, and checks that it fits.
The scraper keeps chips off the seal strip before the strip goes under the carriage.

The case reads the compact-stage CAD files (base, carriage-bottom, carriage-top and the
assembly) and places each part where the assembly puts it. It does not need FreeCAD and it never
changes a CAD file. It adds a pocket to carriage-top in memory only.

## Running

Run from the repository root:

```bash
git lfs pull --include="modules/compact-stage/cad/**"
pip install cadquery-ocp numpy matplotlib shapely
python modules/compact-stage/simulation/cases/scraper-fit/run.py
```

The script stops with `FAILED` if the scraper overlaps carriage-top, carriage-bottom or the base.
It writes the figures to [`../../results/scraper-fit/`](../../results/scraper-fit/).

## Files

| File | What it does |
| --- | --- |
| `run.py` | Runs the fit checks, then draws all figures |
| `scraper.py` | All sizes of the scraper and the pocket, and the 3D shapes |
| `fcstd_shapes.py` | Reads the shapes out of the `.FCStd` files and places them |
| `render.py` | Cuts sections and fills them, for the figures |
| `fig_sections.py`, `fig_drawing.py`, `fig_3d.py` | The figures |

## What is assumed

- The seal strip is 0.25 mm thick and lies flat on the top of the base, at z = 40 mm. It has no
  geometry in CAD yet. The checks use a strip 186 mm wide (y = 12 to 198 mm), the widest strip
  that fits through the slope opening of the carriage.
- Only the start end is built. The end at the other side is the same part, turned 180°.
