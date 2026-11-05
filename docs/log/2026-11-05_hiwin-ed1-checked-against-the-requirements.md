# 2026-11-05 — HIWIN ED1 (E1) drive checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

The HIWIN E2 drive cannot be delivered in Europe. The user asked for a check of the E1 drive
against all drive requirements (DRV-01 to DRV-10, DRV-P1 to DRV-P3), and for the product code of
the E1 drive that fits best. In Europe, HIWIN GmbH sells the E1 under the order code ED1.

## Work Done

### Short answer

- **Best fit: ED1F-EN-0422-01-00, with the ESC-SS-S02 encoder box.** That is the 400 W fieldbus
  drive with EtherCAT, no gantry function, 230 VAC, for linear motors (category 0), with certified
  STO. The ESC box is item 80050247 in the HIWIN GmbH catalogue. In that catalogue the same drive
  is written as ED1F-EN-0422-01.
- **The ED1 fails one hard requirement as written: DRV-08.** The drive cannot read our encoder on
  its own. It needs the external ESC box for BiSS-C, EnDat and 1 Vpp. DRV-08 asks for no converter
  box. With the box, the encoder signal itself passes.
- **One hard requirement is not confirmed: DRV-09.** The manuals give no position loop rate. The
  shortest EtherCAT cycle is 250 µs. That is not the same number, so we cannot count it.
- **Everything else passes on paper,** including the Bode plot tuning tool (DRV-10). The motor
  thermal sensor (DRV-06) needs either the ESC box or a forced stop input.
- **So the ED1 is not better than the E2 was.** It is the same family with the same tuning tool,
  but it needs one more box, one more cable and one more supplier item.

### The ED1F-EN-0422-01-00 against the requirements

| Req. | Needed | ED1F-EN-0422-01-00 (manuals) | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 2.5 A rms | Pass |
| DRV-02 | 5.9 A rms for 1 s | 10 A rms peak. The manual does not say how long the drive itself holds its peak | Pass on current. Time not stated |
| DRV-03 | Peak current limit and a motor thermal model | Custom motor entry with peak current, continuous current and peak time. "Motor overload protection 2" is an I²t limit that folds back to the continuous current | Pass |
| DRV-04 | DC bus 320 V to 600 V | 1 or 3 phase 200 to 240 VAC. On 230 VAC mains this gives about 325 V. Overvoltage trip 390 V | Pass, with no margin at low mains voltage |
| DRV-05 | Linear motor, 30 mm pole pitch, finds the commutation angle | Custom linear motor with a "pole pair pitch" field. "SW method 1" finds the electrical angle with a small move, without Hall sensors | Pass |
| DRV-06 | Reads the motor thermal sensor | PTC input only on the ESC box. Without the box: the forced stop input (FSTP) can stop the drive | Pass, if the MK21 sensor is a PTC, or with a small circuit on FSTP |
| DRV-07 | EtherCAT with CiA 402 | CoE with cyclic synchronous position, velocity and torque modes. Cycle 250 µs and longer, in steps of 250 µs | Pass |
| DRV-08 | Reads the stage encoder with no box | BiSS-C, EnDat 2.1/2.2 and 1 Vpp only through the ESC-SS box | **Fail as written.** Pass with the ESC-SS-S02 |
| DRV-09 | Position loop 4 kHz or faster | Not given | **Not confirmed** |
| DRV-10 | Tuning program shows a Bode plot | Thunder "Spectrum analyzer" measures the plant on the machine and draws a Bode plot. "Loop constructor" shows velocity and position loops, open and closed | Pass |
| DRV-P1 | Own filters, a free second-order filter is best | Seven filters at the same time: a first-order low-pass, a second-order low-pass, and five notch filters with frequency, Q and depth. No free biquad | Not met |
| DRV-P2 | Block diagram of the loop | Block diagrams for position mode, full-closed loop and model following control | Pass |
| DRV-P3 | Position loop 8 kHz or faster | Not given | Not confirmed |

### Why this size and these options

- **400 W (code 04).** The smallest size that HIWIN GmbH lists in its catalogue. It gives 1.25 times
  the MK21 continuous current and 1.7 times the MK21 peak current. The 500 W size (code 05) exists
  in the HIWIN Taiwan manual, but not in the HIWIN GmbH catalogue.
- **Fieldbus with EtherCAT (F and E).** DRV-07 needs EtherCAT. The standard version (S) has only
  pulse and ±10 V inputs.
- **No gantry function (N).** Each compact stage is one axis.
- **Category 0.** This is the code for linear, direct drive and torque motors. Code A is for HIWIN
  rotary motors only. Code T (GT) adds nano-positioning and a 2D error map. We do not need these
  now.
- **Safety version 1.** STO with a safety approval. The 12-digit code without "1" has STO without
  the approval.
- **ESC-SS-S02, not ESC-AN.** The SS box reads BiSS-C, EnDat 2.1/2.2 and 1 Vpp, so it works with
  our BiSS-C encoder, and EnDat and 1 Vpp too. The AN box reads only analogue encoders.

### The stage encoder works through the ESC box

The three places that name the stage encoder agree: `currentStage` in the drive requirements, the
read head in the stage architecture, and the bill of materials. All three name the RSF AK MC 15 B
with BiSS C. The mistake note of 2026-11-04 asks for this comparison before each drive check.

- **RSF MC 15 with BiSS-C.** The RSF frame is 32 bit position, 2 bit status and 6 bit CRC: 40 bit.
  The ESC box reads frames up to 46 bit and clocks BiSS-C at up to 5 MHz. RSF also sells the same
  head with EnDat 2.2, which the ESC-SS box also reads.
- **For reference, the old 1 Vpp encoder with a 20 µm period.** The manual gives 4 m/s for a 20 µm
  period, which is 200 kHz. So the ED1 with the ESC box would also have read the old encoder.

### If the time at peak current matters

The manual gives the peak current but not how long the drive itself can hold it. The motor peak
time is set in Pt52E (0.5 s to 60 s), and the I²t time in Pt554. If HIWIN cannot confirm 5.9 A for
1 s on the 400 W drive, the next size is the ED1F-EN-1022-01-00 (1 kW). It gives 5.6 A rms
continuous and 23.3 A rms peak, so 5.9 A for 1 s is no stress. It makes the current measurement
coarser.

## Decisions Made

No purchase decision. On paper, the ED1F-EN-0422-01-00 with the ESC-SS-S02 is the E1 drive to ask
a price for. It stays "fail as written" on DRV-08, and "not confirmed" on DRV-09 and DRV-P3.

The user decides whether a converter box from the same maker is acceptable for DRV-08. If it is,
the requirement text should say so.

## Open Questions

Send these with the price request to HIWIN GmbH:

1. What are the current, velocity and position loop rates of the ED1F-EN-0422-01-00, with a linear
   motor and the ESC-SS-S02?
2. Does the ESC box add delay to the position feedback? How much?
3. How long can the 400 W drive give 5.9 A rms?
4. Is the MK21 thermal sensor ("3 PNC SNM120 in series") read correctly by the ESC PTC input?
5. Price and delivery time for 1 and for 2 sets: drive, ESC-SS-S02, the cables between drive, ESC
   and encoder, and the connector set.

## Next Steps

- Decide whether a HIWIN converter box is allowed under DRV-08.
- If yes, send the price request and the questions above to HIWIN GmbH.
- Count the ED1 as a pass only after a written position loop rate of 4 kHz or more.

<details>
<summary>Sources</summary>

- HIWIN GmbH catalogue "Drives", ED1-03-0-EN-2410-K, supplied by the user. Order code p. 12,
  230 VAC data p. 13, ESC p. 26.
- HIWIN Mikrosystem "E1 Series Servo Drive User Manual", MD09UE01-2607 V3.3, from the HIWIN Taiwan
  manual page (link below). Section numbers:
  - 2.1.2 model explanation (order code). 2.2.2 linear motor with ESC, tables 2.2.2.2 and 2.2.2.3
    (top speed per encoder period, Pt207 note). 2.2.5 motor current and peak time.
  - 3.1.2 ESC model code. 3.5.1 ESC hardware: BiSS-C 5 MHz, data up to 46 bit, PTC input.
  - 4.1.3 power specification for 230 VAC: 400 W is 2.5 A rms rated, 10 A rms peak, PWM 16 kHz.
  - 6.10 motor overload protection, 6.10.3 Pt52E, 6.10.4 I²t (Pt554).
  - 8.15 forced stop input (FSTP). Control block diagrams in chapter 8 and section 10.6.8.
  - Chapter 10 notch filters with Q and depth.
- HIWIN Mikrosystem "E Series Servo Drive Thunder Software Operation Manual", MD12UE01-2605 V3.7.
  Section 4.3.3 custom motor (figure 4.3.3.1.5). Section 4.3.4 encoder setup and ESC. Section 4.6.4
  phase initialization (SW method 1, STABS, Hall). Section 6.3 spectrum analyzer and Bode plot.
  Section 6.3.1.2 the seven filters.
- HIWIN Mikrosystem "E Series Servo Drive EtherCAT (CoE) Communications Command Manual",
  MD08UE01-2305 V1.3, from hiwin.de. Section 2 cycle time (minimum 250 µs). Section 3.2 modes
  csp, csv, cst.
- RSF "MC 15 BiSS C interface description" and RSF MC 15 catalogue, in
  `modules/stoq/modules/rsf/docs/datasheets/`.
- HIWIN "HIMC3 & E Series Servo Drive" brochure MD98TE02-2506, for the E1 and E2 comparison.
- Download pages:
  - HIWIN Taiwan manual overview: <https://www.hiwinmikro.tw/Downloads/ManualOverview_EN.htm>
  - EtherCAT manual: <https://www.hiwin.de/medias/sys_master/hiwinDocumentMedia/hiwinDocumentMedia/h8b/h41/14712455004190/E-SERIES-SERVO-DRIVE-ETHERCAT-COE-COMMUNICATIONS-COMMAND-MANUAL-V1.3-EN-.pdf?attachment=true>
  - Brochure: <https://hiwin.com/wp-content/uploads/2026/08/HIMC3-E-Series-Servo-Drive-brochure-EN-1-1.pdf>
- The older links on the drive selection page (hiwin.de ED1 manual, hiwin.com E2 manual V1.6) now
  return "not found". The site motioncontrolsystems.hiwin.com no longer exists.
- Requirements:
  [`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml).

</details>
