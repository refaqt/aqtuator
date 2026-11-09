# ADR — The compact stage is partly completed machinery, without limit switches

- **Date:** 2026-11-09
- **Status:** Proposed. Based on answers from Niels Bosmans on 2026-11-06. A machine safety
  specialist must still confirm the legal route.

Write this file in B2 English. Follow `.agents/rules/communication.md`.

## Context

We sell the compact stage assembled (motor, guides, encoder), often with a drive. Customers, such
as university labs and research teams, always build it into a larger setup. The stage will be sold
after 20 January 2027, when the Machinery Regulation (EU) 2023/1230 replaces the Machinery
Directive 2006/42/EC.

The stage had two inductive limit switches. Niels thought the RSF read head gives limit signals.
It does not: its connector carries only power and the BiSS data lines.

## Decision

- **The stage is partly completed machinery under Regulation (EU) 2023/1230.** We write the
  technical documentation (Annex IV, Part B), sign a Declaration of Incorporation (Annex V,
  Part B) and give assembly instructions (Annex XI). The customer makes the CE assessment of the
  whole machine. The drive keeps its maker's CE mark.
- **The limit switches are removed.** The drive stops at software limits from the absolute
  position. Limit switches were never a safety function for people. The end stops are the last
  protection, so they must hold the worst case (STG-15).
- **The largest payload and the top speed are design limits.** The end stops are sized for them,
  and they go on the type plate and in the instructions.
- **Horizontal mounting only.** For other positions the customer adds a brake or holding device.

## Consequences

- If we ever deliver a ready-to-run axis, set up by us, it becomes a complete machine with our own
  CE mark. This decision must then be reviewed.
- STG-15 needs a number for the largest payload, and the moving mass from the CAD.
- Drive limits that we pre-set must be written down and locked with a password.
- The parts list lost `SW-001` and `ELC-001` (autosen AI052 and AA068).
- Details and the full danger list: [the CE assessment](../compact-stage-ce-assessment.md).
