# Quick Start Guide

## Prerequisites

1. **Hardware Setup**:
   - Arduino Opta Lite connected via USB
   - A0602 analog expansion board attached to Opta Lite
   - ODrive S1 connected via USB (optional)
   - External analog signals connected to I1-I6 inputs

2. **Software Setup**:
   - Install Python 3.8 or higher
   - Install Arduino IDE with Opta support
   - Install OptaBlue library in Arduino IDE

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r src/python/requirements.txt
```

### 2. Upload Arduino Firmware

1. Open Arduino IDE
2. Install Arduino Opta Lite board support (if not already installed)
3. Install OptaBlue library via Library Manager
4. Open `src/arduino/opta_acquisition.ino`
5. Select board: Tools > Board > Arduino Opta (Portable PLC)
6. Select port: Tools > Port > [Your COM port]
7. Click Upload

### 3. Run the Application

```bash
python src/python/main_controller.py
```

## Basic Operation

### Step 1: Load Voltage Waveform

1. Click **"Load CSV File"** button
2. Select `src/arduino/example_output.csv` or create your own CSV file
3. Verify file information is displayed correctly

**CSV Format**:
- First line: Sample period in seconds (e.g., `0.001` for 1kHz)
- Subsequent lines: Voltage values 0-3.3V (one value per line)

### Step 2: Configure ODrive (Optional)

1. Connect ODrive S1 via USB
2. Click **"Connect ODrive"** button
3. Wait for connection confirmation
4. Select control mode (Torque/Velocity/Position)
5. Select analog mapping (Position/Velocity/Torque)

### Step 3: Start Output

1. Click **"Start Output"** to begin cyclic voltage playback
2. Observe status changes to "OUTPUTTING"

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
1. Select input signal from dropdown (e.g., "Output Voltage")
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

### Arduino Connection Issues

- Verify COM port is correctly selected in Arduino IDE
- Check USB cable is firmly connected
- Try different USB port
- Verify Arduino firmware uploaded successfully

### ODrive Connection Issues

- Ensure ODrive firmware is up to date
- Check USB cable connection
- Try disconnecting and reconnecting ODrive
- Verify ODrive is powered and running

### Serial Communication Errors

- Check baud rate matches (115200)
- Verify no other program is using the COM port
- Restart Arduino and Python application
- Check serial buffer isn't overflowing (reduce acquisition duration)

### Memory Limitations

- Arduino Opta has ~400KB RAM for data buffers
- Maximum acquisition time depends on sample rate:
  - 1kHz: ~16 seconds max
  - 10kHz: ~1.6 seconds max
- If acquisition fails with buffer overflow, reduce duration or sample rate

### CSV File Issues

- Ensure all voltage values are between 0 and 3.3V
- Verify sample period on first line is valid (typically 0.0001 to 1.0 seconds)
- Check for blank lines at end of file
- Verify file uses Unix line endings (LF) or Windows line endings (CRLF)

### Plot Display Issues

- Verify data was successfully acquired (check status)
- Ensure at least one signal checkbox is selected
- Try clicking "Start Acquisition" again
- Check for memory issues if large datasets

## Advanced Usage

### Creating Custom Waveforms

Create a CSV file with your desired waveform:

```csv
0.001
1.0
1.5
2.0
2.5
3.0
2.5
2.0
1.5
1.0
```

This creates a 1kHz triangular wave.

### High-Speed Acquisition

For sample rates above 10kHz:
1. Reduce acquisition duration
2. Monitor Arduino memory usage
3. Consider streaming data instead of buffering

### ODrive Integration

For full motor control integration:
1. Configure ODrive calibration first (encoder, motor parameters)
2. Set appropriate control gains in ODrive configuration tool
3. Connect Arduino O1 output to ODrive analog input
4. Monitor ODrive feedback in captured data

## Example Workflow

Complete experiment workflow:

1. **Setup**: Load `example_output.csv` (1kHz sine wave)
2. **Configuration**: Connect ODrive, select Position control mode
3. **Calibration**: Run motor calibration if first time
4. **Output Start**: Start voltage output to ODrive
5. **Acquisition**: Record 5 seconds of data
6. **Analysis**: 
   - View time domain for all channels
   - Calculate Bode plot (Input: Output Voltage, Output: theta_x)
   - Export data for further analysis
7. **Repeat**: Change parameters and repeat as needed

## Support

For detailed specifications, see `docs/specs/specifications.md`.

For issues or questions:
1. Check Arduino Serial Monitor for error messages
2. Verify hardware connections
3. Review specifications document
4. Check system requirements are met

