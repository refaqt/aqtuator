# 2026-09-28 — Tune each drive case with the same rule

- **Date:** 2026-09-28
- **Status:** Superseded by [Robust tuning rules for the drive cases](2026-09-28_robust-tuning-rules-for-the-drive-cases.md). Each case still gets its own controller; only the rule changed.

## Context

The cutting force page compares three drives: a linear motor, a ball-screw servo read at the
motor, and a ball-screw servo read at the stage. The ball-screw drives are much heavier as seen by
the controller, and they have a resonance in the coupling. One controller cannot fit all three.
Tuned on the linear motor, its gain would be 8 to 20 times too low for the ball screw.

## Decision

Each case gets its own controller, with the same shape and the same rule. The controller
bandwidth f_b is the highest one where the worst phase margin is still 30°. "Worst" means over
every point where the loop gain crosses 1. With a resonance, the loop can cross 1 a second time
near the resonance, and that crossing can set the limit. After tuning, the page tests the closed
loop for stability.

## Consequences

- The comparison is fair: each drive gets the best controller that this one rule allows.
- The rule only looks at the phase margin. A case can end up with a small gain margin, for
  example 2.5 dB for the collocated ball screw at the defaults. The page shows the gain margin
  next to the phase margin, so this is visible.
- If a case still comes out unstable, the page says so and leaves it out of the time and sweep
  charts.
