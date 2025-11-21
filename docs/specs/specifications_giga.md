# Project Specifications: Arduino Giga R1 WiFi Data Acquisition and Motor Control System

## Overview

This project integrates an Arduino Giga R1 WiFi and an ODrive S1 motor driver to create a synchronized data acquisition and motor control system. The system outputs analog control signals, acquires multiple analog input channels, and captures motor feedback data for analysis.

## System Architecture

### Hardware Components

- **Arduino Giga R1 WiFi**: Main controller for analog I/O operations with built-in DAC and ADC capabilities
- **ODrive S1 Motor Driver**: Provides motor control with high-rate feedback capture
- **Communication**: Serial interface between Arduino and PC, USB/CAN for ODrive

### Software Components

1. **Arduino firmware** (.ino): Handles real-time analog I/O operations
2. **ODrive configuration script** (.py): Configures ODrive S1 parameters and capture modes
3. **Main control application** (.py): Provides GUI for user interaction and data management

## Channel Naming Convention

To maintain consistency and clarity, this document uses a direct mapping between hardware pin names and logical channel names:

- **Hardware Pins**: Physical pin names on Arduino Giga R1 WiFi (A0, A1, A2, A3, A4, A5, DAC0, etc.)
- **Logical Channels**: Names used in data arrays, processing, and storage (A0, A1, A2, A3, A4, A5)

**Mapping:**
- Hardware pin A0 → Logical channel A0 (array index 0)
- Hardware pin A1 → Logical channel A1 (array index 1)
- Hardware pin A2 → Logical channel A2 (array index 2)
- Hardware pin A3 → Logical channel A3 (array index 3)
- Hardware pin A4 → Logical channel A4 (array index 4)
- Hardware pin A5 → Logical channel A5 (array index 5)

This direct mapping ensures that hardware pin names and logical channel names are identical, eliminating confusion and making the system more intuitive.

## Arduino Firmware Requirements

### Analog Output

- **Channel**: DAC0 (built-in DAC on Arduino Giga R1 WiFi)
- **Voltage Range**: 0 to 3.3V
- **Signal Source**: CSV file with voltage samples
- **Behavior**: Cyclic playback - restart from beginning when end of file is reached
- **Timing**: Sample rate specified in CSV file header
- **Implementation**: 
  - Uses **Arduino_AdvancedAnalog library** (`AdvancedDAC` class) for hardware-timed DMA-based output
  - Initialization: `dac.begin(AN_RESOLUTION_12, sample_rate, buffer_size, queue_size)`
  - Writing pattern: Use `dac.dequeue()` to get a `SampleBuffer`, fill it with values, then call `dac.write(buf)`
  - `SampleBuffer` API: `buf.size()`, `buf[i]` for indexed access, `buf.release()` after writing (handled by library)
  - For cyclic playback: Fill buffer with CSV voltage values, write to DAC, repeat
  - Reference: [Arduino Giga R1 WiFi Audio Tutorial](https://docs.arduino.cc/tutorials/giga-r1-wifi/giga-audio/) and [AdvancedAnalog API Documentation](https://github.com/arduino-libraries/Arduino_AdvancedAnalog/blob/main/docs/api.md)
  - The AdvancedAnalog library provides reliable high-speed waveform generation without Mbed OS crashes
  - DMA-based operation ensures minimal jitter and precise timing

### Analog Input Acquisition

- **Hardware Pins**: A0, A1, A2, A3, A4, A5 (six channels using built-in ADC on Arduino Giga R1 WiFi)
- **Logical Channel Names**: A0, A1, A2, A3, A4, A5 (used in data processing and storage)
- **Pin-to-Channel Mapping**: 
  - Hardware pin A0 → Logical channel A0 (array index 0)
  - Hardware pin A1 → Logical channel A1 (array index 1)
  - Hardware pin A2 → Logical channel A2 (array index 2)
  - Hardware pin A3 → Logical channel A3 (array index 3)
  - Hardware pin A4 → Logical channel A4 (array index 4)
  - Hardware pin A5 → Logical channel A5 (array index 5)
- **ADC Architecture**: 
  - Arduino Giga R1 WiFi has **3 independent ADCs** (ADC1, ADC2, ADC3), but we use only ADC1 and ADC2 for hardware compatibility
  - For synchronized timing of 6 channels, channels are grouped by ADC:
    - **A0, A1, A2 → ADC1** (one `AdvancedADC` instance with 3 pins)
    - **A3, A4, A5 → ADC2** (one `AdvancedADC` instance with 3 pins)
  - All channels in one `AdvancedADC` instance must belong to the same ADC hardware unit
  - Multi-channel data from each ADC is **interleaved** in the `SampleBuffer`:
    - ADC1 buffer: [A0, A1, A2, A0, A1, A2, ...] (3 channels interleaved)
    - ADC2 buffer: [A3, A4, A5, A3, A4, A5, ...] (3 channels interleaved)
- **Timing**: Hardware-timed sampling with accurate clock via DMA
- **Implementation**: 
  - Uses **Arduino_AdvancedAnalog library** (`AdvancedADC` class) for hardware-timed DMA-based sampling
  - **Two `AdvancedADC` instances** (one per ADC hardware unit, each with 3 channels):
    - `AdvancedADC adc1(A0, A1, A2)` - ADC1 with channels A0, A1, A2
    - `AdvancedADC adc2(A3, A4, A5)` - ADC2 with channels A3, A4, A5
  - Initialization: `adc.begin(AN_RESOLUTION_12, sample_rate, buffer_size, queue_size, start=false)` for each instance
  - Start sampling: `adc.start(sample_rate)` when `START_ACQUISITION` is called
  - Reading: `adc.read()` returns a `SampleBuffer` object (not a direct value)
  - `SampleBuffer` API: `buf.size()`, `buf.channels()`, `buf[i]` for indexed access, `buf.release()` after reading
  - Multi-channel data is interleaved in the buffer - must extract channel data correctly (3 channels per ADC)
  - Reference: [Arduino Giga R1 WiFi Audio Tutorial](https://docs.arduino.cc/tutorials/giga-r1-wifi/giga-audio/) and [AdvancedAnalog API Documentation](https://github.com/arduino-libraries/Arduino_AdvancedAnalog/blob/main/docs/api.md)
  - The AdvancedAnalog library provides reliable high-speed multi-channel sampling without Mbed OS crashes
  - DMA-based operation ensures minimal jitter and precise timing synchronization
- **Real-time Constraint**: No interruptions during acquisition period
- **Synchronization**: Output voltage and input acquisition synchronized via AdvancedAnalog's built-in timing

### CSV File Format

**Structure:**
- Header comment lines (starting with `#`) containing metadata:
  - Signal parameters (fmin, fmax, fs, df, etc.)
  - Sample rate information (e.g., `# fs: 5000.0 Hz`)
  - Signal properties (N, K, Crest Factor)
  - Column description: `# Columns: Time_s, Signal`
- CSV header row: `Time_s,Signal`
- Data rows: Comma-separated time (seconds) and signal value (voltage, 0-3.3V)

**Example format:**
```
# Multisine Signal Data
# fmin_desired: 5.000000 Hz
# fmax_desired: 500.000000 Hz
# fs: 5000.000000 Hz
# df: 1.000000 Hz
# N: 1000
# K: 496
# Crest Factor: 2.345678
# Columns: Time_s, Signal
Time_s,Signal
0.0000000000e+00,1.6500000000e+00
1.0000000000e-04,1.7000000000e+00
2.0000000000e-04,1.7500000000e+00
...
```

**Parsing Requirements:**
- Arduino firmware must skip header comment lines (lines starting with `#`)
- Extract sample period from metadata header (`# fs: X.XX Hz`) or calculate from time column differences
- Parse CSV header row to identify column structure
- Extract signal values from second column (Signal column)
- Validate voltage range: 0.0 to 3.3V
- Python controller must parse header comments to extract metadata
- Python controller must handle comma-separated data rows

### Timing and Control

- **Start Delay**: Configurable wait time before acquisition begins
- **Acquisition Duration**: Controlled by Python application
- **Data Storage**: Samples stored in RAM during acquisition
- **Data Transfer**: Send all acquired data via serial interface after acquisition completes
- **Output Control**: Voltage output stops when data transfer begins

### Serial Communication Protocol

**Communication Settings:**
- **Baud Rate**: 115200
- **Data Format**: Text-based commands and responses (newline-terminated)
- **Line Endings**: Commands and responses terminated with `\n` (newline character)

**Command Format:**
All commands are sent from Python application to Arduino as text strings terminated with newline (`\n`). Commands are case-sensitive.

**Commands (Python → Arduino):**

1. **START_OUTPUT**
   - Format: `START_OUTPUT\n`
   - Description: Begin cyclic voltage output playback from loaded CSV data
   - Prerequisites: CSV file must be loaded via UPLOAD_CSV
   - Response: `ACK: Output started\n` on success, or `ERROR: <message>\n` on failure

2. **STOP_OUTPUT**
   - Format: `STOP_OUTPUT\n`
   - Description: Halt voltage output (output remains at last value)
   - Response: `ACK: Output stopped\n`

3. **START_ACQUISITION**
   - Format: `START_ACQUISITION,<duration>,<start_delay>\n`
   - Parameters:
     - `<duration>`: Acquisition duration in seconds (float, e.g., `1.5`)
     - `<start_delay>`: Delay before starting acquisition in seconds (float, e.g., `0.5`)
   - Description: Start synchronized data acquisition. If output is not active, it will be started automatically.
   - Behavior: Blocks until acquisition completes (Arduino waits in loop)
   - Response: `ACK: Acquisition started\n` when acquisition begins, then `ACK: Acquisition complete\n` when finished
   - Error: `ERROR: Invalid acquisition duration\n` if duration <= 0

4. **STOP_ACQUISITION**
   - Format: `STOP_ACQUISITION\n`
   - Description: Stop data acquisition immediately (if supported by firmware)
   - Response: `ACK: Acquisition stopped\n` (implementation dependent)

5. **UPLOAD_CSV**
   - Format: `UPLOAD_CSV,<num_lines>\n`
   - Parameters:
     - `<num_lines>`: Number of data lines to follow (integer, excludes header comments and CSV header row)
   - Description: Upload CSV voltage waveform data to Arduino
   - Protocol Flow:
     1. Python sends: `UPLOAD_CSV,<num_lines>\n`
     2. Arduino responds: `READY\n` (after clearing serial buffer)
     3. Python sends CSV data lines (one per line, newline-terminated)
     4. Arduino responds: `ACK: CSV loaded\n` on success, or `NACK: <error_message>\n` on failure
   - CSV Format: See "CSV File Format" section above
   - Notes: Arduino clears serial buffer before sending READY. Python should wait for READY before sending data.

6. **GET_STATUS**
   - Format: `GET_STATUS\n`
   - Description: Request current system status
   - Response: `STATUS:<state>,<output_active>,<acquisition_active>,<csv_sample_count>,<csv_sample_period>\n`
     - `<state>`: Integer state code (0=IDLE, 1=OUTPUTTING, 2=ACQUIRING, 3=TRANSFERRING)
     - `<output_active>`: Boolean (0 or 1)
     - `<acquisition_active>`: Boolean (0 or 1)
     - `<csv_sample_count>`: Integer number of loaded CSV samples
     - `<csv_sample_period>`: Float sample period in seconds (6 decimal places)

7. **GET_DATA**
   - Format: `GET_DATA\n`
   - Description: Request transfer of acquired data
   - Prerequisites: Acquisition must be complete (acq_sample_count > 0)
   - Response Format:
     - Header: `DATA:<sample_count>,<sample_period>,<num_channels>\n`
       - `<sample_count>`: Integer number of samples
       - `<sample_period>`: Float sample period in seconds (6 decimal places)
       - `<num_channels>`: Integer number of channels (always 6)
     - Data Lines: One line per sample, comma-separated values
       - Format: `<ch0>,<ch1>,<ch2>,<ch3>,<ch4>,<ch5>\n`
       - Values are floats with 4 decimal places
       - Channels correspond to logical channels A0-A5 (mapped directly from hardware pins A0-A5)
     - Terminator: `DATA_END\n`
   - Error: `ERROR: No acquisition data available\n` if no data

8. **RESET** (Optional/Debug)
   - Format: `RESET\n`
   - Description: Reset parsing state and clear serial buffer
   - Response: `ACK: Reset complete\n`

9. **DEBUG** (Optional/Debug)
   - Format: `DEBUG\n`
   - Description: Dump current system state for debugging
   - Response: Multiple `DEBUG: <key> = <value>\n` lines

**Response Messages:**

- **ACK Messages**: `ACK: <message>\n` - Command executed successfully
- **NACK Messages**: `NACK: <error_message>\n` - Command failed with error
- **ERROR Messages**: `ERROR: <error_message>\n` - Error occurred
- **INFO Messages**: `INFO: <message>\n` - Informational message
- **DEBUG Messages**: `DEBUG: <message>\n` - Debug information (can be filtered by Python)

**State Codes:**
- `0` = STATE_IDLE: System idle, ready for commands
- `1` = STATE_OUTPUTTING: Outputting voltage waveform
- `2` = STATE_ACQUIRING: Acquiring data (output may also be active)
- `3` = STATE_TRANSFERRING: Transferring data to Python (output stopped)

**Protocol Notes:**
- All commands and responses are text-based (not binary)
- Commands are matched using `startsWith()` - partial matches are acceptable
- Python should filter DEBUG/INFO messages during normal operation
- Serial buffer should be cleared before sending UPLOAD_CSV to avoid race conditions
- Arduino may send DEBUG messages during CSV upload - Python should ignore these until READY is received

## ODrive Configuration Script Requirements

### Control Mode Selection

The ODrive S1 shall support three control modes (user selectable):
- Torque control mode
- Velocity control mode
- Position control mode

### Analog Input Mapping

The analog input from Arduino DAC0 shall be mappable to:
- Position setpoint (command)
- Velocity feedforward
- Torque feedforward

User selects the mapping based on desired control strategy.

### High-Rate Capture Configuration

- **Sampling Rate**: Match the Python acquisition rate
- **Captured Variables**:
  - Velocity command
  - Torque command
  - Position feedback
  - Velocity feedback
  - Torque feedback
  - Control input (one of):
    - Position command
    - Velocity feedforward
    - Torque feedforward

The specific control input captured depends on analog input mapping selection.

## Main Control Application Requirements

### User Interface - Input Configuration

- File selection dialog to load voltage output CSV file
- Display loaded file information (sample rate, duration, number of samples)
- Validation of CSV file format and voltage range

### User Interface - Control Panel

**Output Control:**
- Start button: Begin voltage output playback
- Stop button: Halt voltage output

**Acquisition Control:**
- Start button: Begin data acquisition
- Stop button: End data acquisition
- Time range input: Set acquisition duration in seconds
- Status indicators: Show current state (idle, outputting, acquiring, transferring)

**ODrive Configuration:**
- Control mode selector (Torque/Velocity/Position)
- Analog input mapping selector (Position/Velocity FF/Torque FF)
- Connection status indicator

### Data Processing

**Geometric and Calibration Parameters:**
```
L1 = 0.01 m      # Length parameter 1
L2 = 0.05 m      # Length parameter 2
L3 = 0.2 m       # Length parameter 3
alpha = 20°      # Angle parameter (converted to radians)
r_a = 5 * 9.81 / 10  # Accelerometer sensitivity (m/s²/V)
```

**Calculated Signals:**

Angular displacements:
```
theta_x = -(A0 + A1 - A2 - A3) * sin(alpha) / (2 * L3)
theta_y = -(A0 - A1 - A2 + A3) * cos(alpha) / (2 * L3)
```

Linear accelerations (voltage to m/s²):
```
x = (-(A0 - A1 + A2 - A3) * cos(alpha) / 4 - theta_y * (L1 + L2 + L3 / 2) - A5) * r_a
y = ((A0 + A1 + A2 + A3) * sin(alpha) / 4 + theta_x * (L1 + L2 + L3 / 2) - A4) * r_a
```

**Note:** The formulas above use logical channel names A0-A5. If the Python implementation uses different variable names (e.g., A1-A6), those should be mapped as: A0→A1, A1→A2, A2→A3, A3→A4, A4→A5, A5→A6 in the code.

### Data Storage

**File Location:** `data/` folder in project directory

**CSV File Contents:**
- Output voltage signal (synchronized with inputs)
- Acquired analog inputs: A0, A1, A2, A3, A4, A5 (logical channel names, mapped directly from hardware pins A0-A5)
- Calculated signals: x, y, theta_x, theta_y
- ODrive feedback variables:
  - Velocity command
  - Torque command
  - Position feedback
  - Velocity feedback
  - Torque feedback
  - Active control input (position command OR velocity feedforward OR torque feedforward)

**File Naming:** Include timestamp and experiment identifier

### Visualization - Time Domain Plots

**Features:**
- Display all signals after acquisition completes
- Multi-signal selection: Checkboxes or dropdown for signal selection
- Synchronized x-axes: Zoom and pan operations sync across selected plots
- Time axis: Display in seconds
- Y-axis labels: Include units for each signal type
- Legend: Clear identification of each plotted signal

### Visualization - Frequency Domain (Bode Plot)

**Activation:**
- Button labeled "Bode Plot" switches visualization mode

**Input/Output Selection:**
- Dropdown menu for input signal selection
- Dropdown menu for output signal selection
- Calculate transfer function: Output/Input in frequency domain

**Plot Specifications:**
- Two subplots: Magnitude and Phase
- Log-log scale for magnitude plot
- X-axis: Frequency in Hz (logarithmic)
- Y-axis (Magnitude): Units depend on selected input and output signals
  - Example: If output is position (m) and input is torque (Nm), units are m/Nm
  - Example: If output is velocity (m/s) and input is voltage (V), units are (m/s)/V
  - Display appropriate unit ratio based on signal selection (NOT dB, linear magnitude ratio)
- Y-axis (Phase): Degrees (unwrapped phase)
- Grid: Display on both plots

**Export Options:**
- Save plot as PNG image file
- Export Bode data to CSV file (frequency, magnitude, phase columns)

## Reference Documentation URLs

### Arduino Giga R1 WiFi

- Official documentation: `https://docs.arduino.cc/hardware/giga-r1-wifi/`
- Arduino Giga tutorials: `https://docs.arduino.cc/tutorials/giga-r1-wifi/`
- **Advanced ADC and DAC (Audio Tutorial)**: `https://docs.arduino.cc/tutorials/giga-r1-wifi/giga-audio/` - Demonstrates advanced ADC and DAC capabilities for high-speed waveform generation and sampling, suitable for CSV file waveform output and synchronized multi-channel acquisition
- STM32H7 reference: `https://www.st.com/en/microcontrollers-microprocessors/stm32h7-series.html`
- DAC functionality: `https://docs.arduino.cc/learn/microcontrollers/analog-to-digital-converter/`
- Timer interrupts: `https://docs.arduino.cc/learn/microcontrollers/processor-interrupts/`

### ODrive S1

- ODrive documentation: `https://docs.odriverobotics.com/v/latest/`
- Python API: `https://docs.odriverobotics.com/v/latest/api/odrive.html`
- Analog input configuration: `https://docs.odriverobotics.com/v/latest/guides/analog-input.html`
- High-rate data capture: `https://docs.odriverobotics.com/v/latest/guides/data-logging.html`

### Python Libraries

- PySerial for Arduino communication: `https://pyserial.readthedocs.io/`
- ODrive Python package: `https://pypi.org/project/odrive/`
- Matplotlib for plotting: `https://matplotlib.org/stable/gallery/index.html`
- NumPy for signal processing: `https://numpy.org/doc/stable/reference/routines.fft.html`
- SciPy for frequency analysis: `https://docs.scipy.org/doc/scipy/reference/signal.html`

### Arduino_AdvancedAnalog Library

- **API Documentation**: `https://github.com/arduino-libraries/Arduino_AdvancedAnalog/blob/main/docs/api.md` - Complete API reference for AdvancedADC, AdvancedDAC, and SampleBuffer classes
- **Multi-Channel ADC Documentation**: `https://github.com/arduino-libraries/Arduino_AdvancedAnalog/tree/main/docs#adc-multichannel-giga-r1-wifi` - Specific documentation for multi-channel ADC configuration on Arduino Giga R1 WiFi
- **GitHub Repository**: `https://github.com/arduino-libraries/Arduino_AdvancedAnalog` - Source code and examples

## Technical Constraints

### Timing Accuracy

- Arduino sampling must maintain consistent timing throughout acquisition
- Use hardware timer peripherals (STM32H7 timers) for clock generation
- Minimize jitter and timing variations
- Leverage STM32H7's dual-core architecture for real-time operations if needed

### Memory Management

- Calculate maximum acquisition time based on available RAM on both Arduino Giga R1 WiFi and ODrive S1
- Arduino Giga R1 WiFi: 1 MB RAM available for six input channels plus output voltage and metadata storage
- ODrive S1: High-rate capture buffer limitations for motor feedback variables
- Maximum acquisition duration is the minimum of:
  - Arduino RAM capacity divided by (6 input channels × bytes per sample × sample rate)
  - ODrive capture buffer capacity divided by (number of captured variables × bytes per sample × sample rate)
- Implement bounds checking to prevent buffer overflow on both devices
- Display calculated maximum acquisition time in GUI based on selected sample rate
- Warn user if requested acquisition duration exceeds available memory

**Example Memory Calculation for Arduino Giga R1 WiFi:**
- Available RAM: ~1 MB (accounting for system overhead)
- 6 channels × 4 bytes/float = 24 bytes per sample
- At 1 kHz: 24 KB/s
- Maximum duration: ~40 seconds (conservative estimate)
- At 10 kHz: 240 KB/s
- Maximum duration: ~4 seconds

### Data Synchronization

- Arduino output and input operations must be temporally aligned
- ODrive capture rate must match Arduino acquisition rate
- Timestamp all data sources for post-processing alignment verification

### Communication Reliability

- Implement error checking for serial data transfer
- Verify data integrity after transfer
- Handle timeout conditions and communication failures

## File Organization

```
project_root/
├── src/
│   ├── arduino/
│   │   ├── giga-acquisition.ino
│   │   └── example_output.csv
│   └── python/
│       ├── odrive_config.py
│       ├── main_controller.py
│       ├── main_controller_opta.py  (legacy Opta version)
│       └── requirements.txt
├── data/
│   └── (acquired data CSV files)
├── plots/
│   └── (exported PNG files)
└── docs/
    └── specs/
        ├── specifications.md  (legacy Opta version)
        └── specifications_giga.md
```

## Data Flow

1. User loads voltage output CSV file in Python GUI
2. Python application sends configuration to Arduino via serial
3. Python configures ODrive S1 (mode, mapping, capture rate)
4. User initiates output from GUI
5. Arduino begins cyclic voltage output on DAC0
6. ODrive receives analog input and operates motor
7. User initiates acquisition from GUI
8. Arduino acquires data from hardware pins A0-A5 (logical channels A0-A5) synchronously with output
9. ODrive captures motor feedback at matching rate
10. After specified duration, Arduino stops and transfers data via serial
11. Python retrieves ODrive capture buffer
12. Python calculates derived signals (theta_x, theta_y, x, y)
13. All data saved to timestamped CSV file
14. GUI displays time-domain plots with user selection
15. User can switch to Bode plot view for frequency analysis
16. User can export visualizations and data

## Success Criteria

- Voltage output accurately reproduces CSV file waveform cyclically
- All six analog input channels (hardware pins A0-A5, logical channels A0-A5) sampled synchronously with accurate timing
- ODrive captures motor data at matching sample rate
- Data transfer completes without corruption or loss
- Calculated signals correctly derived from raw inputs
- GUI provides intuitive control and real-time status feedback
- Time-domain plots display selected signals with synchronized axes
- Bode plots correctly show magnitude (m/Nm) and unwrapped phase
- All data successfully exported in documented CSV format
- System operates reliably for repeated acquisition cycles

## Notes

- Sample rates must be consistent across Arduino acquisition and ODrive capture
- RAM limitations may constrain maximum acquisition duration (Giga R1 WiFi has 1 MB RAM, significantly more than Opta Lite)
- Serial communication baud rate may limit data transfer speed
- All voltage values constrained to 0-3.3V range for hardware compatibility
- Arduino Giga R1 WiFi uses STM32H7 architecture, which provides better performance and more memory than Opta Lite
- Built-in DAC eliminates need for expansion board (A0602 not required)
- Hardware timer capabilities of STM32H7 enable precise timing control

## Key Differences from Opta Lite + A0602 System

1. **No Expansion Board Required**: Giga R1 WiFi has built-in DAC (DAC0, DAC1) and ADC (12 channels)
2. **More Memory**: 1 MB RAM vs. limited RAM on Opta Lite allows for longer acquisitions
3. **Different Architecture**: STM32H7 dual-core vs. mbed-based Opta system
4. **Different Pin Mapping**: Direct pin access vs. expansion board abstraction
5. **Different Libraries**: Standard Arduino libraries vs. OptaBlue/mbed libraries
6. **Better Performance**: Higher clock speed and dual-core architecture for improved real-time performance

