# 2026-11-09 — The cooling block and the cable clamp were built as raw shapes

## What happened

On 2026-11-06 the printed cooling block and the printed cable clamp were made by a build script
that computed each solid with Part maths (boxes, cylinders, fuse, cut). The script put the result
into the model as one raw shape. The model had no sketches and no features. Nobody could change a
size in FreeCAD, and the parameter check could not see the sizes. Niels Bosmans noticed it on
2026-11-09.

## Why it went wrong

The shared CAD rules said "never type a number" and "fully constrain every sketch", but did not
say that a part must be made of sketches and features at all. A raw shape has no sketch, so it
broke no written rule, and no check warned about it.

## Prevention rule

- Build every part from PartDesign features: fully constrained sketches, then Pad, Pocket, Hole,
  Pipe or a PartDesign primitive. Bind every size to the `Params` sheet. Use a raw shape only when
  no feature can make the shape, and write in the build script why.
- The rule is now in the shared FreeCAD skill (refaqt/refaqt-agents#19) and in the doqs CAD guide
  (refaqt/doqs#52). The doqs build helper now prints a warning for every part built on a raw
  shape.

## Related

- [Cooling block to the side face, with Festo fittings](../decisions/2026-11-09_cooling-block-to-the-edge-with-festo-fittings.md)
- [Log of the rebuild](../log/2026-11-09_cooling-block-parametric-festo-fittings-cable-clamps.md)
