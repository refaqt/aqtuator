/* -------------------------------------------------------------------------- */
/* FILE NAME:   giga-acquisition.ino
   DESCRIPTION: Arduino Giga R1 WiFi synchronized data acquisition and motor control
                system.
                - Analog output on DAC0 (built-in DAC)
                - Analog input on A0-A5 (built-in ADC, 6 channels)
                - Hardware-timed sampling with minimal jitter
                - CSV file parsing for voltage waveforms
                - Text-based serial protocol for communication
   LICENSE:     See project LICENSE file
/* -------------------------------------------------------------------------- */

#include "mbed.h"

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_CSV_SAMPLES 10000  // Maximum samples in CSV file
#define MAX_ACQ_SAMPLES 10000  // Maximum acquisition samples (6 channels)
                                // Memory constraint: ~480 KB (20000 × 6 channels × 4 bytes/float)
                                // Maximum acquisition duration = MAX_ACQ_SAMPLES / sample_rate
                                // Example: At 1 kHz = 20 seconds, at 10 kHz = 2 seconds
                                // See specifications_giga.md "Memory Management" section
#define DAC0_PIN A0            // DAC0 on Arduino Giga R1 WiFi (physical pin A0)
#define INPUT_CHANNELS 6       // A0-A5 on Arduino Giga R1 WiFi

// Hardware timer configuration using Mbed OS Ticker
// Mbed Ticker provides hardware timer interrupts for precise timing on Giga R1 WiFi
mbed::Ticker timer;

// Memory buffers
float csv_voltage_values[MAX_CSV_SAMPLES];
uint32_t csv_sample_count = 0;
float csv_sample_period = 0.001;  // Default 1kHz

// Acquisition buffers (6 channels)
float acq_buffer[MAX_ACQ_SAMPLES * 6];
uint32_t acq_sample_count = 0;
float acq_sample_period = 0.001;
bool acquisition_active = false;
bool output_active = false;
bool parsing_csv = false;  // Flag to prevent loop() from processing commands during CSV upload

// Timing
uint32_t output_index = 0;
uint32_t acq_index = 0;

// Pending tick counters for producer-consumer pattern
volatile uint32_t pending_output_ticks = 0;
volatile uint32_t pending_acq_ticks = 0;

// ============================================================================
// Serial Protocol Definitions
// ============================================================================

enum CommandType {
  CMD_NONE,
  CMD_START_OUTPUT,
  CMD_STOP_OUTPUT,
  CMD_START_ACQUISITION,
  CMD_STOP_ACQUISITION,
  CMD_UPLOAD_CSV,
  CMD_GET_STATUS,
  CMD_GET_DATA
};

enum State {
  STATE_IDLE,
  STATE_OUTPUTTING,
  STATE_ACQUIRING,
  STATE_TRANSFERRING
};

State current_state = STATE_IDLE;

// ============================================================================
// Setup Function
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(2000);
  
  // Initialize DAC0 for analog output
  // On Arduino Giga R1 WiFi, DAC0 is available as a separate DAC pin
  // Note: Check actual pin mapping for your board - DAC0 may be on A0 or a dedicated DAC pin
  // analogWrite() will automatically use DAC when writing to DAC0 pin
  pinMode(DAC0_PIN, OUTPUT);
  
  // Initialize analog input pins A0-A5 for ADC
  // These are the six analog input channels (logical channels A0-A5)
  // Note: If DAC0 conflicts with A0, adjust pin assignments accordingly
  
  // Timer will be configured when starting output/acquisition
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
}

// ============================================================================
// Timer Interrupt Service Routine
// ============================================================================

void timerISR() {
  // Minimal ISR - just increment counters (takes ~1µs)
  if (output_active && current_state != STATE_TRANSFERRING) {
    pending_output_ticks++;
  }
  
  if (acquisition_active) {
    pending_acq_ticks++;
  }
}

// ============================================================================
// CSV File Parsing
// ============================================================================

bool parseCSVFromSerial(uint32_t expected_lines) {
  Serial.print("DEBUG: parseCSVFromSerial() entered, expected_lines=");
  Serial.println(expected_lines);
  Serial.print("DEBUG: Serial.available()=");
  Serial.println(Serial.available());
  
  csv_sample_count = 0;
  bool sample_period_extracted = false;
  float first_time = -1.0;
  float second_time = -1.0;
  unsigned long start_time = millis();
  const unsigned long timeout_per_line_ms = 5000;  // 5 seconds max per line
  uint32_t lines_read = 0;  // Track lines read from serial for batch acknowledgment
  
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
    
    lines_read++;  // Increment counter for each line read from serial
    
    // No chunk acknowledgments - simple line reading (matches test_serial.py approach)
    
    if (line.length() == 0) continue;
    
    // Skip header comment lines (starting with #)
    if (line.startsWith("#")) {
      // Try to extract sample period from metadata header
      // Format: "# fs: 5000.0 Hz"
      if (line.indexOf("fs:") >= 0) {
        int fs_start = line.indexOf("fs:") + 3;
        String fs_str = line.substring(fs_start);
        fs_str.trim();
        int hz_pos = fs_str.indexOf("Hz");
        if (hz_pos > 0) {
          fs_str = fs_str.substring(0, hz_pos);
          fs_str.trim();
          float fs = fs_str.toFloat();
          if (fs > 0 && fs < 1000000) {
            csv_sample_period = 1.0 / fs;
            sample_period_extracted = true;
          }
        }
      }
      continue;
    }
    
    // Skip CSV header row
    if (line.equalsIgnoreCase("Time_s,Signal")) {
      continue;
    }
    
    // Parse data rows (comma-separated: time, signal)
    int comma_pos = line.indexOf(',');
    if (comma_pos > 0) {
      String time_str = line.substring(0, comma_pos);
      String signal_str = line.substring(comma_pos + 1);
      time_str.trim();
      signal_str.trim();
      
      float time_val = time_str.toFloat();
      float voltage = signal_str.toFloat();
      
      // Validate parsed values
      if (isnan(time_val) || isnan(voltage) || isinf(time_val) || isinf(voltage)) {
        continue;
      }
      
      // Store first two time values to calculate sample period if not extracted
      if (first_time < 0 && time_val >= 0) {
        first_time = time_val;
      } else if (second_time < 0 && !sample_period_extracted && time_val > first_time) {
        second_time = time_val;
        if (second_time > first_time && second_time - first_time < 10.0) {
          csv_sample_period = second_time - first_time;
          sample_period_extracted = true;
        }
      }
      
      // Validate voltage range
      if (voltage < 0.0 || voltage > 3.3) {
        Serial.print("ERROR: Voltage out of range: ");
        Serial.println(voltage);
        return false;
      }
      
      csv_voltage_values[csv_sample_count++] = voltage;
    } else {
      // Fallback: try to parse as single value
      float voltage = line.toFloat();
      if (!isnan(voltage) && !isinf(voltage) && voltage >= 0.0 && voltage <= 3.3) {
        csv_voltage_values[csv_sample_count++] = voltage;
        if (!sample_period_extracted && csv_sample_count == 2) {
          csv_sample_period = 0.001;  // Default 1kHz
          sample_period_extracted = true;
        }
      }
    }
  }
  
  // Validate sample period - use fallback if extraction failed
  if (!sample_period_extracted) {
    if (csv_sample_count > 0) {
      csv_sample_period = 0.001;  // Default 1kHz
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
    Serial.println("ERROR: No voltage samples loaded");
    return false;
  }
  
  Serial.print("INFO: Loaded ");
  Serial.print(csv_sample_count);
  Serial.print(" samples, period: ");
  Serial.print(csv_sample_period, 6);
  Serial.println("s");
  
  Serial.println("DEBUG: parseCSVFromSerial() completed successfully");
  return true;
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  Serial.print("DEBUG: processCommand() - cmd='");
  Serial.print(cmd);
  Serial.print("', parsing_csv=");
  Serial.println(parsing_csv);
  
  if (cmd.startsWith("START_OUTPUT")) {
    if (csv_sample_count == 0) {
      Serial.println("ERROR: No CSV file loaded");
      return;
    }
    output_active = true;
    output_index = 0;
    current_state = STATE_OUTPUTTING;
    // Attach timer interrupt with period from csv_sample_period
    // Mbed Ticker uses period in seconds (float)
    timer.attach(&timerISR, csv_sample_period);
    Serial.println("ACK: Output started");
    
  } else if (cmd.startsWith("STOP_OUTPUT")) {
    output_active = false;
    if (!acquisition_active) {
      // Only detach timer if acquisition is also not active
      timer.detach();
      current_state = STATE_IDLE;
    } else {
      current_state = STATE_ACQUIRING;
    }
    Serial.println("ACK: Output stopped");
    
  } else if (cmd.startsWith("START_ACQUISITION")) {
    // Parse acquisition parameters
    // Format: START_ACQUISITION,duration,start_delay
    int comma1 = cmd.indexOf(',');
    int comma2 = cmd.indexOf(',', comma1 + 1);
    
    float duration = cmd.substring(comma1 + 1, comma2).toFloat();
    float start_delay = cmd.substring(comma2 + 1).toFloat();
    
    acq_sample_period = csv_sample_period;  // Match output timing
    
    if (duration <= 0) {
      Serial.println("ERROR: Invalid acquisition duration");
      return;
    }
    
    // Calculate number of samples needed
    uint32_t required_samples = (uint32_t)(duration / acq_sample_period);
    if (required_samples > MAX_ACQ_SAMPLES) {
      Serial.print("ERROR: Acquisition duration too long. Maximum: ");
      Serial.print((float)MAX_ACQ_SAMPLES * acq_sample_period);
      Serial.println(" seconds");
      return;
    }
    
    // Delay before starting
    delay((uint32_t)(start_delay * 1000));
    
    // Start acquisition
    acq_index = 0;
    acq_sample_count = 0;
    acquisition_active = true;
    
    if (output_active) {
      current_state = STATE_ACQUIRING;
    } else {
      // Start output at the same time
      output_active = true;
      output_index = 0;
      current_state = STATE_ACQUIRING;
      // Attach timer interrupt with period from csv_sample_period
      // Mbed Ticker uses period in seconds (float)
      timer.attach(&timerISR, acq_sample_period);
    }
    
    Serial.println("ACK: Acquisition started");
    
    // Wait for acquisition to complete
    while (acquisition_active) {
      delay(10);
    }
    
    timer.detach();
    output_active = false;
    current_state = STATE_IDLE;
    
    Serial.println("ACK: Acquisition complete");
    
  } else if (cmd.startsWith("UPLOAD_CSV")) {
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
    // This ensures no CSV lines are in the buffer when Python starts sending
    int cleared = 0;
    while (Serial.available() > 0) {
      Serial.read();
      cleared++;
    }
    if (cleared > 0) {
      Serial.print("DEBUG: Cleared ");
      Serial.print(cleared);
      Serial.println(" bytes from buffer");
    }
    
    Serial.print("DEBUG: parsing_csv set to true, Serial.available()=");
    Serial.println(Serial.available());
    Serial.println("READY");
    
    if (parseCSVFromSerial(expected_lines)) {
      Serial.println("ACK: CSV loaded");
    } else {
      Serial.println("NACK: CSV load failed");
    }
    
    // Clear any leftover data from serial buffer before setting parsing_csv = false
    // This prevents leftover CSV lines from being processed as commands
    int leftover_cleared = 0;
    while (Serial.available() > 0) {
      Serial.read();
      leftover_cleared++;
    }
    if (leftover_cleared > 0) {
      Serial.print("DEBUG: Cleared ");
      Serial.print(leftover_cleared);
      Serial.println(" leftover bytes from buffer after CSV parsing");
    }
    
    parsing_csv = false;  // Clear flag when done
    Serial.println("DEBUG: parsing_csv set to false");
    
  } else if (cmd.startsWith("RESET")) {
    // Reset parsing state and clear buffers
    Serial.println("DEBUG: RESET command received");
    parsing_csv = false;
    Serial.println("DEBUG: parsing_csv set to false");
    int cleared = 0;
    while (Serial.available() > 0) {
      Serial.read();
      cleared++;
    }
    Serial.print("DEBUG: Cleared ");
    Serial.print(cleared);
    Serial.println(" bytes from buffer");
    Serial.println("ACK: Reset complete");
    
  } else if (cmd.startsWith("DEBUG")) {
    // Debug command - dump current state
    Serial.println("DEBUG: === State Dump ===");
    Serial.print("DEBUG: parsing_csv = ");
    Serial.println(parsing_csv);
    Serial.print("DEBUG: Serial.available() = ");
    Serial.println(Serial.available());
    Serial.print("DEBUG: csv_sample_count = ");
    Serial.println(csv_sample_count);
    Serial.print("DEBUG: output_active = ");
    Serial.println(output_active);
    Serial.print("DEBUG: acquisition_active = ");
    Serial.println(acquisition_active);
    Serial.print("DEBUG: current_state = ");
    Serial.println(current_state);
    Serial.print("DEBUG: csv_sample_period = ");
    Serial.println(csv_sample_period, 6);
    Serial.println("DEBUG: === End State Dump ===");
    
  } else if (cmd.startsWith("GET_STATUS")) {
    Serial.print("STATUS:");
    Serial.print(current_state);
    Serial.print(",");
    Serial.print(output_active);
    Serial.print(",");
    Serial.print(acquisition_active);
    Serial.print(",");
    Serial.print(csv_sample_count);
    Serial.print(",");
    Serial.println(csv_sample_period, 6);
    
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
    Serial.print(INPUT_CHANNELS);
    Serial.println();
    
    // Send data samples (text format)
    for (uint32_t i = 0; i < acq_sample_count; i++) {
      float *sample_ptr = &acq_buffer[i * 6];
      
      Serial.print(sample_ptr[0], 4);
      for (int ch = 1; ch < 6; ch++) {
        Serial.print(",");
        Serial.print(sample_ptr[ch], 4);
      }
      Serial.println();
      
      // Small delay to prevent serial buffer overflow
      if (i % 100 == 0) delay(1);
    }
    
    Serial.println("DATA_END");
    current_state = STATE_IDLE;
    
  } else {
    Serial.print("ERROR: Unknown command: ");
    Serial.println(cmd);
  }
}

// ============================================================================
// Helper Functions for Processing Frames
// ============================================================================

// Process one output frame (called from loop())
static inline void processOneOutputFrame() {
  if (csv_sample_count > 0) {
    float voltage = csv_voltage_values[output_index];
    // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit DAC)
    // On Arduino Giga R1 WiFi, analogWrite() with DAC0 accepts 0-4095 for 12-bit resolution
    uint16_t dac_value = (uint16_t)(voltage * 4095.0 / 3.3);
    dac_value = constrain(dac_value, 0, 4095);
    analogWrite(DAC0_PIN, dac_value);
    output_index = (output_index + 1) % csv_sample_count;
  }
}

// Process one acquisition frame (called from loop())
static inline void processOneAcqFrame() {
  if (acq_index < MAX_ACQ_SAMPLES) {
    float *sample_ptr = &acq_buffer[acq_index * 6];
    // Read analog inputs A0-A5 (logical channels A0-A5)
    // Note: On Giga R1 WiFi, ADC resolution is 12-bit (0-4095)
    sample_ptr[0] = analogRead(A0) * 3.3 / 4095.0;  // A0
    sample_ptr[1] = analogRead(A1) * 3.3 / 4095.0;  // A1
    sample_ptr[2] = analogRead(A2) * 3.3 / 4095.0;  // A2
    sample_ptr[3] = analogRead(A3) * 3.3 / 4095.0;  // A3
    sample_ptr[4] = analogRead(A4) * 3.3 / 4095.0;  // A4
    sample_ptr[5] = analogRead(A5) * 3.3 / 4095.0;  // A5
    acq_index++;
    acq_sample_count = acq_index;
    
    if (acq_index >= MAX_ACQ_SAMPLES) {
      acquisition_active = false;
      current_state = STATE_IDLE;
    }
  }
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Process pending output ticks (drain from ISR using atomic operations)
  uint32_t output_n;
  noInterrupts();
  output_n = pending_output_ticks;
  pending_output_ticks = 0;
  interrupts();
  
  while (output_n-- > 0) {
    if (output_active && current_state != STATE_TRANSFERRING) {
      processOneOutputFrame();
    }
  }
  
  // Process pending acquisition ticks
  uint32_t acq_n;
  noInterrupts();
  acq_n = pending_acq_ticks;
  pending_acq_ticks = 0;
  interrupts();
  
  while (acq_n-- > 0) {
    if (acquisition_active) {
      processOneAcqFrame();
    }
  }
  
  // Skip reading Serial if parsing CSV to avoid race condition
  if (parsing_csv) {
    static unsigned long last_debug = 0;
    if (millis() - last_debug > 1000) {  // Print every second when stuck
      Serial.print("DEBUG: loop() - parsing_csv=true, Serial.available()=");
      Serial.println(Serial.available());
      last_debug = millis();
    }
    delay(1);
    return;
  }
  
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    Serial.print("DEBUG: Received command: ");
    Serial.println(cmd);
    processCommand(cmd);
  }
  
  delay(1);
}

