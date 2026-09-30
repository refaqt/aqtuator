# 2026-09-30 — Delta ASDA-A3 checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

Check whether the Delta ASDA-A3 servo drive meets the requirements in
[`architecture/motor-drive.sysml`](../../architecture/motor-drive.sysml). Use the Delta catalog in
the shared drive and the Delta user manual of February 2025.

## Work Done

### Short answer

- **The ASDA-A3 does not meet the requirements today.** It fails one hard requirement on paper and
  cannot be confirmed on a second one.
- **It fails DRV-08, the encoder input.** The drive cannot read a 1 Vpp encoder by itself. It needs
  the Delta converter box ASD-IF-EN0A20 between the encoder and the drive. DRV-08 asks for no
  converter box. The box itself is fast enough: it takes up to 500 kHz, and we need 8.3 kHz.
- **DRV-09, the position loop rate, is not confirmed.** Delta does not publish it. The manual gives
  only the shortest EtherCAT cycle (125 µs) and a speed loop bandwidth of 3.1 kHz. Neither is the
  position loop rate.
- **Everything else passes, with the 400 W size (ASD-A3-0421-E) or larger.** The 200 W size has
  too little continuous current.
- **If we accept Delta's own converter box**, the A3 would pass all hard requirements except the
  loop rate. Then one question to Delta decides it: how often does the position loop run?

### ASDA-A3-E, 400 W (the smallest size that has enough current)

| Req. | Needed | ASDA-A3-E 400 W | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 2.65 A rms | Pass |
| DRV-02 | 5.9 A rms for 1 s | 10.61 A rms short time maximum. The motor overload model allows 295 % load for about 2.8 s | Pass |
| DRV-03 | Peak current limit and a motor thermal model | Motor rated and peak current are set in the drive. An overload model with a set time curve stops the drive (alarm AL006) | Pass |
| DRV-04 | DC bus 160 V to 600 V | 200 to 230 VAC, single or three phase, so about 325 V | Pass |
| DRV-05 | Linear motor, 30 mm period, finds the commutation angle | Linear motor mode for third-party motors. Pole pitch can be set from 1 mm to 500 mm. Finds the magnet position at start-up without Hall sensors | Pass |
| DRV-06 | Reads the motor thermal sensor | Input for an NTC or PTC sensor with a set trip level | Pass, if the MK21 sensor is an NTC or PTC. Type not known yet |
| DRV-07 | EtherCAT with CiA 402 | The -E model has EtherCAT with the CiA 402 profile | Pass |
| DRV-08 | Reads 1 Vpp directly, at 8.3 kHz | Only through the ASD-IF-EN0A20 converter box. The drive's own linear scale input takes digital A/B pulses only | Fail as written |
| DRV-09 | Position loop 4 kHz or faster | Not published | Not confirmed |
| DRV-P1 | Free second order filters | Five notch filters and one low-pass filter. Each notch has only a frequency, a width and a depth | Not met. The notches are fixed types, not free biquads |
| DRV-P2 | Published loop diagram | Simple block diagrams of the loops and the command filters. Not every gain is shown in one diagram | Partly met |
| DRV-P3 | Position loop 8 kHz or faster | Not published | Not confirmed |

### Other points

- The 200 W size gives only 1.55 A rms continuous, so it fails DRV-01.
- The earlier warning about drives made after week 23 of 2022 is about BiSS-C and other serial
  encoders. It does not affect the 1 Vpp route through the converter box.
- Without Hall sensors, Delta says: do not use the start-up magnet search on a vertical axis with a
  brake. Our stages are not vertical, so this does not apply today.

## Decisions Made

The ASDA-A3 stays off the short list for now. It goes back on only if both things below are true.

## Open Questions

- Do we accept a converter box when it comes from the drive maker? If yes, DRV-08 should say so, and
  the A3 passes it.
- What is the position loop period of the ASDA-A3? Only Delta can answer. This question is already
  open in the [HIWIN, Delta and Kollmorgen follow-up](2026-09-29_hiwin-delta-kollmorgen-follow-up.md).
- What does the ASD-IF-EN0A20 box cost?
- What type is the MK21 thermal sensor? This is still open from the requirements entry.

## Next Steps

1. Decide whether a converter box from the drive maker is allowed.
2. If yes, ask a Delta distributor for the position loop period and the price of the box.

<details>
<summary>Sources</summary>

- Delta ASDA-A3 catalog, `Delta-ASDA-A3-Servo-Drive-Catalog.pdf` in the shared drive (a copy from
  deltaacdrives.com). Drive table: continuous output current 0.9, 1.55, 2.65, 5.1, 7.3, 8.3, 13.4,
  19.4 A rms for 100 W to 3 kW; short time maximum 3.54, 7.07, 10.61 A rms for 100 W to 400 W.
  Speed loop bandwidth 3.1 kHz. Five notch filters up to 5000 Hz. CN5 takes A, B and Z pulses only.
- Delta ASDA-A3 user manual, revision 20250227:
  <https://www.damencnc.com/userdata/file/7617-5_Delta_ASDA_A3_Manual_English_2025.pdf>
  - Section 11.3.1.1: a 1 Vpp (sine wave) encoder must go to CN2 through the converter box. CN5
    receives pulses only. Parameters PM.003, PM.004, PM.005, PM.045, PM.046, PM.047.
  - Section 11.6.1: ASD-IF-EN0A20, analog input 0.4 to 1.2 Vpp, 500 kHz maximum.
  - Section 11.7.4: PM.011, start-up magnet search without Hall sensors (quick or smooth mode).
  - Section 11.7.5: overload time table, for example 300 % for 2.8 s, 500 % for 1 s (times PM.019).
  - Chapter 8: PM.022 sensor type (0 none, 1 Delta NTC, 2 NTC, 3 PTC) on CN5 pins 13 and 14;
    PM.024 trip resistance; PM.045 pole pitch 1.000 to 500.000 mm.
  - Chapter 8, filter parameters: notch filters 1 to 5 (P2.023, P2.043, P2.045, P2.098, P2.101 and
    their width and depth), resonance low-pass P2.025.
  - Section 6.2.3: control structure of position mode (block diagram).
  - EtherCAT chapter: the shortest SYNC0 cycle for A3-E is 125 µs. This is the bus cycle, not the
    position loop rate.
  - Section 11.2.3.2: the week 23 of 2022 note covers serial encoder formats only.
- Rule applied: [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md).
  The deciding number must come from the maker's own manual.

</details>
