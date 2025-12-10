# UART Debug Instructions

## Overview
UART debug output has been added to verify the program is running. The program will send messages via LPUART1 (Virtual COM Port) at 115200 baud.

## Step-by-Step Instructions

### Step 1: Build the Project
1. In STM32CubeIDE, make sure you're building the **Release** configuration
2. Click the **Build** button (hammer icon) or press **Ctrl+B**
3. Wait for the build to complete successfully

### Step 2: Flash the Program
1. Click the **Run** button (green play button) or press **Ctrl+F11**
2. Select **"nucleo-test-can Release"** from the configuration list
3. The program will be flashed to the NUCLEO board
4. **Note**: The debugger will show "terminated" - this is normal for Run mode. The program continues running on the board.

### Step 3: Open Serial Terminal
You have several options to view the UART output:

#### Option A: Using STM32CubeIDE Serial Monitor
1. In STM32CubeIDE, go to **Window** → **Show View** → **Other...**
2. Expand **Terminal** and select **Terminal**
3. Click **OK**
4. In the Terminal view, click the **Open a Terminal** icon (green + sign)
5. Select **Serial Terminal**
6. Choose the COM port for your NUCLEO board (usually shows as "STMicroelectronics Virtual COM Port")
7. Set baud rate to **115200**
8. Click **OK**

#### Option B: Using PuTTY (Windows)
1. Download PuTTY if not already installed: https://www.putty.org/
2. Open PuTTY
3. Select **Serial** connection type
4. Enter the COM port number (check Device Manager → Ports (COM & LPT))
5. Set **Speed (baud rate)** to **115200**
6. Click **Open**

#### Option C: Using Tera Term
1. Download Tera Term if not already installed: https://ttssh2.osdn.jp/index.html.en
2. Open Tera Term
3. Select **Serial** and choose the COM port
4. Go to **Setup** → **Serial Port**
5. Set baud rate to **115200**
6. Click **OK**

### Step 4: Verify Program Output
After opening the serial terminal, you should see the following messages:

```
========================================
ODrive CAN Torque Control Started
========================================
Initializing MCP2515 CAN controller...
MCP2515 initialized successfully
CAN bitrate: 1 Mbps
Starting cyclic torque commands...
Sequence: 0.0 -> 0.5 -> 1.0 -> 0.5 Nm (repeating)
========================================

[0] Sending torque: 0.00 Nm
[1] Sending torque: 0.50 Nm
[2] Sending torque: 1.00 Nm
[3] Sending torque: 0.50 Nm
[0] Sending torque: 0.00 Nm
[1] Sending torque: 0.50 Nm
...
```

### Step 5: Interpret the Results

**If you see the messages above:**
- ✅ **Program is running correctly!**
- The "terminated" message in the IDE is just the debugger disconnecting after flashing
- The program continues running on the board and sending CAN messages

**If you see "ERROR: MCP2515 initialization failed!":**
- The MCP2515 CAN controller failed to initialize
- Check SPI connections and CAN-BUS Shield wiring
- Verify CS pin (PC7) is properly connected

**If you see no output at all:**
- Check COM port selection (may need to try different ports)
- Verify baud rate is 115200
- Check if the board is powered on
- Try unplugging and replugging the USB cable

**If messages stop after initialization:**
- The program may have entered Error_Handler()
- Check CAN bus connections
- Verify ODrive S1 is connected and powered

## Troubleshooting

### COM Port Not Found
1. Open **Device Manager** (Windows)
2. Look under **Ports (COM & LPT)**
3. Find "STMicroelectronics Virtual COM Port" or similar
4. Note the COM port number (e.g., COM3, COM4)
5. Use this port number in your serial terminal

### No Output After Flashing
1. **Reset the board** by pressing the black reset button on the NUCLEO
2. The program should restart and send startup messages
3. If still no output, check that you're using the correct COM port

### Messages Appear But Stop
- The program may have encountered an error
- Check CAN bus wiring
- Verify MCP2515 is properly connected
- Check if ODrive S1 is responding

## Next Steps

Once you confirm the program is running via UART:
1. **Verify CAN messages** using a CAN analyzer tool
2. **Check ODrive S1** responds to torque commands
3. **Monitor motor behavior** to confirm torque commands are being executed

