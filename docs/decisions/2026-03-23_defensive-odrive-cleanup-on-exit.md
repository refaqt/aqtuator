# 2026-03-23 — Defensive ODrive cleanup on exit

**Context:** During experiments, users may stop early or encounter serial/CAN errors. Leaving ODrive in an unsafe state can require manual recovery.
**Decision:** Implement a best-effort cleanup path that exits closed-loop control and forces a safe configuration (e.g., `Position` control mode) before disconnecting, while ensuring cleanup does not raise.
**Alternatives considered:** Aggressive exceptions that reveal state bugs but risk leaving hardware running; minimal cleanup that might not bring ODrive to a safe state.
**Consequences:** More reliable shutdown behavior; still requires operator awareness for physical safety.
