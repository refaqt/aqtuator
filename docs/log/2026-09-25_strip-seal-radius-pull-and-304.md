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

- [x] Confirm the layout against the CAD model. Confirmed on 2026-09-28, see the update below.
- [ ] Design a spring at one end of the strip to set the preload during fitting: about 54 N
      on the 150 mm strip, with at least 3 mm of travel. Both ends are clamped afterwards.
- [ ] Choose a way to open the bend: a longer ramp, a lower rise, or a small gap at rollers 1
      and 4. Check how far the strip then leaves the profile, with the magnets.
- [ ] Keep 301 (11R51). Drop 304 for this strip thickness.

## Update, 2026-09-28

Answers to the open questions above:

- **The strip is about 150 mm wide**, not 40 mm. The limits per mm of width stay the same.
  The most pull that keeps 30 mm is now 0.36 N/mm times 150 mm, which is **about 54 N**.
- **The layout is read correctly off the sketch**, and the dimensions are right.
- **The ends are clamped after the preload.** A soft spring at one end sets the pull during
  fitting. After that, both ends are clamped. A spring left in place could let the strip
  shift and buckle.
- **0.25 mm is not a requirement.** It was an investigation. A thicker strip is less likely
  to wrinkle or be punctured. A thinner strip has a higher fatigue limit.

What this changes:

- **Clamping both ends after the preload does not bring back the large pull.** The earlier
  result of 56 to 223 N/mm was for a strip that is fixed flat first and then pushed up by
  the carriage. Here the carriage is already in place when the strip is clamped, so the
  extra 2.4 mm of path is already in the strip. When the carriage moves, the bump moves with
  it and the path length stays the same. The pull stays at the preload.
- **The bump itself acts as a soft spring.** Near 0.36 N/mm, a change of 0.1 mm in strip
  length changes the pull by only about 0.08 N/mm, because the strip changes the height of
  its arch. Stretching the steel of a 1 m strip by 0.1 mm would change it by about 4.6 N/mm.
  So small length changes after clamping, for example from heat or creep, change the pull
  only a little. This is an estimate from the current model. The new model must check it,
  also with the carriage near the clamps.
- **A wide strip may be about 9 percent more stressed.** A strip much wider than it is thick
  cannot curl sideways when it bends. This makes it stiffer, and the bending stress goes up
  by about 1 / (1 − 0.3²), which is 1.1. The model does not include this yet. At 30 mm that
  could mean about 850 MPa instead of 771 MPa. This is an estimate. It depends on how Alleima
  calculated the stress in their own fatigue tests. Their test strips are also much wider
  than they are thick, so the effect may already be in their 775 MPa.

### Next step

Build a model and an animation of the strip as the carriage moves along it, in a next commit.
It should use the 150 mm width, a preload set by a spring and then two clamped ends, and
show the tightest radius and the pull at each carriage position.

<details>
<summary>Checks</summary>

The solver was compared with a closed form answer for a strip under pull over two point
supports, with no profile. At 2, 10 and 40 N/mm it agrees within 3 percent. The script
repeats this check at 10 and 40 N/mm on every run and stops if it fails. A grid of 0.2, 0.1,
0.05 and 0.025 mm gave a tightest radius of 19.4, 19.3, 19.2 and 19.1 mm at 5 N/mm, so 0.05 mm
is fine enough.

The case needs `numpy` and `scipy`, like the encoder case needs `magpylib`.

Update of 2026-09-28: the soft-spring estimate comes from the extra path length that the
model gives at 0.3 and 0.5 N/mm, 2.513 mm and 2.253 mm. That is 1.3 mm of length per N/mm
of pull. The steel stretch is E t / L = 185000 × 0.25 / 1000 = 46 N/mm per mm of length,
for a 1 m strip.

</details>
