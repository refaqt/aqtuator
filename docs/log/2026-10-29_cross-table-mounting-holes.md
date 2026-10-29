# 2026-10-29 — Compact stage: two stages screw together as a cross table

**Role(s):** engineering

## Goal

Niels Bosmans added M5 mounting holes to the base, and a 0.5 mm recess in its bottom face. With
the recess, only two strips touch the surface below, so the base does not rock. The request was
for matching threaded holes in the top carriage, so that a second stage, turned by 90 degrees,
can screw onto the first one as a cross table. Later, Niels Bosmans also added a 0.5 mm recess in
the middle of the carriage top face, so that no load rests on that area.

## Short answer

- **The top carriage first got six M5 threaded holes.** They are blind holes: they do not go
  through the plate. They sit in two rows, 200 mm apart. Each row has three holes, 80 mm apart.
- **They match the base holes of a second stage turned by 90 degrees.** The upper base then sits
  40 mm off the carriage centre, along its own travel. Only one row of three base holes fits on
  the carriage on each side. The other base holes fall outside it.
- **The four corner holes are shallow.** The roller pockets under the carriage leave only 8.5 mm
  of material there. These holes have 6 mm of thread (7 mm drill). The two middle holes have
  10 mm of thread (13 mm drill).
- **Six more holes sit in two inner rows, 20 mm inside the first rows.** Niels Bosmans asked for
  them after the first six. They have 9 mm of thread (11 mm drill). A recess in the bottom face
  leaves 14 mm of material there, and at least 2.5 mm stays under each drill point.
- **The top face has a 0.5 mm recess in the middle, 150 mm by 150 mm.** All twelve holes sit
  outside it. The inner holes keep 2.9 mm from its edge.

## Work Done

- Added three hole groups to the top carriage. Every size comes from a new parameter table
  in the part, with the reason for each value.
- Measured the part, the base and the assembly again, so the CAD check passes.
- Wrote the hole layout into the two outside interfaces of the stage: the base bottom face and
  the carriage top face. The project file that lists the interfaces says the same.

## Decisions Made

- Hole positions x = ±100 mm, y = 0 and ±80 mm, and the depths, were chosen by Niels Bosmans.
- The inner rows went to x = ±80 mm. The first request said x = ±160 mm, but that is outside
  the 210 mm plate. Niels Bosmans confirmed ±80 mm and chose 9 mm thread, 11 mm drill.
- The corner holes stay shallow (6 mm thread) instead of moving or shortening the roller
  pockets.

## Open Questions

- The two recesses (base bottom and carriage top) use typed sizes, not values from the
  parameter table. The CAD check lists them as not linked. It does not fail on them.

- 6 mm of M5 thread in aluminium is short, about 1.2 times the screw diameter. Check the screw
  length at assembly. A screw that is too long hits the floor of the hole. A screw that is too
  short may strip the thread.

<details>
<summary>Technical notes</summary>

- New objects in `carriage-top.FCStd`: `Params` (spreadsheet, inside the Part),
  `CentreMountSketch` + `CentreMountHoles`, `CornerMountSketch` + `CornerMountHoles`. Both
  sketches are attached to the Body XY plane with `AttachmentOffset.z = Pad.Length`, so they
  follow the plate thickness. Both are fully constrained, and every dimension is a `Params`
  expression. Second step: `InnerMountSketch` + `InnerMountHoles` at `Params.inner_hole_x`, built
  the same way. The top recess (`Sketch010` + `Pocket007`, by Niels Bosmans) comes last and is
  the Body tip. It was only in the open window; the agent saved `carriage-top.FCStd` before the
  commit.
- Inner rows: the recess under x = ±80 mm reaches z = 5.5 mm at the hole edge. The six holes
  removed 949.4 mm³, the full drilled volume. The smallest distance from a drilled hole to the
  recess is 2.55 mm.
- Holes: ISO metric M5x0.8, thread not modelled, tap drill 4.2 mm, angled drill point.
- Clearance check: a 13 mm drill at (±100, ±80) cuts into the roller pocket region
  (x 84.8 to 98.3 mm, ceiling at z = 11 mm) by about 0.4 mm. With the 7 mm drill, the volume
  removed by the six holes is 783 mm³. That is the full drilled volume, so no hole breaks into a
  pocket.
- The part was changed in the open FreeCAD window through the MCP add-on (`execute_code`, one
  undo step) and saved there. Fingerprints for base, carriage-top and the assembly were written
  with `freecadcmd` 1.1.4 and `cad_fingerprint.write(doc, params={})` after opening all parts,
  so the assembly links restore. The files were measured only, not saved.
- The assembly fingerprint also changes because of the base recess and holes.
- `doqs check`: all gates passed. The warnings about older fingerprints and the TA17-7 frame
  were there before.
- Mistake rules checked: [wrap crashed the open FreeCAD](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)
  (no background calls to the open window), the PowerShell rules (shell work in bash).

</details>
