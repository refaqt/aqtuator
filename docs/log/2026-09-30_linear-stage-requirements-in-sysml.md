# 2026-09-30 — The linear stage requirements are now in the SysML model

**Role(s):** engineering, hardware

## Goal

Write down the requirements for the linear motor stage as a whole, next to the drive
requirements. A design review or a measurement can then cite each one by a short name.

## Work Done

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
| STG-10 | Continuous driving force at least 200 N |
| STG-11 | Peak driving force at least 550 N |
| STG-12 | Mechanical output power at least 100 W |
| STG-13 | Sideways load at the centre of the carriage at least 500 N, in either direction |
| STG-14 | Screw holes at each interface on a 20 mm, 40 mm or 80 mm grid |

## Decisions Made

- The file sits in the top level `architecture/` folder, like the drive requirements. No stage
  family owns the MK21 stages yet.
- All fourteen are hard requirements. The user gave no preferences.

## Open Questions

These new numbers do not match the drive requirements or the motor. They are not changed yet.
Each needs a decision.

- **One MK21 motor is too weak.** The MAXWELL MK2 data sheet gives 181 N continuous and 512 N
  peak for the MK21. STG-10 asks for 200 N and STG-11 for 550 N. The stage needs a stronger
  motor, or two motors.
- **The drive requirements use a much lower top speed.** They use 10 000 mm/min (0.17 m/s).
  STG-09 asks for 3 m/s, which is 18 times faster. With the 20 µm encoder, the encoder signal
  then reaches 3 m/s / 20 µm = 150 kHz, not 8.3 kHz (DRV-08). The motor voltage also rises: the
  MK21 back EMF alone is about 53.4 x 3 = 160 V rms line to line at 3 m/s. The 160 V lower bus
  limit in DRV-04 is then too low. This is a hand estimate and must be checked.
- **How to measure.** The requirements do not yet say which standard or which test method
  checks the accuracy values (for example ISO 230-2 for the positioning error).

## Next Steps

- Decide on the motor: a stronger MAXWELL model, or two MK21 motors per stage.
- Change the top speed in `currentStage` in `architecture/motor-drive.sysml` to 3 m/s once the
  encoder is chosen. Then work out DRV-04 again for the new speed.
- Open the file once in SysON to confirm that it imports without errors. It was written by hand
  and was not checked by a SysML parser.
