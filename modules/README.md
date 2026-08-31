# Modules

Sub-modules of the machine, each with the full doqs structure. Not yet populated — mechanical
breakdown follows the actuator design.

When the linear-stage family is added, follow the proposed ADR
[`docs/decisions/2026-08-31_linear-stage-variant-structure.md`](../docs/decisions/2026-08-31_linear-stage-variant-structure.md):
shared core under `linear-stage/`, length as `cad/params/` models, motor and feedback as
nested modules plus thin composition folders (`linear-stage-stepper`, …). Do not encode
travel or motor type in a way that requires one Git repo per SKU.
