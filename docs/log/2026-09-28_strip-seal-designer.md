# 2026-09-28 — A web page to design the seal strip and its screw preload

**Role(s):** engineering, simulation, software

## Goal

See how the seal strip bends over the four rollers and which forces act on the rollers. Set the
layout, the thickness and the material on a web page, with no server. See what the countersunk
preload screw does: how much screw travel gives how much pull, and how the arch between rollers 2
and 3 shows it.

## Work Done

- Built the page in
  [`simulation/cases/strip-seal-designer/`](../../simulation/cases/strip-seal-designer/). It
  draws the strip and the rollers at scale, with a force arrow on each roller, and shows the pull,
  the arch height, the tightest radius, the highest stress, the yield and tensile strength and the
  fatigue life.
- Ported the strip solver from the `strip-seal-preload` case to JavaScript. A check script
  compares it with the Python solver and with a closed form. They agree to three decimals. CI runs
  the check.
- Found that the force on rollers 1 and 4 was not a real number in the old model. With a rigid
  profile the roller pins the strip at one point, and the force doubled each time the grid was
  halved. The shape was right. The page now treats the magnet strips as an elastic bed, and the
  force stays the same on any grid.
- Added the screw preload. The strip is fitted loose, then a screw travel is taken up by a flatter
  arch and by stretching the steel.
- Added a GitHub Pages workflow that publishes only this page.

Results at the defaults (301, 0.25 mm, 150 mm wide, magnet stiffness 20 N/mm³):

- **About 1 mm of screw travel gives 54 N.** The strip length hardly matters, because the arch
  takes almost all the travel.
- **Past about 1.3 mm the pull rises fast**: 87 N at 1.25 mm, 169 N at 1.5 mm, 439 N at 1.75 mm.
- **The arch drops about 0.4 mm per 10 N near 54 N.** That is easy to measure, so the arch height
  can be the check during fitting. It is measured from a straight edge on the tops of rollers 2
  and 3 to the underside of the strip: 8.85 mm with no pull, about 5.3 mm at 54 N.
- **Rollers 1 and 4 carry about 440 N each, rollers 2 and 3 about 70 N.** The large force comes
  from the pinch on the magnets, not from the pull. It depends on the magnet stiffness: 310 N at
  5 N/mm³, 1140 N at 1000 N/mm³.
- **The elastic magnets also open the bend.** The tightest radius at 54 N is 35 mm, not the 30 mm
  of the rigid model.
- **With no pull the arch top is only 0.77 mm under the carriage.**
- **No fatigue limit is reached at 54 N** with 301: 660 MPa, or 725 MPa with the plate factor,
  against 775 MPa.

Full table: [case README](../../simulation/cases/strip-seal-designer/README.md#results-at-the-defaults).

## Decisions Made

No design decision. The page is a tool. The rules from
[the fatigue mistake entry](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md) were
applied: material data from the data sheets already in the cases, the load case stated on the
page, and the radius from the solver, not from the roller.

## Open Questions

- How stiff are the magnet strips, and how hard do they pull? Both are estimates now. The
  stiffness sets the force on rollers 1 and 4.
- Does the strip slide on the magnets while the screw is tightened? The page assumes it does.
- Is 0.77 mm enough room between the arch and the carriage?

## Next Steps

- [ ] Enable GitHub Pages once: Settings → Pages → Source: GitHub Actions.
- [ ] Measure or look up the magnet strip stiffness and pull.
- [ ] Add a carriage position slider, to see the pull when the carriage is near a clamp.
