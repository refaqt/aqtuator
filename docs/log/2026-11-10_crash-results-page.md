# 2026-11-10 — Interactive results page for the end-stop crash study

**Role(s):** simulation, engineering

## Goal

Niels asked for a web page on GitHub Pages that shows the results of the end-stop crash study of the
compact stage. He wanted to pick one case and see only that case: which models were used and how,
the 3D stress of the finite element model (FEM) in colour, plots for the other models, colours
against the limits, the deformation, and enough evidence to judge whether the study is right. He
reads it as an R&D manager who did not run the study.

## Short answer

- **The page is ready on the branch.** After the merge into `main` it is at
  <https://refaqt.github.io/aqtuator/crash/>. It shows all 45 cases of the study.
- **No mistake found in the calculation.** A new run of the study scripts gives the same 594
  numbers. The energy and impulse balances close in all 45 cases. A second, simpler model agrees.
  A new FEM run gives the same wall stiffness as the study (within 1.7 %).
- **Two findings that change no verdict:**
  - The single highest stress in the base depends on the mesh by about 13 %. It sits at a sharp
    inner corner. So the first yield of the pocket walls may start near 14 kN, not 16 kN.
  - The bumper model uses the 6 J normal rating at 7 mm. ACE also gives 9 J for an emergency stop.
    If that holds, the real crash force curve is up to 1.5 times stiffer than modelled. Ask ACE.
- **The lasting dent of the base stays at a few µm in every case,** checked with a second method
  (the same FEM run once more with an elastic material). The worst payload case gives 1.7 µm
  against 3.9 µm in the study. Both are far below 0.01 mm.

## Work Done

- Ran the stress analysis of the base again, and kept the full 3D field of every load step:
  displacement, stress and plastic strain on the outer surface. 16 steps for the bumper load (to
  48 kN) and 16 for the metal hit (to 64 kN).
- Ran the same load ramps with a purely elastic material. The difference of the two runs is the
  lasting dent. A first attempt that used a simple spring-back rule was wrong: it mixed in the change
  of shape under load (about 1 % of the displacement), which is as large as the dent itself.
- Mesh check: the bumper load at 5 kN on three meshes (36,000 to 182,000 nodes). The wall
  deflection changes by 1.6 %, the peak stress by 13 %.
- Exported all 45 crash cases with their time histories, and added checks for each case: energy
  balance, impulse balance, a one-direction model with its own integrator, hand calculations of
  the bumper capacity, the peak deceleration and the pocket wall.
- Built the page: case picker, verdict tiles in green, amber and red, the models with their
  equations and input sources, a 3D viewer, time plots, the payload map, the proof table, and the
  open points.
- Added the page to the publish workflow, with a data check that runs before every deploy.

## Decisions Made

- The page shows the raw stress the solver gives at the nodes, and says where it overshoots the
  material curve. The verdict tiles use the stress rule of the study (read from the material curve
  once the metal yields).
- Amber limits that are my own choice are marked as such on the page: stress above 2/3 of yield, and
  a joint slip use above 0.8.

## Open Questions

- What force curve does ACE give for the TA17-7 in an emergency stop (9 J), and past its stroke?

## Next Steps

1. Niels reviews the page and the findings.
2. Ask ACE for the TA17-7 force curve (normal, emergency, and past the stroke).

<details>
<summary>Technical notes</summary>

- Page: `simulation/cases/end-stop-crash-results/` (`index.html`, `page.js`, `crash_data.js`,
  `fem_fields.js`, `check_data.mjs`). Libraries from jsDelivr: three.js 0.147.0, Plotly 2.35.2.
- Data: `export_web_crash.py` and `export_web_fem.py` in the study folder. Both read the functions of
  `evaluate.py` and `run_fem.py` from those files (without running their `main()`), so the page and
  the study use the same code.
- The FEM fields are stored as 16 bit numbers per surface node and step (7,814 nodes, 15,648
  triangles). The page interpolates linearly between the two solved steps around the case force.
- Gmsh does not give the same mesh twice (70,128 to 70,194 nodes). The elastic comparison run
  therefore reads the saved mesh of the main run. Gmsh could not mesh the base at twice the element
  size, so the coarse mesh of the mesh check is 1.5 times the normal size.
- CalculiX solved each ramp in 8 to 9 minutes on four cores here, not the 30 to 60 minutes noted in
  the study log.

</details>
