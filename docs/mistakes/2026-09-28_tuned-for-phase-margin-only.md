# 2026-09-28 — Tuned the drive controllers for phase margin only

**What happened:** The cutting force page tuned each drive for 30° phase margin and nothing more.
For the ball-screw servo this gave loops that came very close to the point −1. The collocated loop
had 2.4 dB gain margin and a sensitivity peak of 13.9 dB. The page showed the low gain margin in
orange, but still used that controller for the comparison. The user saw it in the open-loop chart.

The damping ratios of the coupling (0.1) and the axial spring (0.05) were also guesses without a
source. Both were too high for metal parts. High damping lowers the resonance peaks, so both errors
made the ball screw look better than it is.

**Root cause:** One margin does not describe robustness. A loop can have 30° phase margin at its
crossover and still pass close to −1 at a resonance. The rule never asked what happens when the
resonance is not exactly where the model puts it. The damping ratios were typed in as plausible
numbers. The prevention rule in
[the fatigue mistake note](2026-09-22_fatigue-estimate-without-a-datasheet.md) (find a source, or
give a range, before quoting a number for a real part) applied and was not followed.

**Fix applied:** The tuning now asks for a sensitivity peak of at most 6 dB, a phase margin of at
least 30°, a gain margin of at least 6 dB, and a stable loop, on 9 plants with the resonances 15 %
off. The damping ratios are 0.02, with sources and ranges in the case README.

**Prevention rule:** Tune a feedback loop with the sensitivity peak (at most 6 dB for motion) and
the gain and phase margins together, and test it with the resonances moved at least ±15 %. A
controller that fails these is not a result, even when the page marks the problem. Give a source or
a range for every damping ratio.
