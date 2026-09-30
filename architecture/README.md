# Architecture (SysML)

SysML requirements, block definitions and interfaces for the repository as a whole.

Each stage family keeps its own architecture in its module. This folder is empty until there is
something that holds for more than one family.

| Family | Architecture |
| --- | --- |
| Compact stage | [`modules/compact-stage/architecture/`](../modules/compact-stage/architecture/): the stage requirements (`STG-01` to `STG-14`) with the parts and their interfaces in `compact-stage.sysml`, and the servo drive requirements (`DRV-01` to `DRV-09`, `DRV-P1` to `DRV-P3`) in `motor-drive.sysml`. |

The requirements that measurement campaigns verify should be declared in SysML, so that each
`modules/<family>/measurement/results/<case>/summary.md` can cite them by name rather than restating the constraint.

See [`doqs/docs/architecture.md`](../doqs/docs/architecture.md).
