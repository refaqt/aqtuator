# 2026-03-31 — Add runtime-selectable PWM debug strategies

**Context:** After moving PWM compare writes into the ISR, hardware symptoms still suggested the physical RC output might not be following the requested duty. We needed a way to distinguish a broken low-level PWM path from a mixed configuration issue or ODrive-side behavior.
**Decision:** Add a compile-time `PWM_RUNTIME_MODE` to the Controllino identification sketch, plus `GET_STATUS` diagnostics that expose the active PWM runtime mode, slice/channel mapping, GPIO function, compare-register snapshots, and write counters.
**Alternatives considered:** Keep only one PWM implementation and debug externally with manual probing; immediately revert to `analogWrite()` in ISR without instrumenting the low-level path.
**Consequences:** Hardware debugging becomes much faster and more reproducible. The project now supports controlled comparison between:
- Arduino setup + low-level ISR compare writes
- fully low-level PWM setup + low-level ISR compare writes
- `analogWrite()` directly in the ISR as a fallback experiment
