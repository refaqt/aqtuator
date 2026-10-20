# damper-sizing

A web page that sizes the end stop of a linear motor stage. The carriage starts at rest at one
end, the motor pushes with its full force up to the speed limit of the drive, and the carriage hits
the end stop at the other end. The page finds the impact speed and shows how the energy goes into
the end stop along its stroke.

**Choose the type of end stop at the top of the inputs:**

- **Oil damper** (shock absorber). The force depends on the speed, F = c·vⁿ. The page sizes c.
- **Polyurethane bumper** (elastomer stop). The force depends on how far the bumper is pressed
  in. The page finds the compression, the peak force, and the speed of the bounce back.

Only the inputs for the chosen type show. The results table, the warnings and the charts follow
the choice.

The default speed limit is 2 m/s, the top speed the team chose on 2026-10-20. Set the speed limit to
0 to see the full runaway, where only the motor's own top speed limits the carriage. That case
needs a drive that ignores its own speed limit. The realistic cases, and the energy at each impact
speed, are in the [log of 2026-10-20](../../../docs/log/2026-10-20_damper-impact-cases.md).

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
| Speed limit of the drive | 2.0 m/s | Top speed of the stage. 0 means no limit (full runaway) |
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

Bumper inputs. The defaults are the ACE TUBUS TA22-10, from the
[ACE product page](https://www.acecontrols.com/us/products/automation-control/profile-dampers/tubus-ta/ta/ta12-5.html)
(the table there lists all TA sizes):

| Input | Default | Note |
| --- | --- | --- |
| Bumper stroke | 10 mm | TA22-10 |
| Energy per stroke | 11.5 J | 102 in-lbs per cycle |
| Energy for emergency use | 21.0 J | 186 in-lbs per cycle, for a rare crash only |
| Shape of the force curve | p = 1 | F ∝ xᵖ. An estimate: ACE gives no force curve per size |
| Energy turned into heat | 60 % | ACE: 58 to 73 % |

## Model

**Speed-up.** Three phase motor, sine commutation, current on the q axis only (no field weakening).
Per phase, with the line-to-line data sheet values:

    (E + R/2·I)² + (ω·L/2·I)² ≤ (η·V_dc/√6)²,   E = Ke/√3·v,   ω = 2π·v/τ

The force is k_f·I, with the largest current that meets this and the current limit F_max/k_f. The
page steps m·dv/dt = F(v) in time (RK4) until the carriage has moved the acceleration stroke. If the
drive has a speed limit, the carriage speeds up to it and rolls on at that speed for the rest of
the stroke.

**Damper.** Along the damper stroke x:

    m·v·dv/dx = F_motor(v)·push − c·vⁿ

The damper work, the motor work and the time are extra states. Bisection on c finds the damper that
gives the allowed end speed. The energy balance ½·m·v₀² + W_motor = W_damper + ½·m·v_end² is shown on
the page as a check.

**Bumper.** The force depends on the compression x only:

    F_b(x) = F_full·(x/s)^p,   F_full = (p+1)·E_r/s

so the work at the full stroke s is the catalog energy E_r. The page steps
m·dv/dt = F_motor(v)·push − F_b(x) in time (RK4) until the carriage stops, or until the bumper is
fully pressed in. In that last case metal hits metal, and the page shows the energy that is left.
With the motor off, the part (1 − absorbed) of the bumper work pushes the carriage back:
½·m·v_back² = (1 − absorbed)·W_b.

**Catalog values.** Energy per impact E = ½·m·v₀² + motor work in the damper, and equivalent mass
2·E/v₀². This is how Misumi and other makers rate a shock absorber.

**Even-force reference.** The same energy spread evenly over the stroke. A catalog shock absorber
with several orifices comes close to this. It gives the lowest peak force a stroke can have.

## What it shows at the defaults

- **Impact speed 2.00 m/s**, held by the speed limit. The carriage reaches it after 18 mm, and hits
  the damper after 117 ms.
- **10.0 J at impact**, 17 % of the 59 J rating. Equivalent mass 5.0 kg.
- **A pure v² damper brakes very hard at first.** Peak force 3.99 kN (81.5 g), against 0.67 kN
  (13.6 g) for the even-force damper with the same stroke. This is why catalog shock absorbers use
  several orifices.
- **With no speed limit** the carriage hits at 3.80 m/s with 36.1 J. The motor's no-load speed is
  3.90 m/s. Without the voltage limit the speed would be 7.64 m/s.
- **With the motor still pushing, a damper alone cannot stop the carriage.** A c·vⁿ damper only
  slows it to the speed where both forces are equal. The drive must switch off before the impact.

With the **bumper** at the defaults (TA22-10, linear force curve, impact at 2 m/s, motor off):

- The bumper is pressed in 9.3 mm of its 10 mm. That uses 87 % of the 11.5 J rating.
- **Peak force 2.14 kN (43.7 g).** That is lower than the 3.99 kN of a 15 mm oil damper with one
  fixed orifice, but three times the 0.67 kN of an even-force oil damper.
- The carriage bounces back at 1.26 m/s with 4.0 J.
- **At 3 m/s (22.5 J) the bumper is too small.** It is fully pressed in, and 11 J is left for
  metal-on-metal contact.

## Checks

`check_model.mjs` tests:

1. With no voltage limit and a constant force, the impact speed is √(2·F·s/m).
2. n = 1, no push: c = m·(v₀ − v_end)/stroke.
3. n = 2, no push: c = m·ln(v₀/v_end)/stroke.
4. The energy balance closes for n = 1 and 2, with and without the push.
5. The motor force is zero just above the no-load speed η·V_dc/(√2·Ke).
6. With no speed limit, the defaults give 3.80 m/s, as the hand simulation of 2026-10-19 did. With
   the default speed limit, the impact speed is 2 m/s, and the time matches the exact value for a
   constant force.
7. The sized damper gives the allowed end speed.
8. The even-force reference holds the same energy as the damper.
9. A hand-set c is used as it is, and with the push the speed levels off at the terminal speed.
10. Bumper with a linear force curve, motor off: the compression is v₀·√(m/k), the time to stop is
    a quarter period, and the bounce-back speed is √(1 − absorbed)·v₀.
11. Bumper with p = 2: the compression matches the exact energy integral.
12. The bumper energy balance closes for p = 0.5, 1 and 2, with and without the push.
13. A bumper that is too small is fully pressed in, with the impact energy minus the catalog
    energy left.

## Limits

- One rigid mass. No guide friction, which would help a little.
- No field weakening. A drive that weakens the field can reach a higher speed.
- The bumper force depends on the compression only. Real elastomers get stiffer at high impact
  speed and when cold, so the real peak force can be higher. The bounce back assumes no friction.
- The damper force depends on the speed only. Real shock absorbers also change with the position
  (orifices that close) and have a return spring.
