# cutting-force-rejection

A web page that shows how well a digital position controller holds a stage still while a milling
cutter pushes on it. It compares three drives, each with a checkbox:

- **Linear motor.** The stage mass only.
- **Ball-screw servo, collocated.** A BLDC motor drives a ball screw through a coupling. The
  controller reads the rotary encoder on the motor.
- **Ball-screw servo, non-collocated.** The same drive. The controller reads a linear encoder on the
  stage.

For each case the page tunes the controller for a 30° phase margin, and shows the open loop, the
compliance, the stiffness, the vibration of the stage, and the force and power the controller must
deliver.

**Open it:** <https://refaqt.github.io/aqtuator/cutting-force/> (after the one-time Pages setup, see
the [strip seal log](../../../docs/log/2026-09-28_strip-seal-designer.md)). No server and no install.
It runs in the browser.

**Tool:** plain HTML and JavaScript. The checks need Node 18 or newer, no packages.

```bash
node simulation/cases/cutting-force-rejection/check_model.mjs
```

To run the page from a local clone, open `index.html` in the browser. No server is needed. The
model file `control_model.js` is a plain script, not a module, because browsers refuse to load a
module for a page opened straight from disk.

Logs: [2026-09-28](../../../docs/log/2026-09-28_cutting-force-rejection.md),
[ball screw, 2026-09-28](../../../docs/log/2026-09-28_ball-screw-servo-cases.md).

## Inputs

| Input | Default | Note |
| --- | --- | --- |
| Force amplitude | 50 N | Peak of the sine part |
| Force mean | 50 N | |
| Number of teeth | 2 | |
| Spindle speed | 12000 rev/min | Tooth frequency = teeth · rev/min / 60 = 400 Hz |
| Stage mass | 2 kg | The moving stage, in all three cases |
| Loop rate | 10000 Hz | |
| Ball-screw pitch | 5 mm | Per revolution |
| Coupling stiffness | 450 N·m/rad | Between motor and screw |
| Ball-screw diameter | 16 mm | Steel, 7850 kg/m³, a solid cylinder for the inertia |
| Ball-screw length | 400 mm | |
| BLDC rotor inertia | 119 g·cm² | |
| Damping ratio | 0.1 | Of the mode where motor and stage swing against each other |

The defaults are an SFU1605 screw. The page has no computation delay: the controller applies the new
force in the same sample. The hold lag of half a sample is in the plant.

## What the model does

- **Linear motor plant.** G(s) = 1/(m·s²). The controller force is held for one sample (zero-order
  hold), so the discrete plant is G(z) = T²(z + 1) / (2m(z − 1)²). This already holds the half-sample
  lag of the hold.
- **Ball-screw plant.** Written in linear terms with r = pitch/2π. The motor torque τ becomes the
  force u = τ/r. So all cases share the units N, µm/N and N/µm.
  - Motor side mass m₁ = J_rotor/r². At the defaults 18.8 kg.
  - Stage side mass m₂ = m + J_screw/r², with J_screw = π·ρ·L·d⁴/32. At the defaults 2 + 31.9 kg.
  - Coupling spring k = k_c/r² (711 N/µm), damper c = 2ζ·√(k·μ), μ = m₁m₂/(m₁ + m₂).
  - The motor force acts on m₁, the cutting force on m₂. The page always shows the stage position
    x₂. The controller reads x₁ (collocated) or x₂ (non-collocated).
  - Resonance √(k/μ)/2π = 1.22 kHz. The motor encoder also sees an antiresonance
    √(k/m₂)/2π = 729 Hz.
  - The plant with its hold comes from one matrix exponential, so it is exact at the samples. For
    one mass it equals the formula above (a check tests this).
- **Controller.** C(s) = K · 1/s · (s + 2πf_i)(s + 2πf_d) / (s + 2πf_lp)², with f_i = f_b/10,
  f_d = f_b/3, f_lp = 4·f_b. The three factors are translated to discrete time with the bilinear rule
  (Tustin) and run as difference equations.
- **Tuning, the same rule for each case.** K makes |C·G| = 1 at f_b. f_b is the highest bandwidth
  where the worst phase margin, over every point where |C·G| crosses 1, is still 30°. With a
  resonance the loop can cross 1 a second time near the resonance, and that crossing can set the
  limit. A dense set of test frequencies around the resonance makes sure a narrow peak is not missed.
  Then the closed loop at the samples is tested for stability: its largest pole must have |z| < 1.
- **Compliance.** The cutting force acts on the stage. Y/F_d = G_sd − G_su·C·G_md/(1 + C·G_mu), in
  µm/N, where m is the measured position and s the stage. For the linear motor this is
  G/(1 + G·C). The stiffness is its inverse, in N/µm.
- **Vibration.** A time simulation: the plant moves in continuous time and is integrated exactly
  between samples, and the controller runs once per sample. The amplitude is half the peak-to-peak
  motion of the stage after the start transient, also between samples. It still holds when the tooth
  frequency is above half the loop rate, where the discrete transfer functions stop.
- **Controller force.** The force u after the hold. The force ratio is the steady amplitude of u
  divided by F_amp, in N/N. For the ball screw the table also gives the motor torque, u·r.
- **Controller power.** u·v, the force times the speed where it pushes: the stage for the linear
  motor, the motor for the ball screw. In W at the force amplitude on the page. The mean power is
  exact: u is constant over each sample, so each sample adds u·Δx of work.

`check_model.mjs` checks, for each case, the phase margin and crossover, the stability, what a
constant force leaves behind, that the simulation matches compliance × force within 2 % up to 2·f_b,
that the controller force matches the transfer function within 2 %, and that the mean controller
power matches an exact steady-state solution at the samples (also above half the loop rate). It also
checks that the matrix plant equals the formula for one mass, that f_b does not depend on the mass
of the linear motor stage, that a very stiff coupling behaves as one mass m₁ + m₂, that the resonance
sits at √(k/μ)/2π, that a narrow, lightly damped resonance is not missed, that the stability test
agrees with the gain margin, and that the Tustin controller matches C(s) at low frequency.

## What it shows

Results at the defaults:

| Case | f_b | Worst phase margin at | Gain margin | Vibration at 400 Hz | Peak at the start of the cut | Lowest stiffness |
| --- | --- | --- | --- | --- | --- | --- |
| Linear motor | 431 Hz | 431 Hz | 9.7 dB | 7.0 µm | 13.9 µm | 5.6 N/µm |
| Ball screw, collocated | 282 Hz | 1.26 kHz | 2.5 dB | 0.34 µm | 1.06 µm | 64 N/µm |
| Ball screw, non-collocated | 405 Hz | 405 Hz | 3.9 dB | 0.27 µm | 0.62 µm | 115 N/µm |

- **The ball screw looks 10 to 20 times stiffer, but mostly because of its own inertia.** Through a
  5 mm pitch, the screw acts like 32 kg on the stage side, and the motor rotor like 19 kg. The
  cutting force must move all of that. The linear motor stage has only 2 kg. This only holds while
  the screw and the nut are rigid along the axis, which the model assumes. In a real drive the nut
  and the screw are a second spring between the stage and the screw inertia. Above that spring's
  resonance the stage is on its own again. So treat the ball-screw stiffness here as an upper
  limit.
- **Collocated: the coupling resonance sets the bandwidth.** The loop crosses 1 a second time near
  the 1.22 kHz resonance. To keep 30° there, f_b drops to 282 Hz. The gain margin is only 2.5 dB.
- **Collocated: the stage does not come back to zero.** The integrator holds the motor still, but
  the coupling twists under the mean force. At 50 N the stage stays 70 nm off (F_mean/k).
- **Non-collocated: close to the linear motor bandwidth,** 405 Hz, because the resonance at
  1.22 kHz is well above f_b. But the gain margin is only 3.9 dB, because the phase drops 180° more
  at the resonance.
- **A faster loop does not help the ball screw much.** At 40 kHz the linear motor reaches
  f_b = 1.7 kHz, but the collocated case only 303 Hz and the non-collocated case 403 Hz. The
  resonance, not the sampling, is the limit.
- **A larger pitch makes the ball screw softer.** At 10 mm the reflected masses fall by four, and
  the lowest stiffness falls to 15 N/µm (collocated) and 30 N/µm (non-collocated).
- **A ten times stiffer coupling** (4500 N·m/rad) moves the resonance to 3.9 kHz. Both ball-screw
  cases then reach the linear motor bandwidth, with about 10 dB gain margin.

For the linear motor alone:

- **The loop rate sets the bandwidth, not the mass.** With these frequency ratios the continuous
  loop has about 38° of phase margin at any bandwidth. The sampling lag takes the other 8°. So
  f_b = f_s/23 (431 Hz at 10 kHz), with a gain margin of 9.7 dB. A heavier stage only needs a larger
  K. The stiffness scales with m·(2πf_b)². The lowest stiffness is about 0.38 of that, just below
  f_b.
- **The controller pushes up to twice as hard as the cut, near f_b.** The force ratio is about 1
  well below f_b, where the controller takes the whole force. It peaks at 1.95 N/N near f_b. Above
  f_b it falls, and the mass takes the force. At the defaults (400 Hz) the controller swings
  ±97 N against a ±50 N cut. When the cut starts it reaches 149 N, with the mean force.
- **The controller power stays small**: 1.4 W peak at 400 Hz. Its mean is −0.44 W: the controller
  takes energy out of the stage, like a damper. This is mechanical power only. The motor heat
  depends on the current, so on the force, and it is not in the model.

| Linear motor | f_b | Vibration at 400 Hz | Peak at the start of the cut | Lowest stiffness |
| --- | --- | --- | --- | --- |
| Defaults | 431 Hz | 7.0 µm | 13.9 µm | 5.6 N/µm |
| Mass 10 kg | 431 Hz | 1.4 µm | 2.8 µm | 28 N/µm |
| Loop rate 40 kHz | 1724 Hz | 0.55 µm | 0.8 µm | 90 N/µm |

## Limits

- Linear motor: one rigid mass. No resonances, no friction, no guide stiffness.
- Ball screw: the coupling is the only spring. The screw and the nut are rigid along the axis, and
  the screw does not twist. No backlash, no friction, no bearing stiffness.
- The damping ratio is one number for the whole two-mass mode.
- The force is one sine plus a mean. A real cut also has harmonics of the tooth frequency.
- No sensor noise, no quantisation, no force or torque limit on the motor.
- The cut does not react to the motion. This is forced vibration, not chatter.
