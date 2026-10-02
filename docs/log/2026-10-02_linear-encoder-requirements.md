# 2026-10-02 — The linear encoder requirements are now in the SysML model

**Role(s):** engineering, hardware

## Goal

Write down what the linear encoder of the compact stage must do. An encoder search can then
check each candidate against a short name, for example ENC-03.

## Work Done

The requirements are in
[`modules/compact-stage/architecture/linear-encoder.sysml`](../../modules/compact-stage/architecture/linear-encoder.sysml).
The file follows the style of the stage and drive requirements. Every error value is a half band:
"5 µm" means "within +/- 5 µm". The limits that say "less than" or "more than" are strict.

| Short name | Requirement |
| --- | --- |
| ENC-01 | Resolution finer than 0.2 µm |
| ENC-02 | Accuracy within +/- 5 µm over 200 mm |
| ENC-03 | Maximum speed above 3 m/s |
| ENC-04 | Output is 1 Vpp sine and cosine, or BiSS-C. Incremental and absolute are both allowed |
| ENC-05 | Periodic error within +/- 0.3 µm |
| ENC-06 | Reading head less than 15 mm wide |
| ENC-07 | Reading head less than 18 mm high |
| ENC-08 | Reading head less than 40 mm long |
| ENC-09 | Scale less than 1 mm high |
| ENC-10 | Scale less than 12 mm wide |
| ENC-11 | Reading head angle against the scale: roll, pitch and yaw each within what the data sheet allows |

I also added a part for a candidate encoder, so a search can fill in one set of data sheet values
per encoder. Nothing has been checked against a real encoder yet.

ENC-11 has no number. You could not give one, so the requirement compares two things. One is the
angle the encoder allows, from its data sheet. The other is the angle our stage gives, which has
open values for now. Until those are filled in, ENC-11 cannot pass or fail. Mark it "not
confirmed" and keep the data sheet values.

## Decisions Made

- ENC-04 allows 1 Vpp sine and cosine, or BiSS-C. You first asked for BiSS-C absolute only, then
  allowed both. An incremental encoder needs a reference run after power on.

- All eleven are hard requirements. You gave no preferences.
- The file sits in the compact stage module, next to the drive requirements.
- ENC-02 asks for the accuracy over 200 mm. The data sheet must state it for 200 mm or more.
- ENC-03 and ENC-01 should hold together. A data sheet often gives a lower top speed at a finer
  resolution. Read the speed for the resolution we use.

## Open Questions

- **The encoder uses the whole stage error budget.** ENC-02 and the stage positioning error
  (STG-04) are both +/- 5 µm. The guide and the thermal drift add more error on top. Decide
  whether the encoder should be tighter, or whether the stage limit can be wider.
- **The data rate at 3 m/s.** At 3 m/s and 0.2 µm, the position changes 15 million times each
  second. For BiSS-C, the clock and the drive must keep up. For 1 Vpp, the drive must read the signal frequency. This is a hand calculation. Check it
  against the encoder and the drive manuals.
- **The existing drive check uses a 20 µm sine and cosine encoder.** DRV-08 already handles
  BiSS-C. Change `currentStage` in `motor-drive.sysml` when an encoder is chosen.

## Next Steps

- Fill in the angle our stage gives (roll, pitch and yaw). Use the CAD tolerances, the rotational
  error motion of the stage (STG-06, 20 µrad) and the mounting error of the head.
- Search for encoders that meet ENC-01 to ENC-11. Read every deciding number in the maker's
  data sheet.
- Check that the chosen drive reads the signal of that encoder. For BiSS-C, check the full frame.
  For 1 Vpp, check the highest signal frequency (DRV-08).
- Open the file once in SysON to confirm that it imports. It was written by hand and was not
  checked by a SysML parser.
