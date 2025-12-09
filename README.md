# aqtuator-control

NUCLEO-G474RE-based synchronized data acquisition and motor control system with ODrive S1 integration.

## Overview

This project integrates a NUCLEO-G474RE development board and an ODrive S1 motor driver to create a synchronized data acquisition and motor control system. The system sends torque commands via CAN V2.0, acquires multiple analog input channels, and captures motor feedback data for analysis.

## System Architecture

### Hardware Components

- **NUCLEO-G474RE**: Main controller for analog input acquisition and CAN communication
- **ODrive S1 Motor Driver**: High-rate motor control and feedback capture
- **Communication**: Serial interface (NUCLEO-PC), CAN V2.0 (NUCLEO-ODrive), USB (ODrive-PC)

### Software Components

1. **NUCLEO firmware** (`src/nucleo/nucleo-acquisition/`): Real-time analog input acquisition and CAN communication using HAL
2. **ODrive configuration script** (`src/python/odrive_config.py`): ODrive S1 setup and control
3. **Main control application** (`src/python/main_controller.py`): PyQt5 GUI for system control and visualization

## Features

- **Synchronized Data Acquisition**: Hardware-timed sampling on 6 analog input channels with minimal jitter (default 8kHz, configurable)
- **CAN V2.0 Motor Control**: Cyclic transmission of torque commands to ODrive S1 via CAN bus
- **Real-time Control**: Start/stop acquisition and torque command control via intuitive GUI
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

### NUCLEO Setup

1. Install STM32CubeIDE
2. Open STM32CubeIDE and import/create project for NUCLEO-G474RE
3. Build and upload firmware to the NUCLEO-G474RE

## Usage

### Starting the Application

```bash
python src/python/main_controller.py
```

### Typical Workflow

1. **Load CSV File**: Click "Load CSV File" to select a torque command waveform file
   - Format: First line = sample period (seconds), subsequent lines = torque values (Nm)

2. **Configure ODrive** (optional):
   - Click "Connect ODrive" to establish USB connection
   - Configure CAN communication settings
   - Set ODrive node ID for CAN communication

3. **Start Torque Commands**: Click "Start Torque Commands" to begin cyclic torque command transmission via CAN

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

Example `example_torque.csv`:

```
0.000125
0.0
0.1
0.2
0.3
...
```

- First line: Sample period in seconds (e.g., 0.000125 = 8kHz)
- Subsequent lines: Torque values in Nm

## Project Structure

```
aqtuator-control/
├── src/
│   ├── nucleo/
│   │   ├── nucleo-acquisition/    # NUCLEO firmware (STM32CubeIDE project)
│   │   └── example_torque.csv      # Example torque waveform file
│   └── python/
│       ├── main_controller.py      # PyQt5 GUI application
│       ├── odrive_config.py        # ODrive configuration module
│       └── requirements.txt        # Python dependencies
├── data/                            # Acquired data storage
├── plots/                           # Exported plot images
└── docs/
    ├── specs/
    │   └── specifications-nucleo.md # Detailed specifications
    └── datasheets/                 # Hardware datasheets
```

## Data Processing

### Geometric Calculations

The system automatically calculates derived signals from raw analog inputs:

**Angular Displacements:**
- `theta_x = -(A0 + A1 - A2 - A3) * sin(alpha) / (2 * L3)`
- `theta_y = -(A0 - A1 - A2 + A3) * cos(alpha) / (2 * L3)`

**Linear Accelerations:**
- `x = (-(A0 - A1 + A2 - A3) * cos(alpha) / 4 - theta_y * (L1 + L2 + L3 / 2) - A5) * r_a`
- `y = ((A0 + A1 + A2 + A3) * sin(alpha) / 4 + theta_x * (L1 + L2 + L3 / 2) - A4) * r_a`

**Constants:**
- L1 = 0.01 m
- L2 = 0.05 m
- L3 = 0.2 m
- alpha = 20° (converted to radians)
- r_a = 5 * 9.81 / 10 m/s²/V

## Technical Specifications

### NUCLEO-G474RE

- **MCU**: STM32G474RE (Cortex-M4, 170 MHz)
- **Analog Input Channels**: 6 (A0-A5) using built-in ADC
- **CAN Communication**: CAN V2.0 peripheral for ODrive control
- **Sampling Rate**: 8kHz default (configurable)
- **Timing**: Hardware-timed using STM32 HAL timer peripherals
- **Memory**: 128KB RAM available for acquisition buffers
- **Development**: STM32CubeIDE with STM32 HAL libraries

### Serial Communication

- **Baud Rate**: 115200
- **Protocol**: Text-based commands with ACK/NACK responses
- **Commands**: START_TORQUE, STOP_TORQUE, START_ACQUISITION, UPLOAD_CSV, GET_DATA

### CAN Communication

- **Protocol**: CAN V2.0 (ISO 11898)
- **Baud Rate**: 500 kbps
- **Hardware**: STM32G474RE CAN peripheral
- **Pins**: PA11/PA12 (CAN1) or PB8/PB9 (CAN2)

### ODrive S1

- **Connection**: USB (for configuration), CAN (for control)
- **Control Mode**: Torque control via CAN commands
- **Data Capture**: High-rate buffer for motor feedback variables

## License

See LICENSE file for details.

## References

- [NUCLEO-G474RE Documentation](https://www.st.com/en/evaluation-tools/nucleo-g474re.html)
- [STM32G4 Series Reference](https://www.st.com/en/microcontrollers-microprocessors/stm32g4-series.html)
- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)
- [ODrive Documentation](https://docs.odriverobotics.com/)
- [ODrive CAN Protocol](https://docs.odriverobotics.com/v/latest/guides/can-protocol.html)
