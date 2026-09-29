# Architecture (SysML)

SysML requirements, block definitions and interfaces.

The requirements that measurement campaigns verify should be declared here, so that each
`modules/<family>/measurement/results/<case>/summary.md` can cite them by name rather than restating the constraint.

| File | What it holds |
| --- | --- |
| [`motor-drive.sysml`](motor-drive.sysml) | Requirements for the servo drive of the MAXWELL MK21 linear motor stages. Each requirement has a short name (`DRV-01` to `DRV-09`, and `DRV-P1` to `DRV-P3` for preferences) that a drive search can cite. The encoder requirement follows the stage encoder, which is set in one place, `currentStage`. |

See [`doqs/docs/architecture.md`](../doqs/docs/architecture.md).
