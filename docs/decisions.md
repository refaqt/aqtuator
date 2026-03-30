# Decisions

## Blocking serial during real-time operation — 2026-03-23
**Context:** During waveform playback and acquisition, the microcontroller must maintain tight timing. Any extra serial parsing can introduce jitter and risk buffer overruns.
**Decision:** Block serial reads while acquisition/output is active (and send completion acknowledgements only once the real-time window ends).
**Alternatives considered:** Keeping serial parsing active during acquisition (risking timing jitter and data corruption), or streaming during acquisition (more complex framing/backpressure).
**Consequences:** Host-side code must treat acquisition/output as a non-interactive critical section; Python waits for `ACK: ... complete` before issuing `GET_DATA`.

## Use CSD/Welch for transfer estimates — 2026-03-23
**Context:** The project needs a robust frequency-domain estimate of gain/phase between an excitation (torque/command) and a measured response (position or derived outputs).
**Decision:** Estimate transfer function using cross-spectral density and auto-spectral density:
- `H = Pxy / Pxx` where `Pxy` is from `scipy.signal.csd` and `Pxx` is from `scipy.signal.welch`.
**Alternatives considered:** FFT-based single-record transfer, pure FFT magnitude/phase at the excitation bin, or time-domain system identification.
**Consequences:** Consistent behavior across scripts; reduced sensitivity to noise vs naive single FFT, but still depends on windowing/segment length choices (`nperseg`).

## Configure ODrive cyclic CAN capture by interval — 2026-03-23
**Context:** The servo-identification sketch relies on receiving paired cyclic CAN messages (torque target and position estimate) at a known rate.
**Decision:** Configure ODrive cyclic CAN message intervals based on the sweep parameter, using:
- `axis.config.can.encoder_msg_rate_ms`
- `axis.config.can.torques_msg_rate_ms`
**Alternatives considered:** Polling CAN at high frequency from the microcontroller (less deterministic), or using ODrive logging features that require post-processing.
**Consequences:** The firmware can assume cyclic message arrival and focus on pairing/overflow detection; sweep timing directly maps to `sample_period` in the firmware.

## Defensive ODrive cleanup on exit — 2026-03-23
**Context:** During experiments, users may stop early or encounter serial/CAN errors. Leaving ODrive in an unsafe state can require manual recovery.
**Decision:** Implement a best-effort cleanup path that exits closed-loop control and forces a safe configuration (e.g., `Position` control mode) before disconnecting, while ensuring cleanup does not raise.
**Alternatives considered:** Aggressive exceptions that reveal state bugs but risk leaving hardware running; minimal cleanup that might not bring ODrive to a safe state.
**Consequences:** More reliable shutdown behavior; still requires operator awareness for physical safety.

## Handshake framing via READY/ACK/NACK and DATA_END — 2026-03-23
**Context:** Serial transport is text-based, may include debug/info chatter, and large payloads (CSV upload, data blocks) require strict framing.
**Decision:** Use explicit handshake stages (`READY`, then `ACK/NACK`) and a framed data payload (`DATA:...` header + samples + `DATA_END` terminator). Host reads until expected framing markers are received, skipping debug/info lines.
**Alternatives considered:** Implicit framing based on timeouts only, or binary streaming without clear delimiters.
**Consequences:** Higher correctness of upload/download; host code becomes stateful around expected markers.

## Controllino GPIO label to Arduino pin mapping — 2026-03-23
**Context:** The test PWM sketch used an incorrect assumption that Controllino `GPIO0` mapped to RP2040/Arduino pin `2`, which caused output probing on the wrong pin.
**Decision:** Treat Controllino MICRO header labels (`GPIO0`, `GPIO1`) as direct RP2040 GPIO numbers for `controllino_rp2` Arduino sketches (`GPIO0` -> `D0`/`0`, `GPIO1` -> `D1`/`1`), and prefer `D0`/`D1` aliases in code.
**Alternatives considered:** Continue using a project-local custom alias with hard-coded `2u`, or use unnamed literals without documenting source-of-truth mapping.
**Consequences:** Pin assignments are now aligned with official docs/core headers and are easier to validate; future sketches should reference core aliases and include mapping diagnostics when hardware probing is involved.

## Replace CAN torque with PWM->GPIO1 analog mapping — 2026-03-25
**Context:** The torque command path originally used ODrive CAN torque messages. For the target setup we need to drive ODrive via an analog command generated from Controllino PWM (through an RC filter) into ODrive `GPIO1` with analog input mapping.
**Decision:** Remove all torque CAN sending from the Controllino acquisition workflow and instead output PWM on `D0`, clamped to 0.84 of full-scale, feeding ODrive `GPIO1` analog mapping to `axis0.controller._input_torque_property` while keeping `POSITION_CONTROL` + `PASSTHROUGH` input mode.
**Alternatives considered:** Keep CAN for torque and add PWM as a second path, or map analog input to a different endpoint (position/velocity) instead of torque.
**Consequences:** No CAN wiring required for Workflow A; the excitation signal is now a commanded analog voltage (derived from the waveform) and the usable analog range is reduced by the 0.84 clamp.

## Runtime control-mode prompt with step/dir gating — 2026-03-26
**Context:** Operators need to quickly choose between torque and position controller modes at runtime, but the torque-command path should not start while `axis0.config.enable_step_dir` is active.
**Decision:** In `main_sequential.py`, prompt for mode using `t`/`p` with default `p` (position). At startup force `odrv0.axis0.config.enable_step_dir = False`, and after identification/cleanup restore `enable_step_dir = True`.
**Alternatives considered:** Keep control mode hard-coded to position; leave step/dir always enabled; move mode selection to source-code constant only.
**Consequences:** Safer and faster operator workflow without code edits between runs; reduced risk of blocked torque-command behavior during acquisition; cleanup path now explicitly restores step/dir state.

## Hold 0 Nm at idle and gate ODrive analog endpoint — 2026-03-30
**Context:** ODrive `GPIO1` has a pull-up, so “0% PWM” from the Controllino does not produce 0V at the ODrive pin after the RC network. With the project’s analog torque mapping, this can yield an unintended negative torque at rest, causing motion on power-up/shutdown.
**Decision:** Define the safe/idle state as “commanded 0 Nm” and implement it end-to-end:
- Controllino outputs a PWM duty that corresponds to 0 Nm at boot/idle and after output/acquisition completes (instead of forcing duty=0).
- ODrive clears `odrv.config.gpio1_analog_mapping.endpoint = None` when transitioning to `IDLE` and restores the torque endpoint right before entering closed-loop.
**Alternatives considered:** Keep duty=0 as idle; rely on operator timing; add hardware changes (remove pull-up / different RC topology).
**Consequences:** Power-on and shutdown become deterministic and safe w.r.t. unintended torque. The system now relies on correct calibration of the torque-to-voltage mapping used for the 0 Nm duty.

## Spindle controller: pure discrete integrator with hold anti-windup — 2026-03-26
**Context:** The spindle vibration controller output is clamped to safe torque bounds before converting to ODrive GPIO1 voltage/PWM. Without anti-windup, an integrator can accumulate error while saturated, causing long recovery and overshoot once it desaturates.
**Decision:** Use a raw discrete integrator \(z/(z-1)\) with **pure-integrated output** (torque command is the integrator state). Integrate the post-filter signal (after lead-lag + LPF + notches). Apply **anti-windup by holding** the integrator state constant whenever the torque command is clamped.
**Alternatives considered:** PI-style summing (\(y + I\)); conditional integration only when the update would move back toward range; back-calculation anti-windup.
**Consequences:** Simple, deterministic behavior under saturation; however the effective integrator scaling depends on upstream signal units and sample rate, so it may need a gain \(K_i\) later for practical tuning.


