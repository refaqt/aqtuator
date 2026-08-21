# tap-tests — Campaign Definition

## Purpose

Measure the frequency response of the machine at the tool and at the spindle by impact hammer, to
locate the structural modes that limit chatter-free depth of cut. This is the measured counterpart
to the chatter model in [`simulation/`](../../../simulation/).

## Setup

- **Machine:** Mekanika Pro, X/Y/Z position recorded per run in the filename and manifest
- **Instrument:** DATAQ WinDaq HiRes, 8 channels, 20 kHz aggregate (`fs_20000` in filenames)
- **Excitation:** impact hammer, plastic tip
- **Configurations tested:** stepper, servo with rotary encoder, servo with linear encoder,
  flexible suspension, and flexible suspension with reciprocating slide motion

## Channel map

From the analysis configuration used to process these runs:

| Channel | Signal | Sensitivity |
| ------: | ------ | ----------- |
| 0 | `acc_spindle_top` | `a_5g` |
| 2 | `acc_spindle_left` | `a_5g` |
| 3 | `acc_spindle_right` | `a_5g` |
| 4 | `acc_workbed_x` | `a_5g` |
| 5 | `acc_workbed_y` | `a_5g` |
| 6 | `hammer_x` / `hammer_y` | `F_10x` |
| 7 | `acc_tool_x` / `acc_tool_y` | `a_50g` |

Channels 1 is unused. The `x`/`y` pairs share a channel because only one axis is instrumented per run —
the axis under test is recorded in the `axis` column of the manifest.

## Protocol

1. Position the machine to the X/Y/Z recorded in the run name.
2. Configure the drive under test (stepper / servo rotary / servo linear); record gains in
   [`../../servo-configurations/`](../../servo-configurations/).
3. Record a continuous 8-channel capture at 20 kHz aggregate.
4. Strike the tool or spindle repeatedly within the capture window.
5. Segment the capture into individual taps, exported as `..._tapNN.CSV`.

## Runs

| Run | Configuration |
| --- | --- |
| `2026-02-19_001_tap_tests` | Baseline, stepper |
| `2026-04-17_001_tap_tests_flexible_suspension` | Flexible suspension |
| `2026-04-24_001_tap_tests_flexible_suspension_reciprocating` | Flexible suspension, slide reciprocating |
| `2026-05-07_001_tap_tests_stepper` | Stepper |
| `2026-05-07_002_tap_tests_servo_rotary` | Servo, rotary encoder feedback |
| `2026-05-07_003_tap_tests_servo_linear` | Servo, linear encoder feedback |

Findings for the 2026-05-07 set are written up in
[`docs/dev-log/2026-05-07_frf-and-compliance-measurements.md`](../../../docs/dev-log/2026-05-07_frf-and-compliance-measurements.md).

## Analysis

FRF estimation (H1 estimator, `acc_tool_x - acc_workbed_x`) is performed by
[`refaqt/cnc-frf-estimation`](https://github.com/refaqt/cnc-frf-estimation), a separate tool. Its
outputs — Bode plots, real/imaginary tables, FFT tables — are the `derived` rows in
[`../../data-index.csv`](../../data-index.csv).

## Data location

Recorded to the storage root declared in [`../../README.md`](../../README.md) and indexed in
[`../../data-index.csv`](../../data-index.csv). Nothing from this campaign is committed to Git.
