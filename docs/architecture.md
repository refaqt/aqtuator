# Architecture

## Goal
This project performs synchronized data acquisition and motor control using an `ODrive S1` drive:
- A host computer (Python) sends a torque waveform to a microcontroller.
- The microcontroller plays the waveform as **PWM (RC-filtered analog) into ODrive GPIO1** while sampling multiple analog channels.
- The host retrieves the recorded data over `serial` and computes analysis (time-domain plots and frequency-domain transfer estimates).

## Main components
### Microcontroller firmware (Controllino Micro / RP2040, Arduino IDE)
- Torque playback + multi-channel acquisition: [`src/controllino/main-controllino/main-controllino.ino`](src/controllino/main-controllino/main-controllino.ino)
  - Serial protocol: `UPLOAD_CSV` / `START_OUTPUT` / `START_IDENTIFICATION` / `GET_DATA` / `GET_STATUS`
  - Timing: RP2040 repeating timer ISR drives both **PWM duty updates** and ADC sampling
- Servo system identification (ODrive feedback capture): [`src/controllino/controllino-servo-identification/controllino-servo-identification.ino`](src/controllino/controllino-servo-identification/controllino-servo-identification.ino)
  - Serial protocol: `START_ACQUISITION` / `GET_DATA` / `GET_STATUS`
  - Timing: cyclic CAN messages from ODrive are paired (torque + position) and streamed back to Python

### Controllino MICRO pin-mapping convention (important)
- For `controllino_rp2` Arduino sketches, treat MICRO header `GPIO0`/`GPIO1` as direct RP2040/Arduino pins `D0`/`D1`.
- Do not derive Arduino pin indices from RP2040 package-pin numbers in the chip pinout drawing.
- Source of truth for firmware pin constants:
  - Controllino MICRO datasheet + block diagram
  - `controllino_rp2` `pins_arduino.h` (defines `D0 = 0u`, `D1 = 1u`)

### Host-side control + analysis (Python)
- Torque waveform + acquisition workflow (sequential phase 1): [`src/python/main_sequential.py`](src/python/main_sequential.py)
  - Uploads the waveform via serial, starts `START_IDENTIFICATION`, then calls `GET_DATA`
  - Prompts operator for ODrive `CONTROL_MODE` at runtime (`p`/`t`, default `p`)
  - Forces `odrv0.axis0.config.enable_step_dir = False` at startup so torque-command path can run, then restores it to `True` after identification/cleanup
  - Plots time series and a Bode-like transfer estimate via `scipy.signal.csd`/`welch`
- ODrive frequency sweep identification: [`src/python/odrive_servo_identification.py`](src/python/odrive_servo_identification.py)
  - Sweeps frequencies, configures ODrive cyclic CAN message rates, starts `START_ACQUISITION`
  - Estimates gain/phase from the recorded torque setpoint and position estimate
- ODrive configuration wrapper: [`src/python/odrive_config.py`](src/python/odrive_config.py)
  - Connects to ODrive over USB and sets control mode / input mode / closed-loop state

### Notes on the PyQt GUI script
- There is also [`src/python/main_controller.py`](src/python/main_controller.py), a PyQt5 GUI.
- Its serial command set and channel expectations appear to correspond to a different (non-current) firmware protocol than the Controllino sketches.
- Treat it as an alternate/legacy entrypoint unless you confirm the serial protocol matches your connected firmware.

## Data flow (overview)
```mermaid
flowchart TD
  Python["Python host (analysis + plotting)"] -->|"serial commands + waveform upload"| ControllinoFW["Controllino firmware"]
  ControllinoFW -->|"PWM (RC-filtered) -> GPIO1 analog mapping"| ODrive["ODrive S1"]
  ControllinoFW -->|"serial: DATA + DATA_END (and optional sections)"| Python
```

## Workflow A: Torque playback + multi-channel acquisition
### Serial frames (Controllino firmware)
The Controllino torque/acquisition firmware uses framed serial messages:
- `UPLOAD_CSV,<num_lines>` -> responds `READY`, then `ACK: CSV loaded` or `NACK: CSV load failed`
- `START_OUTPUT,<duration>`
  - responds `ACK: Output started`
  - during output, serial is blocked
  - completion is signaled with `ACK: Output complete` from the `loop()`
- `START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>`
  - responds `ACK: Identification started`
  - starts torque playback immediately; acquisition begins after the start delay
  - when acquisition completes, firmware emits `ACK: Acquisition complete`
- `GET_DATA` streams:
  - header: `DATA:<sample_count>,<sample_period>,5`
  - samples: per-line floats in this order: `A0,A1,A2,A3,output_voltage_command`
  - terminator: `DATA_END`

### Analysis done in Python
[`src/python/main_sequential.py`](src/python/main_sequential.py) transforms the received samples into:
- a time vector using `sample_rate = 1.0 / sample_period`
- geometric/derived quantities (`x`, `y`, `z`) and time-series plots
- Bode-style transfer estimates from `scipy.signal.csd`/`welch`

Runtime ODrive state machine in this workflow:
- Startup: connect ODrive -> prompt/apply control mode (`Position` default or `Torque`) -> set `enable_step_dir=False`
- Run: enter closed-loop for output/acquisition window
- Completion/cleanup: exit closed-loop -> set control mode to `Position` -> set `enable_step_dir=True`

## Workflow B: Servo identification (frequency sweep)
### ODrive cyclic CAN capture
In [`src/python/odrive_servo_identification.py`](src/python/odrive_servo_identification.py), ODrive is configured to emit cyclic CAN messages:
- message interval is set from the sweep parameter `ts`
- torque setpoints and encoder estimates arrive cyclically at the requested rates

### Serial frames (servo-identification firmware)
The Controllino servo-identification sketch streams:
- `START_ACQUISITION,<duration>,<cycle_time>,cyclic` -> `ACK: Acquisition started (cyclic mode)`
- `GET_DATA` streams:
  - header: `DATA:<sample_count>,<sample_period>,4`
  - samples per line:
    - `torque_setpoint, pos_estimate, torque_timestamp_us, pos_timestamp_us`
  - terminator: `DATA_END`
  - additional timestamp section:
    - `LOOP_TIMESTAMPS:<N>` ... `LOOP_TIMESTAMPS_END`

### Analysis done in Python
The sweep code computes transfer gain and phase at each excitation frequency from torque setpoint vs position estimate using `scipy.signal.csd`/`welch`-based estimation (`calculate_transfer_function()`).


