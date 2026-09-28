# strip-seal-preload

Which bending radius a 0.25 mm seal strip really takes over the four 10 mm carriage rollers,
how the pull in the strip changes it, and whether EN 1.4301 (AISI 304) can replace
EN 1.4310 (AISI 301).

**Tool:** Python 3 with `numpy` and `scipy`.

```bash
pip install numpy scipy
python3 simulation/cases/strip-seal-preload/strip_seal_preload.py
```

The run takes under ten seconds.

Results: [`simulation/results/strip-seal-preload/summary.md`](../../results/strip-seal-preload/summary.md).
Log: [2026-09-25](../../../docs/log/2026-09-25_strip-seal-radius-pull-and-304.md).
The earlier case for the 0.1 mm strip is [`strip-seal-fatigue`](../strip-seal-fatigue/).

## The arrangement

Read off a sketch of the carriage, and still to be confirmed against the CAD model:

- The strip lies flat on the profile top. Roller 1 sits above it and holds it down.
- Roller 2 sits below it in the slot and lifts it 6 mm. The strip runs flat across the
  carriage for 119 mm to roller 3, and roller 4 lays it back on the profile.
- All rollers are 10 mm. Roller 1 to roller 2 is 26.2 mm, which is what two arcs of 30 mm
  radius need to climb 6 mm.
- The strip is 0.25 mm thick, as measured on the old axis. The width is not known, so
  forces are given per mm of width and also for a 40 mm strip.

## What the model does

The strip is a thin beam under a pull. The model finds the shape with the lowest energy:
bending energy plus the work of the pull. It uses the exact curvature, because the ramps are
steep. The rollers and the profile top are the only things that hold the strip. Nothing
presses it onto the drawn arcs.

A self-check compares the solver with a closed form answer for a strip over two point
supports. The script stops if they differ by more than five percent.

## What the model leaves out

- **The magnets that hold the strip down.** They matter only where the strip leaves the
  profile outside the carriage.
- **Friction on the rollers and on the profile.**
- **The roller position tolerance.** The results show that a few tenths of a millimetre at
  rollers 1 and 4 change the radius a lot.
- **Measured fatigue data for 1.4301 strip.** No maker publishes it. The script uses the
  range 0.32 to 0.48 of the tensile strength, which is what twelve IPCO belt grades show.
  Treat every 304 fatigue figure as an estimate.

## Sources

| Source | What it gives |
| --- | --- |
| Alleima 11R51 data sheet, 2025-05-09 | 1.4310: Rm 2050, Rp0.2 1975, E 185 GPa, fatigue limit 775 MPa at 0.25 mm |
| EN 10151:2002, tables 3, 4 and A.5 | 1.4301 stops at class +C1300 (Rm 1300 to 1500 MPa). 1.4310 goes to +C1900. E about 179 GPa at Rm 1300 |
| ASTM A666 | 304 is sold up to half hard: Rm at least 1035 MPa, yield at least 760 MPa. 301 goes to full hard |
| AK Steel 301 data sheet, 2007 | 301 has less chromium and nickel than 302 and 304 so that it reaches a higher strength by rolling |
| IPCO Steel Belt Specifications v0.3 | Fatigue limit of twelve belt grades: 0.32 to 0.48 of Rm |
