# strip-end-insert

Checks the strip end concept of Niels Bosmans (2026-10-28) against the CAD, with corner pockets in
carriage-top, stepped scraper lips and a spring end, and models how the pull spreads across the
strip. His drawing, with notes, is in
[the log of 2026-10-28](../../../../../docs/log/2026-10-28_strip-end-clamp-and-preload.md).

The concept: each strip end has two inserts, one near each side edge. An insert sits in a hole in
the strip, with no thread and no nut. A countersunk screw presses it into the hole. At the fixed
end, two flat faces on the insert slide in a small groove in the base, and the screw hole sits a
little nearer the base end than the insert when the strip is laid loose. Tightening the screw
centres the insert on it and pulls the strip. At the spring end, the insert is screwed onto a
slider that a compression spring pushes towards the base end. Magnets in pockets hold the strip
down.

The case reads the compact-stage CAD files and places each part where the assembly puts it. It
does not need FreeCAD and it never changes a CAD file. The new pockets and parts exist in memory
only. It reuses the readers and the scraper of [`scraper-fit`](../scraper-fit/).

## Running

Run from the repository root:

```bash
git lfs pull --include="modules/compact-stage/cad/**"
pip install cadquery-ocp numpy scipy matplotlib shapely pillow
python modules/compact-stage/simulation/cases/strip-end-insert/run.py
```

The run takes a few minutes. It stops with `FAILED` if a new pocket or hole breaks into a hollow
part of the base, if new parts overlap, or if carriage-top with its corner pockets, the stepped
scraper, carriage-bottom or a top roller passes over the insert before the dampers start to press
in. The carriage comes from the stage middle, so the check uses the insert drawn out towards the
base end: everything the carriage passes over on its way.
It writes the results to [`../../results/strip-end-insert/`](../../results/strip-end-insert/).

## Files

| File | What it does |
| --- | --- |
| `run.py` | Runs the fit checks, the spring numbers, the membrane model and the figures |
| `insert.py` | All sizes and 3D shapes: groove, insert, screw, strip corner, magnets, corner pockets, stepped scraper, spring end |
| `membrane.py` | Plane stress model of the whole strip: how the pull of the four inserts spreads across the width |
| `fig_common.py` | Colours and drawing helpers |
| `fig_sections.py`, `fig_overlay.py`, `fig_spring.py` | The figures |

## What is assumed

- The positions come from the drawing, at 3.44 pixels per mm. That scale comes from the 74.1 mm
  pitch of the carriage-top screws in the drawing.
- The insert is Ø6 mm, 1.4 mm high, 0.75 mm above the strip, at x = 12.0 mm and y = 8.5 mm, with an
  ISO 14581 M2 screw. The drawing has Ø7.5 mm at x = 11.6 mm and y = 13.2 mm. It moved over the strip
  ear so that the scraper lip behind it stays off the strip where the strip rises towards the
  carriage slope.
- Magnets Ø6 × 2 mm in pockets, top flush with the base. The size is not in the drawing.
- Only the end at x = 0, side y = 0 is built, once as the fixed end and once as the spring end.
  The other corners are mirror images.
- The spring values are textbook formulas with typical values for stainless spring wire.
- The membrane model treats the arch over the carriage as a soft band, 112 mm long, with
  750 N/mm along the travel for the whole width. That value comes from the strip model in the
  [`strip-pull`](../strip-pull/) case. No friction, no magnets.
