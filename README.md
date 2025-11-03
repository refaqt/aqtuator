# aqtuator-control

Arduino Opta Lite-based synchronized data acquisition and motor control system with ODrive S1 integration.

## Overview

This project integrates an Arduino Opta Lite with an A0602 expansion board and an ODrive S1 motor driver to create a synchronized data acquisition and motor control system. The system outputs analog control signals, acquires multiple analog input channels, and captures motor feedback data for analysis.

## System Architecture

### Hardware Components

- **Arduino Opta Lite**: Main controller for analog I/O operations
- **A0602 Expansion Board**: Provides analog output capability (O1)
- **ODrive S1 Motor Driver**: High-rate motor control and feedback capture
- **Communication**: Serial interface (Arduino-PC), USB (ODrive-PC)

### Software Components

1. **Arduino firmware** (`src/arduino/opta_acquisition.ino`): Real-time analog I/O operations
2. **ODrive configuration script** (`src/python/odrive_config.py`): ODrive S1 setup and control
3. **Main control application** (`src/python/main_controller.py`): PyQt5 GUI for system control and visualization

## Features

- **Synchronized Data Acquisition**: Hardware-timed sampling on 6 analog input channels with minimal jitter
- **Cyclic Voltage Output**: Playback of pre-defined voltage waveforms from CSV files
- **Real-time Control**: Start/stop acquisition and output control via intuitive GUI
- **Geometric Calculations**: Automatic computation of angular displacements (theta_x, theta_y) and linear accelerations (x, y)
- **Time-domain Visualization**: Multi-signal synchronized plots with zoom/pan functionality
- **Frequency Analysis**: Bode plot visualization with magnitude and phase plots
- **Data Export**: CSV export of acquisition data and Bode plots with timestamping

## Installation

### Python Dependencies

Install required Python packages:

```bash
pip install -r src/python/requirements.txt
```

### Arduino Setup

1. Install Arduino IDE and Arduino Opta Lite board support
2. Install the OptaBlue library
3. Upload `src/arduino/opta_acquisition.ino` to the Arduino Opta Lite

## Usage

### Starting the Application

```bash
python src/python/main_controller.py
```

### Typical Workflow

1. **Load CSV File**: Click "Load CSV File" to select a voltage waveform file
   - Format: First line = sample period (seconds), subsequent lines = voltage values (0-3.3V)

2. **Configure ODrive** (optional):
   - Click "Connect ODrive" to establish USB connection
   - Select control mode (Torque/Velocity/Position)
   - Select analog input mapping (Position Command/Velocity FF/Torque FF)

3. **Start Output**: Click "Start Output" to begin cyclic voltage playback

4. **Acquire Data**:
   - Set acquisition duration (seconds) and start delay
   - Click "Start Acquisition" to begin synchronized data capture
   - Wait for acquisition to complete

5. **View Results**:
   - **Time Domain Tab**: View selected signals with synchronized axes
   - **Bode Plot Tab**: Select input/output signals and calculate transfer function

6. **Export Data**:
   - Use "Export All Data to CSV" to save acquisition data
   - Use export buttons in Bode Plot tab to save plots and frequency data

### CSV File Format

Example `example_output.csv`:

```
0.001
1.65
1.70
1.75
1.80
...
```

- First line: Sample period in seconds (e.g., 0.001 = 1kHz)
- Subsequent lines: Voltage values in range 0-3.3V

## Project Structure

```
aqtuator-control/
├── src/
│   ├── arduino/
│   │   ├── opta_acquisition.ino    # Arduino firmware
│   │   └── example_output.csv      # Example waveform file
│   └── python/
│       ├── main_controller.py      # PyQt5 GUI application
│       ├── odrive_config.py        # ODrive configuration module
│       └── requirements.txt        # Python dependencies
├── data/                            # Acquired data storage
├── plots/                           # Exported plot images
└── docs/
    ├── specs/
    │   └── specifications.md       # Detailed specifications
    └── datasheets/                 # Hardware datasheets
```

## Data Processing

### Geometric Calculations

The system automatically calculates derived signals from raw analog inputs:

**Angular Displacements:**
- `theta_x = -(A1 + A2 - A3 - A4) * sin(alpha) / (2 * L3)`
- `theta_y = -(A1 - A2 - A3 + A4) * cos(alpha) / (2 * L3)`

**Linear Accelerations:**
- `x = (-(A1 - A2 + A3 - A4) * cos(alpha) / 4 - theta_y * (L1 + L2 + L3 / 2) - A6) * r_a`
- `y = ((A1 + A2 + A3 + A4) * sin(alpha) / 4 + theta_x * (L1 + L2 + L3 / 2) - A5) * r_a`

**Constants:**
- L1 = 0.01 m
- L2 = 0.05 m
- L3 = 0.2 m
- alpha = 20° (converted to radians)
- r_a = 5 * 9.81 / 10 m/s²/V

## Technical Specifications

### Arduino Opta Lite

- **Analog Input Channels**: 6 (I1-I6) on base unit
- **Analog Output**: 1 channel (O1) on A0602 expansion board
- **Output Range**: 0-3.3V
- **Sampling Rate**: Configurable via CSV (max ~100kHz)
- **Timing**: Hardware-timed using STM32 TIM3 peripheral
- **Memory**: ~400KB available for acquisition buffers

### Serial Communication

- **Baud Rate**: 115200
- **Protocol**: Text-based commands with ACK/NACK responses
- **Commands**: START_OUTPUT, STOP_OUTPUT, START_ACQUISITION, UPLOAD_CSV, GET_DATA

### ODrive S1

- **Connection**: USB
- **Control Modes**: Torque, Velocity, Position
- **Analog Input Mapping**: Position setpoint, Velocity feedforward, Torque feedforward
- **Data Capture**: High-rate buffer for motor feedback variables

## License

See LICENSE file for details.

## References

- [Arduino Opta Documentation](https://docs.arduino.cc/hardware/opta/)
- [A0602 Expansion Module](https://www.findernet.com/en/italy/products/automation/controllers/plc-controllers/arduino-opta/)
- [ODrive Documentation](https://docs.odriverobotics.com/)
