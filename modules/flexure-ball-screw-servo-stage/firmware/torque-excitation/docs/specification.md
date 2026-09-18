# Project Specifications: Controllino Micro Data Acquisition and Motor Control System

## Overview

This project integrates a Controllino Micro development board and an ODrive S1 motor driver to create a synchronized data acquisition and motor control system. The system acquires multiple analog input channels, sends torque commands to the ODrive S1 via CAN V2.0, and processes acquired data for analysis.

## Development Phases

The development of the main control application is split into two phases:

### Phase 1: Sequential Flow (Current)

**Objective**: Create a simple, sequential workflow without a full GUI to establish a working version that performs all necessary steps.

**Implementation**: `main_sequential.py`

**Workflow**:
1. **Connect to Controllino**: Automatically connects to hard-coded port COM10
2. **ODrive Connection Prompt**: User is prompted via command line to connect to ODrive (uses USB via `odrive.find_any()`)
3. **CSV File Selection**: File dialog opens to select the multisine CSV file
4. **Acquisition Parameters**: Command-line prompts ask user for:
   - Acquisition duration in seconds
   - Acquisition start delay in seconds (delay after torque output starts)
5. **Optional Test Output**: User can optionally test torque output only (without acquisition)
6. **ODrive Configuration**: ODrive enters closed-loop control state via USB
7. **Start Identification**: Dialog window with "Start Output" button appears
   - Starts torque output immediately
   - Acquisition starts automatically after specified delay
   - Both stop automatically after acquisition duration
   - Serial communication is blocked during operation
8. **Acquisition Completion**: Acquisition stops automatically after duration
9. **ODrive Cleanup**: ODrive exits closed-loop control state via USB
10. **Time Series Visualization**: A graph window opens displaying all selected variables vs. time:
    - All plots in one window with synchronized x-axes
    - Variables displayed: Torque command, A0-A5, acc0-acc5, x, y, theta_x, theta_y
    - Variable selection is hard-coded in the program
11. **Bode Plot Visualization**: Six Bode plots open in a 2 rows × 3 columns grid:
    - Input/output pairs are hard-coded in the program
    - Each plot shows magnitude (log-log) and phase (log-linear) subplots

**Features**:
- Minimal GUI: Only simple dialog windows with buttons, no full GUI application
- Hard-coded configuration: Controllino port (COM10), variable lists, and Bode plot configurations
- Sequential execution: Step-by-step flow with user interaction at each stage
- Full functionality: All core features (connection, CSV upload, torque commands, acquisition, visualization)
- Serial blocking: Serial communication is blocked during torque output for maximum performance

### Phase 2: Full GUI (Future)

**Objective**: Create a comprehensive GUI application for ease of use.

**Implementation**: `main_controller.py` (existing, to be enhanced)

**Planned Features**:
- Full graphical user interface with all controls visible
- Real-time status updates and data visualization
- Interactive plot controls (zoom, pan, signal selection)
- Configuration management and presets
- Data export and import capabilities
- Advanced visualization options

**Status**: Phase 2 will be implemented after Phase 1 is fully tested and validated.

## System Architecture

### Hardware Components

- **Controllino Micro**: Main controller for analog input acquisition and CAN communication (RP2040 MCU)
- **ODrive S1 Motor Driver**: Provides motor control via CAN torque commands
- **Communication**: 
  - Serial interface (USB) between Controllino and PC for commands and data
  - CAN V2.0 for ODrive torque commands (Controllino → ODrive)
  - USB Serial for ODrive state control and configuration (Python → ODrive)

### Software Components

1. **Controllino firmware** (Arduino IDE project): Handles real-time analog input acquisition and CAN communication
2. **ODrive configuration script** (`.py`): Configures ODrive S1 parameters via USB
3. **Main control application** (`.py`): Provides sequential workflow for user interaction and data management

## Channel Naming Convention

To maintain consistency and clarity, this document uses a direct mapping between hardware pin names and logical channel names:

- **Hardware Pins**: Physical pin names on Controllino Micro (A0, A1, A2, A3, A4, A5)
- **Logical Channels**: Names used in data arrays, processing, and storage (A0, A1, A2, A3, A4, A5)

**Mapping:**
- Hardware pin A0 → Logical channel A0 (array index 0)
- Hardware pin A1 → Logical channel A1 (array index 1)
- Hardware pin A2 → Logical channel A2 (array index 2)
- Hardware pin A3 → Logical channel A3 (array index 3)
- Hardware pin A4 → Logical channel A4 (array index 4)
- Hardware pin A5 → Logical channel A5 (array index 5)

This direct mapping ensures that hardware pin names and logical channel names are identical, eliminating confusion and making the system more intuitive.

## Controllino Firmware Requirements

### Analog Input Acquisition

- **Hardware Pins**: A0, A1, A2, A3, A4, A5 (six channels using built-in ADC on Controllino Micro RP2040)
- **Logical Channel Names**: A0, A1, A2, A3, A4, A5 (used in data processing and storage)
- **Pin-to-Channel Mapping**: 
  - Hardware pin A0 → Logical channel A0 (array index 0)
  - Hardware pin A1 → Logical channel A1 (array index 1)
  - Hardware pin A2 → Logical channel A2 (array index 2)
  - Hardware pin A3 → Logical channel A3 (array index 3)
  - Hardware pin A4 → Logical channel A4 (array index 4)
  - Hardware pin A5 → Logical channel A5 (array index 5)
- **ADC Architecture**: 
  - Controllino Micro uses RP2040 MCU with built-in ADC peripherals
  - RP2040 has 4 hardware ADC inputs (GPIO26-29), additional channels may use software-timed reads
  - Hardware-timed sampling via RP2040 hardware timer ISR
  - Default sample rate: 8kHz (configurable via CSV metadata)
- **Timing**: Hardware-timed sampling with accurate clock via RP2040 timer peripherals
- **Implementation**: 
  - Uses **RP2040 hardware timer** (`add_repeating_timer_us`) for precise timing
  - ADC reads triggered from timer ISR for hardware-timed acquisition
  - Synchronized with torque command transmission (same timer interrupt)
  - Default sample rate: 8kHz (configurable)
- **Real-time Constraint**: No interruptions during acquisition period
- **Synchronization**: Torque commands and input acquisition synchronized via hardware timer interrupt

### CAN V2.0 Communication for ODrive Control

- **Protocol**: CAN V2.0 (ISO 11898)
- **Baud Rate**: 1 Mbps (1,000,000 bps)
- **Hardware**: CAN peripheral on Controllino Micro (via CAN transceiver)
- **Pins**: Standard CAN pins (configured via Controllino board support)
- **Message Format**: 
  - CAN ID: ODrive node ID (typically 0x00 for axis 0)
  - Data: Torque command values (Nm) encoded in CAN message payload
  - Message structure follows ODrive CAN protocol specification
- **Implementation**:
  - Uses Controllino CAN library for message transmission
  - Hardware-timed transmission synchronized with acquisition sample rate
  - Cyclic transmission of torque commands from loaded CSV data
- **Behavior**: Cyclic playback - restart from beginning when end of CSV file is reached
- **Timing**: Sample rate specified in CSV file header (default 8kHz)

### CSV File Format

**Structure:**
- Header comment lines (starting with `#`) containing metadata:
  - Signal parameters (fmin, fmax, fs, df, etc.)
  - Sample rate information (e.g., `# fs: 8000.0 Hz`)
  - Signal properties (N, K, Crest Factor)
  - Column description: `# Columns: Time_s, Torque`
- CSV header row: `Time_s,Torque` or `Time_s,Signal`
- Data rows: Comma-separated time (seconds) and torque value (Nm)

**Example format:**
```
# Multisine Signal Data
# fmin_desired: 5.000000 Hz
# fmax_desired: 500.000000 Hz
# fs: 8000.000000 Hz
# df: 1.000000 Hz
# N: 1000
# K: 496
# Crest Factor: 2.345678
# Columns: Time_s, Torque
Time_s,Torque
0.0000000000e+00,0.0000000000e+00
1.2500000000e-04,0.1000000000e+00
2.5000000000e-04,0.2000000000e+00
...
```

**Parsing Requirements:**
- Controllino firmware must skip header comment lines (lines starting with `#`)
- Extract sample period from metadata header (`# fs: X.XX Hz`) or calculate from time column differences
- Parse CSV header row to identify column structure
- Extract torque values from second column (Torque column)
- Validate torque range as appropriate for the motor
- Python controller must parse header comments to extract metadata
- Python controller must handle comma-separated data rows

### Timing and Control

- **Acquisition Start Delay**: Configurable wait time before acquisition begins (after torque output starts)
- **Acquisition Duration**: Controlled by Python application
- **Data Storage**: Samples stored in RAM during acquisition
- **Data Transfer**: Send all acquired data via serial interface after acquisition completes
- **Torque Command Control**: Torque commands continue during data transfer (after acquisition completes)
- **Automatic Stop**: Acquisition and torque output stop automatically after duration (no STOP commands needed)

### Serial Communication Protocol

**Communication Settings:**
- **Baud Rate**: 115200
- **Data Format**: Text-based commands and responses (newline-terminated)
- **Line Endings**: Commands and responses terminated with `\n` (newline character)

**Command Format:**
All commands are sent from Python application to Controllino as text strings terminated with newline (`\n`). Commands are case-sensitive.

**Commands (Python → Controllino):**

1. **UPLOAD_CSV**
   - Format: `UPLOAD_CSV,<num_lines>\n`
   - Parameters:
     - `<num_lines>`: Number of data lines to follow (integer, excludes header comments and CSV header row)
   - Description: Upload CSV torque waveform data to Controllino
   - Protocol Flow:
     1. Python sends: `UPLOAD_CSV,<num_lines>\n`
     2. Controllino responds: `READY\n` (after clearing serial buffer)
     3. Python sends CSV data lines (one per line, newline-terminated)
     4. Controllino responds: `ACK: CSV loaded\n` on success, or `NACK: CSV load failed\n` on failure
   - CSV Format: See "CSV File Format" section above
   - Notes: Controllino clears serial buffer before sending READY. Python should wait for READY before sending data.

2. **START_OUTPUT** (Testing)
   - Format: `START_OUTPUT,<duration>\n`
   - Parameters:
     - `<duration>`: Output duration in seconds (float, e.g., `5.0`)
   - Description: Start torque command transmission for testing (output only, no acquisition)
   - Response: `ACK: Output started\n` on success, or `ERROR: <message>\n` on failure
   - Behavior: Output stops automatically after duration. Serial communication is blocked during output.

3. **START_IDENTIFICATION** (Main Command)
   - Format: `START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>\n`
   - Parameters:
     - `<acquisition_duration>`: Acquisition duration in seconds (float, e.g., `10.0`)
     - `<acquisition_start_delay>`: Delay before starting acquisition in seconds (float, e.g., `0.5`)
   - Description: Start synchronized torque output and data acquisition
   - Behavior: 
     - Starts torque output immediately
     - Begins acquisition automatically after delay seconds
     - Both stop automatically after acquisition duration
     - Serial communication is blocked during operation
   - Response: `ACK: Identification started\n` when operation begins
   - Error: `ERROR: Invalid parameters\n` if duration <= 0 or delay < 0

4. **GET_STATUS**
   - Format: `GET_STATUS\n`
   - Description: Request current system status
   - Response: `STATUS:<state>,<torque_active>,<acquisition_active>,<csv_sample_count>,<csv_sample_period>\n`
     - `<state>`: Integer state code (0=IDLE, 1=OUTPUTTING, 2=ACQUIRING, 3=TRANSFERRING)
     - `<torque_active>`: Boolean (0 or 1)
     - `<acquisition_active>`: Boolean (0 or 1)
     - `<csv_sample_count>`: Integer number of loaded CSV samples
     - `<csv_sample_period>`: Float sample period in seconds (6 decimal places)

5. **GET_DATA**
   - Format: `GET_DATA\n`
   - Description: Request transfer of acquired data
   - Prerequisites: Acquisition must be complete (acq_sample_count > 0)
   - Response Format:
     - Header: `DATA:<sample_count>,<sample_period>,<num_channels>\n`
       - `<sample_count>`: Integer number of samples
       - `<sample_period>`: Float sample period in seconds (6 decimal places)
       - `<num_channels>`: Integer number of channels (always 8)
     - Data Lines: One line per sample, comma-separated values
       - Format: `<A0>,<A1>,<A2>,<A3>,<A4>,<A5>,<torque_command>,<position_feedback>\n`
       - Values are floats with 4 decimal places
       - Channels correspond to logical channels A0-A5, torque command, and position feedback (always 0)
     - Terminator: `DATA_END\n`
   - Error: `ERROR: No acquisition data available\n` if no data

**Response Messages:**

- **ACK Messages**: `ACK: <message>\n` - Command executed successfully
- **NACK Messages**: `NACK: <error_message>\n` - Command failed with error
- **ERROR Messages**: `ERROR: <error_message>\n` - Error occurred
- **INFO Messages**: `INFO: <message>\n` - Informational message

**State Codes:**
- `0` = STATE_IDLE: System idle, ready for commands
- `1` = STATE_OUTPUTTING: Transmitting torque commands via CAN
- `2` = STATE_ACQUIRING: Acquiring data (torque commands may also be active)
- `3` = STATE_TRANSFERRING: Transferring data to Python (torque commands continue)

**Protocol Notes:**
- All commands and responses are text-based (not binary)
- Commands are matched using `startsWith()` - partial matches are acceptable
- Python should filter INFO/ERROR messages during normal operation
- Serial buffer should be cleared before sending UPLOAD_CSV to avoid race conditions
- **Serial communication is BLOCKED during torque output** - no commands can be received
- Acquisition starts/stops automatically - no STOP commands needed

## ODrive Configuration Script Requirements

### Control Mode Selection

The ODrive S1 shall support torque control mode (primary mode for this system):
- Torque control mode (via CAN commands from Controllino)

### CAN Communication

The torque commands from Controllino shall be transmitted via CAN V2.0:
- CAN baud rate: 1 Mbps
- CAN ID: ODrive node ID (typically 0x00 for axis 0)
- Message format: Follows ODrive CAN protocol specification for torque commands

### USB Serial Control

ODrive state control and configuration shall be performed via USB Serial from Python:
- Enter closed-loop control state before starting torque commands
- Configure control mode (torque control)
- Exit closed-loop control after acquisition completes
- **No position feedback retrieval** during operation (to avoid interrupting torque signals)

## Main Control Application Requirements

### User Interface - Input Configuration

- File selection dialog to load torque command CSV file
- Display loaded file information (sample rate, duration, number of samples)
- Validation of CSV file format and torque range

### User Interface - Control Panel

**Torque Command Control:**
- Optional test output: `START_OUTPUT,<duration>` for testing torque output only
- Main command: `START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>` for full operation
- Automatic stop: No STOP commands needed

**Acquisition Control:**
- Automatic start: Acquisition starts after specified delay
- Automatic stop: Acquisition stops after specified duration
- Status indicators: Show current state (idle, outputting, acquiring, transferring)

**ODrive Configuration:**
- USB connection status indicator
- ODrive node ID configuration
- Closed-loop control state management via USB

### Data Processing

**Geometric and Calibration Parameters:**
```
L1 = 0.02 m      # Length parameter 1
L2 = 0.078 m     # Length parameter 2
L3 = 0.160 m     # Length parameter 3
alpha = 20.123°  # Angle parameter (converted to radians)
r_a = 5 * 9.81 / 10  # Accelerometer sensitivity (m/s²/V)
```

**Calculated Signals:**

Angular displacements:
```
theta_x = -(A0 + A1 - A2 - A3) / sin(alpha) / (2 * L3)
theta_y = -(A0 - A1 - A2 + A3) / cos(alpha) / (2 * L3)
```

Linear accelerations (voltage to m/s²):
```
x = (-(A0 - A1 + A2 - A3) / cos(alpha) / 4 - theta_y * (L1 + L2 + L3 / 2) - A4) * r_a
y = ((A0 + A1 + A2 + A3) / sin(alpha) / 4 + theta_x * (L1 + L2 + L3 / 2) - A5) * r_a
```

**Note:** The formulas above use logical channel names A0-A5. The Python implementation uses these directly.

### Data Storage

**File Location:** `data/` folder in project directory

**CSV File Contents:**
- Torque command signal (synchronized with inputs, transmitted via CAN)
- Acquired analog inputs: A0, A1, A2, A3, A4, A5 (logical channel names, mapped directly from hardware pins A0-A5)
- Calculated signals: x, y, theta_x, theta_y
- Position feedback: Always zeros (not retrieved from ODrive to avoid interrupting torque signals)

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
  - Example: If output is velocity (m/s) and input is torque (Nm), units are (m/s)/(Nm)
  - Display appropriate unit ratio based on signal selection (NOT dB, linear magnitude ratio)
- Y-axis (Phase): Degrees (unwrapped phase)
- Grid: Display on both plots

**Export Options:**
- Save plot as PNG image file
- Export Bode data to CSV file (frequency, magnitude, phase columns)

## Reference Documentation URLs

### Controllino Micro

- Official documentation: `https://controllino.com/controllino-micro/`
- RP2040 datasheet: `https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf`
- Arduino RP2040 core: `https://github.com/arduino/ArduinoCore-mbed`
- CAN library: Included with Controllino board support

### ODrive S1

- ODrive documentation: `https://docs.odriverobotics.com/v/latest/`
- Python API: `https://docs.odriverobotics.com/v/latest/api/odrive.html`
- CAN protocol: `https://docs.odriverobotics.com/v/latest/guides/can-protocol.html`

### Python Libraries

- PySerial for Controllino communication: `https://pyserial.readthedocs.io/`
- ODrive Python package: `https://pypi.org/project/odrive/`
- Matplotlib for plotting: `https://matplotlib.org/stable/gallery/index.html`
- NumPy for signal processing: `https://numpy.org/doc/stable/reference/routines.fft.html`
- SciPy for frequency analysis: `https://docs.scipy.org/doc/scipy/reference/signal.html`

## Technical Constraints

### Timing Accuracy

- Controllino sampling must maintain consistent timing throughout acquisition
- Use RP2040 hardware timer peripherals for clock generation
- Minimize jitter and timing variations
- Leverage RP2040's hardware timer capabilities for precise timing control

### Memory Management

- Calculate maximum acquisition time based on available RAM on Controllino Micro
- Controllino Micro (RP2040): 264 KB RAM available for eight-channel data storage
- Maximum acquisition duration is:
  - Controllino RAM capacity divided by (8 channels × bytes per sample × sample rate)
- Implement bounds checking to prevent buffer overflow
- Display calculated maximum acquisition time in GUI based on selected sample rate
- Warn user if requested acquisition duration exceeds available memory

**Example Memory Calculation for Controllino Micro:**
- Available RAM: ~264 KB (accounting for system overhead)
- CSV buffer: 5000 samples × 4 bytes = 20 KB
- Acquisition buffer: 2000 samples × 8 channels × 4 bytes = 64 KB
- Total buffers: ~84 KB
- 8 channels × 4 bytes/float = 32 bytes per sample
- Maximum acquisition samples: 2000
- At 8 kHz: Maximum duration = 2000 / 8000 = 0.25 seconds
- At 1 kHz: Maximum duration = 2000 / 1000 = 2 seconds

### Data Synchronization

- Controllino torque commands and input acquisition operations must be temporally aligned
- Use same hardware timer interrupt for both operations
- Timestamp all data sources for post-processing alignment verification

### Communication Reliability

- Implement error checking for serial data transfer
- Verify data integrity after transfer
- Handle timeout conditions and communication failures
- Implement CAN error handling and retry mechanisms
- **Serial blocking**: Serial communication is blocked during torque output for maximum performance

## File Organization

```
project_root/
├── src/
│   ├── controllino/
│   │   ├── main-controllino/
│   │   │   └── main-controllino.ino  # Main firmware
│   │   └── test-controllino-odrive/
│   │       └── test-controllino-odrive.ino  # Reference/test code
│   └── python/
│       ├── odrive_config.py
│       ├── main_controller.py
│       ├── main_sequential.py
│       └── requirements.txt
├── data/
│   └── (acquired data CSV files)
├── plots/
│   └── (exported PNG files)
└── docs/
    └── specs/
        ├── specifications.md  (legacy Opta version)
        ├── specifications-nucleo.md  (NUCLEO version)
        └── specifications-controllino.md  (this file)
```

## Data Flow

1. User loads torque command CSV file in Python GUI
2. Python application sends configuration to Controllino via serial
3. Python configures ODrive S1 via USB (torque control mode, enter closed-loop control)
4. User initiates identification from GUI
5. Controllino begins cyclic torque command transmission via CAN
6. ODrive receives CAN commands and operates motor
7. Controllino acquires data from hardware pins A0-A5 (logical channels A0-A5) synchronously with torque commands
8. After specified duration, Controllino stops and transfers data via serial
9. Python retrieves data from Controllino
10. Python calculates derived signals (theta_x, theta_y, x, y)
11. All data saved to timestamped CSV file
12. GUI displays time-domain plots with user selection
13. User can switch to Bode plot view for frequency analysis
14. User can export visualizations and data
15. Python exits ODrive closed-loop control via USB

## Success Criteria

- Torque commands accurately transmitted via CAN according to CSV file waveform cyclically
- All six analog input channels (hardware pins A0-A5, logical channels A0-A5) sampled synchronously with accurate timing
- Data transfer completes without corruption or loss
- Calculated signals correctly derived from raw inputs
- GUI provides intuitive control and real-time status feedback
- Time-domain plots display selected signals with synchronized axes
- Bode plots correctly show magnitude (m/Nm) and unwrapped phase
- All data successfully exported in documented CSV format
- System operates reliably for repeated acquisition cycles
- Serial communication properly blocked during operation for maximum performance

## Notes

- Sample rates must be consistent across Controllino acquisition and CSV playback
- RAM limitations constrain maximum acquisition duration (Controllino Micro has 264 KB RAM)
- Serial communication baud rate may limit data transfer speed
- CAN communication provides reliable, high-speed motor control
- Hardware timer capabilities of RP2040 enable precise timing control
- Default sample rate is 8kHz (configurable via CSV metadata)
- Development environment: Arduino IDE with Controllino board support
- **No position feedback**: ODrive position is not retrieved during operation to avoid interrupting torque signals

## Key Differences from NUCLEO System

1. **Hardware Platform**: Controllino Micro (RP2040) instead of NUCLEO-G474RE (STM32)
2. **Development Framework**: Arduino IDE instead of STM32CubeIDE
3. **ADC Implementation**: RP2040 hardware timer ISR triggering ADC reads instead of STM32 HAL DMA
4. **Serial Blocking**: Serial communication is blocked during torque output (unlike NUCLEO which maintained serial parsing)
5. **Command Structure**: Merged START_OUTPUT and START_ACQUISITION into START_IDENTIFICATION
6. **Automatic Stop**: No STOP commands needed - acquisition and output stop automatically
7. **ODrive Control**: USB Serial for state control (Python), CAN for torque commands (Controllino)
8. **No Position Feedback**: ODrive position not retrieved during operation (always zeros in data)
9. **Memory**: 264 KB RAM (more than NUCLEO's 128 KB, but still requires careful management)

