---
name: project-patterns
description: Reusable implementation patterns proven in this project - serial ACK handshakes, framed CSV upload, DATA/DATA_END streaming, CSD/Welch transfer estimation, ODrive high-rate capture and CAN rates, multisine CSV export, Controllino GPIO-to-Arduino pin mapping, RP2040 timer-ISR PWM, GPIO1 analog verification, and RBJ biquad filters. Load before writing new code for serial protocols, ODrive control, RP2040 PWM/ADC, or transfer-function estimation.
---


## Serial command handshake with ACK/ERROR prefix matching
**When to use:** You need deterministic serial command/response behavior where responses may include extra lines (`DEBUG:`/`INFO:`) or where the ACK line includes extra context.
**Pattern:**
```python
def send_command_and_wait_response(serial_port, serial_lock, cmd, expected_ack, timeout=2.0):
    with serial_lock:
        # Clear input buffer before sending
        while serial_port.in_waiting > 0:
            serial_port.read(serial_port.in_waiting)

        serial_port.write((cmd + "\n").encode())
        serial_port.flush()

        max_steps = int(timeout * 100)  # ~10ms polling
        for _ in range(max_steps):
            if serial_port.in_waiting <= 0:
                time.sleep(0.01)
                continue

            line = serial_port.readline().decode().strip()

            if line.startswith("ERROR:"):
                return False, line
            if line.startswith("DEBUG:") or line.startswith("INFO:") or line == "":
                continue

            # Exact match or prefix match (e.g., "ACK: Acquisition started (cyclic mode)")
            if line == expected_ack or line.startswith(expected_ack):
                return True, line

        return False, "timeout"
```
**Gotchas:** If firmware blocks serial during output/acquisition, you must not expect responses until the real-time section ends; also make sure to clear stale buffered lines before issuing the command.
**Last used:** 2026-03-23

## Upload framed CSV to firmware (send count + stream lines)
**When to use:** A firmware expects `UPLOAD_CSV,<num_lines>` followed by exactly `<num_lines>` CSV payload lines (with optional `#` comments and header rows skipped).
**Pattern:**
```python
def upload_csv(serial_port, serial_lock, csv_path):
    # Read file and count only data lines
    data_lines = []
    with open(csv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#") or line.lower() == "time_s,signal":
                continue
            data_lines.append(line)

    with serial_lock:
        # Clear input buffer
        while serial_port.in_waiting > 0:
            serial_port.read(serial_port.in_waiting)

        serial_port.write(f"UPLOAD_CSV,{len(data_lines)}\n".encode())
        serial_port.flush()

        # Wait for READY, then stream lines, then wait for ACK/NACK
        # (Implementation depends on your firmware)
```
**Gotchas:** The firmware typically assumes the host sends the exact number of payload lines; if your CSV parser accidentally includes header/comment rows, the next stage will desynchronize.
**Last used:** 2026-03-23

## Read `DATA:` frames until `DATA_END`
**When to use:** You need to fetch large time-series payloads over text serial without relying on a single read size.
**Pattern:**
```python
def read_data_frame(serial_port):
    # Wait for header like: DATA:<sample_count>,<sample_period>,<num_channels>
    while True:
        line = serial_port.readline().decode().strip()
        if line.startswith("DATA:"):
            break
        # Optionally skip DEBUG/INFO/empty lines

    parts = line[5:].split(",")
    sample_count = int(parts[0])
    sample_period = float(parts[1])
    num_channels = int(parts[2])

    samples = []
    for _ in range(sample_count):
        row = serial_port.readline().decode().strip()
        if row == "DATA_END":
            break
        samples.append([float(x) for x in row.split(",")])

    return samples, sample_period, num_channels
```
**Gotchas:** Some firmwares also emit additional tagged sections after `DATA_END` (e.g., `LOOP_TIMESTAMPS:`). If you need those, don’t stop reading after `DATA_END`.
**Last used:** 2026-03-23

## Transfer function estimation from CSD/Welch (gain + unwrapped phase)
**When to use:** You want a stable gain/phase estimate between an excitation and response using measured data segments.
**Pattern:**
```python
from scipy import signal
import numpy as np

def estimate_transfer(input_signal, output_signal, sample_rate):
    f, Pxy = signal.csd(output_signal, input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
    f, Pxx = signal.welch(input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
    H = Pxy / (Pxx + 1e-10)

    magnitude = np.abs(H)
    phase = np.unwrap(np.angle(H)) * 180 / np.pi  # degrees
    return f, magnitude, phase
```
**Gotchas:** Choose `nperseg` carefully; extremely short signals can make `nperseg` too small and destabilize estimates. Also unwrap phase for continuity.
**Last used:** 2026-03-23

## Configure ODrive cyclic CAN message rates
**When to use:** You need deterministic cyclic CAN emissions from ODrive for system identification (instead of polling).
**Pattern:**
```python
def configure_cyclic_can_messages(axis, interval_ms, enable=True):
    if enable:
        axis.config.can.encoder_msg_rate_ms = interval_ms
        axis.config.can.torques_msg_rate_ms = interval_ms
    else:
        axis.config.can.encoder_msg_rate_ms = 0.0
        axis.config.can.torques_msg_rate_ms = 0.0
```
**Gotchas:** ODrive uses interval units in milliseconds; align your firmware `cycle_time`/sampling period to the interval you configure here.
**Last used:** 2026-03-23

## Servo identification via ODrive high-rate capture
**When to use:** Workflow B frequency sweep — capture `torque_setpoint` and `pos_estimate` at control-loop rate without Controllino/CAN.
**Pattern:**
```python
from odrive.utils import high_rate_capture_start, TimestampFmt

CAPTURE_PROPERTIES = [
    "axis0.controller.torque_setpoint",
    "axis0.pos_estimate",
]

def acquire_window(odrv, duration_s):
    capturer = high_rate_capture_start(odrv, CAPTURE_PROPERTIES)
    time.sleep(duration_s)
    data = capturer.trigger_and_download_sync(
        trigger_point=1.0,
        trigger_timeout=duration_s + 2.0,
        return_as=np.recarray,
        t_fmt=TimestampFmt.NANOSECONDS,
    )
    t_ns = data["timestamps"]
    mask = (t_ns >= -duration_s * 1e9) & (t_ns <= 0)
    return data["axis0.controller.torque_setpoint"][mask], data["axis0.pos_estimate"][mask]
```
**Gotchas:** Requires ODrive firmware 0.6.12+ and Python package `odrive>=0.6.11.post0`. Settle before starting capture. With 2 variables the buffer window is 1024 ms max. Only one `HighRateCapturer` per ODrive at a time.
**Last used:** 2026-05-29

## Robust cyclic CAN capture: store only fresh torque+position updates (legacy)
**When to use:** Legacy Controllino servo-identification firmware (removed). You receive cyclic ODrive CANSimple frames (e.g. `GET_TORQUES` + `GET_ENCODER_ESTIMATES`) but they are not back-to-back within a tiny window; you want stable sampling without resetting acquisition on timing gaps.
**Pattern:**
```cpp
// Keep "latest" values + timestamps updated as frames arrive, and only store a sample
// when BOTH signals have updated since the last stored sample.
static uint32_t lastStoredTorqueTs = 0;
static uint32_t lastStoredPosTs = 0;

void processCANMessages() {
    // ... parse frames and update:
    // latest_torque_setpoint, latest_pos_estimate, torque_timestamp_us, pos_timestamp_us

    const uint32_t tts = (uint32_t)torque_timestamp_us;
    const uint32_t pts = (uint32_t)pos_timestamp_us;

    if (tts == 0 || pts == 0) return;
    if (tts == lastStoredTorqueTs) return;
    if (pts == lastStoredPosTs) return;

    float *sample = &acq_buffer[acq_index * 4];
    sample[0] = latest_torque_setpoint;
    sample[1] = latest_pos_estimate;
    sample[2] = (float)tts;
    sample[3] = (float)pts;

    lastStoredTorqueTs = tts;
    lastStoredPosTs = pts;
    acq_index++;
}
```
**Gotchas:** Don’t “restart acquisition” when one message is missing—just wait for the missing frame. Also ensure CANSimple node-id decode uses a 6-bit mask (\(0x3F\)) so you don’t accept/reject the wrong node’s frames.
**Last used:** 2026-04-17

## Export multisine CSV with metadata header lines
**When to use:** You want the host/firmware to parse multisine files with enough metadata to infer sample rate and columns.
**Pattern:**
```python
def export_multisine_csv(path, time_vector, signal_values, metadata_lines):
    with open(path, "w") as f:
        for line in metadata_lines:
            f.write("# " + line + "\n")
        f.write("Time_s,Signal\n")
        for t, v in zip(time_vector, signal_values):
            f.write(f"{t:.10e},{v:.10e}\n")
```
**Gotchas:** Keep the column header stable (`Time_s,Signal`) if your parsers depend on exact casing/spelling; ensure values stay within the analog range expected by your firmware (e.g., `0..3.3V` for ADC voltage).
**Last used:** 2026-03-23

## Map Controllino GPIO labels to Arduino pins (MICRO / RP2 core)
**When to use:** You need to drive or read `GPIO0`/`GPIO1` on Controllino MICRO and must avoid confusion between terminal labels, RP2040 GPIO numbering, and Arduino pin indices.
**Pattern:**
```cpp
// Controllino MICRO: GPIO0 -> RP2040 GPIO0 -> Arduino D0
#define PWM_OUTPUT_PIN D0

void setup() {
    Serial.begin(115200);
    pinMode(PWM_OUTPUT_PIN, OUTPUT);
    Serial.print("Using Controllino GPIO0 on Arduino pin: ");
    Serial.println(PWM_OUTPUT_PIN);
}
```
**Gotchas:** Do not infer RP2040 GPIO from package pin numbers in the chip pinout figure; use Controllino board docs + `controllino_rp2` `pins_arduino.h` as the source of truth. `D0`/`D1` can have alternate serial/I2C functions, but remain valid GPIO/PWM pins when configured accordingly.
**Last used:** 2026-03-23

## RP2040 timer ISR updates PWM compare directly
**When to use:** You need the PWM command on Controllino MICRO (RP2040) to change on the same sample tick as the timer ISR, without loop-latency or skipped pending duty values.
**Pattern:**
```cpp
#include <hardware/pwm.h>

static uint pwm_output_slice_num = 0;
static uint pwm_output_channel = 0;

static inline void writePwmDutyRealtime(uint16_t duty) {
    pwm_set_chan_level(pwm_output_slice_num, pwm_output_channel, duty);
}

void setup() {
    pinMode(D0, OUTPUT);
    analogWriteFreq(PWM_FREQ_HZ);
    analogWriteRange(PWM_TOP);
    analogWrite(D0, (int)initial_duty);  // one-time setup only

    pwm_output_slice_num = pwm_gpio_to_slice_num(D0);
    pwm_output_channel = pwm_gpio_to_channel(D0);
}

static bool timerCallback(struct repeating_timer *t) {
    writePwmDutyRealtime(duty);
    return true;
}
```
**Gotchas:** Do not assume the low-level path is wrong just because the motor behavior looks wrong. First verify the RC output and inspect runtime PWM state. In this codebase, use `GET_STATUS` to check slice/channel, GPIO function, compare values, `TOP`, `CSR`, and write counters. If the mixed setup (`analogWriteFreq`/`analogWriteRange` + low-level ISR writes) is suspect, compare against the alternate runtime modes before concluding that `pwm_set_chan_level()` is at fault.
**Last used:** 2026-03-31

## Compare PWM runtime modes on Controllino MICRO
**When to use:** The PWM output does not match the expected RC-filter voltage and you need to isolate whether the issue is low-level compare writes, mixed Arduino/Pico PWM setup, or `analogWrite()` behavior inside the ISR.
**Pattern:**
```cpp
// 0 = Arduino setup + low-level ISR compare writes
// 1 = Fully low-level PWM setup + low-level ISR compare writes
// 2 = analogWrite() directly inside timerISR() (fallback experiment)
#define PWM_RUNTIME_MODE 1

void printStatus() {
    Serial.print("PWM Runtime Mode: ");
    Serial.println(pwmRuntimeModeName());
    Serial.print("PWM Slice: ");
    Serial.println((unsigned int)pwm_output_slice_num);
    Serial.print("PWM Channel: ");
    Serial.println((unsigned int)pwm_output_channel);
    Serial.print("PWM GPIO Function: ");
    Serial.println((unsigned int)pwm_debug_last_gpio_func);
}
```
**Gotchas:** Validate in two stages: first with only the Controllino + RC output, then with ODrive connected. Motor motion/noise alone is not enough to prove the PWM path is wrong. If you compare modes, keep the CSV, timer rate, RC filter, and ODrive setup unchanged between runs.
**Last used:** 2026-03-31

## Verify ODrive GPIO1 analog state around closed-loop transitions
**When to use:** The Controllino RC output looks correct, but Python-controlled runs still produce wrong torque behavior and you need to prove whether ODrive `GPIO1` stayed in `ANALOG_IN`.
**Pattern:**
```python
if odrive_ctrl.configure_gpio1_analog_torque_mapping(...):
    odrive_ctrl.print_gpio1_state("ODrive GPIO1 state after configuration")

odrive_ctrl.print_gpio1_state("ODrive GPIO1 state before closed-loop")
if odrive_ctrl.enter_closed_loop():
    odrive_ctrl.print_gpio1_state("ODrive GPIO1 state after closed-loop")

odrive_ctrl.exit_closed_loop()
odrive_ctrl.print_gpio1_state("ODrive GPIO1 state after cleanup")
```
**Gotchas:** Do not only watch `gpio1_analog_mapping.endpoint`; also inspect `gpio1_mode`, mapping min/max, controller mode, and input mode. On the normal path, avoid redundant `STOP_OUTPUT` commands after the firmware already emitted completion, or you make the ODrive/Controllino lifecycle harder to reason about. If manual ODrive GUI setup works while Python does not, treat that as strong evidence to compare ODrive run-state logs before touching the PWM firmware again.
**Last used:** 2026-03-31

## Biquad low-pass + notch filters (RBJ coefficients)
**When to use:** You need tunable 2nd-order low-pass and notch filters in discrete time (set cutoff/center frequency in Hz and quality Q), suitable for an 8 kHz control loop.
**Pattern:**
```cpp
// Configure from fs, fc (or f0) and Q; then run step() per sample.
biquad_config_lowpass_butterworth(lpf2, fs_hz, fc_hz);
biquad_config_notch(notch1, fs_hz, f0_hz, Q);
u = lpf2.step(u);
u = notch1.step(u);
```
**Gotchas:** Enforce `f < fs/2` and `Q > 0`, otherwise bypass the filter (identity). With high Q near Nyquist, coefficients can get sensitive; keep `f0` well below `fs/2` and validate stability on hardware.
**Last used:** 2026-03-26


