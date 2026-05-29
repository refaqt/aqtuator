# Onboarding

## Prerequisites
### Python
Install the Python dependencies:
```bash
pip install -r src/python/requirements.txt
```

### Hardware (Controllino PWM -> ODrive GPIO1)
You need:
- Controllino Micro flashed with the appropriate sketch (see below)
- `ODrive S1` configured to map `GPIO1` analog input to torque input (configured by the Python scripts or manually)
- Wiring:
  - Controllino `D0` PWM output -> RC filter -> ODrive `GPIO1` (analog input)
  - Common GND between Controllino and ODrive

### Serial connection
The Controllino serial baud rate is `115200` (see the sketches).
Most Python scripts hard-code the serial port; update the `CONTROLLINO_PORT` constant in:
- `src/python/main_sequential.py`

## Firmware upload (Arduino IDE)
Use Arduino IDE with the Controllino Micro board support installed, then upload one of the sketches:
- Torque playback + multi-channel acquisition:
  - `src/controllino/main-controllino/main-controllino.ino`
- Standalone 8 kHz spindle controller (A0/A1/A3 -> x_spindle -> filters -> PWM on GPIO0):
  - `src/controllino/spindle-controller/spindle-controller.ino`
  - Enable gate: `GPIO1` / `D1` must be HIGH, otherwise output is forced to 0

The torque/acquisition sketch no longer uses CAN for torque commands.

## Run: Workflow A (torque playback + acquisition)
Entry point:
- `src/python/main_sequential.py`

Typical run:
```bash
python src/python/main_sequential.py
```

What happens:
- Connects to Controllino via serial
- Prompts for ODrive `CONTROL_MODE`: `p` (position, default) or `t` (torque)
- Uploads a multisine CSV waveform
- Starts `START_IDENTIFICATION,<duration>,<start_delay>`
- Waits for `ACK: Acquisition complete`
- Retrieves data via `GET_DATA` and plots time series + Bode-style estimates

Notes:
- This workflow does not attempt to retrieve ODrive position feedback during the real-time operation (per the sequential script’s logic).
- ODrive torque is driven by the Controllino PWM output (RC-filtered) into `GPIO1` analog mapping (not CAN).
- `odrv0.axis0.config.enable_step_dir` is forced to `False` at startup to allow torque-command operation, and set back to `True` after identification/cleanup.

## Run: Workflow B (servo identification sweep)
Entry point:
- `src/python/odrive_servo_identification.py`

Typical run:
```bash
python src/python/odrive_servo_identification.py
```

Prerequisites:
- ODrive firmware **0.6.12+** (high-rate capture)
- USB connection only (no Controllino or CAN adapter required)

What happens:
- Connects to ODrive via USB (through `src/python/odrive_config.py`)
- Iterates over the excitation frequency sweep (`fmin`, `fmax`, `df`)
- For each frequency:
  - sets autotuning frequency and amplitude
  - waits for settling (`t_delay`)
  - records `torque_setpoint` and `pos_estimate` via on-device high-rate capture
  - estimates transfer gain/phase at the excitation frequency

Interactive controls:
- The script prompts before starting identification and lets you stop early by typing `q`.

## Optional: PyQt GUI (alternate/legacy)
- `src/python/main_controller.py`

If you use it, confirm the serial command set and channel mapping match the firmware you flashed, since the Controllino sketches use `START_IDENTIFICATION` (and stream 5 channels) while the GUI code expects a different set of commands/channel counts.


