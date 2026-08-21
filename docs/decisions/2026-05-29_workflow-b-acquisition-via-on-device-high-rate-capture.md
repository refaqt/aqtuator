# 2026-05-29 — Workflow B acquisition via on-device high-rate capture

**Context:** Servo identification previously used a Controllino to receive cyclic CAN torque/encoder messages at ~500 Hz and stream samples over serial. This added hardware, wiring, and message-pairing complexity.
**Decision:** Capture `axis0.controller.torque_setpoint` and `axis0.pos_estimate` directly on the ODrive using `odrive.utils.high_rate_capture` over USB (firmware 0.6.12+). Remove the Controllino servo-identification sketch from the repo.
**Alternatives considered:** Keep cyclic CAN + Controllino (proven but lower rate and extra hardware); poll properties over USB at loop rate (too slow).
**Consequences:** Workflow B needs only ODrive USB; sample rate is ~8 kHz. `duration` must stay within the 2-variable capture window (1024 ms). Cyclic CAN configuration is no longer part of Workflow B.
