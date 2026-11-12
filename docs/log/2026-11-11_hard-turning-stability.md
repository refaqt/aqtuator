# 2026-11-11 — Hard turning on two stacked compact stages

**Role(s):** simulation, engineering

## Goal

Niels asked for a new model, built on the existing ones, that checks if we can hard turn steel at
61 to 63 HRC with our stages. The lathe tool sits on an X-Y cross slide of two stacked stages with
200 mm travel. The lathe bed and the spindle count as rigid. He wanted the stiffness at the tool
tip, and a stability lobe diagram for a given cut. He chose the compact stage for both slides, a
finish cut as the default (CBN insert, 0.8 mm nose radius, 0.2 mm depth of cut, 0.1 mm feed per
turn, 150 m/min on a 50 mm part), and a web page like the other model pages. Ae (width of cut) is a
milling term; in turning the page uses depth of cut, feed and cutting speed.

## Short answer

- **Hard turning works on paper, but only just, and only for a light finish cut.** Chatter starts
  at a depth of 0.22 mm. The cut asks for 0.20 mm. That margin is too small, because the damping
  and the force ratio are estimates.
- **The tool tip is 82, 43 and 29 N/µm stiff for a steady force** (into the part, up, along the
  spindle). The weakest point is 2.3 N/µm at about 450 Hz, where the stack rocks on the lower guide
  blocks.
- **The X motor is too weak for the steady thrust.** The model gives 316 N into the part, 1.75 times
  the 181 N continuous force of the MK21. The force model is uncertain at these thin chips.
- **A 20 kHz position loop and the longer QEH15CA blocks** would allow about 0.9 mm at mid travel
  and 0.4 mm at the worst end. 4 kHz, the minimum of DRV-09, allows only 0.007 mm.

## Work Done

- Built the page in `simulation/cases/hard-turning-stability/`. It reuses the linear motor loop,
  the exact sampled compliance and the lobe function of the cutting force page, and adds the second
  stage, the guide blocks, the tilt of both carriages, the tool shank, three force directions and
  the turning forces.
- Took the block stiffness from the HIWIN catalogue in the parts library, the masses and block
  positions from the end stop crash case, and the cutting force constants from an ISCAR material
  table (hardened steel, 60 HRC). No table gives 62 HRC.
- Wrote 40 checks. They all pass, and the checks of the cutting force page still pass.
- Opened the page from disk in a browser: no errors, and it fits a phone screen.
- Wrote the [results summary](../../simulation/results/hard-turning-stability/summary.md) with
  the variants behind the short answer.

## Decisions Made

- The motor loop and the guide blocks add in series. A full model with the loop around the guide
  modes would need a change to the tuning code of the cutting force page. Not worth it before a tap
  test gives real damping values.
- The ratio of thrust to cutting force stays an estimate (1.5). The paper that gives measured
  values could not be opened, so it is marked "not confirmed".

## Open Questions

- What are the real cutting forces for this cut and insert? The constants hold for 1 mm chips; this
  cut makes 32 µm chips.
- How stiff is the side of a QE15 block? HIWIN gives only the up/down value.
- Can a drive close the position loop at 20 kHz?

## Next Steps

- [ ] Ask the insert maker, or measure, the forces of a hard turning finish cut.
- [ ] Tap test the tool tip on the first stack, and put the measured values into the page.
- [ ] Ask HIWIN for the sideways stiffness of QEH15SA and QEH15CA.

<details>
<summary>Technical notes</summary>

- Sources: HIWIN GW-13-1-EN-2606-K Table 3.44 (QE15S ZA 115 N/µm, QE15C ZA 187 N/µm);
  `modules/compact-stage/simulation/cases/end-stop-crash/case.toml` (masses, block positions);
  [ISCAR material table](https://www.iscar.com/eCatalog/Ecat/datafileENM/INFO/5092.pdf)
  (kc1 4700 N/mm², mc 0.25 at 60 HRC).
- `control_model.js` now also exports its complex number helpers and `csolve`. Nothing else
  changed there.
- `turning_model.js` runs inside one function, because the page loads it as a plain script next
  to `control_model.js` and both declare names such as `zeros`.
- On Pages the hard turning page gets its own copy of `control_model.js`, and both script
  addresses carry the commit, as the mistake note of 2026-09-28 asks.
- Mistake rules checked: deciding numbers from data sheets (block stiffness, cutting constants);
  robust tuning, not phase margin alone; the page opens from disk and loads versioned files.

</details>
