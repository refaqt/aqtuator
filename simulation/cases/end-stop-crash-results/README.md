# end-stop-crash-results

A web page that shows the results of the end-stop crash study of the compact stage, one case at a
time, with the proof that the numbers hold together. It is written for a reader who did not run the
study and wants to judge it.

**Open it:** <https://refaqt.github.io/aqtuator/crash/> (after the pull request is merged into
`main`). To use it from a local clone, open `index.html` in the browser. No server is needed. The 3D
view and the charts load two libraries from the internet (three.js and Plotly), so they need a
connection.

## What the page shows

Pick a case at the top: the four named cases, the motor switched off, the 2.2 m/s overspeed trip, or
any of the 35 payload cases. Every section then shows that case only.

- **Verdict:** one tile for each part (bumpers, base, guide blocks, read head, screw joints), coloured
  green, amber or red against its limit. Each tile names the limit and its source.
- **What happens:** the crash in words, with a side view.
- **The models:** the crash model, the stress model (FEM) of the base, and the hand formulas, with
  their equations, supports, loads and all inputs with their sources.
- **3D stress:** the base in colour: stress against the yield limit, plastic strain, displacement and
  lasting dent, with the deformation drawn larger. Click a point to read its values.
- **Time plots:** forces, travel, read head acceleration, guide block loads, force against travel, and
  where the energy goes.
- **Screw joints and payload map.**
- **Proof:** independent checks for the case: energy and impulse balance, a second simple model, the
  damper sizing page, hand calculations, the support reactions of the FEM, and a mesh check.
- **What can be wrong:** the spread of the unknown inputs, the limits of the model, and the points
  found while checking.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The page |
| `page.js` | The page logic. A plain script, not a module, so the page also works from disk |
| `crash_data.js` | All crash cases with their time histories and checks |
| `fem_fields.js` | The 3D fields of the base, on its outer surface, for each load step |
| `check_data.mjs` | Checks the data. The publish workflow runs it before each deploy |

The two data files are made by scripts in the study folder. Do not edit them by hand.

## Make the data again

From the repository root, after `bash setup-fem.sh` on Linux:

```bash
freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/export_web_crash.py
```

```bash
freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/export_web_fem.py
```

The first takes about two minutes. The second runs the stress analysis again and takes about 45
minutes on four cores. Then check the data:

```bash
node simulation/cases/end-stop-crash-results/check_data.mjs
```

The study itself: [case README](../../../modules/compact-stage/simulation/cases/end-stop-crash/README.md)
and [results summary](../../../modules/compact-stage/simulation/results/end-stop-crash/summary.md).
