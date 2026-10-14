# 2026-10-14 — The bottom carriage clears the top of the base, and the forcer pocket has a formula

**Role(s):** cad

## Goal

Give the outer strip of the bottom carriage 0.5 mm of space above the walls of the base. Make the
depth of the forcer pocket a formula, so it no longer depends on one face of a block pocket.

## Work Done

- **The outer strip of the carriage is 0.5 mm higher.** Its underside is now at z = 16.5 mm in the
  carriage, up from 16 mm. With the carriage on the guide blocks, this leaves 0.5 mm of space above
  the base walls. The strip is now 9.5 mm thick instead of 10 mm.
- **The forcer pocket has a fixed depth from a formula.** It goes 6 mm deeper than the block
  pockets, so its floor stays at z = 16 mm. The step after it keeps the forcer face at z = 20 mm.
  The forcer pocket removes the same volume as before.
- **The forcer pocket now follows the block pockets.** When the block pockets get deeper or
  shallower, the forcer pocket and its frame move with them. A change to the sides of the carriage
  no longer breaks it. Both were tested and undone.
- **All fits were checked by calculation.** With the carriage on the blocks: 0.5 mm of space above
  the walls, and 1 mm of space at the sides. The blocks do not overlap the carriage. The five frames
  did not move.
- **The stored measurements (fingerprint) of the carriage are up to date.** The carriage is about
  2 100 mm³ smaller.

## Open Questions

- The 6 mm and the 10 mm in the forcer pocket formulas are typed numbers inside the formula. They
  come from the earlier design, and their reason is not written down yet.

## Next Steps

1. Save the assembly again and write its fingerprint.

<details>
<summary>Technical notes</summary>

- `Pocket006` (forcer pocket): `Type` `UpToFace` → `Length`. `Length` =
  `Pocket009.Length + 6 mm` (16 mm). `Offset` −6 → 0 mm. `Pocket009` is earlier in the feature
  chain, so there is no loop.
- `Pocket007`: `Length` = `10 mm - (Pocket006.Length - Pocket009.Length)` (4 mm, as before).
- `Sketch010`: constraint 20 is now named `outer_strip_rise`, 6 → 6.5 mm. It is the height of the
  strip underside above the block pocket ceiling (z = 10 mm).
- `Sketch017` (the step in the forcer pocket) is still attached to the floor face of `Pocket006`.
  FreeCAD moved the reference from `Face65` to `Face63` by itself.
- Tests, each undone: `Pocket009.Length` 10 → 9 mm moved the forcer pocket to 15 mm and the forcer
  frame to z = 19 mm, with no error. `lower_body_step` 5 → 6 mm gave no error.
- Carriage volume: 418 515 → 416 420 mm³. Forcer pocket: 193 096.64 mm³ removed, as before.
- Fit check: the carriage was placed on the blocks by calculation (block face at base z = 34 mm).
  Smallest distance to the wall tops: 0.500 mm. Smallest distance to the side walls: 1.000 mm.
- The carriage had no unsaved changes besides this work. It was saved from the FreeCAD 1.1.4
  window.
- `bash doqs.sh check` fails only on the assembly fingerprint.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  and the PowerShell rules (all shell work ran in bash).

</details>
