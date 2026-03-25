# Skills

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


