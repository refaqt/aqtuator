# 2026-10-12 — Water cooling fittings, and MK21 heat at 200 N

**Role(s):** engineering, purchasing

## Goal

Answer three questions about water cooling the MAXWELL MK21 linear motor (the forcer):

1. Can Festo air push-in fittings carry water?
2. Which L-shaped fitting with an M3 thread is the most compact?
3. Is an M3 fitting too small for enough water flow when the motor pushes a constant 200 N?

## Work Done

### Short answer

- **The motor is the limit, not the fitting.** At a constant 200 N, the MK21 coil gets too hot,
  even with perfect water cooling. 200 N is more than the rated continuous force of 181 N.
- **Standard Festo push-in fittings (QS series) and the brass NPQH series are rated for water.**
  The mini M3 fittings (QSML, QSMLL) are rated for compressed air only.
- **An M3 fitting can pass enough water.** About 0.3 to 0.5 l/min carries the heat away. A small
  pump can push that through an M3 bore. At 1 l/min the M3 bore becomes the limit.

### Fittings

The Festo data sheet download was blocked (error 403). The values below come from distributor
pages. Check the official data sheet for the exact part number before you order.

| Fitting | Thread / tube | Bore | Water rated? | Source |
| --- | --- | --- | --- | --- |
| Festo QSMLL-M3-4 (the most compact one) | M3 / 4 mm | 1.1 mm | No, air only | [BSP Automation](https://bspautomation.com/brand/festo/qsmll-m3-4) |
| Festo QSML-M3-4-100 (part 130769) | M3 / 4 mm | 1.3 mm | Not stated. Listings say air only | [Advantage Electric Supply](https://admin.advantageelectricsupply.com/part/festo/130769/1512942) |
| Festo QSML-M3-3-100 (part 130768) | M3 / 3 mm | about 0.8 mm | Air only | [Motion World](https://www.motionworld.com/products/165187/festo-130768-qsml-m3-3-100-push-in-l-fitting) |
| SMC KQ2L04-M3G1 | M3 / 4 mm | not checked | Yes, water from 0 to 40 °C | [Proax](https://proax.ca/en/product/1010107/smckq2l04m3g1), [Rubix](https://uk.rubix.com/en/kq2-one-touch-male-elbow/p-G1324005775) |
| Festo NPQH (nickel-plated brass) | M5 and larger | larger | Yes, up to 0.6 MPa at 0 to 50 °C | [Motion World](https://www.motionworld.com/products/162071/festo-578336-npqh-d-m7-q4-p10-push-in-fitting), [Rowse](https://www.rowse-pneumatics.co.uk/festo-npqh-d-m5-q6-p10-578335) |

The mini Festo fittings may work with clean water for a short test. Festo does not promise this.
For a permanent circuit, use a fitting that is rated for water. The SMC KQ2L04-M3G1 is the closest
M3 elbow with a water rating. If the plate has room for an M5 thread, Festo NPQH or standard QS
fittings have a water rating and a much larger bore.

### Motor heat at 200 N

All motor values are from the
[MAXWELL MK2 data sheet](../../modules/stoq/modules/maxwell/docs/datasheets/maxwell-mk2-iron-core-linear-motor.pdf):
thrust constant 92.5 N/A rms, motor constant 20.3 N/√W at 25 °C, thermal resistance 0.87 °C/W,
coil limit 120 °C, and resistance 13.8 Ω at 25 °C and 19.0 Ω at 120 °C.

- At 200 N the current is 2.16 A rms. The coil loss is 97 W when cold. It rises to about 140 W when
  hot, because copper resistance goes up with temperature.
- The 0.87 °C/W value gives exactly 181 N with the mounting face at 25 °C. So it is very likely
  measured from the coil to the mounting face. Water cooling only sets the temperature of that
  face. It does not change the heat path inside the motor.

| Mounting face temperature | Coil temperature at 181 N | Coil temperature at 200 N |
| --- | --- | --- |
| 25 °C | 120 °C (the limit) | 152 °C |
| 20 °C | 113 °C | 144 °C |
| 10 °C | 100 °C | 129 °C |

A constant 200 N needs a mounting face near 0 °C. That is not practical. The coil temperature
sensor would stop the drive.

### Water flow through M3 fittings

To carry away about 130 W:

| Water flow | Water temperature rise | Speed in 1.3 mm bore | Pressure loss per fitting (rough) |
| --- | --- | --- | --- |
| 0.3 l/min | 6 K | 3.8 m/s | about 0.2 bar |
| 0.5 l/min | 4 K | 6.3 m/s | about 0.5 bar |
| 1.0 l/min | 2 K | 12.6 m/s | about 2 bar |

The pressure loss values are rough estimates, not catalogue data. The 1.1 mm bore of the QSMLL
fitting roughly doubles the loss.

## Decisions

No decision yet. This entry records facts for the cooling design.

## Open Questions

- What is the real force profile during chatter suppression? Heat depends on the root-mean-square
  value (the effective average) of the force, not on the peak. Below about 170 N, the MK21 on a
  water-cooled plate at 15 to 20 °C has some margin.
- What is the 0.87 °C/W rating measured to? Does Maxwell or Saho offer a cooling plate?

## Next Steps

- Work out the root-mean-square force of a typical chatter suppression cut.
- If a constant 200 N is really needed, look at the MK22: 362 N continuous, 0.44 °C/W.
- Use water-rated fittings, M5 if there is room. Add a corrosion inhibitor to the water, because
  the circuit has brass in it.
- Ask Maxwell or Saho about the thermal resistance and a cooling plate.

<details>
<summary>How the numbers were worked out</summary>

- Coil loss: P = (F / Km)², with Km = 20.3 N/√W at 25 °C. The data sheet value fits
  Km = Kf / √(1.5 × R line-to-line) = 92.5 / √(1.5 × 13.8) = 20.3.
- Resistance against temperature: straight line from 13.8 Ω at 25 °C to 19.0 Ω at 120 °C.
- Coil temperature: T = T face + 0.87 × P(T), solved for T.
- Water temperature rise: ΔT = P / (ρ × c × Q), with P = 130 W.
- Pressure loss per fitting: Δp = K × ρ × v² / 2, with K = 2.5 as a rough value for a narrow elbow
  with entry and exit losses. Not from a catalogue.

</details>
