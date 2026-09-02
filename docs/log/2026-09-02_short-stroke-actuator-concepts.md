# 2026-09-02 — Short-stroke actuator concepts

**Role(s):** engineering, hardware, simulation

## Goal

Find three low-cost, two-sided, high-force, short-stroke actuator ideas that fit
50 × 50 × 20 mm, with a first-order feasibility check against > 200 N, > 0.1 mm travel,
> 10 Hz, and BOM < 100 EUR (sensor provided).

## Work Done

- Added simulation case
  [`simulation/cases/short-stroke-actuator-concepts`](../../simulation/cases/short-stroke-actuator-concepts/)
  with a sizing script and a comparison of three concepts:
  1. PM-biased differential reluctance + flexure guide
  2. Flextensional multilayer piezo
  3. Lorentz voice coil + flexure lever
- Recorded results in
  [`simulation/results/short-stroke-actuator-concepts/summary.md`](../../simulation/results/short-stroke-actuator-concepts/summary.md).
- Used the measured spindle stiffness 100 N / 140 µm
  ([2026-01-27](2026-01-27_machine-stiffness-measurement.md)) as the plant load, and the
  [2026-08-24 reluctance note](2026-08-24_reluctance-actuator-investigation.md) as the
  starting point for idea 1.

## Decisions

- This envelope cannot be a 10 Hz reaction-mass shaker: ~1000 kg of proof mass would be
  needed for 200 N at ±50 µm. The actuator has to couple two structures.
- 6-DOF at 200 N per axis does not fit. z + rx + ry is the realistic stretch, and idea 1
  is the only one that offers a clean 3-sector puck for that.
- A rotary BLDC + 50 µm eccentric is a bandwidth trap (reflected inertia ~600 kg, ~5 Hz)
  even though the torque is only 10 mNm.
- First prototype recommendation: idea 1 (reluctance). Idea 2 if the plant pole must sit
  well above 100 Hz. Idea 3 only as a peak-duty linear option that reuses current-loop
  hardware.

## Open Questions

- Is 10 Hz the real operating band, or only a minimum, with the 700 Hz spindle mode as
  the actual target?
- Where does the 50 × 50 × 20 mm package sit on the machine? Non-collocated moment load
  was the other problem on 2026-08-24.
- Is 0.1 mm peak-to-peak or ±0.1 mm?

## Next Steps

- Freeze 1-DOF vs 3-DOF (z/rx/ry) before CAD.
- Magnetic circuit sketch and flexure stress for idea 1.
- Declare the force / stroke / envelope numbers in `architecture/` SysML so later
  measurement summaries can cite them.
