# Compact stage

Compact linear stage.

Empty on purpose. The module is reserved. Nothing here is designed yet: no requirements, no
architecture, no CAD, no bill of materials.

## Next

1. Write the requirements in `architecture/`.
2. Decide what is a number and what is a structure. A travel length is a parameter of one shared
   core. A different drive or a different feedback sensor is a separate option module combined by a
   thin composition module. The rules are in
   [`doqs/docs/variants.md`](../../doqs/docs/variants.md).
3. Add `catalog.toml` once there are real compositions to sell. The commercial name goes there, not
   in a folder name.
