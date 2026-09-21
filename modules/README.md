# Modules

Stage families, each a module with the full doqs structure.

| Module | What |
| --- | --- |
| [`flexure-ball-screw-servo-stage/`](flexure-ball-screw-servo-stage/) | Linear stage with active chatter suppression: flexure guidance, ball screw, servo drive. Holds the measurement, firmware and host software of the identification work |
| [`compact-stage/`](compact-stage/) | Compact linear stage. Name reserved, nothing designed yet |

A family stays a plain folder here while it is still moving. It becomes its own Git repository, and
comes back as a submodule at the same path, when something concrete asks for it: an outside project
that wants that family alone, its own release rhythm, its own access rules, or a repository that has
grown too heavy to clone. The move keeps the history and changes no paths inside the family. See
[`doqs/docs/variants.md`](../doqs/docs/variants.md).

## Parts we buy

[`stoq/`](stoq/) is not a stage family. It is the shared parts library, mounted
as a submodule: the rails, blocks and motors that other companies make and we
only record. Nothing in it is ours.

Bought parts are read from there, never copied in here. The X-axis assembly
links the HIWIN rail and block and the MAXWELL magnet track straight out of
[`stoq/modules/`](stoq/modules/). See
[`doqs/docs/parts-library.md`](../doqs/docs/parts-library.md).
