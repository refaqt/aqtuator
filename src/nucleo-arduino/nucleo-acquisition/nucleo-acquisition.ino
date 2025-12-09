/*
 * FILE NAME:   nucleo-acquisition.ino
 * DESCRIPTION: NUCLEO-G474RE synchronized data acquisition and CAN-based motor control
 *              Acquires 6 analog input channels and sends torque commands to ODrive S1 via CAN
 * 
 * HARDWARE:    NUCLEO-G474RE (STM32G474RE)
 *              - Analog inputs: A0-A5 (PA0, PA1, PA2, PA3, PA4, PA5)
 *              - CAN: PA11/PA12 (CAN1) or PB8/PB9 (CAN2)
 *              - Serial: USB Virtual COM Port
 * 
 * FEATURES:
 *              - CSV file upload with torque commands
 *              - Hardware-timed acquisition at 8kHz (configurable)
 *              - CAN V2.0 communication with ODrive S1
 *              - Synchronized acquisition: ADC -> CAN read position -> CAN send torque -> store
 *              - Data transfer via serial to Python application
 */

#include <Arduino.h>

// Include HAL configuration to enable modules
// This must be included before any HAL headers
#include "hal_conf_extra.h"

// STM32G4 HAL Driver includes
// In STM32duino, HAL headers are in the core's system directory
// After hal_conf_extra.h enables modules, HAL types become available
// through the core's include system
extern "C" {
  // HAL headers should be accessible through the core
  // The exact path depends on STM32duino version
  // Try including from the core's system directory structure
  #include "stm32g4xx_hal.h"
  #include "stm32g4xx_hal_can.h"
  #include "stm32g4xx_hal_adc.h"
  #include "stm32g4xx_hal_tim.h"
  #include "stm32g4xx_hal_gpio.h"
  #include "stm32g4xx_hal_rcc.h"
}

// ============================================================================
// Configuration
// ============================================================================

#define DEFAULT_SAMPLE_RATE_HZ 8000.0f
#define MAX_CSV_SAMPLES 10000
#define MAX_ACQ_SAMPLES 10000
#define SERIAL_BAUD 115200
#define CAN_BAUD_RATE 1000000  // 1 Mbps
#define ODRIVE_CAN_ID 0x00     // ODrive axis 0 node ID

// Analog input pins (Arduino pin names map to STM32 pins)
#define PIN_A0 A0  // PA0
#define PIN_A1 A1  // PA1
#define PIN_A2 A2  // PA2
#define PIN_A3 A3  // PA3
#define PIN_A4 A4  // PA4
#define PIN_A5 A5  // PA5

// CAN pins (using CAN1: PA11/PA12)
#define CAN_RX_PIN PA11
#define CAN_TX_PIN PA12

// ============================================================================
// State Machine
// ============================================================================

enum SystemState {
  STATE_IDLE = 0,
  STATE_TORQUE_ACTIVE = 1,
  STATE_ACQUIRING = 2,
  STATE_TRANSFERRING = 3
};

SystemState current_state = STATE_IDLE;

// ============================================================================
// CSV Data Storage
// ============================================================================

float csv_torque_commands[MAX_CSV_SAMPLES];
uint16_t csv_sample_count = 0;
float csv_sample_period = 1.0f / DEFAULT_SAMPLE_RATE_HZ;
uint16_t csv_current_index = 0;

// ============================================================================
// Acquisition Data Storage
// ============================================================================

struct AcquisitionSample {
  float analog[6];      // A0-A5
  float position;      // ODrive position feedback
  float torque_cmd;     // Torque command sent
};

AcquisitionSample acq_data[MAX_ACQ_SAMPLES];
uint16_t acq_sample_count = 0;
float acq_sample_period = 1.0f / DEFAULT_SAMPLE_RATE_HZ;
bool acq_active = false;

// ============================================================================
// Hardware Peripherals
// ============================================================================

// CAN handle (will be initialized in setup)
CAN_HandleTypeDef hcan1;

// Timer handle for hardware-timed acquisition (using TIM3 instead of TIM6 for TRGO support)
TIM_HandleTypeDef htim3;

// ADC handle
ADC_HandleTypeDef hadc1;

// ============================================================================
// CAN Functions
// ============================================================================

bool CAN_Init() {
  // Configure CAN GPIO pins
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  
  // Enable CAN and GPIO clocks
  __HAL_RCC_CAN1_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  
  // Configure PA11 (CAN1_RX) and PA12 (CAN1_TX)
  GPIO_InitStruct.Pin = GPIO_PIN_11 | GPIO_PIN_12;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  GPIO_InitStruct.Alternate = GPIO_AF9_CAN1;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  
  // Configure CAN
  hcan1.Instance = CAN1;
  hcan1.Init.Prescaler = 2;
  hcan1.Init.Mode = CAN_MODE_NORMAL;
  hcan1.Init.SyncJumpWidth = CAN_SJW_1TQ;
  hcan1.Init.TimeSeg1 = CAN_BS1_13TQ;
  hcan1.Init.TimeSeg2 = CAN_BS2_2TQ;
  hcan1.Init.TimeTriggeredMode = DISABLE;
  hcan1.Init.AutoBusOff = DISABLE;
  hcan1.Init.AutoWakeUp = DISABLE;
  hcan1.Init.AutoRetransmission = ENABLE;
  hcan1.Init.ReceiveFifoLocked = DISABLE;
  hcan1.Init.TransmitFifoPriority = DISABLE;
  
  if (HAL_CAN_Init(&hcan1) != HAL_OK) {
    return false;
  }
  
  // Configure CAN filter to receive ODrive messages
  CAN_FilterTypeDef sFilterConfig;
  sFilterConfig.FilterBank = 0;
  sFilterConfig.FilterMode = CAN_FILTERMODE_IDMASK;
  sFilterConfig.FilterScale = CAN_FILTERSCALE_32BIT;
  sFilterConfig.FilterIdHigh = 0x0000;
  sFilterConfig.FilterIdLow = 0x0000;
  sFilterConfig.FilterMaskIdHigh = 0x0000;
  sFilterConfig.FilterMaskIdLow = 0x0000;
  sFilterConfig.FilterFIFOAssignment = CAN_RX_FIFO0;
  sFilterConfig.FilterActivation = ENABLE;
  sFilterConfig.SlaveStartFilterBank = 14;
  
  if (HAL_CAN_ConfigFilter(&hcan1, &sFilterConfig) != HAL_OK) {
    return false;
  }
  
  // Start CAN
  if (HAL_CAN_Start(&hcan1) != HAL_OK) {
    return false;
  }
  
  return true;
}

bool CAN_SendTorqueCommand(float torque) {
  CAN_TxHeaderTypeDef TxHeader;
  uint8_t TxData[8];
  uint32_t TxMailbox;
  
  // ODrive CAN protocol: Set Input Torque command
  // CAN ID: 0x00 (axis 0) + 0x00 (Set Input Torque) = 0x00
  // Data: 4-byte float (torque in Nm)
  TxHeader.StdId = ODRIVE_CAN_ID;
  TxHeader.ExtId = 0x00;
  TxHeader.RTR = CAN_RTR_DATA;
  TxHeader.IDE = CAN_ID_STD;
  TxHeader.DLC = 4;  // 4 bytes for float
  TxHeader.TransmitGlobalTime = DISABLE;
  
  // Pack float into bytes (little-endian)
  memcpy(TxData, &torque, 4);
  
  if (HAL_CAN_AddTxMessage(&hcan1, &TxHeader, TxData, &TxMailbox) != HAL_OK) {
    return false;
  }
  
  return true;
}

bool CAN_ReadPosition(float* position) {
  CAN_RxHeaderTypeDef RxHeader;
  uint8_t RxData[8];
  
  // Request position from ODrive
  // Send request message (CAN ID 0x09 for Get Encoder Estimate)
  CAN_TxHeaderTypeDef TxHeader;
  uint8_t TxData[8] = {0};
  uint32_t TxMailbox;
  
  TxHeader.StdId = ODRIVE_CAN_ID | 0x09;  // Request encoder estimate
  TxHeader.ExtId = 0x00;
  TxHeader.RTR = CAN_RTR_DATA;
  TxHeader.IDE = CAN_ID_STD;
  TxHeader.DLC = 0;
  TxHeader.TransmitGlobalTime = DISABLE;
  
  HAL_CAN_AddTxMessage(&hcan1, &TxHeader, TxData, &TxMailbox);
  
  // Wait for response (with timeout)
  uint32_t timeout = HAL_GetTick() + 10;  // 10ms timeout
  while (HAL_GetTick() < timeout) {
    if (HAL_CAN_GetRxFifoFillLevel(&hcan1, CAN_RX_FIFO0) > 0) {
      if (HAL_CAN_GetRxMessage(&hcan1, CAN_RX_FIFO0, &RxHeader, RxData) == HAL_OK) {
        // Check if this is the position response
        if (RxHeader.StdId == (ODRIVE_CAN_ID | 0x09)) {
          // Unpack float from bytes
          memcpy(position, RxData, 4);
          return true;
        }
      }
    }
  }
  
  return false;
}

// ============================================================================
// ADC Functions
// ============================================================================

bool ADC_Init() {
  // Enable ADC1 clock
  __HAL_RCC_ADC12_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();  // Enable GPIOA clock for ADC pins
  
  // Configure ADC
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIG_T3_TRGO;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc1.Init.OversamplingMode = DISABLE;
  
  if (HAL_ADC_Init(&hadc1) != HAL_OK) {
    return false;
  }
  
  // Configure ADC channels
  ADC_ChannelConfTypeDef sConfig = {0};
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLE_5;
  
  // Configure 6 channels: A0-A5
  uint32_t channels[] = {ADC_CHANNEL_0, ADC_CHANNEL_1, ADC_CHANNEL_2, 
                         ADC_CHANNEL_3, ADC_CHANNEL_4, ADC_CHANNEL_5};
  uint32_t ranks[] = {1, 2, 3, 4, 5, 6};
  
  for (int i = 0; i < 6; i++) {
    sConfig.Channel = channels[i];
    sConfig.Rank = ranks[i];
    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
      return false;
    }
  }
  
  return true;
}

bool ADC_ReadChannels(float* values) {
  uint16_t adc_values[6];
  
  // Start ADC conversion
  if (HAL_ADC_Start(&hadc1) != HAL_OK) {
    return false;
  }
  
  // Read all 6 channels
  for (int i = 0; i < 6; i++) {
    if (HAL_ADC_PollForConversion(&hadc1, 10) != HAL_OK) {
      HAL_ADC_Stop(&hadc1);
      return false;
    }
    adc_values[i] = HAL_ADC_GetValue(&hadc1);
  }
  
  HAL_ADC_Stop(&hadc1);
  
  // Convert to voltage (0-3.3V, 12-bit ADC)
  for (int i = 0; i < 6; i++) {
    values[i] = (adc_values[i] / 4095.0f) * 3.3f;
  }
  
  return true;
}

// ============================================================================
// Timer Functions (for hardware-timed acquisition)
// ============================================================================

bool Timer_Init(float sample_rate_hz) {
  // Enable TIM3 clock
  __HAL_RCC_TIM3_CLK_ENABLE();
  
  // Configure TIM3 for hardware-timed acquisition (TIM3 has TRGO output for ADC trigger)
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 170 - 1;  // 170 MHz / 170 = 1 MHz
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = (uint32_t)(1000000.0f / sample_rate_hz) - 1;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK) {
    return false;
  }
  
  // Configure timer to trigger ADC
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_ENABLE;
  
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK) {
    return false;
  }
  
  return true;
}

void Timer_Start() {
  HAL_TIM_Base_Start(&htim3);
}

void Timer_Stop() {
  HAL_TIM_Base_Stop(&htim3);
}

// ============================================================================
// Serial Communication Functions
// ============================================================================

void Serial_SendResponse(const char* response) {
  Serial.println(response);
}

void Serial_SendACK(const char* message) {
  Serial.print("ACK: ");
  Serial.println(message);
}

void Serial_SendNACK(const char* message) {
  Serial.print("NACK: ");
  Serial.println(message);
}

void Serial_SendERROR(const char* message) {
  Serial.print("ERROR: ");
  Serial.println(message);
}

// ============================================================================
// CSV Upload Functions
// ============================================================================

void ProcessCSVUpload() {
  // Wait for UPLOAD_CSV command
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  
  if (!cmd.startsWith("UPLOAD_CSV")) {
    return;
  }
  
  // Parse number of lines
  int comma_pos = cmd.indexOf(',');
  if (comma_pos < 0) {
    Serial_SendERROR("Invalid UPLOAD_CSV format");
    return;
  }
  
  int num_lines = cmd.substring(comma_pos + 1).toInt();
  if (num_lines <= 0 || num_lines > MAX_CSV_SAMPLES) {
    Serial_SendERROR("Invalid number of CSV lines");
    return;
  }
  
  // Clear serial buffer
  while (Serial.available() > 0) {
    Serial.read();
  }
  
  // Send READY
  Serial.println("READY");
  delay(10);
  
  // Read CSV lines
  csv_sample_count = 0;
  String line;
  bool header_found = false;
  
  for (int i = 0; i < num_lines + 10; i++) {  // Allow some extra for headers
    if (Serial.available() == 0) {
      delay(10);
      continue;
    }
    
    line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.length() == 0) {
      continue;
    }
    
    // Skip header lines
    if (line.startsWith("#")) {
      // Try to extract sample rate from metadata
      if (line.indexOf("fs:") >= 0) {
        int fs_pos = line.indexOf("fs:") + 3;
        int hz_pos = line.indexOf("Hz", fs_pos);
        if (hz_pos > fs_pos) {
          String fs_str = line.substring(fs_pos, hz_pos);
          fs_str.trim();
          float fs = fs_str.toFloat();
          if (fs > 0) {
            csv_sample_period = 1.0f / fs;
          }
        }
      }
      continue;
    }
    
    // Skip CSV header row
    if (line.equalsIgnoreCase("Time_s,Torque") || line.equalsIgnoreCase("Time_s,Signal")) {
      header_found = true;
      continue;
    }
    
    // Parse data line
    int comma_pos = line.indexOf(',');
    if (comma_pos > 0) {
      // CSV format: time,torque
      String torque_str = line.substring(comma_pos + 1);
      torque_str.trim();
      float torque = torque_str.toFloat();
      
      if (csv_sample_count < MAX_CSV_SAMPLES) {
        csv_torque_commands[csv_sample_count] = torque;
        csv_sample_count++;
      }
    } else {
      // Single value format (just torque)
      float torque = line.toFloat();
      if (csv_sample_count < MAX_CSV_SAMPLES) {
        csv_torque_commands[csv_sample_count] = torque;
        csv_sample_count++;
      }
    }
    
    // If we've read the expected number of data lines, stop
    if (csv_sample_count >= num_lines) {
      break;
    }
  }
  
  if (csv_sample_count > 0) {
    Serial_SendACK("CSV loaded");
  } else {
    Serial_SendNACK("No valid data lines found");
  }
}

// ============================================================================
// Acquisition Functions
// ============================================================================

void StartAcquisition(float duration, float start_delay) {
  if (csv_sample_count == 0) {
    Serial_SendERROR("No CSV data loaded");
    return;
  }
  
  // Calculate number of samples
  uint16_t num_samples = (uint16_t)(duration / acq_sample_period);
  if (num_samples == 0 || num_samples > MAX_ACQ_SAMPLES) {
    Serial_SendERROR("Invalid acquisition duration");
    return;
  }
  
  // Start torque commands if not already active
  if (current_state != STATE_TORQUE_ACTIVE && current_state != STATE_ACQUIRING) {
    csv_current_index = 0;
    current_state = STATE_TORQUE_ACTIVE;
  }
  
  // Wait for start delay
  if (start_delay > 0) {
    delay((uint32_t)(start_delay * 1000));
  }
  
  // Initialize acquisition
  acq_sample_count = 0;
  acq_active = true;
  current_state = STATE_ACQUIRING;
  
  Serial_SendACK("Acquisition started");
  
  // Configure timer for acquisition rate
  float sample_rate = 1.0f / acq_sample_period;
  Timer_Init(sample_rate);
  Timer_Start();
  
  // Acquisition loop
  uint32_t last_sample_time = 0;
  
  while (acq_sample_count < num_samples && acq_active) {
    // Wait for timer trigger (check every loop iteration)
    // In a real implementation, this would be interrupt-driven
    // For now, we'll use a polling approach with precise timing
    
    uint32_t current_time = micros();
    uint32_t sample_interval = (uint32_t)(acq_sample_period * 1000000.0f);
    
    if (current_time - last_sample_time >= sample_interval) {
      last_sample_time = current_time;
      
      // 1. Acquire analog inputs
      float analog_values[6];
      if (!ADC_ReadChannels(analog_values)) {
        continue;  // Skip this sample if ADC read fails
      }
      
      // 2. Read position from ODrive via CAN
      float position = 0.0f;
      CAN_ReadPosition(&position);  // May fail, use 0.0 as default
      
      // 3. Get current torque command and send via CAN
      float torque_cmd = csv_torque_commands[csv_current_index];
      CAN_SendTorqueCommand(torque_cmd);
      
      // 4. Store all data
      if (acq_sample_count < MAX_ACQ_SAMPLES) {
        for (int i = 0; i < 6; i++) {
          acq_data[acq_sample_count].analog[i] = analog_values[i];
        }
        acq_data[acq_sample_count].position = position;
        acq_data[acq_sample_count].torque_cmd = torque_cmd;
        acq_sample_count++;
      }
      
      // Advance CSV index (cyclic)
      csv_current_index++;
      if (csv_current_index >= csv_sample_count) {
        csv_current_index = 0;
      }
    }
    
    // Check for stop command
    if (Serial.available() > 0) {
      String cmd = Serial.readStringUntil('\n');
      cmd.trim();
      if (cmd.startsWith("STOP_ACQUISITION")) {
        acq_active = false;
        break;
      }
    }
  }
  
  Timer_Stop();
  acq_active = false;
  current_state = STATE_IDLE;
  
  Serial_SendACK("Acquisition complete");
}

// ============================================================================
// Data Transfer Functions
// ============================================================================

void SendAcquisitionData() {
  if (acq_sample_count == 0) {
    Serial_SendERROR("No acquisition data available");
    return;
  }
  
  current_state = STATE_TRANSFERRING;
  
  // Send data header
  Serial.print("DATA:");
  Serial.print(acq_sample_count);
  Serial.print(",");
  Serial.print(acq_sample_period, 6);
  Serial.print(",8");  // 8 channels: A0-A5, position, torque
  Serial.println();
  
  // Send data samples
  for (uint16_t i = 0; i < acq_sample_count; i++) {
    // Format: A0,A1,A2,A3,A4,A5,position,torque
    for (int j = 0; j < 6; j++) {
      Serial.print(acq_data[i].analog[j], 4);
      Serial.print(",");
    }
    Serial.print(acq_data[i].position, 4);
    Serial.print(",");
    Serial.print(acq_data[i].torque_cmd, 4);
    Serial.println();
  }
  
  Serial.println("DATA_END");
  
  current_state = STATE_IDLE;
}

// ============================================================================
// Command Processing
// ============================================================================

void ProcessCommand(String cmd) {
  cmd.trim();
  
  if (cmd.length() == 0) {
    return;
  }
  
  // START_OUTPUT or START_TORQUE
  if (cmd.startsWith("START_OUTPUT") || cmd.startsWith("START_TORQUE")) {
    if (csv_sample_count == 0) {
      Serial_SendERROR("No CSV data loaded");
      return;
    }
    csv_current_index = 0;
    current_state = STATE_TORQUE_ACTIVE;
    Serial_SendACK("Output started");
    return;
  }
  
  // STOP_OUTPUT or STOP_TORQUE
  if (cmd.startsWith("STOP_OUTPUT") || cmd.startsWith("STOP_TORQUE")) {
    current_state = STATE_IDLE;
    Serial_SendACK("Output stopped");
    return;
  }
  
  // START_ACQUISITION
  if (cmd.startsWith("START_ACQUISITION")) {
    int comma1 = cmd.indexOf(',');
    int comma2 = cmd.indexOf(',', comma1 + 1);
    
    if (comma1 < 0 || comma2 < 0) {
      Serial_SendERROR("Invalid START_ACQUISITION format");
      return;
    }
    
    float duration = cmd.substring(comma1 + 1, comma2).toFloat();
    float start_delay = cmd.substring(comma2 + 1).toFloat();
    
    StartAcquisition(duration, start_delay);
    return;
  }
  
  // STOP_ACQUISITION
  if (cmd.startsWith("STOP_ACQUISITION")) {
    acq_active = false;
    Serial_SendACK("Acquisition stopped");
    return;
  }
  
  // GET_DATA
  if (cmd.startsWith("GET_DATA")) {
    SendAcquisitionData();
    return;
  }
  
  // GET_STATUS
  if (cmd.startsWith("GET_STATUS")) {
    Serial.print("STATUS:");
    Serial.print((int)current_state);
    Serial.print(",");
    Serial.print(current_state == STATE_TORQUE_ACTIVE || current_state == STATE_ACQUIRING ? 1 : 0);
    Serial.print(",");
    Serial.print(acq_active ? 1 : 0);
    Serial.print(",");
    Serial.print(csv_sample_count);
    Serial.print(",");
    Serial.print(csv_sample_period, 6);
    Serial.println();
    return;
  }
  
  // RESET
  if (cmd.startsWith("RESET")) {
    csv_sample_count = 0;
    acq_sample_count = 0;
    current_state = STATE_IDLE;
    acq_active = false;
    while (Serial.available() > 0) {
      Serial.read();
    }
    Serial_SendACK("Reset complete");
    return;
  }
}

// ============================================================================
// Main Setup and Loop
// ============================================================================

void setup() {
  // Initialize HAL library (required before using HAL functions)
  HAL_Init();
  
  // Initialize serial communication
  Serial.begin(SERIAL_BAUD);
  delay(1000);
  
  Serial.println("NUCLEO-G474RE Data Acquisition System");
  Serial.println("Ready for commands...");
  
  // Initialize CAN
  if (!CAN_Init()) {
    Serial.println("ERROR: CAN initialization failed");
  } else {
    Serial.println("CAN initialized successfully");
  }
  
  // Initialize ADC
  if (!ADC_Init()) {
    Serial.println("ERROR: ADC initialization failed");
  } else {
    Serial.println("ADC initialized successfully");
  }
  
  // Initialize timer (will be reconfigured for acquisition)
  if (!Timer_Init(DEFAULT_SAMPLE_RATE_HZ)) {
    Serial.println("ERROR: Timer initialization failed");
  } else {
    Serial.println("Timer initialized successfully");
  }
  
  current_state = STATE_IDLE;
  acq_active = false;
}

void loop() {
  // Process serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    
    if (cmd.startsWith("UPLOAD_CSV")) {
      ProcessCSVUpload();
    } else {
      ProcessCommand(cmd);
    }
  }
  
  // If torque commands are active, send them continuously
  if (current_state == STATE_TORQUE_ACTIVE && csv_sample_count > 0) {
    static uint32_t last_torque_time = 0;
    uint32_t current_time = micros();
    uint32_t torque_interval = (uint32_t)(csv_sample_period * 1000000.0f);
    
    if (current_time - last_torque_time >= torque_interval) {
      last_torque_time = current_time;
      
      float torque = csv_torque_commands[csv_current_index];
      CAN_SendTorqueCommand(torque);
      
      csv_current_index++;
      if (csv_current_index >= csv_sample_count) {
        csv_current_index = 0;
      }
    }
  }
  
  delay(1);  // Small delay to prevent tight loop
}

