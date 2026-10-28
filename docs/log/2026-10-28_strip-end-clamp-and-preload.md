# 2026-10-28 — Clamping the seal strip ends and setting the pull, together with the scraper

**Role(s):** engineering, cad

## Goal

Design how each end of the seal strip is held and how the pull in the strip is set. It must fit
with the scraper at the carriage ends, the end stop dampers and the length limit of the stage.
The rules from Niels Bosmans, collected during the day:

- For maintenance, only the top and the long sides of the stage can be reached.
- The base is machined from the top only. Slots are preferred, like the slots for the damper nuts.
- Few parts, no open pockets where chips can fall in, and a mechanism users cannot reach.
- The strip is now 0.15 mm thick.
- Record his concept for the strip ends, shown in his own drawing below.
- Is there enough travel for 125 N? He expects that pull to keep the strip down, so that it does
  not hit carriage-top between the bottom rollers.

## Short answer

- **The strip is now 0.15 mm thick everywhere it is set.** It is in the requirements model and
  in a new decision record. The scraper check uses it too.
- **The concept of Niels Bosmans is recorded in his own drawing, with notes.** Two inserts at
  each strip end, one near each side edge. Each insert sits in a hole in the strip, with no thread
  and no nut. A countersunk screw presses it into the hole. The screw hole in the base sits a
  little off the centre of the countersink, so tightening the screw pulls the strip.
- **The concept is feasible, best with the insert sunk flush with the strip.** The groove, the
  tapped hole and the magnet pockets are all made from the top and stay in solid material. A flush
  insert clears carriage-top, carriage-bottom, the scraper and the top rollers, even in a crash,
  with no change to the carriage. As drawn, 1.05 mm above the strip, the insert is hit by the
  scraper lips and carriage-top at the end of the usable travel. It then needs the stepped lips
  of the drawing and a longer scraper pocket in carriage-top at the insert.
- **Under the carriage the pull is even across the width,** although it enters at the four
  corners. Only with the carriage at the end of its travel does the first bottom roller see an
  uneven pull: 71 % of the average in the strip middle, 156 % at the edges. Within 30 mm of the
  strip ends the middle of the strip carries almost no pull, so the magnets must hold it flat.
- **Little travel is needed for 125 N.** Both strip ends together must move only 0.11 to 0.24 mm
  from hand-tight to 125 N.
- **But the travel sets the pull far too sharply.** Near 125 N, 0.1 mm more travel adds 50 to
  100 N. So the positions of the holes in the strip and the base decide the pull, to a few
  hundredths of a millimetre.
- **125 N does not keep the strip off carriage-top.** The strip bows about 2 mm above the bottom
  rollers, and the room there is only 0.35 mm. It presses on carriage-top with about 186 N at any
  pull up to 250 N. Tape under carriage-top would turn that into a friction force of 9 to 37 N
  (typical friction values, not measured), against 180 N of continuous motor force.
- **A ceiling 1.5 to 2 mm higher solves it.** The force on carriage-top then drops to 2 to 16 N,
  and a lower pull is enough.

![The concept of Niels Bosmans, with notes](images/2026-10-28-04.png)

![Strip model](../../modules/compact-stage/simulation/results/strip-pull/strip_model.png)

## Work Done

### Versions 1 and 2, dropped

- **Version 1** clamped bent-down tabs on the end face of the base. The screws could only be
  reached from the end, and the tapped holes ran sideways into the base.
- **Version 2** hung bent-down tabs on the pins of a bar in steps milled from the top. Niels
  Bosmans rejected it: the bar is not guided, so the pins may not hold the tab; the cut corners
  beside the tabs may tear; the sharp 90° bend of a hard strip needs high forces; it has many
  parts; chips fall into the open steps; and users can reach the mechanism.

### Version 3: the concept of Niels Bosmans

The drawing above is his, unchanged. The numbers and the text beside it are notes added to it.
His original drawing is kept as [image 03](images/2026-10-28-03.png).

- Each strip end has two inserts, one near each side edge. The drawing shows one side; the
  other side is the mirror image.
- The insert has no thread and no nut. It sits in a hole in the strip. A countersunk (sunken
  head) screw presses it into that hole.
- The screw hole in the base sits a little off the centre of the countersunk hole in the insert.
  Tightening the screw centres the hole, so the insert, and the strip with it, move towards the
  base end. That sets the pull. The insert spreads the pull into the strip, so the screw head
  does not press on the strip.
- Two flat faces on the insert slide in a small groove in the base, so the insert cannot turn.
- Near the insert the strip is a little wider, so the insert sits on a corner of the strip.
- The scraper lips turn back at an angle at the insert, so they pass behind it.
- Magnets in pockets in the base hold the strip down.

A first reading of this concept on the same day put one insert, with a flange and a nut, on the
centre line. That was a misreading, and it is removed.

### Is the concept feasible?

The concept was built from the drawing in the case
[`strip-end-insert`](../../modules/compact-stage/simulation/cases/strip-end-insert/) and checked
against the CAD of the base, both carriage halves, the scraper and the top rollers. The scale of
the drawing comes from the 74.1 mm pitch of the carriage-top screws in it: 3.44 pixels per mm.
Laid over the CAD at that scale, the half-round pocket, the damper pocket and the carriage screws
of the drawing fall on the CAD.

![The drawing laid over the CAD, and the modelled parts](../../modules/compact-stage/simulation/results/strip-end-insert/overlay.png)

| Part | Size used, read from the drawing or chosen |
| --- | --- |
| Insert | Ø7.5 mm, centred 11.6 mm from the base end and 13.2 mm from the base side, so over the side wall. Two flat faces 6 mm apart. 1.7 mm high: the M2.5 countersink (1.5 mm) plus 0.2 mm. |
| Screw | ISO 14581 M2.5 × 6, countersunk. The insert can travel 0.25 mm before it is centred. |
| Groove | 6.1 mm wide, milled from the top along the travel, with round ends. Two depths checked: 0.5 mm (insert as drawn, 1.05 mm above the strip) and 1.55 mm (insert top flush with the strip top). |
| Strip corner | Strip end 1.5 mm from the base end. The ear reaches 6.5 mm from the base side. Ø7.6 mm hole for the insert. |
| Magnets | At 5.8 mm from the base end, 39.4 and 81.2 mm from the base side. Ø6 × 2 mm, top flush, assumed. |

![Sections through the insert](../../modules/compact-stage/simulation/results/strip-end-insert/sections_insert.png)

What the fit check found:

- **The base can carry it.** The groove, the tapped hole and the magnet pockets stay in solid
  material, at both depths. The groove keeps only 0.75 mm of wall to the half-round pocket in the
  corner of the base. Moving the insert 0.5 mm towards the base side would make that 1.25 mm. The
  outer magnet pocket keeps 1.7 mm to the damper pocket.
- **A flush insert clears everything.** At the end of the usable travel, at the first damper
  touch and with the dampers fully pressed in, nothing touches the insert or the screw. The scraper
  lips pass 0.15 mm above it, as above the strip.
- **An insert as drawn is hit.** At the end of the usable travel the second scraper lip touches it
  and carriage-top overlaps it by 3 mm³. The scraper pocket in carriage-top ends just short of the
  insert. To make it work: step the lips back around the insert, as in the drawing, and make the
  scraper pocket in carriage-top longer at the insert, about 12 mm instead of 10 mm for normal
  travel, or about 19 mm to survive a crash.
- **Carriage-bottom and the top rollers never touch it,** at either height.

One point on the flush insert: the strip then bears on only the top 0.15 mm of the insert side.
Keep the top edge of the insert sharp and the hole a close fit, so the strip cannot ride up over
it. If it does, let the insert stand 0.1 to 0.2 mm proud and step the lips back only there.

### How the pull spreads from four corner inserts

The pull enters the strip at four points near its corners. A plane stress model of the whole strip
shows how it spreads across the 186 mm width. Almost all the travel of the inserts goes into
flattening the arch over the carriage, so the arch is modelled as a soft band (750 N/mm for the
whole width, from the strip model). Friction and magnets are left out.

![How the pull spreads across the strip](../../modules/compact-stage/simulation/results/strip-end-insert/membrane.png)

| Place | Carriage at the end of the travel: middle / highest | Carriage in the middle: middle / highest |
| --- | ---: | ---: |
| 15 mm from the strip end | 0.00 / 8.9 | 0.00 / 8.8 |
| 30 mm from the strip end | 0.26 / 4.3 | 0.03 / 5.3 |
| First bottom roller | 0.71 / 1.56 | 0.99 / 1.01 |
| Middle of the arch | 1.02 / 1.02 | 1.00 / 1.00 |

Values are shares of the average pull stress, 4.5 MPa at 125 N.

- Under the carriage the pull is even. The strip is stiff in its own plane and the arch is soft,
  so the strip spreads the pull before it reaches the carriage.
- With the carriage at the end of the travel, the first bottom roller sees an uneven pull. The
  strip middle may then bow a little higher there than the edges.
- Near the strip ends the middle carries almost no pull, and beside the inserts the strip is
  squeezed sideways by up to 6.7 MPa. A free 50 mm wide panel of 0.15 mm steel buckles at about
  6 MPa, so the strip may wrinkle there. The base under it and the magnets of the drawing must
  hold it flat. A test piece will show it.
- The strip itself is not loaded hard anywhere. The bearing stress in the insert hole is about
  55 MPa, and the stress on the strip edge beside the insert about 40 MPa.

### Is there enough travel for 125 N?

The strip model is the solver of the seal strip designer page. This time it uses the real
carriage, read from the CAD: the top roller at the low edge of the carriage-top slope, the bottom
roller on the high edge of the carriage-bottom slope, 112 mm between the bottom rollers, and both
carriage faces around the strip as walls. The strip is 0.15 mm thick and 186 mm wide.

| From hand-tight (10 N) to 125 N | Travel of both ends together |
| --- | ---: |
| Ceiling as drawn | 0.11 mm |
| Ceiling 1 mm higher | 0.13 mm |
| Ceiling 2 mm higher | 0.24 mm |

The difficulty is the other way round. Near 125 N, 0.1 mm more travel adds 50 to 100 N. The
travel is fixed by where the holes are: the two holes in the strip, the two holes in the base, and
the screw offsets. A laser cut hole is typically placed to about ±0.05 to 0.1 mm. That alone
can move the pull by tens of newtons. Temperature adds a little: the aluminium base grows about
0.03 mm more than the steel strip per 10 °C over 430 mm.

### Does 125 N keep the strip off carriage-top?

No. Between the bottom rollers the room above the roller tops is only 0.35 mm. The strip leaves
the 19° slope over each bottom roller and overshoots. With nothing above it, it would bow:

| Pull | Bow above the bottom roller tops |
| ---: | ---: |
| 50 N | 3.6 mm |
| 125 N | 2.0 mm |
| 250 N | 1.2 mm |
| 500 N | 0.8 mm |

A bow of 1.3 mm needs about 250 N, and the strip still touches. With carriage-top in place, the
strip lies against the ceiling and presses on it with about 186 N, for both carriage ends together.
This hardly depends on the pull. The pull cannot do this job.

| Ceiling | Force of the strip on carriage-top at 125 N |
| --- | ---: |
| As drawn | 186 N |
| 0.5 mm higher | 60 N |
| 1 mm higher | 20 N |
| 1.5 mm higher | 4 N |
| 2 mm higher | 2 N |

Two ways to live with it:

- **Tape or a plastic strip under carriage-top, as drawn.** The strip slides on it with 186 N.
  PTFE on steel typically has a friction coefficient of 0.05 to 0.2, which gives 9 to 37 N. That
  is 5 to 20 % of the 180 N continuous force of STG-10. The friction also changes direction with
  the motion, which costs positioning accuracy. The tape wears.
- **A ceiling 1.5 to 2 mm higher, over the strip width, between the slopes.** The force drops to
  2 to 16 N, depending on the pull. The pull can then be lower, for example 50 N. That also lowers
  the stress at the rollers. The plate of carriage-top above the strip is 6.5 mm thick now and
  would become 4.5 to 5 mm. The same room can come from lowering the bottom rollers and the flat
  top of carriage-bottom instead.

### What the strip carries

At 125 N the tightest radius is about 20 mm and the highest stress about 710 MPa. The fatigue
limit of the 301 strip at 0.15 mm is about 900 MPa, extrapolated from Alleima's measured values at
0.25 and 0.50 mm. At 250 N the stress reaches 860 MPa, which leaves almost no margin.

## Decisions Made

- The seal strip is 0.15 mm thick. Niels Bosmans decided this. See
  [the decision record](../decisions/2026-10-28_seal-strip-0-15-mm.md).
- Versions 1 and 2 of the clamp are dropped.
- Version 3 is the concept of Niels Bosmans. It is checked against the CAD and is feasible. No
  decision yet on the insert height.

## Open Questions

- **The carriage-top ceiling.** Raise it by 1.5 to 2 mm, or lower the bottom rollers, or accept
  contact with tape? This decides the pull and the friction.
- **How proud do the bottom rollers stand?** The 0.35 mm of room assumes 1.5 mm, the same as the
  top rollers. No roller is in the CAD yet. Every number in the table above depends on it.
- **Insert height.** Flush, with no change to the carriage, or as drawn, with stepped lips and a
  longer scraper pocket in carriage-top?
- **Does the strip end stay flat?** Its middle carries almost no pull near the ends, and it is
  squeezed sideways beside the inserts. The magnets must hold it. Check on a test piece.
- **The travel sets the pull sharply.** With the screw offset fixed by the drawing, small errors
  in the hole positions change the pull by tens of newtons. How will the pull be checked at
  fitting?
- **The top rollers** still reach 1.15 mm below the top of the strip, and hit the end wall when
  the dampers press in fully. They must move up.

## Next Steps

- [ ] Decide on the ceiling or the bottom roller height.
- [ ] Put the bottom and top rollers in the CAD, so the room around the strip can be measured.
- [ ] Choose the target pull again once the ceiling is decided.
- [ ] Choose the insert height.
- [ ] Draw the inserts, the grooves, the screws and the magnet pockets in the CAD.
- [ ] Make a test piece of the strip corner with an insert. Check that the strip does not slip or
      wrinkle.

<details>
<summary>Technical notes</summary>

- Strip model: `modules/compact-stage/simulation/cases/strip-pull/`. It uses `strip_model.js`
  from the designer page. The clamp geometry of versions 1 to 3 is no longer in the repository;
  it is in the git history of this branch.
- Concept check: `modules/compact-stage/simulation/cases/strip-end-insert/`. It reuses
  `fcstd_shapes.py` and `scraper.py` from `scraper-fit`. The membrane model uses bilinear plane
  stress elements of 1 mm (scipy). The soft band has 2 990 MPa along the travel and steel values
  across and in shear. The 6 MPa buckling value is the plate formula with k = 4 for a 50 mm
  panel, as an order of size.
- Images 03 and 04: the drawing of Niels Bosmans, and the same drawing with notes. The notes were
  added with a short matplotlib script that is not in the repository.
- `strip_model.js` got an `opts.walls` option (straight walls as upper or lower bounds) and
  returns `wallF`. The contact solver may now take up to 50 000 steps instead of 1 000. The
  designer page checks still pass. Some points with the ceiling raised 2 mm do not settle (70 and
  50 N); they are left out.
- Carriage faces at y = 105 mm, assembly coordinates: carriage-top flat underside z = 40.5 to
  x = 118.77, slope to (147.1, 50.5), ceiling z = 53.5 from x = 147.1 to 276.1. Carriage-bottom
  slope (121.6, 39.5) to (155.6, 51.5), flat top z = 51.5 to x = 267.6.
- Strip model input: a = 36.83 mm (top roller to bottom roller), b = 112 mm, bottom roller axis
  z = 48.0, top roller raised so it just touches the strip, magnet bed 20 N/mm³ and 0.005 N/mm²,
  strip length 430 mm.
- Scraper-fit with 0.15 mm: lips 1.2 mm high, 0.15 mm above the strip; scraper to the base walls
  0.30 mm (was 0.40); screw heads 1.65 mm above the strip (was 1.55).
- Friction values for PTFE on steel are typical textbook values, not from a data sheet.
- Mistake rules checked: the fatigue mistake (the 0.15 mm fatigue limit is flagged as
  extrapolated; friction flagged as typical), the PowerShell rules (all shell work ran in bash),
  and the reverted tooling update (the tooling folders were left as they are).

</details>
