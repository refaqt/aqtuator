# 2026-10-12 — Idea: a path for the motor cable in the bottom carriage

**Role(s):** cad

## Goal

Find a way to bring the cable of the linear motor from the bottom carriage to the top of the
stage. The motor part that moves (the forcer) sits under the carriage, so its cable starts there.

## Work Done

- **Niels drew an idea by hand.** It is only an idea. The CAD model of the bottom carriage has not
  changed.
- **The forcer sits in a pocket in the bottom carriage.** The pocket is a rounded rectangle in the
  middle of the plate, between the rows of rail block holes.
- **A slot in the plate guides the motor cable.** The slot starts at the top corner of the forcer
  pocket. It runs up, then across the plate to the right, then down along the right side.
- **A hole at the end of the slot takes the cable to the top.** The hole sits near the right edge
  of the plate, between the second and the third row of holes.

![](images/2026-10-12-01.jpg)

Hand sketch of the bottom carriage seen from above: the forcer pocket in the middle, the cable slot,
and the exit hole to the top on the right.

## Open Questions

- How wide and how deep must the slot be? This depends on the cable diameter and its smallest
  bending radius. Both must come from the motor data sheet.
- Does the slot make the plate too weak near the rail block holes?
- Does the exit hole clear the top carriage and its screws?
- The note in the top left corner of the sketch is cut off. It seems to name a screw type
  ("…head screw"). Niels can say what it is for.

## Next Steps

1. Read the cable diameter and bending radius in the motor data sheet.
2. Draw the forcer pocket, the cable slot and the exit hole in the CAD model of the bottom
   carriage.
3. Check the stiffness of the plate with the slot in it.

<details>
<summary>Technical notes</summary>

- Source: photo of a hand sketch on squared paper, sent by Niels on 2026-10-12. It was made smaller
  (1200 × 1600 px) before it was added.
- `modules/compact-stage/cad/parts/carriage-bottom/carriage-bottom.FCStd` was not changed. No
  fingerprint was written.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
