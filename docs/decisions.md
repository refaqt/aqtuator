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


