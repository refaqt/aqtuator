# 2026-03-23 — Controllino GPIO label to Arduino pin mapping

**Context:** The test PWM sketch used an incorrect assumption that Controllino `GPIO0` mapped to RP2040/Arduino pin `2`, which caused output probing on the wrong pin.
**Decision:** Treat Controllino MICRO header labels (`GPIO0`, `GPIO1`) as direct RP2040 GPIO numbers for `controllino_rp2` Arduino sketches (`GPIO0` -> `D0`/`0`, `GPIO1` -> `D1`/`1`), and prefer `D0`/`D1` aliases in code.
**Alternatives considered:** Continue using a project-local custom alias with hard-coded `2u`, or use unnamed literals without documenting source-of-truth mapping.
**Consequences:** Pin assignments are now aligned with official docs/core headers and are easier to validate; future sketches should reference core aliases and include mapping diagnostics when hardware probing is involved.
