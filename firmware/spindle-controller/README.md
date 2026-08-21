# spindle-controller

Standalone 8 kHz closed-loop spindle controller. Reads A0/A1/A3, forms `x_spindle`, applies a
lead-lag, a 2nd-order low-pass and two notches (Biquad DF1), and emits the result as a PWM torque
command.

The 8 kHz timer ISR computes the control output; `loop()` applies the pending PWM duty.

**Enable gate:** `GPIO1`/`D1` must be HIGH for the controller to run. Otherwise PWM is forced to 0
and the filter states are reset, so re-enabling never resumes from stale state.

The integrator is a pure discrete integrator with hold anti-windup — see
[the decision record](../../docs/decisions/2026-03-26_spindle-integrator-anti-windup.md). An earlier
version double-counted the integrator input;
[that mistake is logged](../../docs/mistakes/2026-03-26_double-counted-integrator-input-in-torque-summing.md).
