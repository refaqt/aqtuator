# 2026-10-09 — Stiffer bottom carriage

**Role(s):** cad

## Goal

Make the bottom carriage of the compact stage stiffer, and keep it clear of the base.

## Work Done

- **Niels replaced the side tabs with two solid side walls.** Each wall is 8 mm thick and runs
  along one end of the plate, over 140 mm of its width. The walls are as high as the plate, 15 mm.
- **The old step cuts at the ends are gone.** The new walls replace them.
- **Niels cut away the bottom of both side walls.** The cut is 8.3 mm high and runs over the full
  width of the plate. It stops the walls from hitting the base.
- **The plate is a bit heavier than before.** It has about 3.7 cm³ more material. The outside size
  is still 190 × 170 × 15 mm.
- **The fingerprint of the carriage is up to date.** The project checks pass.

## Open Questions

- The block holes in the carriage put the two rows of rail blocks 130 mm apart. The rails in the
  assembly are 128 mm apart. One of the two must change.

## Next Steps

1. Fix the 2 mm difference between the block holes and the rails.
2. Fix the carriage to the four rail blocks in the assembly.
3. Then check in the assembly that the carriage does not touch the base or the strip seal over the
   full travel.

<details>
<summary>Technical notes</summary>

- Feature tree now: `Pad` (15 mm), `Hole` (`Sketch001`), `Pocket001` (`Sketch003`, sloped ends),
  `Pad001` (8 mm, `Sketch009` on the YZ plane, y 15–155 mm, z 0–15 mm), `Mirrored` (about
  `DatumPlane` at x = 95 mm), `Pocket` (`Sketch010` on the XZ plane, x 0–8 and 182–190 mm,
  z 0–8.33 mm, through all).
- Features from the earlier drafts that are no longer in the model: the side tabs (`Pad001` with
  `Sketch006`), `Hole001`, `Hole002` and the step cut `Pocket002`.
- Body volume: 370 145 mm³ before, 373 837 mm³ after. The cut in the walls removed about
  20 300 mm³.
- The clearance was not checked in the assembly. The carriage is still not fixed to the rail
  blocks.
- Fingerprint written with `freecadcmd` 1.1.4 and `cad_fingerprint.write()` after `purgeTouched()`.
  The document was closed without saving. The `.FCStd` hash stayed the same.
- `bash doqs.sh check`: all gates passed. 14 typed-in sizes in the carriage are not yet linked to a
  parameter (24 before).
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
