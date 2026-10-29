# 2026-10-29 — The seal strip in the assembly, preloaded, with its screws

**Role(s):** engineering, simulation, cad

## Goal

Niels Bosmans milled new pockets in the base: a 0.15 mm pocket for the seal strip with its ears,
a 0.5 mm ring pocket for the magnets, and six M4 holes. He asked to:

- draw the seal strip, 0.15 mm thick, in its preloaded state, with the carriage in the middle;
- use the simulation model, without a plastic strip on the ceiling;
- add the two countersunk preload screws and the four corner screws (ISO 7380-2, with collar),
  with the Fasteners workbench;
- leave 1 mm between each strip end and the base end;
- put rollers 1 and 4 on the strip;
- lower rollers 2 and 3 in steps of 0.5 mm and choose the pull, so that the strip touches
  neither carriage half and its fatigue life is infinite, with 20 % margin if possible;
- remove everything about the old sealing clamp.

## Short answer

- **Rollers 2 and 3 go 0.5 mm down. The pull is 270 N.** The strip then touches neither carriage
  half. Its fatigue life is infinite, with 32 % margin on the fatigue limit. That limit, 903 MPa
  at 0.15 mm, is extrapolated from the maker's values at 0.25 and 0.50 mm.
- **Any pull from 190 to 350 N also works**, with at least 20 % margin. This wide window matters,
  because the pull is set by the hole positions and can be off by tens of newtons.
- **One step is the limit.** From 1 mm down, rollers 2 and 3 sit below the flat top of
  carriage-bottom, and the strip lies on its edge at any pull.
- **Rollers 1 and 4 already sat on the strip.** The new pocket puts the strip top level with the
  base top, where the rollers already were. They stay there.
- **The strip, the six screws and the carriage in the middle are in the assembly.** The old
  sealing clamp is gone from the model, the architecture and the part list.
- **The preload screws moved inwards, to 6.5 mm from the base ends.** The magnet ring is cut in
  two around each of them. The strip end then carries the 270 N with a factor of 2.7 to yield.
  Moving the screw only 0.5 mm (to 4.5 mm) was checked too: the strip end would still yield.
- **The strip is 0.4 mm narrower (185.6 mm),** and the strip pocket moved 0.2 mm inwards on each
  side (186 mm). The strip now has 0.2 mm on each side, to the pocket and to the slope openings of
  the carriage.
- **Still open, by choice:** carriage-top runs into the four corner screw heads at both ends of
  the travel. Niels Bosmans will adapt carriage-top and the scraper later. The preload screws are
  taken out once the pull is set, so they do not count.
- All work is on branch `dev-seal-strip`, not committed.

## Work Done

### The simulation: how low, and how hard to pull

New case [`strip-seal-fit`](../../modules/compact-stage/simulation/cases/strip-seal-fit/). It uses
the solver of the seal strip designer page with the sizes of the CAD of today, no plastic strip,
and the pocket floor as the reference. It tries every drop of rollers 2 and 3 in steps of 0.5 mm
and every pull from 0 to 400 N in steps of 5 N.

| Drop of rollers 2 and 3 | Pulls with no contact | Pulls that also keep 20 % fatigue margin |
| --- | --- | --- |
| 0 mm | 205 to 400 N | 205 to 315 N |
| **0.5 mm** | **190 to 400 N** | **190 to 350 N** |
| 1 mm or more | none | none |

The pull is set by where the holes are, so it can be tens of newtons off. So the widest window
wins, and the pull goes in its middle: **0.5 mm and 270 N.**

| At 270 N | Value |
| --- | --- |
| Highest stress | 796 MPa |
| Fatigue limit at 0.15 mm (extrapolated) | 903 MPa, 32 % above the highest stress amplitude |
| Gap to carriage-top | 0.50 mm, next to rollers 1 and 4 |
| Gap to carriage-bottom | 0.08 mm, on its slope next to rollers 2 and 3 |
| Force on rollers 1 and 4 / 2 and 3 (two rollers per place) | 380 N / 112 N |
| Travel of both strip ends together | 0.21 mm |

![The strip in the channel](../../modules/compact-stage/simulation/results/strip-seal-fit/strip_fit.png)

The gap to carriage-bottom is small. Without a drop it would be about 0.2 mm, but the pull window
would be narrower.

### The CAD

- **Carriage in the middle.** The dampers touch the end walls at a carriage centre of 109 and
  331 mm, so the middle is 220 mm. The carriage moved 8.4 mm.
- **Rollers 2 and 3:** the axle slots in carriage-bottom are 6 mm deep (were 5.5 mm). Until now
  carriage-top read that depth, so rollers 1 and 4 would have gone up as well. Carriage-top now has
  its own value, 5.5 mm, so rollers 1 and 4 stay on the strip. The thinnest wall at the axle screw
  holes is still 0.8 mm.
- **The seal strip:** a new build script draws it from the pocket outline, 0.2 mm smaller on each
  side (186 mm wide), with its ends 1 mm from the base ends. Between rollers 1 and 4 it follows the
  shape from the simulation. The corner holes are 4.5 mm. The preload holes are 5 mm, 0.35 mm off
  the screw axis towards the strip middle, so their outer edge touches the screw cone.
- **The screws,** from the Fasteners workbench: two ISO 10642 M4 × 10 at the strip ends and four
  ISO 7380-2 M4 × 10 at the corners. The base has no countersink, so the cone of each preload
  screw rests on the pocket floor.
- **The sealing clamp is removed:** the two links in the assembly, the part file and its
  fingerprint, the part in `okh.toml` and the module README, and its part and interfaces in the
  architecture. A new interface, `StripScrewInterface_v1`, describes the six screws.
- **Part list:** two new rows, MEC-005 (preload screws) and MEC-006 (corner screws).

### Checks

- With the carriage in the middle, the strip overlaps nothing. It touches the rollers, as it
  should. Gaps measured in the CAD: 0.50 mm to carriage-top and 0.08 mm to carriage-bottom, the
  same as the simulation.
- `bash doqs.sh check`: all gates pass.

## Fixes after the first review

Niels Bosmans answered the three problems:

1. Carriage-top and the scraper will be adapted later. The preload screws are taken out after
   the pull is set.
2. Move the preload screw inwards, with its M4 hole 0.5 mm from the magnet ring. If that is not
   enough, cut the magnet ring in two and move the screw further in. Check which is best.
3. 0.2 mm of room on each side: a narrower strip, and the strip pocket 0.2 mm further in.

### Where the preload screw goes

A plane stress model of the strip corner, with the pull pushed into the hole edge by the screw
cone ([`strip_end.py`](../../modules/compact-stage/simulation/cases/strip-seal-fit/strip_end.py)).
Ranges come from a short and a longer contact arc.

| Preload screw from the base end | Strip left beyond the hole | Highest stress at the strip end |
| --- | --- | --- |
| 4 mm (first drawing) | 0.85 mm | 3480 to 5080 MPa |
| 4.5 mm (M4 hole 0.5 mm from the magnet ring) | 1.35 mm | 2060 to 2790 MPa |
| **6.5 mm (magnet ring cut in two)** | **3.35 mm** | **630 to 730 MPa** |
| 7 mm | 3.85 mm | 530 to 600 MPa |

![Stress at the strip end](../../modules/compact-stage/simulation/results/strip-seal-fit/strip_end.png)

The steel yields at 1975 MPa. So the hole 0.5 mm from the ring is not enough. **Chosen: the ring
cut in two, the screw at 6.5 mm.** That gives a factor of 2.7 to yield. 7 mm gains little and
leaves only 1 mm of aluminium between the M4 thread and the slot face; 6.5 mm leaves 1.5 mm. Close
to the cone itself the stress is higher, but within about 0.5 mm. There the steel may yield a
little, which a one-time load can take.

The first estimate in this entry (several thousand MPa at 4 mm) is confirmed by the model.

### Changes in the base

- `Sketch007`: the preload screw holes are now 6.5 mm from each base end (`preload_screw_x`,
  was tangent to a reference circle at 4 mm). The strip pocket sides moved 0.2 mm inwards
  (`strip_pocket_side`), so the pocket is 186 mm wide over the strip body. The ears and their
  45° steps follow; the outer edges of the ears did not move.
- New `MagnetRingSplit`: the magnet ring stays solid over 5 mm around each preload screw (the M4
  hole plus 0.5 mm on each side). So each end of the ring is now two pockets.

### Changes in the strip and the assembly

- The strip is 185.6 mm wide, and its preload holes moved with the screws (still 5 mm, 0.35 mm off
  the screw axis). The preload screws in the assembly moved to 6.5 and 433.5 mm.
- The simulation now uses 185.6 mm and 427 mm between the preload screws. The choice does not
  change: rollers 2 and 3 0.5 mm down, 270 N, 32 % fatigue margin, pull window 190 to 350 N.
- Checked in the CAD: no overlaps; 0.2 mm from each strip edge to the carriage halves, 0.50 mm to
  carriage-top above the strip, 0.08 mm to the slope of carriage-bottom.

### Who holds the pull after the preload screws come out

The four corner screws, by friction: the strip is clamped between the collar and the base. With a
typical tightening force of an M4 A2-70 screw (about 2.5 kN) and a typical friction value of 0.15
on both faces, one corner screw holds about 750 N, so two per end hold about 1500 N, against
270 N. These are typical values, not from a data sheet. Check the tightening torque.

## Problems found in the first version

### Carriage-top hits the screw heads (open, adapted later)

At the first damper touch, carriage-top overlaps the preload screw head by 31 mm³ and each corner
screw head by 29 mm³. With the dampers fully in, the overlap is about twice as large. This happens
at both ends.

### The strip end cannot carry the pull (fixed: screw at 6.5 mm)

The strip ends 1 mm from the base end, and the preload screw sits 4 mm from it. So only about
0.85 mm of strip is left between the hole and the strip end. All of the pull of one end, 270 N,
goes through that narrow bridge. Even plain tension in it gives about 1000 MPa; with the bending
of the bridge, a rough beam estimate gives several thousand MPa. The steel is 2050 MPa strong.
This is an estimate, not a calculation of the real part, but the bridge is too narrow by a large
factor.

### No room at the strip edges (fixed: 0.2 mm on each side)

The slope openings in both carriage halves are 186 mm wide, the same as the strip. The strip edges
touch their side walls.

## Decisions Made

- Niels Bosmans: lower only rollers 2 and 3 (deeper axle slots). Carriage-bottom keeps its
  shape.
- Niels Bosmans: ISO 7380-2 M4 screws (button head with collar) at the four corners.
- Niels Bosmans: remove the sealing clamp everywhere.

## Open Questions

- **Corner screw heads against carriage-top.** Niels Bosmans will adapt carriage-top and the
  scraper later. They need room over the heads: about 2.5 mm deep and 15 mm long from each end.
- **Is 0.08 mm to carriage-bottom enough?** Flatness, burrs and the pull tolerance can use it up.
  Without a drop the gap is about 0.2 mm, with a narrower pull window (205 to 315 N).
- The fatigue limit at 0.15 mm is extrapolated, and the magnet bed under rollers 1 and 4 is an
  estimate. In the CAD those rollers sit over the open slot, not on magnets.

## Next Steps

- [ ] Adapt carriage-top and the scraper to the corner screw heads.
- [ ] Choose the tightening torque of the corner screws, and check the friction on a test piece.
- [ ] Order magnet strips for the split ring: two pieces at each end.

<details>
<summary>Technical notes</summary>

- `strip_model.js` got `stick23`: the stick-out of rollers 2 and 3 alone. The floor uses it, the
  ceiling keeps `stick`. The defaults do not change; `check_model.mjs` passes.
- Model inputs: datum z = 39.85 (pocket floor), `dz = 2 − drop`, `stick = 0.5`,
  `stick23 = 0.5 − drop`, `clear = 13.65`, `liner = 0`, `length = 432`. Fatigue margin = fatigue
  limit / largest Goodman amplitude of the rainflow cycles.
- The model lets the strip sink 0.03 mm into its elastic magnet bed next to rollers 1 and 4. The
  build script stops the centre line at the pocket floor, because the base there is rigid.
- Preload hole offset: the cone of ISO 10642 M4 is 4 mm at the pocket floor and 4.3 mm at the top
  of the strip. The 5 mm hole is placed so that its outer edge touches 4.3 mm. The screw head top
  is at z = 42.33 (head height 2.48 mm).
- `cad_build` looks for `cad/params.csv`, which this module does not have. The strip build script
  reads `cad/params/default.csv` itself. New parameters `strip_*` are in that file.
- The strip and the six screws are held by grounded joints in the assembly. The joints are hidden.
- Fingerprints rewritten from the open FreeCAD window for base, carriage-bottom, carriage-top,
  sealing-strip and the assembly. The base fingerprint now includes the pockets Niels Bosmans
  added.
- The name check crashed on Windows with a text encoding error in the console. With
  `PYTHONUTF8=1` all gates pass.
- Strip end model: CST triangles, plane stress, E = 185 GPa, nu = 0.3; mesh size 0.005 mm at the
  hole, growing with distance; the cut 40 mm from the strip end held along x. Results with
  0.0025 mm differ by less than 2 %.
- First ligament estimate: bridge 0.85 × 0.15 mm, about 5 mm long, 270 N in its middle. Tension alone
  over two sides: 270 / (2 × 0.85 × 0.15) ≈ 1060 MPa. In-plane bending, ends held: M = F L / 8,
  W = t h² / 6, about 9000 MPa.
- Mistake rules checked: fatigue (the limit is marked as extrapolated, the bridge stress as an
  estimate), FreeCAD (only `execute_code`, never `doqs wrap`; one slow probe blocked the window
  for about nine minutes and finished on its own), PowerShell (all shell work in bash), tooling
  (`.agents/` and `doqs/` left as they are).

</details>
