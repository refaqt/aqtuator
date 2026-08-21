# 2026-03-30 — Hold 0 Nm at idle and gate ODrive analog endpoint

**Context:** ODrive `GPIO1` has a pull-up, so “0% PWM” from the Controllino does not produce 0V at the ODrive pin after the RC network. With the project’s analog torque mapping, this can yield an unintended negative torque at rest, causing motion on power-up/shutdown.
**Decision:** Define the safe/idle state as “commanded 0 Nm” and implement it end-to-end:
- Controllino outputs a PWM duty that corresponds to 0 Nm at boot/idle and after output/acquisition completes (instead of forcing duty=0).
- ODrive clears `odrv.config.gpio1_analog_mapping.endpoint = None` when transitioning to `IDLE` and restores the torque endpoint right before entering closed-loop.
**Alternatives considered:** Keep duty=0 as idle; rely on operator timing; add hardware changes (remove pull-up / different RC topology).
**Consequences:** Power-on and shutdown become deterministic and safe w.r.t. unintended torque. The system now relies on correct calibration of the torque-to-voltage mapping used for the 0 Nm duty.
