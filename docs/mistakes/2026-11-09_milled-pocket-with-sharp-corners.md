# 2026-11-09 — A milled pocket with sharp corners, and other parts not made for their process

## What happened

In the cooling redesign of the compact stage, four details could not be made or did not follow the
request:

- The deeper part of the motor cable slot ended in straight lines. The corners where they met
  the slot walls had no radius, so no end mill can cut them.
- Two countersunk holes near the side face could not be reached by a mill.
- The printed cooling block had no flat face to stand on the build plate.
- The cable clamps sat in new, wider pockets with rounded corners. Niels had asked for clamps in
  the existing cable slots, with 0.1 mm of room on each side.

Niels Bosmans found all four in his review on 2026-11-09.

## Why it went wrong

The model was checked for fit and for overlaps, but not against the way each part is made. No
rule asked for that check. For the clamps, the request "0.1 mm of space on each side of the cable
pocket" was read as a new pocket, without asking.

## Prevention rule

- Check every part against its process before you say it is done. Milling: a radius at every
  inside vertical corner, at least the radius of the end mill, and a tool can reach every hole,
  countersink and pocket from the side it is cut from. 3D printing: one flat face for the build
  plate.
- When a part must fit in an existing slot or pocket, take its sizes from that feature. If a
  request can mean a new feature or an existing one, ask.
- The rule is in the shared FreeCAD skill (refaqt/refaqt-agents#20).

## Related

- [Log of the redesign and the review fixes](../log/2026-11-09_cooling-block-parametric-festo-fittings-cable-clamps.md)
- [Cooling block to the side face](../decisions/2026-11-09_cooling-block-to-the-edge-with-festo-fittings.md)
