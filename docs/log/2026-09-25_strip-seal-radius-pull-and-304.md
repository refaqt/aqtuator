# 2026-09-25 — The 0.25 mm seal strip: radius, pull, and 304 instead of 301

**Role(s):** engineering, simulation

## Goal

A new carriage sketch runs the 0.25 mm seal strip over four 10 mm rollers. It draws each ramp
as two arcs of 30 mm radius. Three questions: can 304 stainless replace 301 if the radius
stays above 30 mm, how hard must the strip be pulled to take those arcs, and how much smaller
can the radius go.

## Work Done

- Built a model of the strip under pull, lying on the profile and held only by the rollers, in
  [`simulation/cases/strip-seal-preload/`](../../simulation/cases/strip-seal-preload/).
  Results: [summary](../../simulation/results/strip-seal-preload/summary.md).
- Collected data for 304. EN 10151 sells 1.4301 strip only up to Rm 1300 to 1500 MPa, while
  1.4310 goes to 1900 to 2200 MPa. ASTM A666 stops 304 at half hard, yield at least 760 MPa.
  No maker publishes a fatigue limit for 304 strip. The estimate from belt grades is 420 to
  620 MPa.
- Found that 304 does not work at 30 mm. The 0.25 mm strip carries about 750 MPa there, which
  is at the yield of the strongest 304 and above its fatigue range. It needs 36 to 54 mm.
- Found that 301 at 30 mm is exactly at its measured fatigue limit: 771 MPa against 775 MPa,
  at 50 percent survival. There is no margin.
- Found that pull does the opposite of what was expected. The strip is stiff enough to spread
  the bend by itself. Pull makes it tighter. The strip keeps 30 mm only up to 0.36 N per mm of
  width, 15 N on a 40 mm strip.
- Found that the tightest point is where rollers 1 and 4 press the strip onto the profile.
  That point works like a clamp. Lifting those rollers 0.5 mm off the strip doubles the
  radius, but the strip then leaves the profile just outside the carriage.
- Found that the strip cannot be fixed hard at both ends. The path over the carriage is 2.4 mm
  longer than a flat strip, and stretching the strip by that much adds 56 to 223 N per mm of
  pull.

## Decisions Made

No decision yet. The results change the preload concept from the
[earlier entry today](2026-09-25_strip-seal-thickness-and-preload.md). A fixed stretch set by
off centre screws cannot work alone. One end of the strip needs a soft spring that keeps the
pull low while the carriage moves.

## Mistakes

None new. The prevention rules from
[the fatigue mistake entry](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md)
were applied: supplier data at the real thickness, the load case stated, and the radius
computed from what holds the strip, not from the drawing.

## Open Questions

- Is the layout read correctly off the sketch? Rise 6 mm, roller 1 to roller 2 26.2 mm,
  roller 2 to roller 3 119 mm, and rollers 1 and 4 touching the strip on the profile.
- What is the strip width?
- Is 0.25 mm needed? At 0.10 mm the 301 strip has no fatigue limit down to about 9 mm.

## Next Steps

- [ ] Confirm the layout against the CAD model and run the case again.
- [ ] Design a spring at one end of the strip: about 15 N on a 40 mm strip, with at least
      3 mm of travel.
- [ ] Choose a way to open the bend: a longer ramp, a lower rise, or a small gap at rollers 1
      and 4. Check how far the strip then leaves the profile, with the magnets.
- [ ] Keep 301 (11R51). Drop 304 for this strip thickness.

<details>
<summary>Checks</summary>

The solver was compared with a closed form answer for a strip under pull over two point
supports, with no profile. At 2, 10 and 40 N/mm it agrees within 3 percent. The script
repeats this check at 10 and 40 N/mm on every run and stops if it fails. A grid of 0.2, 0.1,
0.05 and 0.025 mm gave a tightest radius of 19.4, 19.3, 19.2 and 19.1 mm at 5 N/mm, so 0.05 mm
is fine enough.

The case needs `numpy` and `scipy`, like the encoder case needs `magpylib`.

</details>
