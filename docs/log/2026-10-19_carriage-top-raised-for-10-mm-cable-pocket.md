# 2026-10-19 — The bottom carriage is 2.5 mm taller, so the cable pocket can be 10 mm deep

**Role(s):** cad

## Goal

The cable pocket at the side of the bottom carriage (`Pocket014`) was only 5 mm deep. It must be
10 mm deep. The shoulders were only 9.5 mm thick (z = 16.5 to 26 mm), so a 10 mm pocket cut
through them. The pocket floor must keep a 2 mm wall.

## Work Done

- **The shoulder underside cannot move down.** In the assembly it sits 0.5 mm above the top of the
  base walls. So the top face moved up.
- **The bottom carriage is 28.5 mm tall, up from 26 mm** (`Pad.Length`). 16.5 + 10 + 2 = 28.5 mm.
- **The cable pocket is 10 mm deep, up from 5 mm.** Its floor is at z = 18.5 mm. That leaves
  2 mm of material above the shoulder underside.
- **The screw lengths do not change.** Two counterbore depths now follow the top face, so their
  floors stay where they were:
  - block screws (`Pocket004`): `Pad.Length - 16.5 mm`, floor at z = 16.5 mm;
  - forcer screws (`Hole002`): `HoleCutDepth = Pad.Length - 21.6 mm`, floor at z = 21.6 mm.
- **Everything else measured from the top moved up with it:** the slots and small tapped holes
  over the blocks, the corner chamfers, and the sketches attached to the top face. The slanted end
  faces and the shoulders follow the top edge of the pad by themselves.
- **Checked by sections in FreeCAD:** one valid solid, no recompute errors, a 2 mm floor under the
  whole pocket, no lip at the ends.
- **The stage is now 52.5 mm high, up from 50 mm** (without the top carriage, which is still
  empty). The limit in the requirements is 60 mm.
- **The fingerprints of the bottom carriage and the assembly are up to date.**

## Open Questions

- **The top carriage has no geometry yet.** When it gets some, it must sit on z = 28.5 mm of the
  bottom carriage. The stage then has 7.5 mm left under the 60 mm limit.
- **The slanted end faces are a little steeper.** They still start 30 mm from the end, but now
  rise 14.5 mm instead of 12 mm.
