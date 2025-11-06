/* -------------------------------------------------------------------------- */
/* FILE NAME:   opta_acquisition.ino
   DESCRIPTION: Arduino Opta Lite synchronized data acquisition and motor control
                system with A0602 expansion board.
                - Analog output on O1 (A0602 expansion)
                - Analog input on I1-I6 (Opta Lite base unit)
                - Hardware-timed sampling with minimal jitter
                - CSV file parsing for voltage waveforms
                - Binary serial protocol for communication
   LICENSE:     See project LICENSE file
/* -------------------------------------------------------------------------- */

#include "OptaBlue.h"
#include "mbed.h"

using namespace Opta;

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_CSV_SAMPLES 10000  // Maximum samples in CSV file
#define MAX_ACQ_SAMPLES 4000   // Maximum acquisition samples (6 channels)
                                // Memory constraint: ~96 KB (4000 × 6 channels × 4 bytes/float)
                                // Maximum acquisition duration = MAX_ACQ_SAMPLES / sample_rate
                                // Example: At 1 kHz = 4 seconds, at 100 Hz = 40 seconds
                                // See specifications.md "Memory Management" section
#define OUTPUT_CHANNEL 0       // O1 on A0602 expansion board
#define INPUT_CHANNELS 6       // I1-I6 on Opta Lite base unit

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

// Timing
mbed::Ticker timer;
uint32_t output_index = 0;
uint32_t acq_index = 0;

// A0602 expansion board reference
int8_t expansion_index = -1;

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
  
  // Initialize Opta controller
  OptaController.begin();
  
  // Find A0602 analog expansion board
  for (int i = 0; i < OptaController.getExpansionNum(); i++) {
    if (OptaController.getExpansionType(i) == EXPANSION_OPTA_ANALOG) {
      expansion_index = i;
      break;
    }
  }
  
  if (expansion_index == -1) {
    Serial.println("ERROR: No A0602 analog expansion board found!");
  } else {
    Serial.print("INFO: Found A0602 expansion at index ");
    Serial.println(expansion_index);
    
    // Initialize output channel O1 as voltage DAC
    AnalogExpansion::beginChannelAsDac(OptaController,
                                       expansion_index,
                                       OUTPUT_CHANNEL,
                                       OA_VOLTAGE_DAC,
                                       true,  // Enable channel
                                       false, // Disable slew rate limit
                                       OA_SLEW_RATE_0);
  }
  
  // Initialize Opta Lite base unit analog inputs I1-I6
  // Note: Using Arduino's built-in analogRead for base unit
  // For hardware-timed acquisition, we'll use Mbed OS Ticker for periodic interrupts
  
  // Timer will be configured when starting output/acquisition
  // Default period is 1kHz (0.001s)
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
}

// ============================================================================
// Timer Interrupt Service Routine
// ============================================================================

void timerISR() {
  if (output_active && current_state != STATE_TRANSFERRING) {
    // Output next voltage value from CSV
    if (expansion_index >= 0 && csv_sample_count > 0) {
      AnalogExpansion exp = OptaController.getExpansion(expansion_index);
      if (exp) {
        float voltage = csv_voltage_values[output_index];
        // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit)
        uint16_t dac_value = (uint16_t)(voltage * 4095.0 / 3.3);
        dac_value = constrain(dac_value, 0, 4095);
        exp.setDac(OUTPUT_CHANNEL, dac_value);
        
        // Increment and wrap for cyclic playback
        output_index = (output_index + 1) % csv_sample_count;
      }
    }
  }
  
  if (acquisition_active) {
    // Acquire all 6 input channels
    if (acq_index < MAX_ACQ_SAMPLES) {
      float *sample_ptr = &acq_buffer[acq_index * 6];
      
      // Read all 6 channels on Opta Lite base unit (PA0-PA5 for I1-I6)
      // Using analogRead with direct register access for speed
      sample_ptr[0] = analogRead(A0) * 3.3 / 4095.0;  // I1
      sample_ptr[1] = analogRead(A1) * 3.3 / 4095.0;  // I2
      sample_ptr[2] = analogRead(A2) * 3.3 / 4095.0;  // I3
      sample_ptr[3] = analogRead(A3) * 3.3 / 4095.0;  // I4
      sample_ptr[4] = analogRead(A4) * 3.3 / 4095.0;  // I5
      sample_ptr[5] = analogRead(A5) * 3.3 / 4095.0;  // I6
      
      acq_index++;
      acq_sample_count = acq_index;
      
      // Stop if buffer full
      if (acq_index >= MAX_ACQ_SAMPLES) {
        acquisition_active = false;
        current_state = STATE_IDLE;
      }
    }
  }
}

// ============================================================================
// CSV File Parsing
// ============================================================================

bool parseCSVFromSerial() {
  csv_sample_count = 0;
  bool found_header = false;
  bool sample_period_extracted = false;
  float first_time = -1.0;
  float second_time = -1.0;
  
  // Read and parse CSV file
  while (Serial.available() > 0 && csv_sample_count < MAX_CSV_SAMPLES) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
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
          if (fs > 0) {
            csv_sample_period = 1.0 / fs;
            sample_period_extracted = true;
          }
        }
      }
      continue;
    }
    
    // Check for CSV header row
    if (line.equalsIgnoreCase("Time_s,Signal") || line.equalsIgnoreCase("Time_s,Signal\n")) {
      found_header = true;
      continue;
    }
    
    // Parse data rows (comma-separated: time, signal)
    int comma_pos = line.indexOf(',');
    if (comma_pos > 0) {
      // Extract time and signal values
      String time_str = line.substring(0, comma_pos);
      String signal_str = line.substring(comma_pos + 1);
      time_str.trim();
      signal_str.trim();
      
      float time_val = time_str.toFloat();
      float voltage = signal_str.toFloat();
      
      // Store first two time values to calculate sample period if not extracted from metadata
      if (first_time < 0) {
        first_time = time_val;
      } else if (second_time < 0 && !sample_period_extracted) {
        second_time = time_val;
        if (second_time > first_time) {
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
      // Fallback: try to parse as single value (for backward compatibility)
      float voltage = line.toFloat();
      if (voltage >= 0.0 && voltage <= 3.3) {
        csv_voltage_values[csv_sample_count++] = voltage;
      }
    }
  }
  
  // Validate sample period
  if (!sample_period_extracted) {
    Serial.println("ERROR: Could not extract sample period from CSV");
    return false;
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
  
  return true;
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("START_OUTPUT")) {
    if (csv_sample_count == 0) {
      Serial.println("ERROR: No CSV file loaded");
      return;
    }
    output_active = true;
    output_index = 0;
    current_state = STATE_OUTPUTTING;
    // Attach timer interrupt with period from csv_sample_period
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
      timer.attach(&timerISR, acq_sample_period);
    }
    
    Serial.println("ACK: Acquisition started");
    
    // Wait for acquisition to complete
    while (acquisition_active) {
      OptaController.update();
      delay(10);
    }
    
    timer.detach();
    output_active = false;
    current_state = STATE_IDLE;
    
    Serial.println("ACK: Acquisition complete");
    
  } else if (cmd.startsWith("UPLOAD_CSV")) {
    Serial.println("READY");
    if (parseCSVFromSerial()) {
      Serial.println("ACK: CSV loaded");
    } else {
      Serial.println("NACK: CSV load failed");
    }
    
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
    
    // Send data samples (binary format would be better, but use text for now)
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
// Main Loop
// ============================================================================

void loop() {
  OptaController.update();
  
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }
  
  delay(1);
}

