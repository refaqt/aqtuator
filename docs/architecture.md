# Architecture

Short overview and pointers. The layout convention itself is specified in
[`doqs/docs/architecture.md`](../doqs/docs/architecture.md) — this file does not restate it.

## What this project is

AQTUATOR investigates **chatter suppression on a Mekanika Pro milling machine** by adding an active
actuator. The work so far has been to characterise the machine — measure its frequency response and
stability limits under stepper and servo drives — so that an actuator can be designed against real
numbers rather than assumptions.

The repository holds the machine: its CAD, the models that predict its behaviour, the campaigns that
measured it, and the firmware and host software built to run those campaigns. Actuator concept
sizing (50 × 50 × 20 mm, 200 N, 0.1 mm, > 10 Hz) lives in
[`simulation/cases/short-stroke-actuator-concepts`](../simulation/cases/short-stroke-actuator-concepts/).

## Module map

| Folder | What |
| --- | --- |
| [`cad/`](../cad/) | FreeCAD models of the machine and the actuator |
| [`architecture/`](../architecture/) | SysML requirements and block definitions |
| [`simulation/`](../simulation/) | Design-time models: structural dynamics, PWM/RC trade-off |
| [`measurement/`](../measurement/) | Physical campaigns — tap tests, stability tests — and the manifest indexing 1.88 GB of data held on Google Drive |
| [`firmware/`](../firmware/) | Controllino MICRO (RP2040) targets |
| [`software/`](../software/) | Host-side Python: identification stack, measurement tooling |
| [`docs/log/`](log/) | Chronological record of the work (activity log) |
| [`docs/decisions/`](decisions/) | Why things are the way they are |
| [`docs/mistakes/`](mistakes/) | What not to repeat |

## The identification signal chain

The central technical arrangement: a torque command generated on the host reaches the ODrive as an
*analog* voltage, because the CAN path could not sustain the required rate.

```mermaid
flowchart LR
  Host["Host<br/>software/identification"]
  FW["Controllino MICRO<br/>firmware/torque-excitation"]
  ODrive["ODrive S1"]
  Machine["Mekanika Pro"]
  DAQ["WinDaq DAQ<br/>8 ch @ 20 kHz"]

  Host -->|"serial: waveform upload"| FW
  FW -->|"PWM -> RC filter -> GPIO1 analog in"| ODrive
  ODrive -->|torque| Machine
  Machine -->|accelerometers + hammer| DAQ
  FW -->|"serial: DATA / DATA_END"| Host
  DAQ -->|".WDH / .CSV"| Drive[("Google Drive<br/>indexed by measurement/data-index.csv")]
```

Workflow B bypasses the Controllino entirely and captures inside the ODrive over USB at the
control-loop rate.

Details live with the code they describe:
[`firmware/torque-excitation/README.md`](../firmware/torque-excitation/README.md) for the serial
protocol, PWM behaviour, pin mapping and safety invariants;
[`software/identification/README.md`](../software/identification/README.md) for both workflows and
the ODrive lifecycle.

## Hardware generations

Two earlier generations were tried and abandoned; their code is deleted but recoverable from git
history and the `dev-nucleo` / `dev-gui` branches.

| Generation | Outcome |
| --- | --- |
| Arduino Opta | Analog output could not exceed ~20 Hz — [dev-log 2025-11-14](dev-log/2025-11-14_opta-analog-bandwidth-limit.md) |
| NUCLEO-G474RE + CAN | CAN torque commands too slow and awkward — [dev-log 2025-12-10](dev-log/2025-12-10_nucleo-odrive-can-connection.md) |
| **Controllino MICRO + PWM→GPIO1** | Current — [decision record](decisions/2026-03-25_replace-can-torque-with-pwm-to-gpio1-analog-mapping.md) |
