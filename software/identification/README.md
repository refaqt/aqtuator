# identification

Host-side torque excitation, acquisition and servo identification for the AQTUATOR test rig.

## Install

```bash
pip install -e software/identification
```

Needs Python 3.10+, an ODrive S1 on USB, and for Workflow A a Controllino MICRO running
[`firmware/torque-excitation`](../../firmware/torque-excitation/).

## Workflows

### A — Torque playback and multi-channel acquisition

```bash
aqtuator-sequential
```

Uploads a multisine waveform to the Controllino over serial, runs `START_IDENTIFICATION`, then pulls
the samples back with `GET_DATA`. Plots the time series and a Bode-style transfer estimate
(`torque_command` → `x_spindle`) via `scipy.signal.csd` / `welch`.

Prompts for the ODrive control mode at runtime (`p` position, default, or `t` torque). ODrive
lifecycle:

1. **Startup** — connect, apply control mode, set `enable_step_dir = False` so the torque-command
   path can run
2. **Run** — verify and log `gpio1_mode` and the analog mapping, enter closed loop for the
   acquisition window, re-check the same state afterwards
3. **Cleanup** — leave closed loop, clear the analog endpoint while keeping
   `gpio1_mode = ANALOG_IN`, restore position mode and `enable_step_dir = True`

`gpio1_mode` is logged at all four points precisely so a Python-driven run can be diffed against a
working manual GUI session. Keep `input_torque` feedforward enabled in both control modes: the
confirmed 2026-03-31 bug was never "using `input_torque` in position mode", it was failing to verify
the GPIO1 analog-input state across the lifecycle.

### B — Servo identification by frequency sweep

```bash
aqtuator-servo-id
```

No Controllino and no CAN bus. Sweeps frequencies using ODrive autotuning in torque mode
(`TUNING` input mode) and captures `axis0.controller.torque_setpoint` and `axis0.pos_estimate` at the
native control-loop rate (~8 kHz) with `odrive.utils.high_rate_capture`.

Per frequency: set autotuning → settle (`t_delay`) → `high_rate_capture_start()` → record for
`duration` → `trigger_and_download_sync(trigger_point=1.0)`. Gain and phase come from Welch/CSD on
the recorded signals.

**Requires** ODrive firmware 0.6.12+ and the `odrive` package 0.6.11.post0+. With two captured
variables the on-device buffer spans at most 1024 ms, so keep `duration` ≤ 1 s. See
[the decision record](../../docs/decisions/2026-05-29_workflow-b-acquisition-via-on-device-high-rate-capture.md).

### Waveform generation

```bash
aqtuator-multisine
```

Crest-factor-optimised multisine, exported as CSV with a metadata header.
`MAX_CSV_SAMPLES = 2000` is kept in sync with the firmware buffer — changing one requires changing
the other. A generated reference waveform is in [`config/`](config/).

## Modules

| Module | Role |
| --- | --- |
| `aqtuator_id.odrive_config` | `ODriveController` — USB connect, control/input mode, closed loop, and enforcement of the `gpio1_mode = ANALOG_IN` invariant |
| `aqtuator_id.sequential_run` | Workflow A entry point |
| `aqtuator_id.servo_identification` | Workflow B entry point |
| `aqtuator_id.multisine` | `MultisineOptimizer` — waveform generation |

Modules import each other package-relatively, so run them via the console scripts above or
`python -m aqtuator_id.<module>`, not as loose files.
