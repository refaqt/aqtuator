# 2026-09-25 — A measured seal strip, and a way to preload ours

**Role(s):** engineering, measurement, hardware

## Goal

Find a real value for the seal strip thickness, and find a simple way to put a known pull
in the strip when it is fitted.

## Work Done

- Measured the steel seal strip on an old linear axis in the lab. It is **0.25 mm** thick.
- This is two and a half times the 0.1 mm strip in our current design. It is also the
  thickness at which Alleima measure their fatigue limit of 775 MPa, so for a strip of this
  size a measured value exists and no extrapolation is needed.
- Worked out a concept to preload the strip at fitting, which means to pull it tight before
  it is locked in place:
  1. Fix each end of the strip with two or three countersunk screws (screws with a sunken,
     cone shaped head).
  2. Make the holes in the strip a little off centre from the threaded holes in the frame.
     Each strip hole sits slightly closer to the middle of the strip than its threaded hole.
  3. When a screw is tightened, its cone shaped head presses on the edge of the hole and
     pulls the strip towards the screw axis. That movement stretches the strip. The size of
     the offset sets how far it is stretched, so the pull comes from the drawing and not
     from the fitter's hand.
  4. Once the strip is under pull, a bar over the full length of the strip clamps it and
     locks it in place.

## Decisions Made

No decision yet. This is a concept to test. It connects to
[Strip seal material and roller size](../decisions/2026-09-22_strip-seal-material-and-roller-size.md),
which says the pull in the strip must stay well under 26 N per mm of width and must be
measured, not assumed. With this concept the pull becomes something the design sets.

## Open Questions

- Do we keep 0.1 mm, or move to 0.25 mm like the old axis? At the same bending radius the
  bending stress grows in direct proportion to thickness. A thicker strip is also much
  stiffer, so it bridges the rollers more. The seal strip model must be run again at
  0.25 mm before the answer is known.
- What pull do we want in the strip, and what hole offset gives it? The offset depends on
  the strip length, the strip material and the screw head angle.
- Is the preload at one end only, or at both ends?
- Does the cone shaped head damage the edge of a thin hole? The strip maker says cracks
  start at edge damage. The holes may need to be made in a way that leaves a clean edge.
- Does the clamping bar hold the pull over time, or does the strip creep back?

## Next Steps

- [ ] Note the maker and the model of the old axis, if it can still be read, and measure
      its strip width too.
- [ ] Run the seal strip model at 0.25 mm and compare it with 0.1 mm.
- [ ] Choose a target pull, then calculate the hole offset for it.
- [ ] Make a short test piece with two or three off centre holes and check the pull with a
      spring scale or a force gauge.
