# 2026-10-12 — Linear motor pocket in the bottom carriage

**Role(s):** cad

## Goal

Make room in the bottom carriage of the compact stage for the moving part of the linear motor.

## Work Done

- **Niels cut a pocket for the linear motor into the bottom of the carriage.** The pocket is 10 mm
  deep, in two steps. The first step is 6 mm deep and about 88 × 130 mm. The second step is 4 mm
  deeper and about 77 × 130 mm.
- **Only 5 mm of material is left above the pocket.** The carriage is 15 mm thick.
- **Niels added six 4.5 mm holes through that thin floor** to fix the motor to the carriage.
- **The carriage is lighter.** The pocket removed about 40 000 mm³. The outside size is still
  190 × 180 × 15 mm.
- **The stored measurements of the carriage are up to date.** The project checks pass.

## Open Questions

Niels noticed these problems with the new pocket. They are logged only. Nothing was changed for
them yet.

- **There is little space for the motor cable.** The cable needs a path from the motor out of the
  carriage.
- **There is little space for cooling.** The motor makes heat, and the pocket leaves almost no room
  for air or a cooling channel.
- **The carriage can be made thicker on the bottom side.** That would give more room for the cable
  and the cooling, and more material above the pocket.

## Next Steps

1. Decide how much thicker the carriage can be on the bottom side. Check the gap to the base and to
   the stator first.
2. Plan a path for the motor cable.
3. Plan how to cool the motor.

<details>
<summary>Technical notes</summary>

- New features: `Pocket006` (6 mm, `Sketch016` on the bottom face, x 48–136 mm, y 25–155 mm),
  `Pocket007` (4 mm, `Sketch017` on the floor of `Pocket006`, x 48–125 mm, y 25–155 mm),
  `Hole002` (4.5 mm, `Sketch018` on the top face, six circles in a 50 × 70 mm pattern).
- Body volume after this change: 257 404 mm³. `Pocket007` alone removed 39 892 mm³.
- Fingerprint written with `freecadcmd` 1.1.4 and `cad_fingerprint.write()` after `purgeTouched()`.
  The document was closed without saving. The `.FCStd` hash stayed the same.
- 46 typed-in sizes in the carriage are not yet linked to a parameter.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
