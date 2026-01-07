# Project Specifications: NUCLEO-G474RE Data Acquisition and Motor Control System

## Overview

This project integrates a NUCLEO-G474RE development board and an ODrive S1 motor driver to create a synchronized data acquisition and motor control system. The system acquires multiple analog input channels, sends torque commands to the ODrive S1 via CAN V2.0, and captures motor feedback data for analysis.

## Development Phases

The development of the main control application is split into two phases:

### Phase 1: Sequential Flow (Current)

**Objective**: Create a simple, sequential workflow without a full GUI to establish a working version that performs all necessary steps.

**Implementation**: `main_sequential.py`

**Workflow**:
1. **Connect to NUCLEO**: Automatically connects to hard-coded port COM10
2. **ODrive Connection Prompt**: User is prompted via command line to connect to ODrive (default COM12, uses USB via `odrive.find_any()`)
3. **CSV File Selection**: File dialog opens to select the multisine CSV file
4. **Acquisition Duration**: Command-line prompt asks user for acquisition duration in seconds
5. **Start Torque Commands Window**: Dialog window with "Start Torque Commands" button appears
6. **Control Window**: After torque commands start, a new dialog window appears with:
   - "Stop Torque Commands" button (stops torque commands and ends the program)
   - "Start Acquisition" button (keeps torque commands going and starts acquisition)
7. **Stop Acquisition Window**: When acquisition starts, a new dialog window appears with "Stop Acquisition" button
8. **Acquisition Completion**: Acquisition stops when either:
   - The specified duration is reached, OR
   - User clicks "Stop Acquisition" button
9. **Time Series Visualization**: A graph window opens displaying all selected variables vs. time:
   - All plots in one window with synchronized x-axes
   - Variables displayed: Torque command, A0-A5, acc0-acc5, x, y, theta_x, theta_y, and ODrive variables
   - Variable selection is hard-coded in the program
10. **Bode Plot Visualization**: Six Bode plots open in a 2 rows × 3 columns grid:
    - Input/output pairs are hard-coded in the program
    - Each plot shows magnitude (log-log) and phase (log-linear) subplots

**Features**:
- Minimal GUI: Only simple dialog windows with buttons, no full GUI application
- Hard-coded configuration: NUCLEO port (COM10), variable lists, and Bode plot configurations
- Sequential execution: Step-by-step flow with user interaction at each stage
- Full functionality: All core features (connection, CSV upload, torque commands, acquisition, visualization)

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

- **NUCLEO-G474RE**: Main controller for analog input acquisition and CAN communication (STM32G474RE MCU)
- **ODrive S1 Motor Driver**: Provides motor control with high-rate feedback capture
- **Communication**: Serial interface between NUCLEO and PC, CAN V2.0 for ODrive torque commands

### Software Components

1. **NUCLEO firmware** (STM32CubeIDE project): Handles real-time analog input acquisition and CAN communication using HAL
2. **ODrive configuration script** (.py): Configures ODrive S1 parameters and capture modes
3. **Main control application** (.py): Provides GUI for user interaction and data management

## Channel Naming Convention

To maintain consistency and clarity, this document uses a direct mapping between hardware pin names and logical channel names:

- **Hardware Pins**: Physical pin names on NUCLEO-G474RE (A0, A1, A2, A3, A4, A5, etc.)
- **Logical Channels**: Names used in data arrays, processing, and storage (A0, A1, A2, A3, A4, A5)

**Mapping:**
- Hardware pin A0 → Logical channel A0 (array index 0)
- Hardware pin A1 → Logical channel A1 (array index 1)
- Hardware pin A2 → Logical channel A2 (array index 2)
- Hardware pin A3 → Logical channel A3 (array index 3)
- Hardware pin A4 → Logical channel A4 (array index 4)
- Hardware pin A5 → Logical channel A5 (array index 5)

This direct mapping ensures that hardware pin names and logical channel names are identical, eliminating confusion and making the system more intuitive.

## NUCLEO Firmware Requirements

### Analog Input Acquisition

- **Hardware Pins**: A0, A1, A2, A3, A4, A5 (six channels using built-in ADC on NUCLEO-G474RE)
- **Logical Channel Names**: A0, A1, A2, A3, A4, A5 (used in data processing and storage)
- **Pin-to-Channel Mapping**: 
  - Hardware pin A0 → Logical channel A0 (array index 0)
  - Hardware pin A1 → Logical channel A1 (array index 1)
  - Hardware pin A2 → Logical channel A2 (array index 2)
  - Hardware pin A3 → Logical channel A3 (array index 3)
  - Hardware pin A4 → Logical channel A4 (array index 4)
  - Hardware pin A5 → Logical channel A5 (array index 5)
- **ADC Architecture**: 
  - NUCLEO-G474RE has built-in ADC peripherals (ADC1, ADC2, ADC3, ADC4)
  - For synchronized timing of 6 channels, use hardware-timed ADC sampling via HAL
  - Multi-channel scanning can be implemented using DMA for efficient data transfer
- **Timing**: Hardware-timed sampling with accurate clock via HAL timer peripherals
- **Implementation**: 
  - Uses **STM32 HAL libraries** for hardware-timed ADC sampling
  - Hardware timing implemented using STM32 timer peripherals (e.g., TIM1, TIM2, TIM3)
  - DMA-based data transfer for efficient multi-channel acquisition
  - Default sample rate: 8kHz (configurable)
  - Reference: STM32G4 HAL documentation and STM32G474RE reference manual
- **Real-time Constraint**: No interruptions during acquisition period
- **Synchronization**: Torque commands and input acquisition synchronized via hardware timers

### CAN V2.0 Communication for ODrive Control

- **Protocol**: CAN V2.0 (ISO 11898)
- **Baud Rate**: 500 kbps (standard for ODrive S1)
- **Hardware**: CAN peripheral on STM32G474RE
- **Pins**: Standard CAN pins (PA11/PA12 for CAN1 or PB8/PB9 for CAN2)
- **Message Format**: 
  - CAN ID: ODrive node ID (typically 0x00 for axis 0)
  - Data: Torque command values (Nm) encoded in CAN message payload
  - Message structure follows ODrive CAN protocol specification
- **Implementation**:
  - Uses STM32 HAL CAN library for message transmission
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
- CSV header row: `Time_s,Torque`
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
- NUCLEO firmware must skip header comment lines (lines starting with `#`)
- Extract sample period from metadata header (`# fs: X.XX Hz`) or calculate from time column differences
- Parse CSV header row to identify column structure
- Extract torque values from second column (Torque column)
- Validate torque range as appropriate for the motor
- Python controller must parse header comments to extract metadata
- Python controller must handle comma-separated data rows

### Timing and Control

- **Start Delay**: Configurable wait time before acquisition begins
- **Acquisition Duration**: Controlled by Python application
- **Data Storage**: Samples stored in RAM during acquisition
- **Data Transfer**: Send all acquired data via serial interface after acquisition completes
- **Torque Command Control**: Torque commands continue during data transfer

### Serial Communication Protocol

**Communication Settings:**
- **Baud Rate**: 115200
- **Data Format**: Text-based commands and responses (newline-terminated)
- **Line Endings**: Commands and responses terminated with `\n` (newline character)

**Command Format:**
All commands are sent from Python application to NUCLEO as text strings terminated with newline (`\n`). Commands are case-sensitive.

**Commands (Python → NUCLEO):**

1. **START_TORQUE**
   - Format: `START_TORQUE\n`
   - Description: Begin cyclic torque command transmission via CAN from loaded CSV data
   - Prerequisites: CSV file must be loaded via UPLOAD_CSV
   - Response: `ACK: Torque commands started\n` on success, or `ERROR: <message>\n` on failure

2. **STOP_TORQUE**
   - Format: `STOP_TORQUE\n`
   - Description: Halt torque command transmission (motor stops)
   - Response: `ACK: Torque commands stopped\n`

3. **START_ACQUISITION**
   - Format: `START_ACQUISITION,<duration>,<start_delay>\n`
   - Parameters:
     - `<duration>`: Acquisition duration in seconds (float, e.g., `1.5`)
     - `<start_delay>`: Delay before starting acquisition in seconds (float, e.g., `0.5`)
   - Description: Start synchronized data acquisition. If torque commands are not active, they will be started automatically.
   - Behavior: Blocks until acquisition completes (NUCLEO waits in loop)
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
   - Description: Upload CSV torque waveform data to NUCLEO
   - Protocol Flow:
     1. Python sends: `UPLOAD_CSV,<num_lines>\n`
     2. NUCLEO responds: `READY\n` (after clearing serial buffer)
     3. Python sends CSV data lines (one per line, newline-terminated)
     4. NUCLEO responds: `ACK: CSV loaded\n` on success, or `NACK: <error_message>\n` on failure
   - CSV Format: See "CSV File Format" section above
   - Notes: NUCLEO clears serial buffer before sending READY. Python should wait for READY before sending data.

6. **GET_STATUS**
   - Format: `GET_STATUS\n`
   - Description: Request current system status
   - Response: `STATUS:<state>,<torque_active>,<acquisition_active>,<csv_sample_count>,<csv_sample_period>\n`
     - `<state>`: Integer state code (0=IDLE, 1=TORQUE_ACTIVE, 2=ACQUIRING, 3=TRANSFERRING)
     - `<torque_active>`: Boolean (0 or 1)
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
- `1` = STATE_TORQUE_ACTIVE: Transmitting torque commands via CAN
- `2` = STATE_ACQUIRING: Acquiring data (torque commands may also be active)
- `3` = STATE_TRANSFERRING: Transferring data to Python (torque commands continue)

**Protocol Notes:**
- All commands and responses are text-based (not binary)
- Commands are matched using `startsWith()` - partial matches are acceptable
- Python should filter DEBUG/INFO messages during normal operation
- Serial buffer should be cleared before sending UPLOAD_CSV to avoid race conditions
- NUCLEO may send DEBUG messages during CSV upload - Python should ignore these until READY is received

## ODrive Configuration Script Requirements

### Control Mode Selection

The ODrive S1 shall support torque control mode (primary mode for this system):
- Torque control mode (via CAN commands)

### CAN Communication

The torque commands from NUCLEO shall be transmitted via CAN V2.0:
- CAN baud rate: 500 kbps
- CAN ID: ODrive node ID (typically 0x00 for axis 0)
- Message format: Follows ODrive CAN protocol specification for torque commands

### High-Rate Capture Configuration

- **Sampling Rate**: Match the NUCLEO acquisition rate (default 8kHz)
- **Captured Variables**:
  - Torque command (received via CAN)
  - Position feedback
  - Velocity feedback
  - Torque feedback
  - Current feedback

## Main Control Application Requirements

### User Interface - Input Configuration

- File selection dialog to load torque command CSV file
- Display loaded file information (sample rate, duration, number of samples)
- Validation of CSV file format and torque range

### User Interface - Control Panel

**Torque Command Control:**
- Start button: Begin torque command transmission via CAN
- Stop button: Halt torque command transmission

**Acquisition Control:**
- Start button: Begin data acquisition
- Stop button: End data acquisition
- Time range input: Set acquisition duration in seconds
- Status indicators: Show current state (idle, torque_active, acquiring, transferring)

**ODrive Configuration:**
- CAN connection status indicator
- ODrive node ID configuration

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
- Torque command signal (synchronized with inputs, transmitted via CAN)
- Acquired analog inputs: A0, A1, A2, A3, A4, A5 (logical channel names, mapped directly from hardware pins A0-A5)
- Calculated signals: x, y, theta_x, theta_y
- ODrive feedback variables:
  - Torque command (received via CAN)
  - Position feedback
  - Velocity feedback
  - Torque feedback
  - Current feedback

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

### NUCLEO-G474RE

- Official documentation: `https://www.st.com/en/evaluation-tools/nucleo-g474re.html`
- STM32G4 series reference: `https://www.st.com/en/microcontrollers-microprocessors/stm32g4-series.html`
- STM32G474RE datasheet: `https://www.st.com/resource/en/datasheet/stm32g474re.pdf`
- STM32G4 HAL documentation: `https://www.st.com/resource/en/user_manual/um2609-stm32cube-g4-mcu-package-stmicroelectronics.pdf`
- ADC functionality: STM32G4 HAL ADC examples
- CAN functionality: STM32G4 HAL CAN examples
- Timer interrupts: STM32G4 HAL timer examples

### ODrive S1

- ODrive documentation: `https://docs.odriverobotics.com/v/latest/`
- Python API: `https://docs.odriverobotics.com/v/latest/api/odrive.html`
- CAN protocol: `https://docs.odriverobotics.com/v/latest/guides/can-protocol.html`
- High-rate data capture: `https://docs.odriverobotics.com/v/latest/guides/data-logging.html`

### Python Libraries

- PySerial for NUCLEO communication: `https://pyserial.readthedocs.io/`
- ODrive Python package: `https://pypi.org/project/odrive/`
- Matplotlib for plotting: `https://matplotlib.org/stable/gallery/index.html`
- NumPy for signal processing: `https://numpy.org/doc/stable/reference/routines.fft.html`
- SciPy for frequency analysis: `https://docs.scipy.org/doc/scipy/reference/signal.html`

### STM32CubeIDE

- **STM32CubeIDE**: Official STM32 development environment
- STM32CubeIDE download and installation: `https://www.st.com/en/development-tools/stm32cubeide.html`
- STM32 HAL library integration: Included with STM32CubeIDE (no separate installation needed)
- Project creation and configuration: Use STM32CubeIDE project wizard for NUCLEO-G474RE

## Technical Constraints

### Timing Accuracy

- NUCLEO sampling must maintain consistent timing throughout acquisition
- Use hardware timer peripherals (STM32G4 timers) for clock generation
- Minimize jitter and timing variations
- Leverage STM32G4's hardware timer capabilities for precise timing control

### Memory Management

- Calculate maximum acquisition time based on available RAM on both NUCLEO-G474RE and ODrive S1
- NUCLEO-G474RE: 128 KB RAM available for six input channels plus metadata storage
- ODrive S1: High-rate capture buffer limitations for motor feedback variables
- Maximum acquisition duration is the minimum of:
  - NUCLEO RAM capacity divided by (6 input channels × bytes per sample × sample rate)
  - ODrive capture buffer capacity divided by (number of captured variables × bytes per sample × sample rate)
- Implement bounds checking to prevent buffer overflow on both devices
- Display calculated maximum acquisition time in GUI based on selected sample rate
- Warn user if requested acquisition duration exceeds available memory

**Example Memory Calculation for NUCLEO-G474RE:**
- Available RAM: ~128 KB (accounting for system overhead)
- 6 channels × 4 bytes/float = 24 bytes per sample
- At 8 kHz: 192 KB/s (exceeds RAM capacity - must use streaming or reduce duration)
- At 1 kHz: 24 KB/s
- Maximum duration at 1 kHz: ~5 seconds (conservative estimate)
- At 8 kHz: Maximum duration ~0.6 seconds (conservative estimate)

### Data Synchronization

- NUCLEO torque commands and input acquisition operations must be temporally aligned
- ODrive capture rate must match NUCLEO acquisition rate
- Timestamp all data sources for post-processing alignment verification

### Communication Reliability

- Implement error checking for serial data transfer
- Verify data integrity after transfer
- Handle timeout conditions and communication failures
- Implement CAN error handling and retry mechanisms

## File Organization

```
project_root/
├── src/
│   ├── nucleo/
│   │   ├── nucleo-acquisition/  # STM32CubeIDE project
│   │   └── example_torque.csv
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
        └── specifications-nucleo.md
```

## Data Flow

1. User loads torque command CSV file in Python GUI
2. Python application sends configuration to NUCLEO via serial
3. Python configures ODrive S1 (CAN communication, capture rate)
4. User initiates torque commands from GUI
5. NUCLEO begins cyclic torque command transmission via CAN
6. ODrive receives CAN commands and operates motor
7. User initiates acquisition from GUI
8. NUCLEO acquires data from hardware pins A0-A5 (logical channels A0-A5) synchronously with torque commands
9. ODrive captures motor feedback at matching rate
10. After specified duration, NUCLEO stops and transfers data via serial
11. Python retrieves ODrive capture buffer
12. Python calculates derived signals (theta_x, theta_y, x, y)
13. All data saved to timestamped CSV file
14. GUI displays time-domain plots with user selection
15. User can switch to Bode plot view for frequency analysis
16. User can export visualizations and data

## Success Criteria

- Torque commands accurately transmitted via CAN according to CSV file waveform cyclically
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

- Sample rates must be consistent across NUCLEO acquisition and ODrive capture
- RAM limitations constrain maximum acquisition duration (NUCLEO-G474RE has 128 KB RAM)
- Serial communication baud rate may limit data transfer speed
- CAN communication provides reliable, high-speed motor control
- Hardware timer capabilities of STM32G4 enable precise timing control
- Default sample rate is 8kHz (configurable)
- Development environment: STM32CubeIDE with STM32 HAL libraries

## Key Differences from Previous Systems

1. **CAN Communication**: Uses CAN V2.0 for motor control instead of analog voltage output
2. **Torque Commands**: CSV files contain torque values (Nm) instead of voltage (V)
3. **No Analog Output**: System focuses on acquisition and CAN-based control
4. **HAL Programming**: Uses STM32 HAL libraries for hardware-timed operations
5. **STM32CubeIDE**: Development in STM32CubeIDE (official STM32 development environment)
6. **Memory Constraints**: 128 KB RAM requires careful buffer management compared to previous systems

