/*
 * Controllino Micro ODrive CAN Multisine Control and Data Acquisition
 * 
 * Synchronized torque command transmission via CAN and analog input acquisition.
 * Uses hardware timers for precise timing.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Install Controllino board support in Arduino IDE
 * 2. CAN.h library is included with Controllino board support
 * 3. Connect CAN bus: CANH to CANH, CANL to CANL, common GND
 * 4. Add 120-ohm termination resistors at both ends of CAN bus
 * 5. Configure ODrive S1 node ID (default: 0) to match ODRIVE_NODE_ID constant
 * 6. Connect analog inputs A0-A5 to sensors
 * 
 * USAGE:
 * - Open Serial Monitor at 115200 baud
 * - Upload CSV file with UPLOAD_CSV command
 * - Use START_OUTPUT,<duration> for testing (torque output only)
 * - Use START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay> for full operation
 * 
 * NOTE: Serial communication is blocked during torque output for maximum performance.
 */

#include <CAN.h>

#ifdef ARDUINO_ARCH_RP2040
  #include <hardware/timer.h>
  #include <hardware/irq.h>
  #include <hardware/adc.h>
#endif

// ============================================================================
// Configuration Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_CSV_SAMPLES 2000   // Maximum samples in CSV file (20 KB)
#define MAX_ACQ_SAMPLES 4000   // Maximum acquisition samples (8 channels: 6 inputs + torque + position)
                                // Memory: 2000 × 8 × 4 bytes = 64 KB
                                // Total: CSV (20 KB) + Acquisition (64 KB) = 84 KB (RP2040 has 264KB RAM)
#define ODRIVE_NODE_ID 0
#define CAN_BAUD_RATE 1000000  // 1 Mbps

// ODrive CAN message IDs (CANSimple protocol)
#define CAN_ID_SET_TORQUE 0x0E
#define CAN_ID_SET_AXIS_STATE 0x007

// ODrive Axis States
#define AXIS_STATE_IDLE 1
#define AXIS_STATE_CLOSED_LOOP_CONTROL 8

// ADC pins (Controllino Micro - check pin mapping)
// RP2040 ADC channels: GPIO26-29 are ADC0-3
// Controllino Micro A0-A5 mapping needs to be verified
// For now, assuming A0-A5 map to ADC channels 0-5 (GPIO26-31)
#define ADC_PIN_A0 26
#define ADC_PIN_A1 27
#define ADC_PIN_A2 28
#define ADC_PIN_A3 29
#define ADC_PIN_A4 30  // May need adjustment
#define ADC_PIN_A5 31  // May need adjustment

// ============================================================================
// State Machine
// ============================================================================

enum State {
  STATE_IDLE,
  STATE_OUTPUTTING,
  STATE_ACQUIRING,
  STATE_TRANSFERRING
};

State current_state = STATE_IDLE;

// ============================================================================
// CSV Data Storage
// ============================================================================

float csv_torque_values[MAX_CSV_SAMPLES];
uint32_t csv_sample_count = 0;
float csv_sample_period = 0.001;  // Default 1kHz
uint32_t csv_sample_rate_hz = 1000;

// ============================================================================
// Acquisition Data Storage
// ============================================================================

float acq_buffer[MAX_ACQ_SAMPLES * 8];  // 8 channels: A0-A5, torque_command, position_feedback
uint32_t acq_sample_count = 0;
volatile uint32_t acq_index = 0;
float acq_sample_period = 0.001;

// ============================================================================
// Operation Control
// ============================================================================

volatile bool torque_output_active = false;
volatile bool acquisition_active = false;
volatile bool serial_blocked = false;
bool parsing_csv = false;
bool completion_sent = false;

// Timing control
volatile uint32_t csv_index = 0;  // Current position in CSV for cyclic playback
volatile unsigned long sample_interval_us = 0;
volatile unsigned long last_sample_time_us = 0;

// Acquisition timing
uint32_t required_acq_samples = 0;
unsigned long acquisition_start_time = 0;
unsigned long acquisition_delay_ms = 0;
unsigned long output_start_time = 0;
unsigned long output_duration_ms = 0;

// ============================================================================
// Hardware Timer (RP2040)
// ============================================================================

#ifdef ARDUINO_ARCH_RP2040
  struct repeating_timer timer;
  bool timer_initialized = false;
  
  // ADC configuration
  bool adc_initialized = false;
  uint8_t adc_channels[6] = {ADC_PIN_A0, ADC_PIN_A1, ADC_PIN_A2, ADC_PIN_A3, ADC_PIN_A4, ADC_PIN_A5};
#endif

// ============================================================================
// Function Prototypes
// ============================================================================

void setupCAN();
void setupTimer();
void setupADC();
bool timerCallback(struct repeating_timer *t);
void timerISR();
void sendTorqueSetpoint(float torque);
bool parseCSVFromSerial(uint32_t expected_lines);
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
  Serial.println("Controllino Micro ODrive Control");
  Serial.println("========================================");
  Serial.flush();
  
  // Initialize CAN
  setupCAN();
  
  // Initialize ADC (RP2040)
  #ifdef ARDUINO_ARCH_RP2040
    setupADC();
  #endif
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
  Serial.println();
  Serial.println("Commands:");
  Serial.println("  UPLOAD_CSV,<num_lines>");
  Serial.println("  START_OUTPUT,<duration>");
  Serial.println("  START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>");
  Serial.println("  GET_DATA");
  Serial.println("  GET_STATUS");
  Serial.flush();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Skip reading Serial if parsing CSV
  if (parsing_csv) {
    delay(1);
    return;
  }
  
  // Skip reading Serial if blocked during operation
  if (serial_blocked) {
    // Check if acquisition completed
    if (!acquisition_active && acq_sample_count > 0 && !completion_sent) {
      // Acquisition just completed - send completion message
      // Note: This requires serial to be unblocked, which happens when torque stops
      // For now, we'll send it when serial becomes available again
      completion_sent = true;
    }
    return;
  }
  
  // Check for acquisition completion notification
  if (!completion_sent && acq_sample_count > 0 && !acquisition_active && !torque_output_active) {
    Serial.println("ACK: Acquisition complete");
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
// ADC Setup (RP2040)
// ============================================================================

void setupADC() {
  #ifdef ARDUINO_ARCH_RP2040
    adc_init();
    // Configure ADC pins (will be read in ISR)
    for (int i = 0; i < 6; i++) {
      adc_gpio_init(adc_channels[i]);
    }
    adc_initialized = true;
    Serial.println("ADC initialized (hardware-timed via timer ISR)");
  #endif
}

// ============================================================================
// Timer Setup
// ============================================================================

void setupTimer() {
  if (csv_sample_rate_hz == 0) {
    Serial.println("ERROR: Sample rate not set");
    return;
  }
  
  sample_interval_us = 1000000UL / csv_sample_rate_hz;
  
  #ifdef ARDUINO_ARCH_RP2040
    // Cancel existing timer if running
    if (timer_initialized) {
      cancel_repeating_timer(&timer);
      timer_initialized = false;
    }
    
    // Use RP2040 hardware timer (alarm pool)
    // Negative delay means repeating timer
    int64_t delay_us = -((int64_t)sample_interval_us);
    
    if (add_repeating_timer_us(delay_us, timerCallback, NULL, &timer)) {
      timer_initialized = true;
      Serial.print("Hardware timer initialized: ");
      Serial.print(csv_sample_rate_hz);
      Serial.println(" Hz");
    } else {
      Serial.println("ERROR: Hardware timer initialization failed!");
      timer_initialized = false;
    }
  #else
    Serial.println("WARNING: Hardware timer not available for this board.");
    timer_initialized = false;
  #endif
}

// ============================================================================
// Timer ISR Callback
// ============================================================================

#ifdef ARDUINO_ARCH_RP2040
bool timerCallback(struct repeating_timer *t) {
  timerISR();
  return true;  // Continue repeating
}
#endif

// ============================================================================
// Timer ISR - Main Processing
// ============================================================================

void timerISR() {
  unsigned long current_time_us = micros();
  last_sample_time_us = current_time_us;
  
  float current_torque = 0.0;
  
  // ========================================================================
  // Torque Command Transmission (if active)
  // ========================================================================
  if (torque_output_active && csv_sample_count > 0) {
    // Get torque value from CSV (cyclic playback)
    current_torque = csv_torque_values[csv_index];
    csv_index = (csv_index + 1) % csv_sample_count;
    
    // Send torque command via CAN
    sendTorqueSetpoint(current_torque);
    
    // Check if output duration expired (for START_OUTPUT test mode)
    if (output_duration_ms > 0) {
      unsigned long elapsed = millis() - output_start_time;
      if (elapsed >= output_duration_ms) {
        torque_output_active = false;
        output_duration_ms = 0;
        // Serial will be unblocked when torque stops
      }
    }
  }
  
  // ========================================================================
  // Check if acquisition should start (after delay)
  // ========================================================================
  if (torque_output_active && !acquisition_active && required_acq_samples > 0) {
    unsigned long elapsed = millis() - output_start_time;
    if (elapsed >= acquisition_delay_ms) {
      // Delay has passed - start acquisition
      acquisition_active = true;
      acq_index = 0;
      acq_sample_count = 0;
      current_state = STATE_ACQUIRING;
    }
  }
  
  // ========================================================================
  // Acquisition (if active)
  // ========================================================================
  if (acquisition_active && acq_index < MAX_ACQ_SAMPLES) {
    float *sample_ptr = &acq_buffer[acq_index * 8];
    
    // Read ADC channels (hardware-timed)
    #ifdef ARDUINO_ARCH_RP2040
      // RP2040 has 4 ADC inputs (GPIO26-29), map A0-A5 accordingly
      // For 6 channels, we'll read the available ones and cycle
      for (int ch = 0; ch < 6; ch++) {
        uint8_t gpio_pin = adc_channels[ch];
        if (gpio_pin >= 26 && gpio_pin <= 29) {
          // Valid ADC input (0-3)
          adc_select_input(gpio_pin - 26);
          uint16_t adc_raw = adc_read();
          // Convert to voltage (0-3.3V, 12-bit ADC: 0-4095)
          sample_ptr[ch] = (float)adc_raw * 3.3f / 4095.0f;
        } else {
          // For pins beyond ADC3, use analogRead as fallback
          // Note: This is not hardware-timed, but necessary for A4-A5 if not on ADC0-3
          sample_ptr[ch] = analogRead(gpio_pin) * 3.3f / 4095.0f;
        }
      }
    #else
      // Fallback: use analogRead (not hardware-timed, but works)
      sample_ptr[0] = analogRead(A0) * 3.3f / 4095.0f;
      sample_ptr[1] = analogRead(A1) * 3.3f / 4095.0f;
      sample_ptr[2] = analogRead(A2) * 3.3f / 4095.0f;
      sample_ptr[3] = analogRead(A3) * 3.3f / 4095.0f;
      sample_ptr[4] = analogRead(A4) * 3.3f / 4095.0f;
      sample_ptr[5] = analogRead(A5) * 3.3f / 4095.0f;
    #endif
    
    // Store torque command (current value being sent)
    sample_ptr[6] = current_torque;
    
    // Position feedback (always 0 - not retrieved from ODrive)
    sample_ptr[7] = 0.0f;
    
    acq_index++;
    acq_sample_count = acq_index;
    
    // Check if acquisition duration reached
    if (required_acq_samples > 0 && acq_index >= required_acq_samples) {
      acquisition_active = false;
      torque_output_active = false;  // Stop torque when acquisition completes
      serial_blocked = false;  // Unblock serial
      current_state = STATE_IDLE;
    } else if (acq_index >= MAX_ACQ_SAMPLES) {
      // Buffer limit reached
      acquisition_active = false;
      torque_output_active = false;
      serial_blocked = false;
      current_state = STATE_IDLE;
    }
  }
}

// ============================================================================
// CAN Communication
// ============================================================================

void sendTorqueSetpoint(float torque) {
  // Calculate CAN ID: ODrive uses node_id in bits 5-7
  uint32_t canId = CAN_ID_SET_TORQUE + (ODRIVE_NODE_ID << 5);
  
  // Begin CAN packet
  CAN.beginPacket(canId);
  
  // Write torque (4 bytes, little-endian float)
  uint8_t* torqueBytes = (uint8_t*)&torque;
  CAN.write(torqueBytes[0]);
  CAN.write(torqueBytes[1]);
  CAN.write(torqueBytes[2]);
  CAN.write(torqueBytes[3]);
  
  // Write reserved bytes (4 bytes, set to 0)
  CAN.write(0);
  CAN.write(0);
  CAN.write(0);
  CAN.write(0);
  
  // End packet and send
  CAN.endPacket();
}

// ============================================================================
// CSV Upload Protocol (based on giga-acquisition.ino)
// ============================================================================

bool parseCSVFromSerial(uint32_t expected_lines) {
  csv_sample_count = 0;
  bool sample_period_extracted = false;
  float first_time = -1.0;
  float second_time = -1.0;
  const unsigned long timeout_per_line_ms = 5000;  // 5 seconds max per line
  
  // Read exactly expected_lines lines
  for (uint32_t i = 0; i < expected_lines && csv_sample_count < MAX_CSV_SAMPLES; i++) {
    // Wait for data to be available with timeout
    unsigned long line_start = millis();
    while (Serial.available() == 0) {
      if (millis() - line_start > timeout_per_line_ms) {
        Serial.println("ERROR: Timeout waiting for CSV data");
        return false;
      }
    }
    
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.length() == 0) continue;
    
    // Skip header comment lines (starting with #)
    if (line.startsWith("#")) {
      // Try to extract sample period from metadata header
      // Format: "# fs: 8000.0 Hz" or "# fs: 8000.000000 Hz"
      int fs_pos = line.indexOf("fs:");
      if (fs_pos >= 0) {
        // Extract everything after "fs:"
        int fs_start = fs_pos + 3;  // Position after "fs:"
        String fs_str = line.substring(fs_start);
        fs_str.trim();
        
        // Find "Hz" (case-insensitive search)
        String fs_str_lower = fs_str;
        fs_str_lower.toLowerCase();
        int hz_pos = fs_str_lower.indexOf("hz");
        if (hz_pos > 0) {
          // Extract the number part from original string
          fs_str = fs_str.substring(0, hz_pos);
          fs_str.trim();
          float fs = fs_str.toFloat();
          if (fs > 0 && fs < 1000000) {
            csv_sample_period = 1.0 / fs;
            csv_sample_rate_hz = (uint32_t)(fs + 0.5f);  // Round to nearest integer
            sample_period_extracted = true;
            Serial.print("INFO: Extracted sample rate from header: ");
            Serial.print(csv_sample_rate_hz);
            Serial.println(" Hz");
          }
        }
      }
      continue;
    }
    
    // Skip CSV header row
    if (line.equalsIgnoreCase("Time_s,Signal") || line.equalsIgnoreCase("Time_s,Torque")) {
      continue;
    }
    
    // Parse data rows (comma-separated: time, torque)
    int comma_pos = line.indexOf(',');
    if (comma_pos > 0) {
      String time_str = line.substring(0, comma_pos);
      String torque_str = line.substring(comma_pos + 1);
      time_str.trim();
      torque_str.trim();
      
      float time_val = time_str.toFloat();
      float torque = torque_str.toFloat();
      
      // Validate parsed values
      if (isnan(time_val) || isnan(torque) || isinf(time_val) || isinf(torque)) {
        continue;
      }
      
      // Store first two time values to calculate sample period if not extracted
      if (first_time < 0 && time_val >= 0) {
        first_time = time_val;
      } else if (second_time < 0 && !sample_period_extracted && time_val > first_time) {
        second_time = time_val;
        if (second_time > first_time && second_time - first_time < 10.0) {
          csv_sample_period = second_time - first_time;
          float calculated_rate = 1.0 / csv_sample_period;
          csv_sample_rate_hz = (uint32_t)(calculated_rate + 0.5f);  // Round to nearest integer
          sample_period_extracted = true;
        }
      }
      
      // Store torque value (no range validation - torque can be positive or negative)
      csv_torque_values[csv_sample_count++] = torque;
    } else {
      // Fallback: try to parse as single value
      float torque = line.toFloat();
      if (!isnan(torque) && !isinf(torque)) {
        csv_torque_values[csv_sample_count++] = torque;
        if (!sample_period_extracted && csv_sample_count == 2) {
          csv_sample_period = 0.001;  // Default 1kHz
          csv_sample_rate_hz = 1000;
          sample_period_extracted = true;
        }
      }
    }
  }
  
  // Validate sample period - use fallback if extraction failed
  if (!sample_period_extracted) {
    if (csv_sample_count > 0) {
      csv_sample_period = 0.001;  // Default 1kHz
      csv_sample_rate_hz = 1000;
      Serial.println("WARNING: Could not extract sample period, using default 0.001s (1kHz)");
    } else {
      Serial.println("ERROR: Could not extract sample period from CSV and no samples loaded");
      return false;
    }
  }
  
  if (csv_sample_period <= 0 || csv_sample_period > 1.0) {
    Serial.println("ERROR: Invalid sample period");
    return false;
  }
  
  if (csv_sample_count == 0) {
    Serial.println("ERROR: No torque samples loaded");
    return false;
  }
  
  Serial.print("INFO: Loaded ");
  Serial.print(csv_sample_count);
  Serial.print(" samples, period: ");
  Serial.print(csv_sample_period, 6);
  Serial.print("s (");
  Serial.print(csv_sample_rate_hz);
  Serial.println(" Hz)");
  
  // Initialize timer with CSV sample rate
  setupTimer();
  
  return true;
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("UPLOAD_CSV")) {
    // Parse line count from command: UPLOAD_CSV,<num_lines>
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing line count in UPLOAD_CSV command");
      return;
    }
    
    uint32_t expected_lines = cmd.substring(comma_pos + 1).toInt();
    if (expected_lines == 0 || expected_lines > MAX_CSV_SAMPLES) {
      Serial.println("ERROR: Invalid line count");
      return;
    }
    
    parsing_csv = true;  // Set flag immediately to prevent loop() from reading
    
    // Clear any stale data from serial buffer BEFORE sending READY
    while (Serial.available() > 0) {
      Serial.read();
    }
    Serial.println("READY");
    Serial.flush();
    
    if (parseCSVFromSerial(expected_lines)) {
      Serial.println("ACK: CSV loaded");
    } else {
      Serial.println("NACK: CSV load failed");
    }
    
    // Clear any leftover data from serial buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
    parsing_csv = false;  // Clear flag when done
    
  } else if (cmd.startsWith("START_OUTPUT")) {
    // Testing command: START_OUTPUT,<duration>
    if (csv_sample_count == 0) {
      Serial.println("ERROR: No CSV file loaded");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing duration in START_OUTPUT command");
      return;
    }
    
    float duration = cmd.substring(comma_pos + 1).toFloat();
    if (duration <= 0) {
      Serial.println("ERROR: Invalid duration");
      return;
    }
    
    output_duration_ms = (unsigned long)(duration * 1000.0f);
    output_start_time = millis();
    csv_index = 0;
    torque_output_active = true;
    serial_blocked = true;  // Block serial during output
    current_state = STATE_OUTPUTTING;
    
    Serial.println("ACK: Output started");
    Serial.flush();
    
  } else if (cmd.startsWith("START_IDENTIFICATION")) {
    // Main command: START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>
    if (csv_sample_count == 0) {
      Serial.println("ERROR: No CSV file loaded");
      return;
    }
    
    int comma1 = cmd.indexOf(',');
    int comma2 = cmd.indexOf(',', comma1 + 1);
    
    if (comma1 < 0 || comma2 < 0) {
      Serial.println("ERROR: Missing parameters in START_IDENTIFICATION command");
      return;
    }
    
    float acq_duration = cmd.substring(comma1 + 1, comma2).toFloat();
    float acq_delay = cmd.substring(comma2 + 1).toFloat();
    
    if (acq_duration <= 0 || acq_delay < 0) {
      Serial.println("ERROR: Invalid parameters");
      return;
    }
    
    // Calculate required samples
    required_acq_samples = (uint32_t)(acq_duration / csv_sample_period);
    if (required_acq_samples > MAX_ACQ_SAMPLES) {
      Serial.print("ERROR: Acquisition duration too long. Maximum: ");
      Serial.print((float)MAX_ACQ_SAMPLES * csv_sample_period);
      Serial.println(" seconds");
      return;
    }
    
    // Reset acquisition state
    acq_index = 0;
    acq_sample_count = 0;
    acq_sample_period = csv_sample_period;
    completion_sent = false;
    
    // Start torque output immediately
    csv_index = 0;
    output_start_time = millis();
    acquisition_delay_ms = (unsigned long)(acq_delay * 1000.0f);
    acquisition_start_time = output_start_time + acquisition_delay_ms;
    
    torque_output_active = true;
    acquisition_active = false;  // Will be activated after delay
    serial_blocked = true;  // Block serial during operation
    current_state = STATE_OUTPUTTING;
    
    Serial.println("ACK: Identification started");
    Serial.flush();
    
  } else if (cmd.startsWith("GET_DATA")) {
    if (acq_sample_count == 0) {
      Serial.println("ERROR: No acquisition data available");
      return;
    }
    
    current_state = STATE_TRANSFERRING;
    
    // Send data header
    Serial.print("DATA:");
    Serial.print(acq_sample_count);
    Serial.print(",");
    Serial.print(acq_sample_period, 6);
    Serial.print(",");
    Serial.print(8);  // 8 channels: A0-A5, torque_command, position_feedback
    Serial.println();
    
    // Send data samples (text format)
    for (uint32_t i = 0; i < acq_sample_count; i++) {
      float *sample_ptr = &acq_buffer[i * 8];
      
      Serial.print(sample_ptr[0], 4);  // A0
      for (int ch = 1; ch < 8; ch++) {  // A1-A5, torque_command, position_feedback
        Serial.print(",");
        Serial.print(sample_ptr[ch], 4);
      }
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
    case STATE_OUTPUTTING: Serial.println("OUTPUTTING"); break;
    case STATE_ACQUIRING: Serial.println("ACQUIRING"); break;
    case STATE_TRANSFERRING: Serial.println("TRANSFERRING"); break;
  }
  Serial.print("CSV Samples: ");
  Serial.println(csv_sample_count);
  Serial.print("CSV Sample Rate: ");
  Serial.print(csv_sample_rate_hz);
  Serial.println(" Hz");
  Serial.print("CSV Sample Period: ");
  Serial.print(csv_sample_period, 6);
  Serial.println(" s");
  Serial.print("Acquisition Samples: ");
  Serial.println(acq_sample_count);
  Serial.print("Torque Output: ");
  Serial.println(torque_output_active ? "ACTIVE" : "INACTIVE");
  Serial.print("Acquisition: ");
  Serial.println(acquisition_active ? "ACTIVE" : "INACTIVE");
  Serial.print("Serial Blocked: ");
  Serial.println(serial_blocked ? "YES" : "NO");
  Serial.print("ODrive Node ID: ");
  Serial.println(ODRIVE_NODE_ID);
  Serial.println("========================================\n");
}

