# 2026-09-28 — The cutting force page tunes every drive with robust rules

**Role(s):** engineering, simulation, software

## Goal

The ball-screw controllers on the cutting force page crossed |C·G| = 1, or came very close to it,
where the phase was near or below −180°. They would not work on a real machine. Tune all three
drives with the rules a real design must meet, use the same rules for the linear motor, and use
realistic damping for the coupling and the screw.

## Work Done

- The tuning now asks for five rules at once: sensitivity peak at most 6 dB, phase margin at least
  30°, gain margin at least 6 dB, a stable loop, and all of this with each resonance 15 % off the
  model. The ball screw is tested on 9 plants, the linear motor on 1. See
  [the decision note](../decisions/2026-09-28_robust-tuning-rules-for-the-drive-cases.md).
- The default damping ratios are now 0.02 for the coupling (metal bellows or disc) and 0.02 for the
  axial spring. They were 0.1 and 0.05, without a source. The sources and ranges are in the
  [case README](../../simulation/cases/cutting-force-rejection/README.md#sources-for-the-damping-ratios).
- The page has two new inputs: the sensitivity peak limit and the resonance spread. It has a new
  chart of the sensitivity, and the results table shows the worst margins over all plants and the
  rule that stops a faster loop.
- The checks test all rules on all plants, that the rules break 2 % above each bandwidth, and that
  the sensitivity peak matches a dense scan.

Results at the defaults (bandwidth, before → after):

| Case | Old rule, old damping | New rules, old damping | New rules, new damping |
| --- | --- | --- | --- |
| Linear motor | 431 Hz (sensitivity peak 6.8 dB) | 287 Hz | 287 Hz |
| Ball screw, motor encoder | 290 Hz (13.9 dB, gain margin 2.4 dB) | 196 Hz | 102 Hz |
| Ball screw, linear encoder | 128 Hz (5.4 dB) | 108 Hz | 73 Hz |

- **The ball screw still moves the stage less at 400 Hz** (2.1 and 2.5 µm against 7.8 µm), but it
  is less stiff at its weakest frequency (1.3 and 2.1 N/µm against 2.5 N/µm).
- **The damping decides a lot.** With 0.01 the ball-screw bandwidths are 79 and 56 Hz; with 0.03 and
  0.05 they are 120 and 107 Hz.

## Decisions Made

- Replace the 30° phase margin rule with the robust rules above. The old decision is marked as
  replaced.

## Open Questions

- What are the real damping ratios? A frequency response measured on the built drive answers this.
- Would a notch filter on the coupling mode make the ball screw worth it? It needs the same rules.

## Next Steps

- [ ] Measure the frequency response of the ball-screw drive once it is built, and fit the damping.
- [ ] Try a notch filter on the collocated ball-screw loop, with the same rules.
