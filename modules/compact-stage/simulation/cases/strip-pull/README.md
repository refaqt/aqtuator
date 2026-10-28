# strip-pull

The strip model for the 0.15 mm seal strip in the real carriage. It answers three questions:

- How high does the strip bow between the bottom rollers, for a given pull?
- How hard does the strip press on carriage-top, with the ceiling as drawn or raised?
- How far must the two strip ends move to go from a hand-tight strip to a given pull?

The answers do not depend on how the strip ends are held.

It uses the solver of the [seal strip designer page](../../../../../simulation/cases/strip-seal-designer/),
with the faces of both carriage halves added as walls.

## Running

Run from the repository root:

```bash
pip install numpy matplotlib
python modules/compact-stage/simulation/cases/strip-pull/run.py
```

It needs Node 18 or newer. It writes the results to
[`../../results/strip-pull/`](../../results/strip-pull/).

## Files

| File | What it does |
| --- | --- |
| `run.py` | Runs the strip model and draws the figure |
| `strip_pull.mjs` | The strip model: bow, force on carriage-top, and travel against pull |
| `fig_strip_model.py` | The figure |

## What is assumed

- The seal strip is 0.15 mm thick, 186 mm wide (y = 12 to 198 mm) and 430 mm long between its
  two ends.
- The carriage faces are read from the CAD at y = 105 mm.
- The bottom rollers stand 1.5 mm proud of carriage-bottom, the same as the top rollers below
  carriage-top. The top rollers are taken as raised, so they just touch the strip. Neither roller
  is in the CAD yet.
- The designer page now models the carriage channel itself, with the rollers 0.5 mm proud. This
  case switches that off (`carriage: false`) and uses its own walls, so its numbers stay
  comparable with the log of 2026-10-28.
- The magnet strips are the estimates of the designer page: 20 N/mm³ and 0.005 N/mm².
