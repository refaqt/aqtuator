# stability-tests — Campaign Definition

## Purpose

Find the chatter stability limit by cutting at increasing depth of cut across a range of spindle
speeds, for each drive configuration. Together with [`tap-tests`](../tap-tests/) this gives both the
predicted stability lobes (from the measured FRF) and the observed limit.

## Setup

- **Machine:** Mekanika Pro
- **Instrument:** DATAQ WinDaq HiRes, 8 channels, 20 kHz aggregate
- **Materials:** aluminium and S235JR steel
- **Tool:** flat end mill, Fortis 19545060

## Cutting parameters

Encoded in the filenames and extracted into the manifest:

| Field | Manifest column | Example |
| --- | --- | --- |
| Radial depth of cut | `ae_mm` | `0.25` |
| Axial depth of cut (swept) | `ap_mm` | `0-10` |
| Spindle speed | `spindle_rpm` | `24000` |
| Feed | `feed` | `1800` |
| Material | `material` | `aluminium`, `steel-S235JR` |
| Axis | `axis` | `x`, `y` |
| Repeat | `repeat` | `1`, `2` |

Two naming styles appear. The 2026-02-19 run uses the long dated form
(`2026-02-19_13-37-00_X502_Y447_Z56_x_XYZ_fs_20000_..._F1200_S10000_steel_S235JR`); the 2026-05 runs
use the short form (`Alu_x_S24000_F1800_1`). Both parse into the same manifest columns.

## Protocol

1. Configure the drive under test; record gains in
   [`../../servo-configurations/`](../../servo-configurations/).
2. Fix `Ae` and spindle speed; ramp `Ap` from 0 to 10 mm through the cut.
3. Record the full 8-channel capture for the cut.
4. Repeat across the spindle-speed range, then per material and axis.

## Runs

| Run | Configuration |
| --- | --- |
| `2026-02-19_002_stability_tests_stepper` | Stepper |
| `2026-05-08_001_stability_tests_linear_encoder` | Servo, linear encoder feedback |
| `2026-05-11_001_stability_tests_rotary_encoder` | Servo, rotary encoder feedback |

Material parameters used for each run are recorded alongside the data in `Alu_parameters.txt` and
`St235JR_parameters.txt`.

## Data location

Recorded to the storage root declared in [`../../README.md`](../../README.md) and indexed in
[`../../data-index.csv`](../../data-index.csv). These runs are `raw` `.WDH` only — no CSV exports
were made, so reading them currently requires WinDaq.
