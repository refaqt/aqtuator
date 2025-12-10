# STM32CubeIDE Configuration Instructions

## SPI1 and GPIO Configuration for CAN-BUS Shield V2.0

Follow these steps to configure SPI1 and GPIO for the CAN-BUS Shield V2.0 in STM32CubeIDE:

### 1. Open Pinout & Configuration View
- Open the `nucleo-test-can.ioc` file in STM32CubeIDE
- Ensure you're in the **Pinout & Configuration** view (tab at the bottom)

### 2. Configure SPI1
- In the pinout diagram, locate **SPI1** peripheral
- Configure the following pins:
  - **PA5**: Set to **SPI1_SCK** (Serial Clock)
  - **PA6**: Set to **SPI1_MISO** (Master In Slave Out)
  - **PA7**: Set to **SPI1_MOSI** (Master Out Slave In)
- Click on **SPI1** in the **Connectivity** section of the left panel
- In the **Configuration** tab, set the following parameters:
  - **Mode**: Full-Duplex Master
  - **Prescaler (for Baud Rate)**: 16 (this gives ~10.6 MHz SPI clock at 170 MHz system clock)
  - **Data Size**: 8 bits
  - **First Bit**: MSB First
  - **Clock Polarity (CPOL)**: Low
  - **Clock Phase (CPHA)**: 1 Edge
  - **NSS Signal Type**: Software (NSS pin will be controlled manually via GPIO)

### 3. Configure GPIO for CS Pin (PC7)
- In the pinout diagram, locate **PC7**
- Set **PC7** to **GPIO_Output**
- Right-click on PC7 and select **Enter User Label**
- Enter label: **CAN_CS**
- In the **System Core** → **GPIO** section:
  - Find **PC7** in the list
  - Set **GPIO mode**: GPIO_Output
  - Set **GPIO Pull-up/Pull-down**: No pull-up and no pull-down
  - Set **Maximum output speed**: Low
  - Set **User Label**: CAN_CS
  - Set **Initial Output Level**: High (CS inactive)

### 4. Generate Code
- Go to **Project** → **Generate Code** (or press **Ctrl+G**)
- STM32CubeIDE will generate the initialization code for SPI1 and GPIO
- **Important**: Any manual edits to generated code files will be overwritten on regeneration

### 5. Verify Generated Code
After code generation, verify that:
- `MX_SPI1_Init()` function is generated in `main.c`
- `MX_GPIO_Init()` includes PC7 configuration
- `hspi1` handle is available globally
- `CAN_CS_Pin` and `CAN_CS_GPIO_Port` defines are created in `main.h`

## Notes
- The SPI clock frequency should be between 8-16 MHz for reliable MCP2515 communication
- CS pin (PC7) must be controlled manually in software (pull low before SPI transaction, high after)
- Do NOT manually edit the `.ioc` file - always use STM32CubeIDE GUI

