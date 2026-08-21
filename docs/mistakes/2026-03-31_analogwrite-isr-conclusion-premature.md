# 2026-03-31 — Treated `analogWrite()` ISR unsafety as settled too early

**What happened:** I initially treated "do not use `analogWrite()` in `timerISR()`" as a settled rule and moved directly to a low-level RP2040 PWM compare-write solution.
**Root cause:** I generalized from timing/determinism concerns before checking the current arduino-pico implementation details and before adding hardware-visible debug instrumentation.
**Fix applied:** Re-checked the core sources, confirmed the mutex path is ISR-aware, and added runtime-selectable PWM strategies plus detailed PWM status instrumentation so hardware behavior can be compared directly.
**Prevention rule:** For embedded timing decisions, distinguish "not ideal for deterministic ISR use" from "proven unsafe," and add observability before locking in one hardware-control strategy.
**Affected files:** `src/controllino/main-controllino/main-controllino.ino`, `docs/mistakes.md`, `docs/skills.md`, `docs/decisions.md`, `docs/architecture.md`
