<!-- SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# forcer-cooling-thermal-results

A web page that shows the results of the thermal study of the compact stage. The motor runs all
the time at its rated current, and 20 °C water flows through the cooling channel. The page shows
how hot every part gets and how much the stage grows. It also checks the printed cooling block
against the heat limits of SLA resins and FDM filaments, and shows which pump suits six axes and a
spindle. It explains the model, every input and boundary condition, and the checks behind the
numbers.

**Open it:** <https://refaqt.github.io/aqtuator/thermal/>. The link works after the pull request
is merged into `main`. To use it from a local clone, open `index.html` in the browser. No server
is needed. The 3D view and the charts load two libraries from the internet (three.js and Plotly),
so they need a connection.

## What the page shows

- **Short answers:** one tile for each part or question, coloured against its limit, with the
  source of the limit.
- **The model:** how the geometry comes from the CAD, the parts, the mesh, and the boundary
  condition of every face.
- **3D view:** the parts, the boundary conditions, the temperature and the thermal growth (drawn
  larger). Parts can be switched off to look inside. Click a point to read its values.
- **Inputs and assumptions**, each with its source.
- **Temperatures, cooling block, pump and flow, warm-up, thermal growth.**
- **Unknown inputs:** how much each one changes the coil and the cooling block.
- **Proof** and **What can be wrong.**

## Files

| File | What it is |
| --- | --- |
| `index.html` | The page |
| `page.js` | The page logic. A plain script, not a module, so the page also works from disk |
| `thermal_data.js` | All results, inputs, pumps, materials and checks |
| `thermal_fields.js` | A light surface mesh of each part with the temperature and the growth |
| `check_data.mjs` | Checks the data. The publish workflow runs it before each deploy |

The two data files are made by `export_web.py` in the study folder. Do not edit them by hand.

## Make the data again

See the [case README](../../../modules/compact-stage/simulation/cases/forcer-cooling-thermal/README.md).
Then check the data:

```bash
node simulation/cases/forcer-cooling-thermal-results/check_data.mjs
```
