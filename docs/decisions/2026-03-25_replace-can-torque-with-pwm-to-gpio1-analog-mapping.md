# 2026-03-25 — Replace CAN torque with PWM->GPIO1 analog mapping

**Context:** The torque command path originally used ODrive CAN torque messages. For the target setup we need to drive ODrive via an analog command generated from Controllino PWM (through an RC filter) into ODrive `GPIO1` with analog input mapping.
**Decision:** Remove all torque CAN sending from the Controllino acquisition workflow and instead output PWM on `D0`, clamped to 0.84 of full-scale, feeding ODrive `GPIO1` analog mapping to `axis0.controller._input_torque_property` while keeping `POSITION_CONTROL` + `PASSTHROUGH` input mode.
**Alternatives considered:** Keep CAN for torque and add PWM as a second path, or map analog input to a different endpoint (position/velocity) instead of torque.
**Consequences:** No CAN wiring required for Workflow A; the excitation signal is now a commanded analog voltage (derived from the waveform) and the usable analog range is reduced by the 0.84 clamp.
