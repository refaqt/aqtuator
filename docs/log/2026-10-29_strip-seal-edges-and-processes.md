# 2026-10-29 — How to make the seal strip, and how to get edges without burrs

**Role(s):** engineering, purchasing

## Goal

Niels Bosmans asked which processes and which material the seal strip needs. He also asked which
process gives a rounded edge, or any other edge that prevents cracks and burrs.

## Short answer

- **The material stays as decided:** EN 1.4310 (AISI 301) spring steel strip to EN 10151, cold
  rolled to about 2050 MPa, 0.15 mm thick. One source is Alleima 11R51.
- **There are three steps:** buy the strip, cut the outline and the holes, then finish the edges.
- **The edges decide the life of the strip.** Fatigue cracks in this hard, thin strip start at edge
  damage. The strip maker says a sheared edge can cost a factor of ten in fatigue life.
- **The ears make the long edges a cut edge.** The ears at the four corners stand 8 mm out past
  each side of the strip: 186 mm wide without the ears, about 202 mm across them. So the long edges
  cannot be the rounded edges of the steel mill. They must be cut, and they bend at every roller on
  every pass. The decision of 2026-09-22 did not see this.
- **Proposed route:** cut the outline and the holes by photochemical etching, then electropolish
  the whole strip.

## Work Done

Read the strip decisions, the clamp log of 2026-10-28 and the strip outline in the model of the
strip end insert. Compared the processes below. The process facts are general industry practice,
not supplier data. Every tolerance and radius must be confirmed by a supplier.

### Step 1: buy the strip

A precision strip maker cuts the coil to width (slitting). A slit edge has a burr. The maker can
roll or grind the long edges round. That is the best edge, but it only exists on the long sides of
the coil, and the ears rule it out for this strip (see the short answer).

### Step 2: cut the outline and the holes

| Process | Edge | Fit for this strip |
| --- | --- | --- |
| Photochemical etching (chemical milling: acid removes the metal through a printed mask) | No burr, no heat, no bending. Smooth and slightly rounded. | First choice. The hole positions come from a photo mask, so they are accurate. Shops often quote about ±10 % of the thickness for a feature. |
| Laser cutting | Heat makes a thin layer of re-melted metal and a softer zone. Small cracks can start there. | Prototypes only, and only with edge finishing afterwards. |
| Punching or fine blanking with a die | Always a burr. | Only for larger numbers, and the burr must be removed. |

Accurate holes also help the preload. The clamp log of 2026-10-28 found that a laser hole tolerance
of ±0.05 to 0.1 mm moves the pull by 25 to 100 N when the pull is set by travel.

### Step 3: finish the edges

- **Electropolishing.** The strip hangs in an electrolyte (a chemical bath) under electric current.
  Corners and burrs dissolve faster than flat faces, so sharp edges become round and micro-burrs go
  away. It also leaves a clean protective layer on the stainless steel, which helps against the
  coolant. It removes a few micrometres, so the thickness must allow for it.
- **Passivation** (an acid bath that renews the protective layer) is enough against corrosion if
  electropolishing is skipped. It does not round the edges.
- **Not suitable:** tumbling or vibratory finishing, shot peening, and heavy belt grinding. A large
  0.15 mm sheet bends, dents or warps under them.

### The shape on the drawing

- Every inside corner gets a generous radius, mainly where an ear meets the strip body. A sharp
  inside corner starts cracks. Clamp version 2 was dropped partly for corners that could tear.
- The hole edges carry little load, about 68 MPa next to the insert, so a clean etched edge is
  enough there.

## Decisions Made

Added to [Strip seal material and roller size](../decisions/2026-09-22_strip-seal-material-and-roller-size.md),
point 2, as a proposal: etching and electropolishing, and an edge requirement on the drawing.
Niels Bosmans still has to choose between keeping the ears and changing the outline.

## Open Questions

- **Keep the ears, or change the outline?**
  - Option A: keep the ears, etch the whole outline and electropolish. This is simple. The radius on
    the long edges is small, so check the edges under a microscope.
  - Option B: change the outline so that nothing stands out past the strip body. The long edges can
    then stay as the rounded edges of the mill, and only the ends are cut. This conflicts with the
    insert over the ear, which keeps the scraper lip off the strip.
- **Is an etched and electropolished edge as good as a rounded mill edge for fatigue?** The fatigue
  limit of about 900 MPa at 0.15 mm is already extrapolated. It depends on the edge quality.
- **Which inside corner radius?** Ask the etching shop what it can make.

## Next Steps

- [ ] Ask Alleima, or another strip maker, which edge types they sell at 0.15 mm. Add it to the
      open question on thin strip fatigue data.
- [ ] Ask the strip maker's application engineer whether an etched and electropolished edge reaches
      the fatigue life of their rounded edge.
- [ ] Ask an etching shop for a quote with electropolishing, and for its hole position tolerance.
- [ ] Decide between option A and option B.
- [ ] Write the edge requirement on the strip drawing.
- [ ] Protect the edges during transport and fitting. A nicked edge is a reason to replace the
      strip.

<details>
<summary>Technical notes</summary>

- Strip outline from `modules/compact-stage/simulation/cases/strip-end-insert/insert.py` and
  `membrane.py`: strip body from y = 12 to 198 mm (186 mm), ears out to y = 4 and 206 mm, so
  202 mm across the ears. Ear from x = 1.5 to 16 mm, then a taper to 21.5 mm (35.4 and 40.9 mm at
  the spring end). Hole Ø6.1 mm. Length 440 mm in the membrane model.
- Bearing stress in the insert hole, about 68 MPa, and stress on the strip edge beside the insert,
  about 36 MPa: from the clamp log of 2026-10-28.
- Factor of ten for a sheared edge, and the large gain from rounded edges: strip maker statement,
  already recorded in the decision of 2026-09-22.
- Etching tolerance and electropolishing material removal are typical values, not supplier data.
- Mistake rules checked: the fatigue mistake (no invented supplier numbers; typical values are
  flagged as typical). Nothing ran in PowerShell. The tooling folders were not touched.
- No model or CAD changed. `bash doqs.sh check` was run before the commit. Only `validate_variants.py` fails, on three missing parts library families in the compact stage bill of materials. It fails the same way on main without this change.

</details>
