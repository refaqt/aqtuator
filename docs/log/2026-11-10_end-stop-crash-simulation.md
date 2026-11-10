# 2026-11-10 — Crash of the compact stage into its end stops at 2 m/s

**Role(s):** simulation, engineering, safety

## Goal

Niels asked what happens when a wrong position command drives the carriage into the end stops
at full motor force, with the speed held at 2 m/s. He wanted to know the stress and the lasting
deformation of the base, the loads on the guide blocks and their life, the shock on the read head,
and whether screw joints slip. He asked for no payload, 1 kg, a second stage on top as a cross table,
and a table of payload (0 to 20 kg) against centre-of-mass height (20 to 200 mm). He chose
EN AW-7075-T651 for the base, and 6 × M5 screws for the payload.

## Short answer

- **No payload: the stage survives, only just.** The read head gets 1010 m/s², at its 1000 m/s²
  rating. The guide blocks and the base have a large margin.
- **1 kg: the read head goes over its rating (1230 m/s²),** and the two carriage halves are at the
  point where they can shift on each other.
- **A second stage on top: the crash breaks the stage.** Metal hits metal. The guide blocks get up to
  1.8 times their static rating, so the balls dent the tracks. The six M4 screws between the
  carriage halves shear off. The upper stage slides by up to 0.25 mm on its screws, and the base
  slides on the machine table.
- **The 7075 base is not the weak point.** It keeps a dent of 0.004 mm at most, in every case.
- **The motor must stop at the crash.** With the motor off, 0 kg and 1 kg stay well inside the
  ratings.
- **For 2 m/s, the payload limit is about 1 kg.** That agrees with the CE assessment table.
- Full results: [summary](../../modules/compact-stage/simulation/results/end-stop-crash/summary.md).

## Work Done

- Installed CalculiX, the stress solver, in the cloud environment, next to FreeCAD and Gmsh. A new
  script, `setup-fem.sh`, does this on any Linux computer. PrePoMax was not needed: it is a Windows
  front end for the same solver.
- Built a new case, `end-stop-crash`, in the compact stage simulation folder. It has three parts:
  - a stress analysis of the base end wall, with lasting (plastic) deformation;
  - a model of the moving carriage on its four guide blocks, using the base stiffness from the
    stress analysis;
  - checks of the guide blocks, the read head and six screw joints.
- Checked the model against the damper sizing page: same result (6.25 mm, 2.62 kN for 5 kg).
- Found again that the top carriage hits the seal strip corner screws 6.7 mm before the bumpers
  touch. This is known since 2026-10-29. The study assumes the planned relief is made.

## Decisions Made

- None. The results support a payload limit and design changes, which Niels decides.

## Open Questions

- How stiff is a TA17-7 once it is pressed past its 7 mm stroke? ACE publishes nothing. This input
  moves the results by a factor of two to three.
- Does RSF allow a 1 ms shock of 1500 to 2500 m/s² on the read head? The rating is for 6 ms.
- Which end of the guide blocks does the E2 lubrication unit sit on? The assembly and the
  architecture disagree. In a hard crash the blocks run 1.7 mm past the rail ends.

## Next Steps

1. Ask ACE for the TA17-7 force curve past its stroke.
2. Ask RSF about short shocks on the AK MC 15 head.
3. Add dowel pins or a step between carriage-top and carriage-bottom, and for the forcer.
4. Hold the base on the machine table with dowel pins or a stop edge.
5. Decide the payload limit for 2 m/s, or the speed limit for heavier payloads.

<details>
<summary>Technical notes</summary>

- Case: `modules/compact-stage/simulation/cases/end-stop-crash/` (`case.toml`, `run_fem.py`,
  `crash_model.py`, `evaluate.py`, `figures.py`). Results:
  `modules/compact-stage/simulation/results/end-stop-crash/`.
- CalculiX 2.23 from conda-forge has only the SPOOLES solver. The base was cut to x = 0 to 100 mm
  (41,098 elements) to keep each load ramp under an hour. Gmsh could not mesh a threaded corner
  screw hole at the far end, which the cut also removes.
- The end wall face ramp stopped at 112 kN, where the wall collapses. `run_fem.py` now stops at a
  step of 2e-3, so a new run ends there by itself.
- Material: IBL data sheet PD 7075 Platten 11/2022, EN 485-2 minimum values for 25 to 50 mm plate.
  Screw torques: Designwerk DW_009BAIAZD-EN, VDI 2230:2014, friction 0.12. Guide ratings: HIWIN
  GW-13-1-EN-2606-K. Read head: RSF AK MC 15 mounting instructions.

</details>
