# 2026-09-29 — Why a lighter stage is less stiff, and why more gain does not help

**Role(s):** engineering, simulation

## Goal

On the cutting force page, the linear motor with a 2 kg stage has a lowest stiffness of
2.5 N/µm. With a 10 kg stage it has 12.5 N/µm. Explain why a lighter stage is less stiff, and why
the controller does not simply use more gain to make up for it.

## Work Done

No change to the model. This entry explains results that the page already shows. See the
[case README](../../simulation/cases/cutting-force-rejection/README.md#what-it-shows).

**Why a lighter stage is less stiff.** The stiffness against the cutting force has two parts.
Which part counts depends on the frequency.

- Well below the bandwidth f_b, the controller holds the stage. The stiffness is about the
  controller gain |C|.
- Well above f_b, the controller is too slow to react. Only the inertia of the stage resists the
  cut, so the stiffness is about m·(2πf)².
- Near f_b the two parts meet, and the stage is weakest there. The lowest stiffness is about
  0.38 · m·(2πf_b)², just below f_b.

The tuning sets |C·G| = 1 at f_b. For one mass this means |C(f_b)| = m·(2πf_b)². So the controller
gain also grows with the mass. Both parts scale with m, so the whole stiffness curve scales with m:

- 2 kg: 0.38 · 2 · (2π·287)² ≈ 2.5 N/µm
- 10 kg: five times more, 12.5 N/µm

**Why more gain does not help.** The controller already scales its gain with the mass. A lighter
stage gets a smaller gain K, and a heavier stage gets a larger one. The stability of the loop
depends only on the ratio K/m. A light stage with more gain is the same loop as a heavy stage with
the normal gain. Both push the crossover frequency (where |C·G| = 1) higher.

A higher crossover comes closer to the 10 kHz loop rate. The controller holds each force for one
sample, which adds a lag of about half a sample. That lag is a fixed time, so its phase cost grows
with the frequency. Above f_b = f_s/35 = 287 Hz, the sensitivity peak goes over 6 dB, and the
tuning rules stop there. So K is already at its limit for each mass, and f_b does not depend on the
mass. The check script tests this.

In simple terms: the cutting force first moves the stage. The controller sees the motion only at
the next sample, and it needs time to push back. During that time, only the inertia of the stage
resists the force. A heavy stage moves less in that time than a light one.

**The 11.3 dB gain margin is not room for more gain.** The page shows 11.3 dB. This can look like
room for 3.6 times more gain. But the sensitivity peak is already at 6.0 dB, and that is the rule
that sets the limit. The loop would still be stable with some more gain. But it would amplify
disturbances near f_b, and a small error in the model would remove the rest of the margin.

**What does raise the stiffness:** a faster loop, a heavier stage, or less delay in the loop. At a
40 kHz loop rate, f_b is 1146 Hz and the lowest stiffness is 40 N/µm, 16 times more than at 10 kHz.

**The ball screw follows a different rule.** Its bandwidth is limited by the coupling resonance and
the axial resonance, not by the loop rate. The stage mass changes where the axial resonance sits.
So the stage mass does not simply scale its stiffness.

## Open Questions

- What stage mass will the MK21 stages have? A heavier stage is stiffer against the cut, but it
  needs more force to accelerate.
