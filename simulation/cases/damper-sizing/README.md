# damper-sizing

A web page that sizes the end damper of a linear motor stage. The worst case is a runaway: the
carriage starts at rest at one end, the motor pushes with its full force, and the carriage hits the
damper at the other end. The page finds the impact speed, sizes a damper with the force law
F = c·vⁿ, and shows how the energy goes into the damper along its stroke.

This runaway is an upper bound, not the likely case. It needs a drive that ignores its own speed
limit. The realistic cases, and the energy at each impact speed, are in the
[log of 2026-10-20](../../../docs/log/2026-10-20_damper-impact-cases.md).

**Open it:** <https://refaqt.github.io/aqtuator/damper/> (after the pull request is merged into
`main`). No server and no install. It runs in the browser.

**Tool:** plain HTML and JavaScript. The checks need Node 18 or newer, no packages.

```bash
node simulation/cases/damper-sizing/check_model.mjs
```

To run the page from a local clone, open `index.html` in the browser. No server is needed. The
model file `damper_model.js` is a plain script, not a module, because browsers refuse to load a
module for a page opened straight from disk.

Log: [2026-10-20](../../../docs/log/2026-10-20_damper-sizing-page.md).

## Inputs

| Input | Default | Note |
| --- | --- | --- |
| Moving mass | 5.0 kg | Solid aluminium carriage 30 × 208 × 210 mm (3.54 kg), MK21 forcer (1.1 kg), 4 × QEH15SA (0.36 kg) |
| Acceleration stroke | 218 mm | From rest to the damper |
| Maximum force | 670 N | MK21 limiting force for 0.5 s |
| DC bus voltage | 310 V | DGSMARTWIN AKS on 220 VAC |
| Usable part of the bus | 0.95 | |
| Force constant | 92.5 N/A rms | MK21 |
| Back-EMF constant | 53.4 V rms per m/s | MK21, line to line |
| Resistance | 19.0 Ω | MK21 hot coil, line to line (13.8 Ω cold) |
| Inductance | 64 mH | MK21, line to line |
| Pole pitch | 30 mm | MK21 |
| Damper stroke | 15 mm | Misumi two-stage fixed type, M20 |
| Force law | n = 2 | n = 2: oil through a fixed orifice. n = 1: linear |
| Speed allowed at the end | 0.1 m/s | What is left hits the hard stop |
| Damping constant by hand | 0 | 0 means: size it from the end speed |
| Motor keeps pushing | off | On: nothing switches the drive off before the impact |
| Catalog energy per impact | 59 J | Misumi two-stage M20, 15 mm. Read from search results; verify |
| Catalog highest impact speed | 5 m/s | Same |

## Model

**Speed-up.** Three phase motor, sine commutation, current on the q axis only (no field weakening).
Per phase, with the line-to-line data sheet values:

    (E + R/2·I)² + (ω·L/2·I)² ≤ (η·V_dc/√6)²,   E = Ke/√3·v,   ω = 2π·v/τ

The force is k_f·I, with the largest current that meets this and the current limit F_max/k_f. The
page steps m·dv/dt = F(v) in time (RK4) until the carriage has moved the acceleration stroke.

**Damper.** Along the damper stroke x:

    m·v·dv/dx = F_motor(v)·push − c·vⁿ

The damper work, the motor work and the time are extra states. Bisection on c finds the damper that
gives the allowed end speed. The energy balance ½·m·v₀² + W_motor = W_damper + ½·m·v_end² is shown on
the page as a check.

**Catalog values.** Energy per impact E = ½·m·v₀² + motor work in the damper, and equivalent mass
2·E/v₀². This is how Misumi and other makers rate a shock absorber.

**Even-force reference.** The same energy spread evenly over the stroke. A catalog shock absorber
with several orifices comes close to this. It gives the lowest peak force a stroke can have.

## What it shows at the defaults

- **Impact speed 3.80 m/s**, after 78 ms. The motor's no-load speed is 3.90 m/s. Without the
  voltage limit the speed would be 7.64 m/s.
- **36.1 J at impact**, 61 % of the 59 J rating. Equivalent mass 5.0 kg.
- **A pure v² damper brakes very hard at first.** Peak force 17.5 kN (357 g), against 2.4 kN (49 g)
  for the even-force damper with the same stroke. This is why catalog shock absorbers use several
  orifices.
- **With the motor still pushing, a damper alone cannot stop the carriage.** A c·vⁿ damper only
  slows it to the speed where both forces are equal. The drive must switch off before the impact.

## Checks

`check_model.mjs` tests:

1. With no voltage limit and a constant force, the impact speed is √(2·F·s/m).
2. n = 1, no push: c = m·(v₀ − v_end)/stroke.
3. n = 2, no push: c = m·ln(v₀/v_end)/stroke.
4. The energy balance closes for n = 1 and 2, with and without the push.
5. The motor force is zero just above the no-load speed η·V_dc/(√2·Ke).
6. The defaults give 3.80 m/s, as the hand simulation of 2026-10-19 did.
7. The sized damper gives the allowed end speed.
8. The even-force reference holds the same energy as the damper.
9. A hand-set c is used as it is, and with the push the speed levels off at the terminal speed.

## Limits

- One rigid mass. No guide friction, which would help a little.
- No field weakening. A drive that weakens the field can reach a higher speed.
- The damper force depends on the speed only. Real shock absorbers also change with the position
  (orifices that close) and have a return spring.
