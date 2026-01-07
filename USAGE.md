# Quick Start Guide

## Prerequisites

1. **Hardware Setup**:
   - NUCLEO-G474RE connected via USB
   - CAN bus connection between NUCLEO and ODrive S1
   - ODrive S1 connected via USB (optional, for configuration)
   - External analog signals connected to A0-A5 inputs

2. **Software Setup**:
   - Install Python 3.8 or higher
   - Install STM32CubeIDE

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r src/python/requirements.txt
```

### 2. Upload NUCLEO Firmware

1. Open STM32CubeIDE
2. Create a new STM32 project:
   - File > New > STM32 Project
   - Select Board: NUCLEO-G474RE
   - Configure project settings and click Finish
3. Import or copy the firmware source files from `src/nucleo/nucleo-acquisition/` into your project
4. Build the project: Project > Build All (or Ctrl+B)
5. Connect NUCLEO-G474RE via USB
6. Upload firmware: Run > Debug (or F11) to program the board

### 3. Run the Application

```bash
python src/python/main_controller.py
```

## Basic Operation

### Step 1: Load Torque Waveform

1. Click **"Load CSV File"** button
2. Select `src/nucleo/example_torque.csv` or create your own CSV file
3. Verify file information is displayed correctly

**CSV Format**:
- First line: Sample period in seconds (e.g., `0.000125` for 8kHz)
- Subsequent lines: Torque values in Nm (one value per line)

### Step 2: Configure ODrive (Optional)

1. Connect ODrive S1 via USB
2. Click **"Connect ODrive"** button
3. Wait for connection confirmation
4. Configure CAN communication settings
5. Set ODrive node ID for CAN communication

### Step 3: Start Torque Commands

1. Click **"Start Torque Commands"** to begin cyclic torque command transmission via CAN
2. Observe status changes to "TORQUE_ACTIVE"

### Step 4: Acquire Data

1. Set **Acquisition Duration** (seconds) - default 1.0 s
2. Set **Start Delay** if needed (seconds) - default 0.0 s
3. Click **"Start Acquisition"** button
4. Wait for acquisition to complete (status will show "ACQUIRING" then "IDLE")
5. Data will automatically be processed and displayed

### Step 5: View Results

**Time Domain Tab**:
- Check/uncheck signal checkboxes to show/hide traces
- All plots share synchronized x-axis (time)
- Zoom and pan are synchronized across all subplots

**Bode Plot Tab**:
1. Select input signal from dropdown (e.g., "Torque Command")
2. Select output signal from dropdown (e.g., "theta_x")
3. Click **"Calculate Bode Plot"**
4. View magnitude (linear ratio, NOT dB) and phase plots

### Step 6: Export Data

**Export All Data**:
- Click **"Export All Data to CSV"** button
- Data saved to `data/acquisition_YYYYMMDD_HHMMSS.csv`

**Export Bode Plot**:
- Click **"Export Plot (PNG)"** to save Bode plot image
- Click **"Export Bode Data (CSV)"** to save frequency response data

## Troubleshooting

### NUCLEO Connection Issues

- Verify COM port is correctly selected in STM32CubeIDE
- Check USB cable is firmly connected
- Try different USB port
- Verify NUCLEO firmware uploaded successfully
- Check STM32CubeIDE is correctly configured

### ODrive Connection Issues

- Ensure ODrive firmware is up to date
- Check USB cable connection (for configuration)
- Check CAN bus connection between NUCLEO and ODrive
- Verify CAN baud rate matches (500 kbps)
- Verify ODrive node ID is correctly configured
- Try disconnecting and reconnecting ODrive
- Verify ODrive is powered and running

### Serial Communication Errors

- Check baud rate matches (115200)
- Verify no other program is using the COM port
- Restart NUCLEO and Python application
- Check serial buffer isn't overflowing (reduce acquisition duration)

### CAN Communication Errors

- Verify CAN bus wiring (CAN_H, CAN_L, GND)
- Check CAN baud rate matches (500 kbps)
- Verify CAN termination resistors are present (120Ω at each end)
- Check ODrive node ID configuration
- Verify NUCLEO CAN peripheral is correctly initialized

### Memory Limitations

- NUCLEO-G474RE has 128KB RAM for data buffers
- Maximum acquisition time depends on sample rate:
  - 1kHz: ~5 seconds max
  - 8kHz: ~0.6 seconds max
- If acquisition fails with buffer overflow, reduce duration or sample rate
- Consider streaming data instead of buffering for longer acquisitions

### CSV File Issues

- Ensure all torque values are within appropriate range for your motor
- Verify sample period on first line is valid (typically 0.0001 to 1.0 seconds)
- Default sample rate is 8kHz (0.000125 seconds period)
- Check for blank lines at end of file
- Verify file uses Unix line endings (LF) or Windows line endings (CRLF)

### Plot Display Issues

- Verify data was successfully acquired (check status)
- Ensure at least one signal checkbox is selected
- Try clicking "Start Acquisition" again
- Check for memory issues if large datasets

## Advanced Usage

### Creating Custom Waveforms

Create a CSV file with your desired torque waveform:

```csv
0.000125
0.0
0.1
0.2
0.3
0.4
0.3
0.2
0.1
0.0
```

This creates an 8kHz triangular torque wave.

### High-Speed Acquisition

For sample rates at 8kHz and above:
1. Reduce acquisition duration (memory is limited to 128KB)
2. Monitor NUCLEO memory usage
3. Consider streaming data instead of buffering for longer acquisitions
4. Default sample rate is 8kHz - adjust CSV file sample period accordingly

### ODrive Integration

For full motor control integration:
1. Configure ODrive calibration first (encoder, motor parameters)
2. Set appropriate control gains in ODrive configuration tool
3. Configure CAN communication:
   - Set CAN baud rate to 500 kbps
   - Configure ODrive node ID
   - Connect CAN bus (CAN_H, CAN_L, GND) between NUCLEO and ODrive
4. Monitor ODrive feedback in captured data

## Example Workflow

Complete experiment workflow:

1. **Setup**: Load `example_torque.csv` (8kHz torque waveform)
2. **Configuration**: Connect ODrive via USB, configure CAN communication
3. **Calibration**: Run motor calibration if first time
4. **Torque Start**: Start torque command transmission via CAN
5. **Acquisition**: Record data (duration limited by memory at 8kHz)
6. **Analysis**: 
   - View time domain for all channels
   - Calculate Bode plot (Input: Torque Command, Output: theta_x)
   - Export data for further analysis
7. **Repeat**: Change parameters and repeat as needed

## Support

For detailed specifications, see `docs/specs/specifications-nucleo.md`.

For issues or questions:
1. Check NUCLEO Serial Monitor for error messages
2. Verify hardware connections (USB, CAN bus)
3. Review specifications document
4. Check system requirements are met
5. Verify STM32CubeIDE is correctly installed and configured

