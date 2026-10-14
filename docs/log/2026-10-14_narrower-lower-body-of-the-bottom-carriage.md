# 2026-10-14 — The lower body of the bottom carriage is 2 mm narrower

**Role(s):** cad

## Goal

Give the sides of the bottom carriage space to the walls of the base. The pocket in the base became
166 mm wide earlier today, and the lower body of the carriage was 166 mm wide too.

## Work Done

- **The lower body of the carriage is now 164 mm wide, down from 166 mm.** It runs from
  x = 13 mm to x = 177 mm. Each side moved in by 1 mm.
- **Each side now has 1 mm of space to the base wall.** This was checked by calculation, with the
  carriage on the guide blocks.
- **The forcer pocket had to be repaired.** Its depth was set "up to a face": the ceiling of a
  block pocket. That face started at the side of the lower body, so it changed shape, and FreeCAD
  lost it. The pocket now points at the same ceiling in its new shape. The forcer pocket is the
  same as before: its floor is at z = 16 mm, and it removes the same volume.
- **The guide blocks and the frames did not change.** The blocks still fit with no overlap. All
  five frames are where they were.
- **The stored measurements (fingerprints) of the carriage and the base are up to date.** The
  carriage is about 3 900 mm³ smaller. The shape of the base did not change.

## Open Questions

- **The carriage edge still rests on the top of the base walls, with 0 mm of space.** The outer
  strip of the carriage is at z = 40 mm, the top of the walls. See
  [The rails in the base are 130 mm apart](2026-10-14_rails-130-mm-apart.md).
- **The forcer pocket still depends on one face of a block pocket.** A later change to the block
  pockets can break it again. A depth that is a formula would be safer, but that changes the
  design of the pocket, so it was not done here. Both done later the same day: see
  [The bottom carriage clears the top of the base](2026-10-14_carriage-clears-the-top-of-the-base.md).

## Next Steps

1. Raise the outer strip of the carriage, or lower the walls of the base.
2. Save the assembly again and write its fingerprint.

<details>
<summary>Technical notes</summary>

- `Sketch010` (the cut at the sides of the lower body): constraint 19 is now named
  `lower_body_step`, 4 → 5 mm. It is the step from the outer strip (x = 8 mm) to the side of the
  lower body. The other side follows by symmetry.
- `Pocket006` (forcer pocket): `UpToFace` stays on `Hole001` `Face2`. After the change, `Face2` is
  again the block pocket ceiling at z = 10 mm (x = 13…47, y = 0…47 mm). The first try failed with
  "Up to face: Failed to extract face" and was undone. The second try passed: no feature in error,
  and the pocket removes 193 096.64 mm³, the same as before. `Offset` stays −6 mm.
- Carriage volume: 422 375 → 418 515 mm³.
- Fit check: the carriage was placed on the blocks by calculation (carriage x → base y, block face
  at base z = 34 mm). Between z = 25 and 35 mm, the smallest distance to the walls is 1.000 mm, at
  base y = 22 and 188 mm. Blocks on the carriage frames: 0 mm³ overlap.
- The carriage had no unsaved changes besides this work. It was saved from the FreeCAD 1.1.4
  window.
- The base and the assembly were saved again from the window at 15:12. The base fingerprint was
  written again, and only the file checksum changed.
- `bash doqs.sh check` fails only on the assembly fingerprint.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  and the PowerShell rules (all shell work ran in bash).

</details>
