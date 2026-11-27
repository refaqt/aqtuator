# 2026-11-27 — Disturbance Rejection page: cascade controller, feedforward and encoder resolution

**Role(s):** engineering, simulation, software

## What happened

The page "Cutting Force Rejection" is now
[Disturbance Rejection](https://refaqt.github.io/aqtuator/disturbance-rejection/). The old address
forwards to it. The case folder moved to
[`simulation/cases/disturbance-rejection/`](../../simulation/cases/disturbance-rejection/).

New on the page:

- A choice of controller. The **single-loop controller** is the one the page had, now with
  acceleration feedforward m_tot·a. The **cascade controller** is a position PID around a velocity
  PI, with the velocity derived from the encoder, an output filter, and the feedforward Vff, Aff
  and Vcff. Its structure follows the Copley CME and Xenus Plus manuals.
- The encoder resolution (default 0.1 µm). Every measured position in a time simulation is rounded
  to whole counts.
- Two new charts: the contour error on a circle (two equal stages, default Ø50 mm at 3000 mm/min)
  and the following error on a straight line (default 10 mm/min).
- All gains are tuned automatically with the same robustness rules as before (sensitivity peak
  6 dB, margins, ±15 % on the resonances). The cascade must meet them for the velocity loop alone
  and for the whole loop.

Results at the defaults (details in the case README):

- **Linear motor: the cascade is five times stiffer** (lowest stiffness 13.3 against 2.5 N/µm,
  velocity bandwidth 678 Hz against 287 Hz). The price is encoder noise: one count per sample
  changes the force by about 8 N, and the stage shakes 0.024 µm rms on the slow line, five times
  more than with the single loop.
- **Ball screw: both controllers are about equal.** The resonances set the limit.
- **Feedforward works.** Without encoder rounding, both controllers follow the circle within 1 nm
  (the collocated ball screw keeps 11 nm of spring deflection). With 0.1 µm rounding all errors
  stay below one count.

How Vff and Aff reach the force (the question asked): they add to the speed command, so they pass
through the velocity PI. Vff = 100 % does not depend on the velocity loop. Aff and Vcff do: for an
exact feedforward, Vcff = −Vi·A and Vi·A² − (Vp + Vi·T/2)·A + m = 0, with A = Aff + T/2. See the
[decision](../decisions/2026-11-27_feedforward-of-the-cascade-controller.md).

## Later the same day: new defaults, and why the error has no steps

The page now starts at a loop rate of 4000 Hz (the rate of the Copley Xenus Plus velocity and
position loops) and a line speed of 1 mm/min. The model file keeps 10 kHz, so the checks are
unchanged.

Question asked: why does the following error show no steps of one count, with overshoot and
settling? Answer, now also on the page and in the case README:

- The stage is a mass. A new count changes only the measured position, not the true position.
- The feedforward gives the force for the path. Without friction, constant speed needs no force,
  so the stage moves on by itself. The feedback only sees a saw tooth of ±half a count.
- The stage swings over the edge of a count, by about one count from peak to peak (about
  ±0.05 µm at the new defaults). It never settles.
- The derived velocity is very noisy (0 for 24 samples, then 0.4 mm/s), and the force follows it
  (about ±1.4 N, linear motor, cascade). The mass turns these short pulses into a small movement.
- Real steps come from friction: the stage sticks between counts until the integrator breaks it
  free. The model has no friction, so it cannot show them.

## Open Questions

- Does the Copley drive accept a negative Vcff? The manual gives no range. Ask Copley.
- Is Copley's derived velocity exactly the change of position per sample? Not stated in the manual.
- The tuning ignores encoder noise. A rule for the output filter against noise is still missing.

## Next Steps

- Measure the coupling and axial damping of the ball-screw drive; the ball-screw results depend on
  them.
- Ask Copley the two open questions before the drive is tuned.

<details>
<summary>Checks</summary>

- `node simulation/cases/disturbance-rejection/check_model.mjs`: all 158 checks pass (both
  controllers, feedforward, circle, line, rounding).
- `node simulation/cases/hard-turning-stability/check_model.mjs`: all pass, results unchanged.
- The page was opened from disk and from a local copy of the published site, with both
  controllers, at desktop and phone width: no errors.

</details>
