# 2026-10-09 — Carriage sides clear the base

**Role(s):** cad

## Goal

Change the sides of the bottom carriage so they do not hit the base block of the compact stage.

## Work Done

- **Niels cut a step into the underside of both ends of the carriage.** The step is 8 mm wide and
  78 mm long, at the start and at the end of the plate.
- **The bottom sides no longer hit the base block.** They can now go down through the gap between
  the base and the strip seal.
- **The plate lost about 5.7 cm³ of material.** The outside size is still 190 × 170 × 15 mm.
- **The fingerprint of the carriage is up to date.** The project checks pass.

## Open Questions

- The screws of the side tabs still go in from below. The question from the
  [first draft](2026-10-09_first-draft-of-the-bottom-carriage.md) is still open.

## Next Steps

1. Fix the carriage to the four rail blocks in the assembly.
2. Then check in the assembly that the carriage does not touch the base or the strip seal over the
   full travel.

<details>
<summary>Technical notes</summary>

- New features: `Sketch009` on the XY plane, two rectangles at x 0–8 mm and x 182–190 mm, y 46–124
  mm. `Pocket002` cuts them with type `UpToFace`, reversed, on top of `LinearPattern`.
- Body volume: 375 797 mm³ before, 370 145 mm³ after.
- The clearance was not checked in the assembly. The carriage is still not fixed to the rail
  blocks, so the assembly does not show its real position.
- Fingerprint written with `freecadcmd` 1.1.4 and `cad_fingerprint.write()` after `purgeTouched()`.
  The document was closed without saving. The `.FCStd` hash stayed the same.
- `bash doqs.sh check`: all gates passed. 24 typed-in sizes in the carriage are not yet linked to a
  parameter, as before.
- `modules/stoq` still has local changes that are not part of this work.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
