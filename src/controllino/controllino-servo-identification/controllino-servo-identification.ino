/*
 * Controllino Micro ODrive Servo Identification via CAN
 * 
 * Reads torque_setpoint and pos_estimate from ODrive S1 via CAN at configurable rate
 * (set via cycle_time parameter) and sends data to Python via serial communication.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Install Controllino board support in Arduino IDE
 * 2. CAN.h library is included with Controllino board support
 * 3. Connect CAN bus: CANH to CANH, CANL to CANL, common GND
 * 4. Add 120-ohm termination resistors at both ends of CAN bus
 * 5. Configure ODrive S1 node ID (default: 0) to match ODRIVE_NODE_ID constant
 * 
 * USAGE:
 * - Open Serial Monitor at 115200 baud
 * - Use START_ACQUISITION,<duration>,<cycle_time>,cyclic to start data acquisition
 *   (cycle_time in seconds, e.g., 0.001 for 1 ms cycle time)
 * - Use GET_DATA to retrieve stored data
 */

#include <CAN.h>
#include <string.h>  // For memset

// ============================================================================
// Configuration Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_ACQ_SAMPLES 2000   // Maximum acquisition samples (0.5s at 4 kHz)
                                // Memory: 2000 × 2 × 4 bytes = 16 KB
#define ODRIVE_NODE_ID 0
#define CAN_BAUD_RATE 1000000  // 1 Mbps
#define MIN_ACQUISITION_RATE_HZ 100   // Minimum acquisition rate
#define MAX_ACQUISITION_RATE_HZ 10000 // Maximum acquisition rate

// ODrive CAN message IDs (CANSimple protocol)
#define CAN_ID_GET_ENCODER_ESTIMATES 0x09
#define CAN_ID_GET_TORQUES 0x1C

// ============================================================================
// State Machine
// ============================================================================

enum State {
  STATE_IDLE,
  STATE_ACQUIRING,
  STATE_TRANSFERRING
};

State current_state = STATE_IDLE;

// ============================================================================
// Acquisition Data Storage
// ============================================================================

// Buffer size: MAX_ACQ_SAMPLES * 4 for 4-channel data
// 4 channels: torque_setpoint, pos_estimate, torque_timestamp_us, pos_timestamp_us
float acq_buffer[MAX_ACQ_SAMPLES * 4];  // Memory: 2000 × 4 × 4 bytes = 32 KB
volatile uint32_t acq_sample_count = 0;
volatile uint32_t acq_index = 0;
uint32_t acquisition_rate_hz = 1000;  // Configurable acquisition rate (calculated from cycle time)
float acq_sample_period = 1.0f / 1000.0f;  // Cycle time in seconds (calculated from parsed cycle time parameter)

// Loop timestamp storage for diagnostic purposes
uint32_t loop_timestamps[MAX_ACQ_SAMPLES];  // Memory: 2000 × 4 bytes = 8 KB
volatile uint32_t loop_timestamp_count = 0;

// ============================================================================
// Operation Control
// ============================================================================

volatile bool acquisition_active = false;
volatile bool serial_blocked = false;
bool completion_sent = false;

// Acquisition timing
uint32_t required_acq_samples = 0;
volatile unsigned long acquisition_start_time = 0;

// Latest CAN data (updated from ISR, read in main loop)
volatile float latest_torque_setpoint = 0.0f;
volatile float latest_pos_estimate = 0.0f;
volatile bool torque_data_valid = false;
volatile bool pos_data_valid = false;

// Debug mode for message order tracking
volatile bool debug_message_order = false;
volatile unsigned long torque_timestamp_us = 0;
volatile unsigned long pos_timestamp_us = 0;

// Track what we last stored so we only store fresh pairs
uint32_t last_stored_torque_ts_us = 0;
uint32_t last_stored_pos_ts_us = 0;

// Flag to discard the first batch after START_ACQUISITION
volatile bool discard_first_sample = false;

// Batch processing state variable
bool first_batch_discarded = false;

// Always using cyclic messages - no mode flag needed

// ============================================================================
// Function Prototypes
// ============================================================================

void setupCAN();
void processCANMessages();
void processCommand(String cmd);
void printStatus();

// ============================================================================
// Setup Function
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(2000);  // Longer delay for Controllino stability
  Serial.flush();
  
  Serial.println("========================================");
  Serial.println("Controllino Micro ODrive Servo Identification");
  Serial.println("========================================");
  Serial.flush();
  
  // Initialize CAN
  setupCAN();
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
  Serial.println();
  Serial.println("Commands:");
  Serial.println("  START_ACQUISITION,<duration>,<cycle_time>,cyclic");
  Serial.println("    (always uses cyclic mode, cycle_time in seconds)");
  Serial.println("  GET_DATA");
  Serial.println("  GET_STATUS");
  Serial.println("  DEBUG_ORDER_ON");
  Serial.println("  DEBUG_ORDER_OFF");
  Serial.flush();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Collect loop timestamp at the very start (for diagnostic purposes)
  if (acquisition_active && loop_timestamp_count < MAX_ACQ_SAMPLES) {
    loop_timestamps[loop_timestamp_count++] = micros();
  }
  
  // Only process CAN messages during active acquisition
  if (acquisition_active) {
    processCANMessages();
  }
  
  // Skip reading Serial if blocked during operation
  if (serial_blocked) {
    return;
  }
  
  // Check for acquisition completion notification
  if (!completion_sent && acq_sample_count > 0 && !acquisition_active && !serial_blocked) {
    Serial.println("ACK: Acquisition complete");
    Serial.flush();
    completion_sent = true;
  }
  
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }
}

// ============================================================================
// CAN Setup
// ============================================================================

void setupCAN() {
  Serial.print("Initializing CAN bus at ");
  Serial.print(CAN_BAUD_RATE);
  Serial.println(" bps...");
  
  #ifdef ARDUINO_ARCH_RP2040
    SPI1.setRX(PIN_SPI1_MISO);
    SPI1.setTX(PIN_SPI1_MOSI);
    SPI1.setSCK(PIN_SPI1_SCK);
  #endif
  
  if (!CAN.begin(CAN_BAUD_RATE)) {
    Serial.println("ERROR: CAN initialization failed!");
    Serial.println("Check CAN wiring and connections.");
    while (1) {
      delay(1000);
    }
  }
  Serial.println("CAN bus initialized successfully.");
}

// ============================================================================
// CAN Communication
// ============================================================================

// No requestCANData() function needed - messages come automatically via cyclic mode

// Helper function to parse a CAN message and return type (0=torque, 1=position, 255=invalid)
// Also stores the value and timestamp in the provided pointers
uint8_t parseCANMessage(float* torque_out, float* position_out, unsigned long* torque_ts_out, unsigned long* position_ts_out) {
  int packetSize = CAN.parsePacket();
  if (packetSize <= 0) {
    return 255;  // No message
  }
  
  unsigned long msg_timestamp_us = micros();
  uint32_t canId = CAN.packetId();
  uint32_t baseId = canId & 0x1F;  // Lower 5 bits are the command ID
  uint32_t nodeId = (canId >> 5) & 0x3F;  // Bits 5-10 are node ID (CANSimple: 6-bit node ID)
  
  if (nodeId != ODRIVE_NODE_ID) {
    return 255;  // Not from our ODrive
  }
  
  if (packetSize < 8) {
    return 255;  // Invalid packet size
  }
  
  uint8_t data[8];
  for (int i = 0; i < 8 && i < packetSize; i++) {
    data[i] = CAN.read();
  }
  
  if (baseId == CAN_ID_GET_TORQUES) {
    // Parse GET_TORQUES response: (Torque_Target, Torque_Estimate) as two floats
    float torque_target;
    uint8_t* torqueBytes = (uint8_t*)&torque_target;
    torqueBytes[0] = data[0];
    torqueBytes[1] = data[1];
    torqueBytes[2] = data[2];
    torqueBytes[3] = data[3];
    
    *torque_out = torque_target;
    *torque_ts_out = msg_timestamp_us;
    
    // Update global tracking variables
    torque_timestamp_us = msg_timestamp_us;
    latest_torque_setpoint = torque_target;
    torque_data_valid = true;
    
    return 0;  // Torque message
  } else if (baseId == CAN_ID_GET_ENCODER_ESTIMATES) {
    // Parse GET_ENCODER_ESTIMATES response: (pos_estimate, vel_estimate) as two floats
    float pos_est;
    uint8_t* posBytes = (uint8_t*)&pos_est;
    posBytes[0] = data[0];
    posBytes[1] = data[1];
    posBytes[2] = data[2];
    posBytes[3] = data[3];
    
    *position_out = pos_est;
    *position_ts_out = msg_timestamp_us;
    
    // Update global tracking variables
    pos_timestamp_us = msg_timestamp_us;
    latest_pos_estimate = pos_est;
    pos_data_valid = true;
    
    return 1;  // Position message
  }
  
  return 255;  // Unknown message type
}

void processCANMessages() {
  if (!acquisition_active || acq_index >= MAX_ACQ_SAMPLES) {
    return;
  }
  
  // First batch: discard any in-flight messages to start from a clean boundary.
  if (!first_batch_discarded) {
    const unsigned long drain_budget_us = 2000;  // 2ms is enough to flush a typical cyclic burst
    unsigned long drain_start = micros();
    while ((micros() - drain_start) < drain_budget_us) {
      if (CAN.parsePacket() > 0) {
        while (CAN.available()) {
          CAN.read();
        }
        continue;
      }
      delayMicroseconds(1);
    }
    first_batch_discarded = true;
    return;
  }
  
  // Read/parse whatever is currently available within a bounded time budget.
  // We store a sample only when we have seen both a fresh torque and a fresh position
  // since the last stored sample.
  float torque = 0.0f, position = 0.0f;
  unsigned long torque_ts = 0, position_ts = 0;

  float budget_us_f = acq_sample_period * 1e6f * 0.5f;
  if (budget_us_f < 200.0f) budget_us_f = 200.0f;
  if (budget_us_f > 5000.0f) budget_us_f = 5000.0f;
  const unsigned long read_budget_us = (unsigned long)budget_us_f;

  unsigned long read_start = micros();
  while ((micros() - read_start) < read_budget_us) {
    uint8_t msg_type = parseCANMessage(&torque, &position, &torque_ts, &position_ts);
    if (msg_type == 255) {
      delayMicroseconds(1);
      continue;
    }
  }

  if (!torque_data_valid || !pos_data_valid) {
    return;
  }

  const uint32_t torque_ts_u32 = (uint32_t)torque_timestamp_us;
  const uint32_t pos_ts_u32 = (uint32_t)pos_timestamp_us;
  if (torque_ts_u32 == 0 || pos_ts_u32 == 0) {
    return;
  }

  // Only store when both signals have updated since the last stored sample.
  if (torque_ts_u32 == last_stored_torque_ts_us || pos_ts_u32 == last_stored_pos_ts_us) {
    return;
  }

  float *sample = &acq_buffer[acq_index * 4];
  sample[0] = latest_torque_setpoint;
  sample[1] = latest_pos_estimate;
  sample[2] = (float)torque_ts_u32;
  sample[3] = (float)pos_ts_u32;

  last_stored_torque_ts_us = torque_ts_u32;
  last_stored_pos_ts_us = pos_ts_u32;

  acq_index++;
  acq_sample_count = acq_index;

  if (required_acq_samples > 0 && acq_index >= required_acq_samples) {
    acquisition_active = false;
    serial_blocked = false;
    current_state = STATE_IDLE;
    return;
  }
  if (acq_index >= MAX_ACQ_SAMPLES) {
    acquisition_active = false;
    serial_blocked = false;
    current_state = STATE_IDLE;
    return;
  }
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("START_ACQUISITION")) {
    // Command: START_ACQUISITION,<duration>,<cycle_time>,cyclic
    // Always uses cyclic mode - cycle_time parameter is in seconds
    if (acquisition_active) {
      Serial.println("ERROR: Acquisition already in progress");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing duration in START_ACQUISITION command");
      return;
    }
    
    // Parse duration
    int second_comma_pos = cmd.indexOf(',', comma_pos + 1);
    float acq_duration;
    
    if (second_comma_pos > 0) {
      // Duration provided
      acq_duration = cmd.substring(comma_pos + 1, second_comma_pos).toFloat();
    } else {
      // Only duration provided
      acq_duration = cmd.substring(comma_pos + 1).toFloat();
    }
    
    if (acq_duration <= 0) {
      Serial.println("ERROR: Invalid duration");
      return;
    }
    
    // Parse cycle time (third parameter)
    float cycle_time = 0.001f;  // Default to 1 ms if not provided
    if (second_comma_pos > 0) {
      int third_comma_pos = cmd.indexOf(',', second_comma_pos + 1);
      if (third_comma_pos > 0) {
        // Cycle time provided
        cycle_time = cmd.substring(second_comma_pos + 1, third_comma_pos).toFloat();
      } else {
        // Try to parse from end of string (in case "cyclic" is not present)
        String cycle_time_str = cmd.substring(second_comma_pos + 1);
        cycle_time_str.trim();
        if (cycle_time_str.length() > 0 && cycle_time_str != "cyclic") {
          cycle_time = cycle_time_str.toFloat();
        }
      }
    }
    
    // Validate cycle time
    if (cycle_time <= 0) {
      Serial.println("ERROR: Invalid cycle time (must be > 0)");
      return;
    }
    
    // Calculate acquisition rate from cycle time
    acq_sample_period = cycle_time;
    acquisition_rate_hz = 1.0f / cycle_time;
    
    // Calculate required samples using the fixed rate
    required_acq_samples = (uint32_t)(acq_duration * acquisition_rate_hz);
    if (required_acq_samples > MAX_ACQ_SAMPLES) {
      Serial.print("ERROR: Acquisition duration too long. Maximum: ");
      Serial.print((float)MAX_ACQ_SAMPLES / acquisition_rate_hz);
      Serial.println(" seconds");
      return;
    }
    
    // Reset acquisition state
    acq_index = 0;
    acq_sample_count = 0;
    completion_sent = false;
    torque_data_valid = false;
    pos_data_valid = false;
    torque_timestamp_us = 0;
    pos_timestamp_us = 0;
    last_stored_torque_ts_us = 0;
    last_stored_pos_ts_us = 0;
    discard_first_sample = true;  // Discard the first batch
    first_batch_discarded = false;  // Track if first batch was discarded
    loop_timestamp_count = 0;  // Reset loop timestamp counter
    
    // Clear buffer to remove any old data from previous acquisitions
    memset(acq_buffer, 0, sizeof(acq_buffer));
    
    // Send ACK BEFORE starting acquisition and blocking serial
    Serial.println("ACK: Acquisition started (cyclic mode)");
    Serial.flush();
    
    // Start acquisition
    acquisition_start_time = millis();
    acquisition_active = true;
    serial_blocked = true;  // Block serial during acquisition
    current_state = STATE_ACQUIRING;
    
  } else if (cmd.startsWith("DEBUG_ORDER_ON")) {
    debug_message_order = true;
    Serial.println("ACK: Message order debugging enabled");
    
  } else if (cmd.startsWith("DEBUG_ORDER_OFF")) {
    debug_message_order = false;
    Serial.println("ACK: Message order debugging disabled");
    
  } else if (cmd.startsWith("GET_DATA")) {
    if (acq_sample_count == 0) {
      Serial.println("ERROR: No acquisition data available");
      return;
    }
    
    current_state = STATE_TRANSFERRING;
    
    // Always 4 channels: torque, position, torque_timestamp_us, pos_timestamp_us
    uint8_t num_channels = 4;
    
    // Send data header
    Serial.print("DATA:");
    Serial.print(acq_sample_count);
    Serial.print(",");
    Serial.print(acq_sample_period, 6);
    Serial.print(",");
    Serial.print(num_channels);  // 4 channels: torque, position, torque_timestamp_us, pos_timestamp_us
    Serial.println();
    
    // Send data samples (text format)
    for (uint32_t i = 0; i < acq_sample_count; i++) {
      // 4 channels: torque, position, torque_timestamp_us, pos_timestamp_us
      float *sample_ptr = &acq_buffer[i * 4];
      Serial.print(sample_ptr[0], 6);  // torque_setpoint
      Serial.print(",");
      Serial.print(sample_ptr[1], 9);  // pos_estimate (turns) - higher precision to avoid rounding to 0
      Serial.print(",");
      Serial.print(sample_ptr[2], 1);  // torque_timestamp_us
      Serial.print(",");
      Serial.print(sample_ptr[3], 1);  // pos_timestamp_us
      Serial.println();
      
      // Small delay to prevent serial buffer overflow
      if (i % 100 == 0) delay(1);
    }
    
    Serial.println("DATA_END");
    
    // Send loop timestamps as separate section
    Serial.println("LOOP_TIMESTAMPS:");
    Serial.print(loop_timestamp_count);
    Serial.println();
    for (uint32_t i = 0; i < loop_timestamp_count; i++) {
      Serial.println(loop_timestamps[i]);
      // Small delay to prevent serial buffer overflow
      if (i % 100 == 0) delay(1);
    }
    Serial.println("LOOP_TIMESTAMPS_END");
    
    current_state = STATE_IDLE;
    
  } else if (cmd.startsWith("GET_STATUS")) {
    printStatus();
    
  } else if (cmd.length() > 0) {
    Serial.print("ERROR: Unknown command: ");
    Serial.println(cmd);
  }
}

// ============================================================================
// Status Printing
// ============================================================================

void printStatus() {
  Serial.println("\n========================================");
  Serial.println("Current Status:");
  Serial.println("========================================");
  Serial.print("State: ");
  switch (current_state) {
    case STATE_IDLE: Serial.println("IDLE"); break;
    case STATE_ACQUIRING: Serial.println("ACQUIRING"); break;
    case STATE_TRANSFERRING: Serial.println("TRANSFERRING"); break;
  }
  Serial.print("Acquisition Samples: ");
  Serial.println(acq_sample_count);
  Serial.print("Acquisition Rate: ");
  Serial.print(acquisition_rate_hz);
  Serial.println(" Hz");
  Serial.print("Acquisition Period: ");
  Serial.print(acq_sample_period, 6);
  Serial.println(" s");
  Serial.print("Acquisition: ");
  Serial.println(acquisition_active ? "ACTIVE" : "INACTIVE");
  Serial.print("Serial Blocked: ");
  Serial.println(serial_blocked ? "YES" : "NO");
  Serial.print("ODrive Node ID: ");
  Serial.println(ODRIVE_NODE_ID);
  Serial.println("========================================\n");
}
