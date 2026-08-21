# 2026-03-26 — Double-counted integrator input in torque summing

**What happened:** The first integrator attempt computed `torque_unclamped = y_in + (i1 + y_in)` which equals `i1 + 2*y_in` (double-counting the current sample) instead of a pure-integrated output.
**Root cause:** Mixed two different control output conventions (PI-style `y + I` vs pure-integrated `I`) without explicitly defining what the integrator state represents.
**Fix applied:** Switched to pure-integrated output: `i_candidate = i1 + u_in`, `torque_cmd = clamp(i_candidate)`, and freeze `i1` whenever clamped (hold-on-saturation).
**Prevention rule:** Before implementing discrete integrators, write the exact discrete equations and define whether the integrator state is the output or is summed with a proportional path; then translate equations into code 1:1.
**Affected files:** `src/controllino/spindle-controller/spindle-controller.ino`, `docs/mistakes.md`
