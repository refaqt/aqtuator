# cutting-force-rejection

A web page that shows how well a digital position controller holds a stage still while a milling
cutter pushes on it. It tunes the controller for a 30° phase margin and shows the open loop, the
compliance, the stiffness and the vibration of the stage.

**Open it:** <https://refaqt.github.io/aqtuator/cutting-force/> (after the one-time Pages setup, see
the [strip seal log](../../../docs/log/2026-09-28_strip-seal-designer.md)). No server and no install.
It runs in the browser.

**Tool:** plain HTML and JavaScript. The checks need Node 18 or newer, no packages.

```bash
node simulation/cases/cutting-force-rejection/check_model.mjs
```

To run the page from a local clone, serve the folder, because browsers block modules opened
straight from disk:

```bash
python3 -m http.server -d simulation/cases/cutting-force-rejection 8000
# then open http://localhost:8000
```

Log: [2026-09-28](../../../docs/log/2026-09-28_cutting-force-rejection.md).

## Inputs

| Input | Default | Note |
| --- | --- | --- |
| Force amplitude | 50 N | Peak of the sine part |
| Force mean | 50 N | |
| Number of teeth | 2 | |
| Spindle speed | 12000 rev/min | Tooth frequency = teeth · rev/min / 60 = 400 Hz |
| Stage mass | 2 kg | One rigid mass |
| Loop rate | 10000 Hz | |
| One sample computation delay | off | Extra. The hold lag is already in the plant |

## What the model does

- **Plant.** G(s) = 1/(m·s²). The controller force is held for one sample (zero-order hold), so the
  discrete plant is G(z) = T²(z + 1) / (2m(z − 1)²). This already holds the half-sample lag of the
  hold.
- **Controller.** C(s) = K · 1/s · (s + 2πf_i)(s + 2πf_d) / (s + 2πf_lp)², with f_i = f_b/10,
  f_d = f_b/3, f_lp = 4·f_b. The low-pass term needs the 2π, like the others. The three factors are
  translated to discrete time with the bilinear rule (Tustin) and run as difference equations.
- **Tuning.** K makes |C·G| = 1 at f_b. f_b is searched so that the phase margin is 30°.
- **Compliance.** The cutting force acts on the mass next to the controller force, so
  Y/F_d = G/(1 + G·C), in µm/N. The stiffness is its inverse, in N/µm.
- **Vibration.** A time simulation: the mass moves in continuous time and is integrated exactly
  between samples, and the controller runs once per sample. The amplitude is half the peak-to-peak
  motion after the start transient, also between samples. It still holds when the tooth frequency is
  above half the loop rate, where the discrete transfer functions stop.

`check_model.mjs` checks the phase margin and crossover, that f_b does not depend on the mass, that
a constant force leaves no deflection, that the simulation matches compliance × force within 2 %
up to 2·f_b, and that the Tustin controller matches C(s) at low frequency.

## What it shows

- **The loop rate sets the bandwidth, not the mass.** With these frequency ratios the continuous
  loop has about 38° of phase margin at any bandwidth. The sampling lag takes the other 8°. So
  f_b = f_s/23 (431 Hz at 10 kHz), with a gain margin of 9.7 dB. A heavier stage only needs a larger
  K.
- **The stiffness scales with m·(2πf_b)².** The lowest stiffness is about 0.38 of that, just
  below f_b. At the defaults that is 5.6 N/µm.
- **A computation delay costs a factor of three in bandwidth**: f_b = f_s/69 (144 Hz at 10 kHz).
  The lowest stiffness falls to 0.63 N/µm, and the start of the cut pushes the stage 76 µm instead
  of 14 µm.

Results at the defaults:

| Case | f_b | Vibration at 400 Hz | Peak at the start of the cut | Lowest stiffness |
| --- | --- | --- | --- | --- |
| Defaults | 431 Hz | 7.0 µm | 13.9 µm | 5.6 N/µm |
| With the computation delay | 144 Hz | 5.2 µm | 76 µm | 0.63 N/µm |
| Mass 10 kg | 431 Hz | 1.4 µm | 2.8 µm | 28 N/µm |
| Loop rate 40 kHz | 1724 Hz | 0.55 µm | 0.8 µm | 90 N/µm |

With the delay the vibration at 400 Hz is smaller, because 400 Hz is then well above f_b, where
the mass alone carries the force. The mass alone would move 4.0 µm.

## Limits

- One rigid mass. No resonances, no friction, no guide stiffness.
- The force is one sine plus a mean. A real cut also has harmonics of the tooth frequency.
- No sensor noise, no quantisation, no force limit on the actuator.
- The cut does not react to the motion. This is forced vibration, not chatter.
