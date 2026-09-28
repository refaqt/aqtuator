# 2026-09-28 — A web page for the controller against the cutting force

**Role(s):** engineering, simulation, software

## Goal

See how much the stage moves when a milling cutter pushes on it, and how the stage mass and the
controller loop rate change that. Do it on a web page, with no server, and with every transfer
function in discrete time.

## Work Done

- Built the page in
  [`simulation/cases/cutting-force-rejection/`](../../simulation/cases/cutting-force-rejection/).
  It shows a block diagram, the open loop of the plant, the controller and the loop with the
  margins, the compliance in µm/N, the stiffness in N/µm, the stage position over time, and the
  vibration against spindle speed.
- The controller is tuned on the page for a 30° phase margin. The vibration comes from a time
  simulation that also sees the motion between samples.
- A check script tests the tuning, the integrator and the agreement between the simulation and the
  transfer function. CI runs it, and the Pages workflow now publishes both web pages with a small
  start page.

- Later the same day: the page now also shows the force the controller puts out, at the start of
  the cut and in the steady state. Two new charts against spindle speed show the controller force
  per newton of cutting force (N/N) and the controller power (W). The check script tests both.

Results at the defaults (2 kg, 10 kHz, 2 teeth at 12000 rev/min, 50 N mean and 50 N amplitude):

- **The loop rate sets the bandwidth, not the mass.** The bandwidth is the loop rate divided by 23:
  431 Hz. The gain margin is 9.7 dB.
- **The stage vibrates 7.0 µm at the 400 Hz tooth frequency**, and moves 13.9 µm when the cut
  starts. The lowest stiffness is 5.6 N/µm, just below the bandwidth.
- **A one-sample computation delay cuts the bandwidth by three**, to 144 Hz. The lowest stiffness
  falls to 0.63 N/µm.

- **The controller pushes up to twice as hard as the cut.** Near the bandwidth it puts out
  1.95 N for each newton of cutting force: ±97 N against a ±50 N cut. When the cut starts it
  reaches 149 N. Well below the bandwidth the ratio is 1. Far above it the ratio falls, and the
  mass takes the force.
- **The controller power is small**: 1.4 W peak at 400 Hz, and on average the controller takes
  0.44 W out of the stage. With the computation delay the peak rises to 4.0 W near 144 Hz.

Full table: [case README](../../simulation/cases/cutting-force-rejection/README.md#what-it-shows).

## Decisions Made

- The hold lag is part of the discrete plant, so it is not added a second time. A computation delay
  is a separate effect. It is a checkbox on the page, off by default.
- The low-pass term is (s + 2π·f_lp)², with the 2π, like the other terms.

- Power is shown in watts at the force set on the page, not per newton. Power grows with the square
  of the force, so a ratio per newton would have no fixed meaning.

## Open Questions

- Does our controller apply the new force in the same sample, or one sample later? This changes
  the bandwidth by a factor of three.
- What cutting forces do we expect on the Mekanika Pro? The defaults are round numbers.

## Next Steps

- [ ] Add the motor: force constant and winding resistance, to turn the controller force into
  current and heat.
- [ ] Check the page on GitHub Pages after the merge.
- [ ] Add the harmonics of the tooth frequency, if a single sine turns out to be too simple.
