# 2026-09-28 — The cutting force page compares a linear motor with a ball-screw servo

**Role(s):** engineering, simulation, software

## Goal

Compare three ways to drive the stage against the cutting force: a linear motor, and a BLDC motor
with a coupling and a ball screw. The ball-screw controller can read the encoder on the motor
(collocated) or a linear encoder on the stage (non-collocated). Show all three on the same page, in
different colours, with a checkbox for each.

## Work Done

- The page in
  [`simulation/cases/cutting-force-rejection/`](../../simulation/cases/cutting-force-rejection/)
  now has three cases and a checkbox for each. New inputs: ball-screw pitch, coupling stiffness,
  ball-screw diameter and length, rotor inertia, and the damping ratio of the drive. The screw is
  steel.
- The coupling makes the ball-screw drive a two-mass system: the motor on one side, the screw and
  the stage on the other. The cutting force always acts on the stage. The motor torque is shown as
  the force on the screw (torque · 2π / pitch), so all three cases use the same units.
- Each case gets its own controller, tuned with the same rule as before: 30° phase margin, now at the
  worst point where the loop gain crosses 1. The page also tests each closed loop for stability.
- The results are now a table with one column per case. Every chart shows one line per case.
- The optional one-sample computation delay is gone. It will not be there in practice.
- The check script tests all three cases, and it compares the new matrix model of the plant with the
  old formula for one mass.
- The page still opens straight from disk, and the Pages build still works.

Results at the defaults (2 kg stage, 10 kHz, SFU1605 screw 400 mm long, 119 g·cm² rotor,
450 N·m/rad coupling, damping 0.1, 400 Hz tooth frequency):

- **The ball screw looks 10 to 20 times stiffer than the linear motor.** Vibration 0.34 µm
  (collocated) and 0.27 µm (non-collocated) against 7.0 µm. The reason is inertia: through a 5 mm
  pitch the screw acts like 32 kg on the stage and the rotor like 19 kg. **This is an upper limit.**
  The model treats the screw and the nut as rigid along the axis. In a real drive they are a spring
  between the stage and all that inertia.
- **With the motor encoder, the coupling resonance (1.22 kHz) limits the bandwidth** to 282 Hz,
  with 2.5 dB gain margin. The stage also stays 70 nm off under the 50 N mean force, because the
  coupling twists and the motor encoder cannot see it.
- **With the linear encoder, the bandwidth is 405 Hz**, close to the linear motor (431 Hz), but the
  gain margin is only 3.9 dB.
- **A faster loop does not help the ball screw.** At 40 kHz the linear motor reaches 1.7 kHz
  bandwidth. The ball-screw cases stay near 300 and 400 Hz.

Full table: [case README](../../simulation/cases/cutting-force-rejection/README.md#what-it-shows).

## Decisions Made

- Each case is tuned with the same rule, not with one shared controller. See
  [the decision note](../decisions/2026-09-28_tune-each-drive-case-with-the-same-rule.md).
- The ball-screw length is an input (default 400 mm, for the 418 mm HGR15 rail), because the screw
  inertia needs it.

## Open Questions

- How stiff are the nut and the screw along the axis? This decides how much of the screw inertia
  really helps the stage. Answered later the same day: about 32 N/µm, and it removes most of the
  advantage. See [the axial stiffness log](2026-09-28_ball-screw-axial-stiffness.md).
- What coupling, pitch and motor would we actually use? The defaults are a common choice, not a
  selection.

## Next Steps

- [x] Add the axial stiffness of the screw and the nut as a second spring.
- [ ] Check the page on GitHub Pages after the merge.
