/*
 * Controllino Micro ODrive Servo Identification via CAN
 * 
 * Reads torque_setpoint and pos_estimate from ODrive S1 via CAN at 4 kHz
 * and sends data to Python via serial communication.
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
 * - Use START_ACQUISITION,<duration> to start data acquisition
 * - Use GET_DATA to retrieve stored data
 */

#include <CAN.h>

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

// Buffer size: MAX_ACQ_SAMPLES * 2 for dual-channel (Welch mode), MAX_ACQ_SAMPLES for single-channel (cyclic mode)
// Use larger buffer to support both modes
float acq_buffer[MAX_ACQ_SAMPLES * 2];  // 2 channels: torque_setpoint, pos_estimate (or 1 channel: pos_estimate in cyclic mode)
volatile uint32_t acq_sample_count = 0;
volatile uint32_t acq_index = 0;
uint32_t acquisition_rate_hz = 1000;  // Configurable acquisition rate (default 1 kHz)
float acq_sample_period = 1.0f / 1000.0f;  // Will be recalculated when rate changes

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
  Serial.println("  START_ACQUISITION,<duration>,<rate>,cyclic");
  Serial.println("    (always uses cyclic mode at 1000 Hz)");
  Serial.println("  GET_DATA");
  Serial.println("  GET_STATUS");
  Serial.flush();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
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

void processCANMessages() {
  // Process any available CAN messages (non-blocking)
  int packetSize = CAN.parsePacket();
  
  if (packetSize > 0) {
    uint32_t canId = CAN.packetId();
    
    // Check if this is a response from ODrive
    uint32_t baseId = canId & 0x1F;  // Lower 5 bits are the command ID
    uint32_t nodeId = (canId >> 5) & 0x7;  // Bits 5-7 are node ID
    
    if (nodeId == ODRIVE_NODE_ID) {
      if (baseId == CAN_ID_GET_TORQUES) {
        // Parse GET_TORQUES response: (Torque_Target, Torque_Estimate) as two floats
        if (packetSize >= 8) {
          uint8_t data[8];
          for (int i = 0; i < 8 && i < packetSize; i++) {
            data[i] = CAN.read();
          }
          
          // Extract Torque_Target (first float, little-endian)
          float torque_target;
          uint8_t* torqueBytes = (uint8_t*)&torque_target;
          torqueBytes[0] = data[0];
          torqueBytes[1] = data[1];
          torqueBytes[2] = data[2];
          torqueBytes[3] = data[3];
          
          // Store torque data immediately when cyclic message arrives (event-driven)
          if (acquisition_active && acq_index < MAX_ACQ_SAMPLES) {
            // Store torque in first channel
            float *sample_ptr = &acq_buffer[acq_index * 2];
            sample_ptr[0] = torque_target;
            
            // Mark torque as valid for this sample
            latest_torque_setpoint = torque_target;
            torque_data_valid = true;
          }
        }
      } else if (baseId == CAN_ID_GET_ENCODER_ESTIMATES) {
        // Parse GET_ENCODER_ESTIMATES response: (pos_estimate, vel_estimate) as two floats
        if (packetSize >= 8) {
          uint8_t data[8];
          for (int i = 0; i < 8 && i < packetSize; i++) {
            data[i] = CAN.read();
          }
          
          // Extract pos_estimate (first float, little-endian)
          float pos_est;
          uint8_t* posBytes = (uint8_t*)&pos_est;
          posBytes[0] = data[0];
          posBytes[1] = data[1];
          posBytes[2] = data[2];
          posBytes[3] = data[3];
          
          // Store position data immediately when cyclic message arrives (event-driven)
          if (acquisition_active && acq_index < MAX_ACQ_SAMPLES) {
            // Store position in second channel
            float *sample_ptr = &acq_buffer[acq_index * 2];
            sample_ptr[1] = pos_est;
            
            // Mark position as valid for this sample
            latest_pos_estimate = pos_est;
            pos_data_valid = true;
            
            // Both torque and position received - advance index
            // Note: We advance when position arrives since it's the last piece of data for a sample
            // In practice, both messages arrive at 1 kHz, so they should be close together
            acq_index++;
            acq_sample_count = acq_index;
            
            // Check if acquisition duration reached
            if (required_acq_samples > 0 && acq_index >= required_acq_samples) {
              acquisition_active = false;
              serial_blocked = false;  // Unblock serial to send completion message
              current_state = STATE_IDLE;
            } else if (acq_index >= MAX_ACQ_SAMPLES) {
              // Buffer limit reached
              acquisition_active = false;
              serial_blocked = false;
              current_state = STATE_IDLE;
            }
          }
        }
      }
    }
  }
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("START_ACQUISITION")) {
    // Command: START_ACQUISITION,<duration>,<rate>,cyclic
    // Always uses cyclic mode - rate parameter is for compatibility but fixed at 1000 Hz
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
    
    // In cyclic mode, rate is fixed at 1000 Hz (1 ms interval from ODrive)
    acquisition_rate_hz = 1000;
    acq_sample_period = 1.0f / 1000.0f;
    
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
    
    // Send ACK BEFORE starting acquisition and blocking serial
    Serial.println("ACK: Acquisition started (cyclic mode)");
    Serial.flush();
    
    // Start acquisition
    acquisition_start_time = millis();
    acquisition_active = true;
    serial_blocked = true;  // Block serial during acquisition
    current_state = STATE_ACQUIRING;
    
  } else if (cmd.startsWith("GET_DATA")) {
    if (acq_sample_count == 0) {
      Serial.println("ERROR: No acquisition data available");
      return;
    }
    
    current_state = STATE_TRANSFERRING;
    
    // Always 2 channels: torque and position
    uint8_t num_channels = 2;
    
    // Send data header
    Serial.print("DATA:");
    Serial.print(acq_sample_count);
    Serial.print(",");
    Serial.print(acq_sample_period, 6);
    Serial.print(",");
    Serial.print(num_channels);  // Always 2 channels: torque and position
    Serial.println();
    
    // Send data samples (text format)
    for (uint32_t i = 0; i < acq_sample_count; i++) {
      // Always dual channel: torque and position
      float *sample_ptr = &acq_buffer[i * 2];
      Serial.print(sample_ptr[0], 6);  // torque_setpoint
      Serial.print(",");
      Serial.print(sample_ptr[1], 6);  // pos_estimate
      Serial.println();
      
      // Small delay to prevent serial buffer overflow
      if (i % 100 == 0) delay(1);
    }
    
    Serial.println("DATA_END");
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
