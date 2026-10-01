# 2026-10-01 — The base has pockets for the linear motors

**Role(s):** cad

## What happened

The base part of the compact stage now has pockets for the linear motors. The motors are built
from segments of different lengths, so the pockets cannot have milled reference edges. A fixed edge
would only fit one segment length.

The motors will be aligned with locating pins instead. The pins work for any segment length.

The CAD fingerprint of the base was written again, so the CAD check passes for all six files. The
pin holes are not modelled yet.

## Decisions

- **Locating pins, not milled reference features.** Segments of varying length make a milled
  reference impossible. Pins can be placed to suit the segments in use.

## Open Questions

- Where do the pin holes go, and what pin size do we use?

## Next Steps

- Model the pin holes in the base.

<details>
<summary>Technical notes</summary>

- The fingerprint was rewritten headless with `cad_fingerprint.write()` in FreeCAD 1.1.
- The base now holds three pockets (`Pocket`, `Pocket001`, `Pocket002`) on top of the `Block` pad.

</details>
