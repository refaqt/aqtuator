# 2026-09-28 — Robust tuning rules for the drive cases

- **Date:** 2026-09-28
- **Status:** Accepted

## Context

The cutting force page compares a linear motor with a ball-screw servo, read at the motor or at
the stage. Each case had its own controller, tuned for 30° phase margin only. For the ball screw
this gave loops that came very close to the point −1: the loop gain was near 1 where the phase was
near or below −180°. The collocated loop had only 2.4 dB gain margin, and a sensitivity peak of
13.9 dB. A resonance 5 % off from the model, or a small change in gain, would make it unstable.
Such a controller would not work on a real machine, so the comparison was not honest.

## Decision

Each case keeps its own controller with the same shape. The bandwidth f_b is the highest one,
counted up from a slow one, where all of these rules hold:

- The sensitivity peak, max |1/(1 + C·G)|, is at most 6 dB. This is the usual limit for motion
  systems. It keeps the loop at least 0.5 away from −1.
- The phase margin is at least 30° at every gain crossing.
- The gain margin is at least 6 dB at every −180° crossing.
- The closed loop is stable.
- All of this still holds when each resonance is 15 % lower or higher than the model says, with
  the same controller (9 plants for the ball screw, 1 for the linear motor).

The linear motor gets exactly the same rules. The limits are inputs on the page.

The damping ratios also change, from 0.1 and 0.05 to 0.02 and 0.02, for a metal bellows or disc
coupling and a ball screw without extra damping. Both are estimates with a stated range.

## Consequences

- The comparison is fair and closer to what a real machine allows. All bandwidths drop: linear
  motor 431 to 287 Hz, ball screw 290 to 102 Hz (motor encoder) and 127 to 73 Hz (linear encoder).
- The results depend strongly on the damping ratios, which are estimates. The case README gives
  the results for the ends of the range. A measured frequency response of the real drive should
  replace them.
- The controller shape is still fixed. A notch filter on the coupling mode could raise the
  ball-screw bandwidth, but that is a separate design step and would also need the same rules.
- Tuning takes longer, because it tests 9 plants. The page still updates in about 2 s.
