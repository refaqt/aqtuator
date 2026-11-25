# 2026-11-25 — Water cooling of the compact stage motor at rated current

**Role(s):** simulation, engineering, purchasing

## Goal

Niels asked for a detailed thermal simulation of the motor water cooling of the compact stage. The
MAXWELL MK21 runs all the time at its rated current, with water at 20 °C. He wanted to know:

- how hot the coil, carriage-bottom, carriage-top and the base get;
- the temperature difference from the coil to the water;
- whether the printed cooling block deforms, compared with SLA resins and FDM filaments;
- which common, affordable pump of industrial quality to use, when one manifold feeds six axes
  and a spindle in parallel;
- the thermal growth of the stage, with the rails and the guide blocks in the model.

He chose EN AW-7075-T651 for carriage-bottom and carriage-top, and still air at 20 °C.

## Short answer

- **At the full 2.0 A, the coil runs 4.7 K over its limit:** its hottest point reaches 124.7 °C.
  The limit is 120 °C. The 120 °C PTC sensor may stop the drive after about 40 minutes at full
  current.
- **This is not a cooling problem.** The water holds the motor mounting face at 24.5 °C, about the
  25 °C of the data sheet test. 100 K of the rise is inside the motor.
- **The data sheet rounds the rated current up.** Its 181 N needs 1.957 A. At 1.957 A the coil
  reaches 118.5 °C, under the limit.
- **The water warms by 1.8 K** (20.0 → 21.8 °C) and takes 64 % of the 116 W. Most of the rest goes
  through the base into the machine table.
- **The printed cooling block stays at 26 °C** (32 °C at worst). Every resin and filament checked,
  even PLA (55 °C), stays well below its heat deflection temperature.
- **Pump:** a TEYU CW-5200 chiller with the 4 bar pump option gives 0.59 l/min to each axis. A D5
  pump is too weak for these narrow paths.
- **Thermal growth:** carriage-top lifts 3 µm. The read head moves 3 to 12 µm against the scale,
  depending on how firmly the forcer holds the carriage. The encoder cannot see that movement.
- Full results: [summary](../../modules/compact-stage/simulation/results/forcer-cooling-thermal/summary.md)
  and the page <https://refaqt.github.io/aqtuator/thermal/>.

## Work Done

- Built a new case, `forcer-cooling-thermal`. It takes the real base, carriage-bottom,
  carriage-top and cooling block from the CAD and places them where the assembly has them. It adds
  blocks for the forcer, the magnet track, the rails and the guide blocks, with their catalogue
  sizes. It also models the water volume.
- Meshed each part on its own and joined the parts in the solver with a contact conductance at each
  joint. One shared mesh of all parts failed at small near-contacts in the CAD.
- Wrote a small element code for heat and growth (10-node tetrahedra, scipy and pyamg). It gives
  exact answers on test blocks. CalculiX could not hold contact conductance between separate
  meshes in a heat solve.
- Set the forcer to the data sheet 0.87 K/W inside the full model.
- Ran the main case, 33 cases for the unknown inputs and the pumps, a 4-hour warm-up, and three
  growth cases.
- Found the pump candidates and the heat limits of 14 printing materials in the makers' data sheets.
- Built the results page, in the style of the crash page, and added it to the publish workflow.
- `setup-fem.sh` now also installs scipy and pyamg.

## Decisions Made

- None. The results support a choice of continuous current and pump, which Niels decides.

## Open Questions

- What does MAXWELL measure R<sub>TH</sub> 0.87 K/W to? The study assumes the hottest coil point to
  the mounting face. This decides whether 2.0 A is allowed continuously.
- Is the switch point of the SNM120 PTC sensor exactly 120 °C? It is not confirmed in writing.
- What is the pump curve of the CW-5200 4 bar option, and which model code has it? TEYU publishes
  only the maximum pressure and flow.
- How firmly do the six M4 screws hold the forcer? This decides how much the carriage bends.

## Next Steps

1. Set the drive continuous current to 1.96 A (181 N) for the MK21, or accept a PTC trip at full
   current in long cuts.
2. Ask MAXWELL what R<sub>TH</sub> is measured to, and to confirm the 120 °C switch point.
3. Ask TEYU for the pump curve and the model code of the CW-5200 with the 4 bar pump.
4. Fit a needle valve on the spindle branch of the manifold.
5. Measure the coil temperature (PTC resistance) and the read head drift on the first stage.

<details>
<summary>Technical notes</summary>

- Case: `modules/compact-stage/simulation/cases/forcer-cooling-thermal/` (`build_geometry.py`,
  `meshing.py`, `fem.py`, `hydraulics.py`, `run_thermal.py`, `export_web.py`, `case.toml`,
  `print_materials.toml`). Results: `modules/compact-stage/simulation/results/forcer-cooling-thermal/`.
- Page: `simulation/cases/forcer-cooling-thermal-results/`; `pages.yml` publishes it at `/thermal/`.
- Heat mesh: 952 263 nodes. Growth mesh: 224 297 nodes (2.5 times coarser, the printed block kept
  fine), because the growth solve on the heat mesh needed more than the 15 GB of the cloud machine.
- Forcer conductivity 0.757 W/(m K) gives 0.867 K/W with the whole top face held at one
  temperature, the air gap path to the magnet track included.
- The Gmsh mesh of carriage-top needs one small corner face removed (a 4 mm radius tangent to a
  pocket wall). The script does this by itself and lists it on the page.
- The stoq CAD of the rails, blocks, forcer and track (Git LFS) could not be downloaded in this
  session, so those parts are blocks with catalogue sizes.
- The cases run in three forked processes; the full run takes about 2.5 hours on four cores.

</details>
