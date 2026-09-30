# 2026-09-30 — Delta ASDA-A3 drives checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

Check whether any Delta ASDA-A3 servo drive meets the requirements in
[`architecture/motor-drive.sysml`](../../architecture/motor-drive.sysml). The user supplied the
ASDA-A3 catalog (edition 2025-02-24) and the full user manual (edition 2025-02-27). If no drive
passes, say which requirements it misses.

## Work Done

### Short answer

- **No ASDA-A3 drive is confirmed to meet all hard requirements.** One model comes close: the
  **ASD-A3-0421-E** (400 W, 230 VAC, EtherCAT). It passes seven of the nine hard requirements on
  paper.
- **It fails DRV-08 as the requirement is written.** The drive cannot read a 1 Vpp encoder by
  itself. It needs Delta's own converter box, the ASD-IF-EN0A20. The box takes 1 Vpp signals up to
  500 kHz, so the signal speed is not a problem. The problem is only that DRV-08 asks for no box.
- **DRV-09 is not confirmed.** Neither the catalog nor the 1,000-page manual gives the position
  loop rate. The fastest EtherCAT cycle is 125 µs, but that is a different number and does not
  count.
- **It does run a linear motor.** The manual has a full chapter on linear and third-party motors.
  The pole pitch is a setting (1 mm to 500 mm), it finds the commutation angle without Hall sensors,
  and it reads NTC and PTC motor thermal sensors.
- **So the ASDA-A3 is a better fit than the earlier note said.** The open questions are the
  loop rate, and whether we accept Delta's own converter box.

### ASD-A3-0421-E (the closest drive)

| Req. | Needed | ASD-A3-0421-E | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 2.6 A rms continuous | Pass |
| DRV-02 | 5.9 A rms for 1 s | 10.61 A rms maximum. 5.9 A is 227 % of rated current, and the overload curve allows 6.1 s at 220 % and 4.8 s at 240 % | Pass |
| DRV-03 | Peak current limit and a motor thermal model | PM.046 sets the rated and PM.047 the maximum current of the linear motor. PM.019 and PM.020 set a motor overload model (alarm AL006) | Pass |
| DRV-04 | DC bus 160 V to 600 V | 1 or 3 phase 200 to 230 VAC, so about 300 V to 325 V | Pass |
| DRV-05 | Linear synchronous motor, 30 mm period, finds the commutation angle | Linear motor mode. PM.045 pole pitch from 1 mm to 500 mm. With PM.003 set to "no Hall sensor", the motor moves slightly at the first servo on to find the magnetic pole | Pass |
| DRV-06 | Reads the motor thermal sensor | PM.022 reads an NTC or a PTC sensor on CN5 pins 13 and 14 and stops the drive at a set resistance (PM.024) | Pass, if the MK21 sensor is a PTC or NTC. Type still unknown |
| DRV-07 | EtherCAT with CiA 402 | EtherCAT, CoE, CiA 402 with cyclic synchronous position, velocity and torque modes | Pass |
| DRV-08 | Reads 1 Vpp at 8.3 kHz, no converter box | 1 Vpp only through the ASD-IF-EN0A20 box on CN2 (500 kHz maximum). The drive's own scale input (CN5) takes only digital A/B pulses | **Fail as written** |
| DRV-09 | Position loop 4 kHz or faster | Not published | **Not confirmed** |
| DRV-P1 | Free second order filters | Five notch filters, each with frequency (up to 5,000 Hz), depth and Q factor. Two "vibration elimination" filters, each a pair of resonance and anti-resonance frequencies, but only up to 400 Hz and only in the command path. No free biquad | Partial |
| DRV-P2 | Published loop diagram | Block diagrams of the position, speed and torque loops, and of the filter chain | Pass |
| DRV-P3 | Position loop 8 kHz or faster | Not published | Not confirmed |

### Other ASDA-A3 sizes

| Model | Continuous / maximum current (A rms) | Result |
| --- | --- | --- |
| ASD-A3-0221-E (200 W) | 1.55 / 7.07 | Fails DRV-01 |
| **ASD-A3-0421-E (400 W)** | **2.6 / 10.61** | Closest match, see above |
| ASD-A3-0721-E (750 W) | 5.1 / 21.21 | Works, but more than twice the MK21 current. Only needed if the 400 W drive runs too hot |
| ASD-A3-0743-E (750 W, 400 VAC class) | 3.12 / 9.7 | Current fits. But the drive takes 380 to 480 VAC three phase. At 480 VAC the bus is about 680 V, which is above the 600 V limit of the MK21. Needs a three phase supply of about 420 VAC or less |

The "L", "M" and "F" versions have no EtherCAT. They fail DRV-07.

### If the encoder changes to BiSS-C

The A3-E reads BiSS-C, EnDat 2.2 and several other serial encoders directly on CN2, without the
box. But the manual marks BiSS-C and EnDat on the A3-E with a note: because of a chip shortage,
this function is "temporarily affected" for all drives made from week 23 of 2022. So a BiSS-C
encoder would not help until Delta confirms the function works on new drives.

## Decisions Made

No purchase decision. The ASD-A3-0421-E goes on the short list as "not confirmed", together with
the ASD-IF-EN0A20 converter box.

Later the same day the user made it the fallback drive, in case the Servotronix CDHD2 does not
work. See [the decision record](../decisions/2026-09-30_delta-asda-a3-as-fallback-drive.md).

## Open Questions

- **What is the position loop rate of the ASDA-A3?** Only Delta can answer this. It decides
  DRV-09.
- **Do we accept Delta's own converter box for DRV-08?** The box sits between the encoder and the
  drive, but it is a Delta part, it takes its power from the drive, and its 500 kHz limit is far
  above our 8.3 kHz. The requirement says "no converter box" today. If the reason is extra delay,
  ask Delta how much delay the box adds.
- What is the price of the ASD-A3-0421-E and of the ASD-IF-EN0A20 box?
- Is the MK21 thermal sensor ("3 PNC SNM120 in series") a PTC? If yes, DRV-06 passes.
- Does BiSS-C work on an A3-E made today?

## Next Steps

1. Send the questions above to a Delta distributor.
2. Decide whether DRV-08 should allow a converter box from the drive maker itself. If yes, change
   the requirement text in the SysML model, not in this entry.

<details>
<summary>Sources</summary>

Both files were supplied by the user and read in full text search. They are not in the repository.

- Catalog `DELTA_IA-ASDA_ASDA-A3_C_EN_20250224.pdf`: drive model code (EtherCAT only on "E"),
  220 V and 400 V drive tables (currents, supply range), CN5 wiring with Hall and TEMP pins, speed
  loop bandwidth 3.1 kHz.
- User manual `DELTA_IA-ASD_ASDA-A3_UM_EN_20250227.pdf`:
  - Section 3 (CN5 pin table, p. 3-95): A/B/Z differential up to 4 MHz, Hall inputs, TEMP+ and
    TEMP−, NTC and PTC supported.
  - Chapter 8: PM.003 (CN2 signal type, Hall sensor setting, p. 8-227), PM.019 and PM.020
    (motor overload model), PM.022 and PM.024 (thermal sensor, p. 8-237), PM.045 to PM.047
    (pole pitch, rated and maximum current, p. 8-240 and 8-241), P1.089 to P1.094 (vibration
    elimination, 1 Hz to 400 Hz, p. 8-63).
  - Section 5.7 (p. 5-45 onward): filter block diagram, five notch filters with Q factor.
  - Section 6.2.3, 6.3.2 and 6.4.2: control structure diagrams.
  - Section 11.2.3.2 (p. 11-12): serial encoder formats and the chip shortage note.
  - Section 11.6.1 (p. 11-34): ASD-IF-EN0A20, analog input 500 kHz maximum.
  - Section 13.2: EtherCAT specification, CiA 402 modes, SYNC0 cycle of 125 µs, 250 µs, 500 µs
    or a multiple of 1 ms.
  - Appendix A.2.4 (p. A-21): overload curve, 220 % for 6.1 s, 240 % for 4.8 s.
- Search for a loop period: the words "position loop" appear only next to gain and bandwidth. No
  update period or loop rate is given anywhere in the manual.

</details>
