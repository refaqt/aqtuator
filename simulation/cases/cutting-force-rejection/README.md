# cutting-force-rejection

A web page that shows how well a digital position controller holds a stage still while a milling
cutter pushes on it. It compares three drives, each with a checkbox:

- **Linear motor.** The stage mass only.
- **Ball-screw servo, collocated.** A BLDC motor drives a ball screw through a coupling. The
  controller reads the rotary encoder on the motor.
- **Ball-screw servo, non-collocated.** The same drive. The controller reads a linear encoder on the
  stage.

For each case the page tunes the controller with the same robustness rules (see below), and shows
the open loop, the sensitivity, the compliance, the stiffness, the vibration of the stage, and the
force and power the controller must deliver.

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
[ball screw, 2026-09-28](../../../docs/log/2026-09-28_ball-screw-servo-cases.md),
[robust tuning, 2026-09-28](../../../docs/log/2026-09-28_robust-tuning-and-damping.md).

## Inputs

| Input | Default | Note |
| --- | --- | --- |
| Force amplitude | 50 N | Peak of the sine part |
| Force mean | 50 N | |
| Number of teeth | 2 | |
| Spindle speed | 12000 rev/min | Tooth frequency = teeth · rev/min / 60 = 400 Hz |
| Stage mass | 2 kg | The moving stage, in all three cases |
| Loop rate | 10000 Hz | |
| Sensitivity peak limit | 6 dB | The usual limit for motion systems, see the tuning rules |
| Resonance spread | ±15 % | The margins must hold with each resonance this much off |
| Ball-screw pitch | 5 mm | Per revolution |
| Coupling stiffness | 450 N·m/rad | Between motor and screw |
| Ball-screw diameter | 16 mm | Steel, 7850 kg/m³, a solid cylinder for the inertia |
| Ball-screw length | 400 mm | |
| BLDC rotor inertia | 119 g·cm² | |
| Coupling damping ratio | 0.02 | Metal bellows or disc coupling. An estimate, range 0.01 to 0.03, see below |
| Screw root diameter | 13.324 mm | HIWIN 16-5 (see sources below) |
| Nut distance from the fixed bearing | 380 mm | The far end of the screw, the worst case |
| Nut stiffness | 118 N/µm | HIWIN 16-5T4 |
| Fixed bearing stiffness | 104 N/µm | TBI Motion BK12 |
| Axial damping ratio | 0.02 | Of the stage on the axial spring. An estimate, range 0.01 to 0.05, see below |

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
- **Tuning, the same rules for each case.** K makes |C·G| = 1 at f_b. f_b is the highest bandwidth,
  counted up from a slow one, where the loop meets all of these rules:
  1. **Sensitivity peak at most 6 dB.** The sensitivity S = 1/(1 + C·G) says how much the loop
     amplifies a disturbance. Its peak Ms is 1 over the closest distance between C·G and the point
     −1. Ms ≤ 2 (6 dB) keeps that distance at least 0.5 in any direction. This one rule already
     gives at least 6 dB gain margin and 29° phase margin. It is the rule that catches a loop gain
     near 1 where the phase is near −180°.
  2. **Phase margin at least 30°** wherever |C·G| crosses 1, also near a resonance.
  3. **Gain margin at least 6 dB** wherever the phase crosses −180° with |C·G| below 1.
  4. **A stable closed loop** at the samples (its largest pole has |z| < 1).
  5. **Rules 1 to 4 hold with the resonances off by ±15 %.** The controller is designed on the
     nominal plant and then tested on 9 plants: the coupling stiffness and the axial stiffness each
     at (1 − 0.15)², 1 and (1 + 0.15)². A real resonance is never exactly where a model puts it. The
     linear motor has no resonance, so its family is one plant, with the same limits.

  The search stops at the first bandwidth where a rule breaks. A loop that would meet the rules
  again at a higher bandwidth, with a resonance above 0 dB, is not used. A dense set of test
  frequencies around each resonance makes sure a narrow peak is not missed. The stability test
  also catches a peak so sharp that no grid sees it. Sources for the limits: Åström and Murray,
  *Feedback Systems*, chapter "Robust performance" (Ms of 1.2 to 2 is the usual range); Bruijnen,
  van de Molengraft and Steinbuch,
  [Optimization aided loop shaping for motion systems](https://pure.tue.nl/ws/files/1735760/722626141095799.pdf)
  (a sensitivity peak below 6 dB).
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

`check_model.mjs` checks, for each case, that all robustness rules hold on all 9 plants, that the
rules break 2 % above f_b, that the sensitivity peak matches a dense scan, the phase margin and
crossover, the stability, what a
constant force leaves behind, that the simulation matches compliance × force within 2 % up to 2·f_b,
that the controller force matches the transfer function within 2 %, and that the mean controller
power matches an exact steady-state solution at the samples (also above half the loop rate). It also
checks that the matrix plant equals the formula for one mass, that f_b does not depend on the mass
of the linear motor stage, that stiff springs behave as one mass m₁ + m_s + m, that a very stiff
axial spring gives back the two-mass model (f_b 159 Hz), that the two resonances sit at the natural
frequencies of the chain, that a soft axial spring, a narrow resonance and a very sharp resonance do
not break the tuning, that the stability test agrees with the gain margin, and that the Tustin
controller matches C(s) at low frequency.

## What it shows

Results at the defaults:

| Case | f_b | Limited by | Sensitivity peak (worst plant) | Gain margin (worst plant) | Vibration at 400 Hz | Peak at the start of the cut | Lowest stiffness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Linear motor | 287 Hz | Sensitivity peak | 6.0 dB | 11.3 dB | 7.8 µm | 25.3 µm | 2.5 N/µm |
| Ball screw, collocated | 102 Hz | Sensitivity peak and gain margin, coupling mode −15 % | 6.0 dB | 6.2 dB | 2.1 µm | 10.3 µm | 1.3 N/µm |
| Ball screw, non-collocated | 73 Hz | Phase margin at the stage mode, both modes −15 % | 5.1 dB | 12.4 dB | 2.5 µm | 12.5 µm | 2.1 N/µm |

- **All three bandwidths are lower than with the old rule (30° phase margin only).** The old rule
  gave 431, 290 and 127 Hz. Those loops had a sensitivity peak of 6.8, 13.9 and 5.4 dB, and the
  collocated one only 2.4 dB gain margin. They would not work on a real machine.
- **The linear motor drops from 431 to 287 Hz.** Its loop is limited by the loop rate only. The old
  30° loop came 0.46 away from −1, just below the 0.5 the rule asks. So f_b = f_s/35 now.
- **The ball screw drops to about a third of its old bandwidth.** Two things add up. The new rules
  do not let a resonance come near |C·G| = 1 with a poor phase. And the damping ratios are lower:
  0.02 in place of 0.1 and 0.05, so the resonance peaks are 2 to 5 times higher.
- **Collocated: the coupling mode sets the limit (102 Hz).** When the coupling is 15 % softer than
  planned, its peak comes closest to −1.
- **Non-collocated: the stage mode sets the limit (73 Hz).** The linear encoder sees the stage
  bounce with a further 180° of phase lag. Just above 73 Hz, the peak of the stage mode crosses
  |C·G| = 1 with too little phase margin.
- **The ball screw still moves the stage less at 400 Hz** (2.1 and 2.5 µm against 7.8 µm), because
  its large inertia takes much of the cut. It also moves less when the cut starts (10 and 13 µm
  against 25 µm). But at its weakest frequency it is less stiff than the linear motor (1.3 and
  2.1 N/µm against 2.5 N/µm).
- **Collocated: the stage does not come back to zero.** The integrator holds the motor still, but
  the coupling and the axial spring give way under the mean force. At 50 N the stage stays
  1.6 µm off: F_mean·(1/k_c + 1/k_a).
- **A faster loop only helps the linear motor.** At 40 kHz the linear motor reaches f_b = 1.15 kHz
  and 40 N/µm. The ball-screw cases stay at 104 and 73 Hz. The resonances, not the sampling, are the
  limit.
- **The damping ratios matter a lot, and they are estimates.** With 0.01 on both springs the
  ball-screw bandwidths fall to 79 and 56 Hz. With 0.03 on the coupling and 0.05 on the axial
  spring they rise to 120 and 107 Hz. Measure the drive before trusting these numbers.
- **The spread costs about 15 %.** Without it (resonances exactly as modelled) the ball-screw
  bandwidths would be 120 and 86 Hz.
- **The nut position matters.** With the nut 100 mm from the fixed bearing, the shaft is almost four
  times stiffer. The vibration at 400 Hz falls to 1.2 and 1.4 µm, and the lowest stiffness rises to
  2.0 and 3.1 N/µm.
- **A stiffer nut helps less than expected.** With TBI's 32 kgf/µm (314 N/µm) in place of HIWIN's
  value, the vibration at 400 Hz is 1.6 and 1.8 µm. The shaft and the bearing are now the soft parts.

For the linear motor alone:

- **The loop rate sets the bandwidth, not the mass.** The controller shape is fixed, so the
  continuous loop has the same sensitivity peak at any bandwidth. The sampling lag adds to it. So
  f_b = f_s/35 (287 Hz at 10 kHz), with 32.6° phase margin and 11.3 dB gain margin. A heavier stage
  only needs a larger K. The stiffness scales with m·(2πf_b)². The lowest stiffness is about 0.38 of
  that, just below f_b.
- **The controller pushes up to 1.8 times as hard as the cut, near f_b.** The force ratio is about 1
  well below f_b, where the controller takes the whole force. It peaks at 1.81 N/N at 254 Hz. Above
  f_b it falls, and the mass takes the force. At the defaults (400 Hz) the controller swings ±65 N
  against a ±50 N cut. When the cut starts it reaches 131 N, with the mean force.
- **The controller power stays small**: 1.0 W peak at 400 Hz. Its mean is −0.29 W: the controller
  takes energy out of the stage, like a damper. This is mechanical power only. The motor heat
  depends on the current, so on the force, and it is not in the model.

| Linear motor | f_b | Vibration at 400 Hz | Peak at the start of the cut | Lowest stiffness |
| --- | --- | --- | --- | --- |
| Defaults | 287 Hz | 7.8 µm | 25.3 µm | 2.5 N/µm |
| Mass 10 kg | 287 Hz | 1.6 µm | 5.1 µm | 12.5 N/µm |
| Loop rate 40 kHz | 1146 Hz | 1.25 µm | 2.0 µm | 40 N/µm |

## Sources for the axial stiffness

Checked on 2026-09-28.

| Value | Source | Condition |
| --- | --- | --- |
| Root diameter 13.324 mm | [HIWIN Ballscrew Technical Information](https://www.hiwin.com/wp-content/uploads/Ballscrew-Catalog.pdf), 16-5 nut tables (RD column) | |
| Nut 12 kgf/µm = 118 N/µm | Same catalogue, FSI type, 16-5T4 | "Axial load is 30 % of dynamic load rating without preload" |
| Nut 32 kgf/µm = 314 N/µm | [TBI Motion Ball Screw catalogue](https://www.tuli.si/files/TBI_Ball_Screw_EN_2018.pdf), page C71, SFNU01605-4 | Not stated. Not used as the default |
| Bearing 10.6 kgf/µm = 104 N/µm | [TBI BK series sheet (Anaheim Automation)](https://anaheimautomation.com/media/anaheim/files/manuals/linearcomponents/L011175_-_TBI_Support_Unit_BK_Series.pdf), BK12 row | The column heading in the sheet is unclear. The unit, kgf/µm, shows it is a stiffness. Check with the maker |
| E = 2.1·10⁴ kgf/mm² (206 GPa), shaft formula δ = P·L₀/(A·E) | TBI catalogue, page C21 | Fixed-supported: only the shaft between the fixed bearing and the nut |

## Sources for the damping ratios

Checked on 2026-09-28. No maker of couplings or ball screws publishes a damping ratio, so both
values are estimates. Use the range, not the single number, when you judge a result.

| Value | Source | Note |
| --- | --- | --- |
| Coupling ζ = 0.02, range 0.01 to 0.03 | [Machine Design, "Servocoupling dynamics"](https://www.machinedesign.com/mechanical-motion-systems/article/21832369/motion-design-101-servocoupling-dynamics); [Design World, "Servomotor couplings: stiffness, damping, hunting"](https://www.designworldonline.com/servomotor-couplings-stiffness-damping-hunting-and-stabilization-considerations/) | Metal bellows and disc couplings are all metal, and their damping is "minimal at best". Only elastomer couplings damp well. No number is given. 0.01 to 0.03 is the usual range for bolted steel parts. |
| Axial ζ = 0.02, range 0.01 to 0.05 | [Measured axial mode of a ball-screw test stand, 349 Hz, loss factor 0.04](https://www.researchgate.net/figure/Measured-axial-mode-shape-of-the-large-ball-screw-test-stand-at-349-Hz-with-loss-factor_fig5_245372959) | A loss factor η is about 2ζ, so ζ ≈ 0.02. The full paper could not be opened. Other studies of feed drives report 0.02 to 0.1; the high end includes friction in the guides, which this model does not have. |

The old values, 0.1 and 0.05, came from no source. They were too high, and they made the ball screw
look better than it is.

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
