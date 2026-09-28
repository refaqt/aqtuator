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
| Coupling damping ratio | 0.1 | Of the coupling |
| Screw root diameter | 13.324 mm | HIWIN 16-5 (see sources below) |
| Nut distance from the fixed bearing | 380 mm | The far end of the screw, the worst case |
| Nut stiffness | 118 N/µm | HIWIN 16-5T4 |
| Fixed bearing stiffness | 104 N/µm | TBI Motion BK12 |
| Axial damping ratio | 0.05 | Of the stage on the axial spring. An estimate, not a catalogue value |

The defaults are an SFU1605 screw with a BK12 fixed support at the motor end and a supported far
end. The page has no computation delay: the controller applies the new
force in the same sample. The hold lag of half a sample is in the plant.

## What the model does

- **Linear motor plant.** G(s) = 1/(m·s²). The controller force is held for one sample (zero-order
  hold), so the discrete plant is G(z) = T²(z + 1) / (2m(z − 1)²). This already holds the half-sample
  lag of the hold.
- **Ball-screw plant.** Written in linear terms with r = pitch/2π. The motor torque τ becomes the
  force u = τ/r. So all cases share the units N, µm/N and N/µm.
  - Three masses in a chain: the rotor m₁ = J_rotor/r² (18.8 kg), the screw m_s = J_screw/r²
    (31.9 kg, J_screw = π·ρ·L·d⁴/32), and the stage m (2 kg).
  - The coupling joins rotor and screw: k_c = coupling stiffness/r² (711 N/µm).
  - The axial spring joins screw and stage. It is three springs in series,
    1/k_a = 1/k_shaft + 1/k_nut + 1/k_bearing. With the fixed bearing at the motor end, the shaft
    between the bearing and the nut carries the load: k_shaft = E·π·d_root²/4 / x_nut, with
    E = 206 GPa. At the defaults: shaft 76, nut 118, bearing 104, together 32 N/µm.
  - Each spring has a damper c = 2ζ·√(k·μ), with μ the masses on either side of it. Each ζ is
    exact for its own mode when the other spring is rigid.
  - The motor force acts on m₁, the cutting force on the stage. The page always shows the stage
    position. The controller reads the motor (collocated) or the stage (non-collocated).
  - Two resonances: 646 Hz (mostly the stage bouncing on the axial spring) and 1.24 kHz (mostly the
    motor against the screw on the coupling). The motor encoder also sees two antiresonances, at
    600 Hz and 796 Hz.
  - The plant with its hold comes from one matrix exponential, so it is exact at the samples. For
    one mass it equals the formula above (a check tests this).
- **Controller.** C(s) = K · 1/s · (s + 2πf_i)(s + 2πf_d) / (s + 2πf_lp)², with f_i = f_b/10,
  f_d = f_b/3, f_lp = 4·f_b. The three factors are translated to discrete time with the bilinear rule
  (Tustin) and run as difference equations.
- **Tuning, the same rule for each case.** K makes |C·G| = 1 at f_b. f_b is the highest bandwidth
  where the worst phase margin, over every point where |C·G| crosses 1, is still 30°, and where the
  closed loop at the samples is stable (its largest pole has |z| < 1). With a resonance the loop can
  cross 1 a second time near the resonance, and that crossing can set the limit. Then the margin at
  f_b itself is more than 30°. A dense set of test frequencies around each resonance makes sure a
  narrow peak is not missed. The stability test also catches a peak so sharp that no grid sees it.
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
of the linear motor stage, that stiff springs behave as one mass m₁ + m_s + m, that a very stiff
axial spring gives back the two-mass model (f_b 405 Hz), that the two resonances sit at the natural
frequencies of the chain, that a soft axial spring, a narrow resonance and a very sharp resonance do
not break the tuning, that the stability test agrees with the gain margin, and that the Tustin
controller matches C(s) at low frequency.

## What it shows

Results at the defaults:

| Case | f_b | Worst phase margin at | Gain margin | Vibration at 400 Hz | Peak at the start of the cut | Lowest stiffness |
| --- | --- | --- | --- | --- | --- | --- |
| Linear motor | 431 Hz | 431 Hz | 9.7 dB | 7.0 µm | 13.9 µm | 5.6 N/µm |
| Ball screw, collocated | 290 Hz | 1.28 kHz | 2.4 dB | 1.9 µm | 5.5 µm | 3.9 N/µm |
| Ball screw, non-collocated | 127 Hz | 127 Hz (35°) | 9.1 dB | 3.3 µm | 6.8 µm | 4.8 N/µm |

- **The axial spring takes away most of the ball-screw advantage.** With the screw and nut rigid,
  the ball screw looked 10 to 20 times stiffer than the linear motor (0.27 to 0.34 µm at 400 Hz,
  64 to 115 N/µm lowest stiffness). With the catalogue stiffness, the 2 kg stage sits on a 32 N/µm
  spring and bounces at 646 Hz. The cut still moves the stage less at 400 Hz (1.9 and 3.3 µm
  against 7.0 µm), but the lowest stiffness is now below the linear motor (3.9 and 4.8 N/µm
  against 5.6 N/µm).
- **Non-collocated: the stage mode limits the bandwidth to 127 Hz.** The linear encoder sees the
  stage bounce at 646 Hz, with a further 180° of phase lag. To keep 30° there, f_b must stay low.
  At f_b itself the margin is then 35°.
- **Collocated: the coupling mode still sets the bandwidth (290 Hz),** with only 2.4 dB gain
  margin. The motor encoder does not see the stage mode well, so the stage bounces at 646 Hz with
  little help from the controller.
- **Collocated: the stage does not come back to zero.** The integrator holds the motor still, but
  the coupling and the axial spring give way under the mean force. At 50 N the stage stays
  1.6 µm off: F_mean·(1/k_c + 1/k_a).
- **A faster loop does not help the ball screw.** At 40 kHz the linear motor reaches f_b = 1.7 kHz
  and 90 N/µm. The ball-screw cases stay at 310 and 126 Hz, and near 4 N/µm. The resonances, not
  the sampling, are the limit.
- **The nut position matters.** With the nut 100 mm from the fixed bearing, the shaft is almost four
  times stiffer. The vibration at 400 Hz falls to 1.05 and 1.9 µm, and the lowest stiffness rises to
  5.3 and 7.6 N/µm.
- **A stiffer nut helps less than expected.** With TBI's 32 kgf/µm (314 N/µm) in place of HIWIN's
  value, the vibration at 400 Hz is 1.4 and 2.5 µm. The shaft and the bearing are now the soft parts.

For the linear motor alone:For the linear motor alone:

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

## Sources for the axial stiffness

Checked on 2026-09-28.

| Value | Source | Condition |
| --- | --- | --- |
| Root diameter 13.324 mm | [HIWIN Ballscrew Technical Information](https://www.hiwin.com/wp-content/uploads/Ballscrew-Catalog.pdf), 16-5 nut tables (RD column) | |
| Nut 12 kgf/µm = 118 N/µm | Same catalogue, FSI type, 16-5T4 | "Axial load is 30 % of dynamic load rating without preload" |
| Nut 32 kgf/µm = 314 N/µm | [TBI Motion Ball Screw catalogue](https://www.tuli.si/files/TBI_Ball_Screw_EN_2018.pdf), page C71, SFNU01605-4 | Not stated. Not used as the default |
| Bearing 10.6 kgf/µm = 104 N/µm | [TBI BK series sheet (Anaheim Automation)](https://anaheimautomation.com/media/anaheim/files/manuals/linearcomponents/L011175_-_TBI_Support_Unit_BK_Series.pdf), BK12 row | The column heading in the sheet is unclear. The unit, kgf/µm, shows it is a stiffness. Check with the maker |
| E = 2.1·10⁴ kgf/mm² (206 GPa), shaft formula δ = P·L₀/(A·E) | TBI catalogue, page C21 | Fixed-supported: only the shaft between the fixed bearing and the nut |

The axial damping ratio 0.05 is an estimate. No catalogue gives it.

## Limits

- Linear motor: one rigid mass. No resonances, no friction, no guide stiffness.
- Ball screw: the screw does not twist, and its inertia sits in one point. No backlash, no
  friction, no stiffness of the table or of the nut mounting.
- The nut stiffness is the catalogue value at 30 % of the load rating. A nut without preload is
  softer at the small forces on this page, and it can lose contact when the force changes sign. A
  preloaded nut is stiffer.
- One damping ratio per spring. Each is exact only when the other spring is rigid.
- The force is one sine plus a mean. A real cut also has harmonics of the tooth frequency.
- No sensor noise, no quantisation, no force or torque limit on the motor.
- The cut does not react to the motion. This is forced vibration, not chatter.
