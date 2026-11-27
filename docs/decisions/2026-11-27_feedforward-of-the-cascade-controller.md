# The cascade controller offers exact and standard feedforward

- **Date:** 2026-11-27
- **Status:** Accepted

## Context

The Disturbance Rejection page models a cascade controller like the Copley drives: a position PID
gives a speed command to a velocity PI. In the Copley manuals (CME User Guide 16-01157 Rev05,
§12.6.1), Vff and Aff add to the speed command, not to the current. So their effect on the force
goes through the velocity PI and depends on Vp and Vi.

With the usual values, Vff = 100 % and Aff = m/Vp, the velocity integrator sees the speed error
Aff·a and holds Vi·Aff·v. This is a force proportional to the speed, about m·(Vi/Vp)·v: about 70 N
at 50 mm/s for the linear motor at the defaults. The position loop must push it back.

## Decision

- The page computes the feedforward from the tuned velocity loop and the mass line m_tot.
- **Exact (default):** Vff = 1, Vcff = −Vi·A, and A from Vi·A² − (Vp + Vi·T/2)·A + m_tot = 0, with
  Aff = A − T/2 (the derived velocity lags half a sample). For a rigid mass this gives exactly
  m_tot·a.
- **Standard (box off):** Vff = 1, Aff = m_tot/Vp, Vcff = 0, as a drive is usually set.
- Vcff is inside the loop, so the tuning includes it.

## Consequences

- The user can see how much the standard values cost on the circle and the line.
- The exact values need a negative Vcff. The Copley manual gives no range for Vcff, so this is not
  confirmed for the real drive. Ask Copley before relying on it.
- When the quadratic has no real root (a very large Vi), the page falls back to the standard values
  and marks it in the table.
