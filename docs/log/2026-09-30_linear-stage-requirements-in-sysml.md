# 2026-09-30 — The linear stage requirements are now in the SysML model

**Role(s):** engineering, hardware

## Goal

Write down the requirements for the linear motor stage as a whole, next to the drive
requirements. A design review or a measurement can then cite each one by a short name.

## Work Done

### Update after review

Later the same day the user changed three things:

- **The force is lower.** STG-10 is now 180 N continuous, and STG-11 is 500 N peak. One MK21
  meets both: its data sheet gives 181 N and 512 N.
- **The drive requirements now use 3 m/s.** The stage in `motor-drive.sysml` now has a top speed of
  3 m/s. With the 20 µm encoder, DRV-08 now asks for 1 Vpp at 150 kHz, not 8.3 kHz. The CDHD2S
  reads 1 Vpp up to 300 kHz, and the Delta converter box up to 500 kHz, so both still meet
  the speed. Those numbers come from the manuals, as recorded in the earlier log entries.
- **The drive bus voltage was checked again for 3 m/s.** DRV-04 now asks for 320 V to 600 V,
  not 160 V to 600 V. The table below shows the hand calculation.

| Case, coil at 120 °C | Bus voltage needed |
| --- | ---: |
| 180 N at 3 m/s | 320 V |
| 500 N at 3 m/s | 491 V |
| 500 N at 0.17 m/s (the old case) | 155 V |

| Bus voltage | Force at 3 m/s | Speed at 500 N |
| --- | ---: | ---: |
| 293 V (230 VAC, 10 % low) | 118 N | 1.4 m/s |
| 325 V (230 VAC) | 190 N | 1.7 m/s |
| 565 V (400 VAC) | 626 N | 3.6 m/s |

The calculation is the same as in the
[drive survey of 2026-09-25](2026-09-25_linear-stage-drive-and-motion-controller-survey.md): sine
commutation, 90 % use of the bus voltage, and the MK21 values from its data sheet. At 3 m/s the
back EMF (the voltage the moving motor makes) is 160 V rms line to line. The coil inductance now
matters too, because the current changes at 100 Hz. This is a hand calculation, not a measurement.

The user chose 180 N at 3 m/s as the rule. The full 500 N is only needed while the stage speeds up,
at lower speed. A 400 VAC drive would give 500 N at 3 m/s. But its bus can go above the 600 V
limit of the MK21 when the mains voltage is high or when the motor brakes.


The requirements are in [`architecture/linear-stage.sysml`](../../architecture/linear-stage.sysml).
Every error value is a half band: "5 µm" means "within +/- 5 µm".

| Short name | Requirement |
| --- | --- |
| STG-01 | Width at most 210 mm |
| STG-02 | Height at most 60 mm |
| STG-03 | Length at most travel + 340 mm - 2 x height |
| STG-04 | Total positioning error (systematic and random) within +/- 5 µm, without calibration |
| STG-05 | Linear error motion (straightness and flatness) within +/- 2 µm |
| STG-06 | Rotational error motion (roll, pitch and yaw) within +/- 20 µrad |
| STG-07 | Repeatability from one direction within +/- 0.1 µm |
| STG-08 | Repeatability from both directions within +/- 0.3 µm |
| STG-09 | Top speed at least 3 m/s |
| STG-10 | Continuous driving force at least 180 N |
| STG-11 | Peak driving force at least 500 N |
| STG-12 | Mechanical output power at least 100 W |
| STG-13 | Sideways load at the centre of the carriage at least 500 N, in either direction |
| STG-14 | Screw holes at each interface on a 20 mm, 40 mm or 80 mm grid |

## Decisions Made

- The file sits in the top level `architecture/` folder, like the drive requirements. No stage
  family owns the MK21 stages yet.
- All fourteen are hard requirements. The user gave no preferences.

## Open Questions

- **A 230 VAC drive has no voltage margin at 3 m/s.** It gives about 325 V, and DRV-04 asks for
  320 V. The bus voltage drops under load and when the mains voltage is low. At 293 V, the MK21
  gives only about 118 N at 3 m/s. The CDHD2S is rated for 220 VAC, which gives about 311 V. That
  is below 320 V, so check it against DRV-04 again.
- **How to measure.** The requirements do not yet say which standard or which test method
  checks the accuracy values (for example ISO 230-2 for the positioning error).

## Next Steps

- Check the CDHD2S and the Delta ASDA-A3 against the new DRV-04, with the real bus voltage at our
  mains supply.
- Measure the force at 3 m/s on the real stage to confirm the hand calculation.
- Open both SysML files once in SysON to confirm that they import without errors. They were
  written by hand and were not checked by a SysML parser.
