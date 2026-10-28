# strip-end-insert

Checks the strip end concept of Niels Bosmans (2026-10-28) against the CAD, and models how its
pull spreads across the strip. His drawing, with notes, is in
[the log of 2026-10-28](../../../../../docs/log/2026-10-28_strip-end-clamp-and-preload.md).

The concept: each strip end has two inserts, one near each side edge. An insert sits in a hole in
the strip, with no thread and no nut. A countersunk screw presses it into the hole. Two flat
faces on the insert slide in a small groove in the base, so it cannot turn. The screw hole in the
base sits a little nearer the base end than the insert when the strip is laid loose, so tightening
the screw centres the insert on it and pulls the strip. Magnets in pockets hold the strip down.

The case reads the compact-stage CAD files and places each part where the assembly puts it. It
does not need FreeCAD and it never changes a CAD file. The groove, the magnet pockets, the strip,
the insert and the screw exist in memory only. It reuses the readers and the scraper of
[`scraper-fit`](../scraper-fit/).

## Running

Run from the repository root:

```bash
git lfs pull --include="modules/compact-stage/cad/**"
pip install cadquery-ocp numpy scipy matplotlib shapely pillow
python modules/compact-stage/simulation/cases/strip-end-insert/run.py
```

The run takes a few minutes. It stops with `FAILED` if the groove, the tapped hole or a magnet
pocket breaks into a hollow part of the base, if the insert, the screw and the strip overlap, or
if the flush insert is hit by carriage-top, carriage-bottom or the scraper before the dampers start
to press in. For the insert as drawn, and in a crash, it reports the overlaps only.
It writes the results to [`../../results/strip-end-insert/`](../../results/strip-end-insert/).

## Files

| File | What it does |
| --- | --- |
| `run.py` | Runs the fit checks, the membrane model and the figures |
| `insert.py` | All sizes of the insert, the screw, the groove, the strip corner and the magnets, and the 3D shapes |
| `membrane.py` | Plane stress model of the whole strip: how the pull of the four inserts spreads across the width |
| `fig_common.py` | Colours and drawing helpers |
| `fig_sections.py`, `fig_overlay.py` | The figures |

## What is assumed

- The positions come from the drawing, at 3.44 pixels per mm. That scale comes from the 74.1 mm
  pitch of the carriage-top screws in the drawing. The overlay figure shows that the base pockets
  of the drawing and of the CAD fall on each other.
- Insert Ø7.5 mm, 1.7 mm high, two flat faces 6 mm apart, centred at x = 11.6 mm and y = 13.2 mm.
  The height is the M2.5 countersink (1.5 mm) plus 0.2 mm.
- Two heights are checked. **As drawn:** the insert stands in a 0.5 mm groove, 1.05 mm above the
  strip. **Flush:** the groove is 1.55 mm deep and the insert top is level with the strip top.
- Screw ISO 14581 M2.5 × 6. The insert can travel 0.25 mm.
- Magnets Ø6 × 2 mm in pockets, top flush with the base. The size is not in the drawing.
- Only the end at x = 0, side y = 0 is built. The other three corners are mirror images.
- The membrane model treats the arch over the carriage as a soft band, 112 mm long, with
  750 N/mm along the travel for the whole width. That value comes from the strip model in the
  [`strip-pull`](../strip-pull/) case. No friction, no magnets.
