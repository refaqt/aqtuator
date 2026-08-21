# 2026-03-23 — Configure ODrive cyclic CAN capture by interval

**Context:** The servo-identification sketch relies on receiving paired cyclic CAN messages (torque target and position estimate) at a known rate.
**Decision:** Configure ODrive cyclic CAN message intervals based on the sweep parameter, using:
- `axis.config.can.encoder_msg_rate_ms`
- `axis.config.can.torques_msg_rate_ms`
**Alternatives considered:** Polling CAN at high frequency from the microcontroller (less deterministic), or using ODrive logging features that require post-processing.
**Consequences:** The firmware can assume cyclic message arrival and focus on pairing/overflow detection; sweep timing directly maps to `sample_period` in the firmware.
