# 2026-10-02 — The ODrive is a test drive only. We will not use it in future developments

- **Date:** 2026-10-02
- **Status:** Accepted

## Context

The ODrive S1 servo drive is in many logs, decisions, firmware files and software files in this
repository. This history makes people think the ODrive is part of the product. It comes up again in
discussions about drives, encoders and suppliers.

The ODrive was only a test tool. We used it on the Mekanika Pro test machine to learn how the
machine behaves, and to try the identification methods. It was never chosen as the drive for a
product.

## Decision

We will not use the ODrive in future developments.

- Do not pick a drive, an encoder or any other part because it works with the ODrive.
- Do not list "works with the ODrive" as a requirement or as a reason to prefer a part.
- Do not plan new modules, stage families or products around the ODrive.
- The drive for the compact stage is chosen by the requirements in
  [`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml).
  The ODrive is not a candidate. The
  [Delta fallback decision](2026-09-30_delta-asda-a3-as-fallback-drive.md) does not change this.

## Consequences

- The ODrive stays in the repository only where it was used for testing. That covers the
  measurements, the identification software, the Controllino firmware and the logs that describe
  them. We keep it so that old results can be repeated and understood.
- Nothing is deleted. Old logs and decisions that mention the ODrive stay as they are. They record
  what was true at the time.
- The entry documents now say that the ODrive is for testing only: the README, the architecture
  overview, the onboarding guide and the repository profile for agents.
- The sister repository `aqtuator-business` has the same decision. Its encoder searches treated the
  ODrive as a limit on the choice. That limit no longer applies.
- If a future design really needs a drive that behaves like the ODrive, write a new decision that
  replaces this one. Do not add the ODrive back quietly.
