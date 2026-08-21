# Decisions

Architecture decision records, one file per decision, per the doqs convention
`docs/decisions/YYYY-MM-DD_topic.md`.

Template: [`doqs/templates/adr.md`](../../doqs/templates/adr.md).

| Date | Entry |
| ---- | ----- |
| 2026-03-23 | [Blocking serial during real-time operation](2026-03-23_blocking-serial-during-real-time-operation.md) |
| 2026-03-23 | [Configure ODrive cyclic CAN capture by interval](2026-03-23_configure-odrive-cyclic-can-capture-by-interval.md) |
| 2026-03-23 | [Controllino GPIO label to Arduino pin mapping](2026-03-23_controllino-gpio-label-to-arduino-pin-mapping.md) |
| 2026-03-23 | [Defensive ODrive cleanup on exit](2026-03-23_defensive-odrive-cleanup-on-exit.md) |
| 2026-03-23 | [Handshake framing via READY/ACK/NACK and DATA_END](2026-03-23_handshake-framing-via-ready-ack-nack-and-data-end.md) |
| 2026-03-23 | [Use CSD/Welch for transfer estimates](2026-03-23_use-csd-welch-for-transfer-estimates.md) |
| 2026-03-25 | [Replace CAN torque with PWM->GPIO1 analog mapping](2026-03-25_replace-can-torque-with-pwm-to-gpio1-analog-mapping.md) |
| 2026-03-26 | [Runtime control-mode prompt with step/dir gating](2026-03-26_runtime-control-mode-prompt-with-step-dir-gating.md) |
| 2026-03-26 | [Spindle controller: pure discrete integrator with hold anti-windup](2026-03-26_spindle-integrator-anti-windup.md) |
| 2026-03-30 | [Hold 0 Nm at idle and gate ODrive analog endpoint](2026-03-30_hold-0-nm-at-idle-and-gate-odrive-analog-endpoint.md) |
| 2026-03-31 | [Add runtime-selectable PWM debug strategies](2026-03-31_add-runtime-selectable-pwm-debug-strategies.md) |
| 2026-03-31 | [Treat ODrive GPIO1 mode as a runtime invariant](2026-03-31_treat-odrive-gpio1-mode-as-a-runtime-invariant.md) |
| 2026-03-31 | [Update RP2040 PWM compare from timer ISR](2026-03-31_update-rp2040-pwm-compare-from-timer-isr.md) |
| 2026-04-17 | [Fix CANSimple node-id decode and store fresh torque+position pairs](2026-04-17_cansimple-node-id-decode-fix.md) |
| 2026-05-29 | [Workflow B acquisition via on-device high-rate capture](2026-05-29_workflow-b-acquisition-via-on-device-high-rate-capture.md) |
