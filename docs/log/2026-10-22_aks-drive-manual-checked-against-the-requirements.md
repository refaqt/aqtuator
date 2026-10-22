# 2026-10-22 — AKS drive manual checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

The user added the full DGSMARTWIN AKS user manual to the repository. Check the AKS drive against
the drive requirements DRV-01 to DRV-10 and DRV-P1 to DRV-P3. Name the drive to ask a price for.
The stage will use an absolute linear encoder with EnDat 2.2 or BiSS-C.

## Work Done

### Short answer

- **Ask a price for the AKS-4D52AECAB.** That is the smallest size (4.5 A rms continuous, 16 A rms
  for 2 s), for 220 VAC, with EtherCAT and the "AB" encoder board. The same answer as on
  19 October, now based on the manual and not only on the catalog.
- **The "AB" board reads both EnDat 2.2 and BiSS-C.** The manual has a setup page for each one on
  a linear motor, with a 4 MHz clock. So the encoder choice is free. The "DB" board reads neither.
- **The manual settles four open points.** The drive follows the CiA 402 drive profile (DRV-07).
  Its tuning program shows a measured Bode plot (DRV-10). It has four filter slots with a fully
  free second-order filter (DRV-P1). It shows a block diagram of the control loop (DRV-P2).
- **One hard requirement is still open: the position loop rate (DRV-09).** The manual gives no
  current, velocity or position loop rate. The drive stays "not confirmed" until DGSMARTWIN
  gives the number in writing. This question must go with the price request.

### The AKS-4D52AECAB against the requirements

| Req. | Needed | AKS-4D52AECAB (manual) | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 4.5 A rms | Pass |
| DRV-02 | 5.9 A rms for 1 s | 16 A rms for 2 s | Pass |
| DRV-03 | Peak current limit and a motor thermal model | Max. motor current setting, and a motor I²t limit with current fold back | Pass. See the note on fold back below |
| DRV-04 | DC bus 320 V to 600 V | 220 VAC ±10 % input. On 230 VAC mains this gives about 325 V. Brake resistor on at 385 V | Pass, with no margin at low mains voltage |
| DRV-05 | Linear motor, 30 mm pole pitch, finds the commutation angle | Linear motor type with a pole pitch field. Phase search for absolute encoders, and a short-stroke search | Pass |
| DRV-06 | Reads the motor thermal sensor | PTC or NTC (KTY in the software), own alarm threshold | Pass, if the MK21 sensor is a PTC |
| DRV-07 | EtherCAT with CiA 402 | CiA 301 and CiA 402. Cycle 0.125 ms to 16 ms. Cyclic synchronous position mode | Pass |
| DRV-08 | Reads the stage encoder | EnDat 2.2 and BiSS-C on the "AB" board, 4 MHz clock | Pass |
| DRV-09 | Position loop 4 kHz or faster | Not given | **Not confirmed** |
| DRV-10 | Tuning program shows a Bode plot | Gain and phase from a measured speed loop test, 10 Hz to 1 kHz. Current loop also shown as Bode plots | Pass. See the note below |
| DRV-P1 | Own filters, a free second-order filter is best | Four filter slots. Types: low pass, general second-order, band stop, low pass with reduction, notch | Pass |
| DRV-P2 | Block diagram of the loop | Figure on page 136: position, speed and current loops, speed and torque feed forward | Pass, but it is a simple sketch |
| DRV-P3 | Position loop 8 kHz or faster | Not given | Not confirmed |

### Why the AKS-4D5 and not a larger size

The AKS-4D5 is the smallest size, and it already gives 2.7 times the MK21 peak current. A larger
size adds cost and makes the current measurement coarser. The 380 VAC sizes are not allowed: their
DC bus trips only at 780 VDC, which is above the 600 V limit of the MK21.

### What the manual does not answer

- **Loop rates.** Pages 137 and 138 use the words "speed loop rate" and "position loop rate", but
  they mean the gain of each loop, not how often it runs. The PWM is 10 kHz.
- **A hint, not a proof.** The drive accepts an EtherCAT cycle of 0.125 ms (8 kHz). Drives seldom
  accept a cycle shorter than their own position loop. So an 8 kHz position loop is likely. Under
  our rule this does not count. We need the number in writing.
- **The frequency sweep.** The table of contents calls section 9.6.1 "Speed Loop Frequency Sweep
  (Function Not Supported Temporarily)". The page itself shows a measured Bode plot, and its
  heading has no such note. Ask DGSMARTWIN to confirm that the sweep works in the current
  Drive Studio version.
- **Motor fold back.** Page 110 says the fold back values of a motor from the library cannot be
  changed by the user. The MK21 is not in the library. Ask how to set the I²t values for a
  third-party motor: 2.0 A rms continuous, 5.9 A rms for 1 s.
- **The encoder filter.** By default the drive filters the encoder position at 800 Hz. The manual
  says that a high-resolution encoder needs no filter, and that 0 Hz turns it off. Turn it off for
  our stage. An 800 Hz filter would add delay in the speed loop.

### EnDat 2.2 or BiSS-C

The AKS reads both, so the drive does not decide the encoder. Two points to weigh:

- With EnDat 2.2, DGSMARTWIN sells the matching SA32 encoder and the TC1 cable to the drive. One
  supplier answers for the full chain.
- With BiSS-C, the Numerik Jena LAK and LAKgo are on the short list of the
  [encoder selection page](../linear-encoder-selection.md). Their data sheets are better known.
  Ask DGSMARTWIN which BiSS-C encoders they have tested with the AKS.

## Decisions Made

No purchase decision. The AKS-4D52AECAB is the drive to ask a price for. It is still
"not confirmed" on DRV-09 and DRV-P3.

## Open Questions

Send these with the price request:

1. What are the current, speed and position loop rates of the AKS-4D52AECAB?
2. Is the speed loop frequency sweep (section 9.6.1) available in the current Drive Studio?
3. How do we set the motor I²t fold back for a third-party linear motor?
4. Is the MK21 thermal sensor ("3 PNC SNM120 in series") read correctly as a PTC?
5. Which EnDat 2.2 and BiSS-C linear encoders have you tested with the AKS?
6. Price and delivery time for 1 and for 2 drives, the Drive Studio software, and the connector set
   (power, encoder, I/O and STO).

## Next Steps

- Ask DGSMARTWIN (win@dgsmartwin.com) for a price for the AKS-4D52AECAB, with the questions above.
- Count the drive as a pass only after a written position loop rate of 4 kHz or more.

<details>
<summary>Sources</summary>

- DGSMARTWIN "AKS Series Servo Drives User Manual", file
  [`docs/documentation/AKS Drive Manual.pdf`](../documentation/AKS%20Drive%20Manual.pdf), 164 pages.
  Page numbers in the file match the printed page numbers.
  - Order codes and encoder boards: pages 19 to 21.
  - Supported motor types and control modes: page 27.
  - AKS-4D52A data: pages 28 and 29 (16 A rms for 2 s, PWM 10 kHz, brake resistor on at 385 VDC).
  - 380 VAC sizes, overvoltage trip 780 VDC: pages 32 to 39.
  - EtherCAT, CiA 301 and CiA 402, cycle 0.125 ms to 16 ms: page 44.
  - Encoder inputs and motor temperature input: page 46.
  - Motor setup with pole pitch and KTY or PTC sensor: page 84.
  - Encoder setup, 800 Hz default filter: page 85. EnDat and BiSS-C on a linear motor: pages 86
    and 87.
  - Current loop design with Bode plots: page 93. Phase search: page 95.
  - Speed loop test with Bode plot, four filter slots: page 96.
  - Current fold back: page 110.
  - Block diagram of the loop: page 136. Loop gains: pages 137 and 138.
  - Filter types: pages 139 to 146.
  - Alarm E0177 and the usual 500 µs EtherCAT cycle (p11610): alarm table, pages 155 and 156.
- The pages are partly images, and the plain text tool loses text on them. The text was read with
  `pypdfium2`, and the screenshots were read as images.
- Earlier catalog check: [AKS drive for the MK21 with EnDat](2026-10-19_dgsmartwin-aks-drive-for-mk21-with-endat.md).
- Requirements:
  [`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml).

</details>
