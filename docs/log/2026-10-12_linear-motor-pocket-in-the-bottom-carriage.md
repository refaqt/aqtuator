# 2026-10-12 — Linear motor pocket and cooling channel in the bottom carriage

**Role(s):** cad

## Goal

Make room in the bottom carriage of the compact stage for the moving part of the linear motor, and
cool the motor with water.

## Work Done

- **Niels cut a pocket for the linear motor into the bottom of the carriage.** The pocket is 10 mm
  deep, in two steps. The first step is 6 mm deep and about 88 × 130 mm. The second step is 4 mm
  deeper. Later in the day Niels made the second step as wide as the first one, about 88 × 130 mm.
- **Only 5 mm of material is left above the pocket.** The carriage is 15 mm thick.
- **Niels added six 4.5 mm holes through that thin floor** to fix the motor to the carriage.
- **A cooling channel is cut 1 mm deep into the floor of the motor pocket.** The motor closes the
  channel from below. The channel is a double spiral: the water goes in, turns in the middle, and
  comes back out between its own loops. Both ends sit side by side, so a custom connector on the
  top of the carriage can reach them. That connector can then lead the water out on any of the
  four sides.
- **The channel can be milled with a 4 mm tool.** It is 4 mm wide. All outer corners have a radius
  of 4.5 mm, and all inner corners have a radius of 0.5 mm. The distance from one pass to the next
  is 5.2 mm everywhere, so the walls between the passes are 1.2 mm thick.
- **The channel stays clear of the motor holes.** The nearest motor hole is 2.55 mm away. The
  channel stays 5 mm inside the edge of the pocket floor.
- **The sketch of the channel is fully driven by constraints.** Seven named sizes set the whole
  shape: tool diameter, outer radius, pitch, and four positions. A change to one of them keeps the
  shape regular.
- **Corners that share one centre were tried and rejected.** They gave walls of the same thickness
  in the corners too, but Niels found the version with equal radii better.
- **The carriage is lighter.** The motor pocket and the cooling channel removed about 48 000 mm³
  together. The outside size is still 190 × 180 × 15 mm.
- **The stored measurements of the carriage are up to date.** The project checks pass.

## Open Questions

Niels noticed these problems with the motor pocket. Nothing was changed for the first and third
one yet.

- **There is little space for the motor cable.** The cable needs a path from the motor out of the
  carriage.
- **There is little space for cooling.** The motor makes heat, and the pocket leaves almost no room
  for air. The cooling channel is a first answer.
- **The carriage can be made thicker on the bottom side.** That would give more room for the cable
  and the cooling, and more material above the pocket.
- **The channel needs a seal.** Water must not leak between the motor and the floor of the pocket.
  How to seal it is not decided yet.
- **The holes from the top to the two channel ends are not in the model yet.** They depend on the
  design of the connector.

## Next Steps

1. Decide how much thicker the carriage can be on the bottom side. Check the gap to the base and to
   the stator first.
2. Plan a path for the motor cable.
3. Design the cooling connector, the holes to the channel ends, and the seal.

<details>
<summary>Technical notes</summary>

- Motor pocket: `Pocket006` (6 mm, `Sketch016` on the bottom face, x 48–136 mm, y 25–155 mm),
  `Pocket007` (4 mm, `Sketch017` on the floor of `Pocket006`, now x 48–136 mm, y 25–155 mm, was
  x 48–125 mm in the first commit), `Hole002` (4.5 mm, `Sketch018` on the top face, six circles in a
  50 × 70 mm pattern).
- Cooling channel: `Pocket008`, 1 mm, `Sketch019` on the floor of the motor pocket (z = 10 mm).
  It removes 3546 mm³. Channel outline x 74.8–115.2 mm, y 30–150 mm, ends at y = 115 mm.
- `Sketch019` named sizes: `tool_diameter` 4, `outer_radius` 4.5, `channel_pitch` 5.2, `channel_x`
  74.8, `channel_end_y` 115, `channel_top` 30, `channel_bottom` 150. Equal spacing comes from hidden
  helper lines with "equal" constraints. The sketch has 0 degrees of freedom and no redundant or
  conflicting constraints.
- The pitch cannot go below 5 mm. The turn in the middle of the spiral needs two tool-path corners
  of 2.5 mm.
- Body volume: 257 404 mm³ after the first commit of the day, 249 666 mm³ now.
- Fingerprint written with `freecadcmd` 1.1.4 and `cad_fingerprint.write()` after `purgeTouched()`.
  The document was closed without saving. The `.FCStd` hash stayed the same.
- 56 typed-in sizes in the carriage are not yet linked to a parameter.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
