/* -------------------------------------------------------------------------- */
/* FILE NAME:   giga-acquisition.ino
   DESCRIPTION: Arduino Giga R1 WiFi synchronized data acquisition and motor control
                system.
                - Analog output on DAC0 using AdvancedAnalog library (hardware-timed DMA)
                - Analog input on A0-A5 using AdvancedAnalog library (hardware-timed DMA, 6 channels)
                - Multi-channel ADC configuration: A0-A2 on ADC1 (3 channels), A3-A5 on ADC2 (3 channels)
                - Hardware-timed sampling with minimal jitter via DMA
                - CSV file parsing for voltage waveforms
                - Text-based serial protocol for communication
   LICENSE:     See project LICENSE file
   NOTE:        Uses Arduino_AdvancedAnalog library for reliable high-speed operation
                Multi-channel ADC uses 2 AdvancedADC instances (ADC1 and ADC2, 3 channels each)
                Reference: https://github.com/arduino-libraries/Arduino_AdvancedAnalog/blob/main/docs/api.md
/* -------------------------------------------------------------------------- */

#include <Arduino_AdvancedAnalog.h>

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_CSV_SAMPLES 10000  // Maximum samples in CSV file
#define MAX_ACQ_SAMPLES 10000  // Maximum acquisition samples (7 channels: 6 inputs + 1 output voltage)
                                // Memory constraint: ~560 KB (10000 × 7 channels × 4 bytes/float = 280 KB)
                                // Maximum acquisition duration = MAX_ACQ_SAMPLES / sample_rate
                                // Example: At 1 kHz = 10 seconds, at 10 kHz = 1 second
                                // See specifications_giga.md "Memory Management" section
#define DAC0_PIN A12          // DAC0 on Arduino Giga R1 WiFi (A12 is DAC0 channel)
#define INPUT_CHANNELS 6       // A0-A5 on Arduino Giga R1 WiFi

// AdvancedAnalog library configuration
#define ADC_BUFFER_SIZE 32     // DMA buffer size for ADC
#define ADC_QUEUE_SIZE 32      // Queue size for ADC
#define DAC_BUFFER_SIZE 32     // DMA buffer size for DAC
#define DAC_QUEUE_SIZE 32      // Queue size for DAC

// AdvancedAnalog ADC instance (single instance for all 6 channels)
// Single ADC instance for all channels A0-A5 for simplified processing
AdvancedADC adc_all(A0, A1, A2, A3, A4, A5);  // Single ADC with all 6 channels

// AdvancedAnalog DAC instance
AdvancedDAC dac_output(DAC0_PIN);

// Memory buffers
float csv_voltage_values[MAX_CSV_SAMPLES];
uint32_t csv_sample_count = 0;
float csv_sample_period = 0.001;  // Default 1kHz

// Acquisition buffers (7 channels: 6 inputs + 1 output voltage)
float acq_buffer[MAX_ACQ_SAMPLES * 7];
uint32_t acq_sample_count = 0;
float acq_sample_period = 0.001;
volatile bool acquisition_active = false;
volatile bool output_active = false;
bool parsing_csv = false;  // Flag to prevent loop() from processing commands during CSV upload

// Timing
uint32_t output_index = 0;
volatile uint32_t acq_index = 0;
uint32_t required_samples = 0;  // Required samples for current acquisition (0 = use buffer limit)
unsigned long acquisition_start_time = 0;  // Start time of current acquisition

// Current output voltage (saved after DAC processing, used for acquisition)
volatile float current_output_voltage = 0.0;

// AdvancedAnalog state
bool adc_initialized = false;
bool dac_initialized = false;
uint32_t current_sample_rate = 1000;  // Current sample rate in Hz (default 1kHz)

// Error flags (set in processing function, checked in loop())
volatile bool error_flag = false;
volatile uint32_t error_code = 0;

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
  
  // AdvancedAnalog ADC and DAC will be initialized when CSV is loaded
  // (sample rate is needed for initialization)
  // For now, just mark as not initialized
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
  Serial.println("INFO: AdvancedAnalog library ready - ADC/DAC will initialize when CSV is loaded");
}

// ============================================================================
// AdvancedAnalog Initialization
// ============================================================================

bool initializeADC(uint32_t sample_rate) {
  // Initialize single ADC instance for all 6 channels (A0-A5)
  // Use start=false to prevent immediate sampling - will start when START_ACQUISITION is called
  if (!adc_all.begin(AN_RESOLUTION_12, sample_rate, ADC_BUFFER_SIZE, ADC_QUEUE_SIZE, false)) {
    return false;  // Error reported in calling function
  }
  adc_initialized = true;
  current_sample_rate = sample_rate;
  return true;
}

bool initializeDAC(uint32_t sample_rate) {
  // Initialize DAC with the specified sample rate
  if (!dac_output.begin(AN_RESOLUTION_12, sample_rate, DAC_BUFFER_SIZE, DAC_QUEUE_SIZE)) {
    Serial.println("ERROR: Failed to initialize DAC");
    return false;
  }
  dac_initialized = true;
  current_sample_rate = sample_rate;
  return true;
}

void stopADC() {
  // Stop ADC instance
  adc_all.stop();
  adc_initialized = false;
}

void stopDAC() {
  // Stop DAC
  dac_output.stop();
  dac_initialized = false;
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
  
  // Initialize AdvancedAnalog ADC and DAC with the sample rate from CSV
  uint32_t sample_rate = (uint32_t)(1.0 / csv_sample_period);
  Serial.print("INFO: Initializing AdvancedAnalog with sample rate: ");
  Serial.print(sample_rate);
  Serial.println(" Hz");
  
  // Stop existing ADC/DAC if running
  if (adc_initialized) {
    stopADC();
  }
  if (dac_initialized) {
    stopDAC();
  }
  
  // Initialize ADC and DAC with CSV sample rate
  if (!initializeADC(sample_rate)) {
    Serial.println("ERROR: Failed to initialize ADC channels");
    return false;
  }
  
  if (!initializeDAC(sample_rate)) {
    Serial.println("ERROR: Failed to initialize DAC");
    stopADC();  // Clean up ADC if DAC fails
    return false;
  }
  
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
    if (!dac_initialized) {
      Serial.println("ERROR: DAC not initialized. Please load CSV file first.");
      return;
    }
    output_active = true;
    output_index = 0;
    current_state = STATE_OUTPUTTING;
    // AdvancedAnalog DAC handles timing via DMA - no timer needed
    // Just start writing to DAC buffer in loop()
    Serial.println("ACK: Output started");
    
  } else if (cmd.startsWith("STOP_OUTPUT")) {
    output_active = false;
    if (!acquisition_active) {
      current_state = STATE_IDLE;
    } else {
      current_state = STATE_ACQUIRING;
    }
    // AdvancedAnalog DAC will stop when we stop writing
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
    
    // Check if acquisition is already active - stop it first
    if (acquisition_active) {
      Serial.println("WARNING: Acquisition already active, stopping first");
      acquisition_active = false;
      if (adc_initialized) {
        adc_all.stop();
      }
      // Wait a bit for ADC to fully stop
      delay(100);
    }
    
    // Calculate number of samples needed
    uint32_t calc_required_samples = (uint32_t)(duration / acq_sample_period);
    if (calc_required_samples > MAX_ACQ_SAMPLES) {
      Serial.print("ERROR: Acquisition duration too long. Maximum: ");
      Serial.print((float)MAX_ACQ_SAMPLES * acq_sample_period);
      Serial.println(" seconds");
      return;
    }
    
    if (!adc_initialized) {
      Serial.println("ERROR: ADC not initialized. Please load CSV file first.");
      return;
    }
    
    Serial.print("DEBUG: Acquisition parameters - duration=");
    Serial.print(duration, 3);
    Serial.print("s, start_delay=");
    Serial.print(start_delay, 3);
    Serial.print("s, required_samples=");
    Serial.print(calc_required_samples);
    Serial.print(", sample_period=");
    Serial.print(acq_sample_period, 6);
    Serial.println("s");
    
    // Delay before starting
    delay((uint32_t)(start_delay * 1000));
    
    // Reset acquisition state
    acq_index = 0;
    acq_sample_count = 0;
    current_output_voltage = 0.0;  // Reset voltage value
    
    // Ensure ADC is stopped before starting (in case it was left running)
    adc_all.stop();
    delay(50);  // Give ADC time to fully stop
    
    // Start ADC sampling (ADC was initialized with start=false, so we need to start it now)
    Serial.print("DEBUG: Starting ADC with sample_rate=");
    Serial.print(current_sample_rate);
    Serial.println(" Hz");
    
    if (!adc_all.start(current_sample_rate)) {
      Serial.println("ERROR: Failed to start ADC sampling");
      Serial.print("  adc_all.available()=");
      Serial.println(adc_all.available());
      // Clean up on failure
      adc_all.stop();
      return;
    }
    
    // Debug: Verify ADC started
    Serial.print("DEBUG: ADC started, available()=");
    Serial.print(adc_all.available());
    Serial.print(", sample_rate=");
    Serial.print(current_sample_rate);
    Serial.println(" Hz");
    
    if (output_active) {
      current_state = STATE_ACQUIRING;
    } else {
      // Start output at the same time
      if (!dac_initialized) {
        Serial.println("ERROR: DAC not initialized. Please load CSV file first.");
        // Stop ADC if DAC is not ready
        adc_all.stop();
        return;
      }
      output_active = true;
      output_index = 0;
      current_state = STATE_ACQUIRING;
    }
    
    // Store required samples and start time for duration-based completion
    // Now set acquisition_active after everything is set up
    required_samples = calc_required_samples;
    acquisition_start_time = millis();
    acquisition_active = true;
    
    Serial.println("ACK: Acquisition started");
    Serial.flush();  // Ensure message is sent before continuing
    // Note: Acquisition is now handled in loop(), not blocking here
    // This allows STOP_ACQUISITION and other commands to be processed
    
  } else if (cmd.startsWith("STOP_ACQUISITION")) {
    // Stop acquisition immediately
    Serial.println("DEBUG: STOP_ACQUISITION command received");
    acquisition_active = false;
    
    // Stop ADC sampling
    if (adc_initialized) {
      adc_all.stop();
      Serial.println("DEBUG: ADC stopped");
    }
    
    // Reset acquisition state
    acq_index = 0;
    acq_sample_count = 0;
    required_samples = 0;
    acquisition_start_time = 0;
    
    // Update state
    if (output_active) {
      current_state = STATE_OUTPUTTING;
    } else {
      current_state = STATE_IDLE;
    }
    
    Serial.println("ACK: Acquisition stopped");
    Serial.flush();  // Ensure message is sent
    
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
    // Note: 7 channels = 6 input channels + 1 output voltage channel
    Serial.print("DATA:");
    Serial.print(acq_sample_count);
    Serial.print(",");
    Serial.print(acq_sample_period, 6);
    Serial.print(",");
    Serial.print(7);  // 7 channels: A0-A5 (6) + output_voltage (1)
    Serial.println();
    
    // Send data samples (text format)
    // Format: A0,A1,A2,A3,A4,A5,output_voltage
    for (uint32_t i = 0; i < acq_sample_count; i++) {
      float *sample_ptr = &acq_buffer[i * 7];
      
      Serial.print(sample_ptr[0], 4);  // A0
      for (int ch = 1; ch < 7; ch++) {  // A1-A5, output_voltage
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

// Combined DAC and ADC processing (called from loop())
// AdvancedAnalog handles timing via DMA
// NO Serial communication in this function - all communication handled in loop()
void processAnalogIO() {
  // Temporary storage for voltage values from DAC buffer
  // Used to synchronize output voltages with ADC samples
  static float dac_voltage_buffer[DAC_BUFFER_SIZE];
  static uint32_t dac_voltage_count = 0;
  
  // ========================================================================
  // DAC Processing (first) - if output is active
  // ========================================================================
  if (output_active && dac_initialized && csv_sample_count > 0) {
    if (dac_output.available() > 0) {
      SampleBuffer dac_buf = dac_output.dequeue();
      
      if (dac_buf) {
        // Reset voltage count for this buffer
        dac_voltage_count = 0;
        
        // Fill buffer with CSV voltage values
        for (size_t i = 0; i < dac_buf.size(); i++) {
          float voltage = csv_voltage_values[output_index];
          
          // Store voltage for later use with ADC samples
          if (dac_voltage_count < DAC_BUFFER_SIZE) {
            dac_voltage_buffer[dac_voltage_count++] = voltage;
          }
          
          // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit DAC)
          uint16_t dac_value = (uint16_t)(voltage * 4095.0 / 3.3);
          dac_value = constrain(dac_value, 0, 4095);
          dac_buf[i] = dac_value;
          
          // Advance to next CSV sample (cyclic)
          output_index = (output_index + 1) % csv_sample_count;
        }
        
        // Write filled buffer to DAC (DMA transfer happens automatically)
        dac_output.write(dac_buf);
        // Note: dac_buf.release() is handled automatically by the library
      } else {
        // Invalid buffer - set error flag
        error_flag = true;
        error_code = 1;  // DAC buffer error
        dac_voltage_count = 0;  // Reset count on error
      }
    }
  } else {
    // Output not active - reset voltage count
    dac_voltage_count = 0;
  }
  
  // ========================================================================
  // ADC Processing (second) - if acquisition is active
  // ========================================================================
  if (acquisition_active && adc_initialized && acq_index < MAX_ACQ_SAMPLES) {
    if (adc_all.available() > 0) {
      SampleBuffer adc_buf = adc_all.read();
      
      if (adc_buf) {
        // Check buffer size (must be multiple of 6 for 6 channels)
        if (adc_buf.size() % 6 != 0) {
          adc_buf.release();
          error_flag = true;
          error_code = 2;  // ADC buffer size error
          return;
        }
        
        // Process samples from buffer
        // Buffer format: [A0, A1, A2, A3, A4, A5, A0, A1, A2, ...] (6 channels interleaved)
        size_t samples_to_process = adc_buf.size() / 6;
        samples_to_process = min(samples_to_process, (size_t)(MAX_ACQ_SAMPLES - acq_index));
        
        for (size_t i = 0; i < samples_to_process; i++) {
          if (acq_index >= MAX_ACQ_SAMPLES) {
            break;
          }
          
          // Check for buffer overflow
          if (acq_index * 7 + 6 >= MAX_ACQ_SAMPLES * 7) {
            error_flag = true;
            error_code = 3;  // Acquisition buffer overflow
            acquisition_active = false;
            break;
          }
          
          float *sample_ptr = &acq_buffer[acq_index * 7];
          
          // Extract interleaved channel data from buffer
          // Buffer: A0, A1, A2, A3, A4, A5 at indices i*6, i*6+1, ..., i*6+5
          uint16_t adc_ch0 = adc_buf[i * 6 + 0];  // A0
          uint16_t adc_ch1 = adc_buf[i * 6 + 1];  // A1
          uint16_t adc_ch2 = adc_buf[i * 6 + 2];  // A2
          uint16_t adc_ch3 = adc_buf[i * 6 + 3];  // A3
          uint16_t adc_ch4 = adc_buf[i * 6 + 4];  // A4
          uint16_t adc_ch5 = adc_buf[i * 6 + 5];  // A5
          
          // Convert ADC values (0-4095) to voltage (0-3.3V)
          sample_ptr[0] = adc_ch0 * 3.3 / 4095.0;  // A0
          sample_ptr[1] = adc_ch1 * 3.3 / 4095.0;  // A1
          sample_ptr[2] = adc_ch2 * 3.3 / 4095.0;  // A2
          sample_ptr[3] = adc_ch3 * 3.3 / 4095.0;  // A3
          sample_ptr[4] = adc_ch4 * 3.3 / 4095.0;  // A4
          sample_ptr[5] = adc_ch5 * 3.3 / 4095.0;  // A5
          
          // Save output voltage from corresponding DAC sample
          // Each ADC sample uses the voltage from the corresponding DAC sample
          if (i < dac_voltage_count) {
            sample_ptr[6] = dac_voltage_buffer[i];
          } else {
            // No corresponding voltage (shouldn't happen if buffers are same size)
            // Use 0.0 if output not active or buffer mismatch
            sample_ptr[6] = 0.0;
          }
          
          acq_index++;
          acq_sample_count = acq_index;
          
          if (acq_index >= MAX_ACQ_SAMPLES) {
            acquisition_active = false;
            break;
          }
        }
        
        // Release buffer back to memory pool
        adc_buf.release();
        
        // Reset voltage count after processing (for next iteration)
        dac_voltage_count = 0;
      } else {
        // Invalid buffer - set error flag
        error_flag = true;
        error_code = 4;  // ADC buffer read error
      }
    }
  }
}


// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  
  // Process analog I/O (DAC and ADC) - combined function
  // This function handles both DAC output and ADC acquisition in same execution
  // NO Serial communication in this function
  processAnalogIO();
  
  // Check for errors from processing function
  if (error_flag) {
    static unsigned long last_error_report = 0;
    if (millis() - last_error_report > 1000) {
      Serial.print("ERROR: Processing error code=");
      Serial.print(error_code);
      Serial.print(" (1=DAC buffer, 2=ADC buffer size, 3=Buffer overflow, 4=ADC read)");
      Serial.print(", acq_index=");
      Serial.println(acq_index);
      last_error_report = millis();
    }
    error_flag = false;  // Clear flag after reporting
  }
  
  // Check for duration-based completion
  if (acquisition_active && required_samples > 0 && acq_index >= required_samples) {
    acquisition_active = false;
    adc_all.stop();
    Serial.println("DEBUG: Acquisition completed - reached required samples");
  }
  
  // Progress reporting (reduced frequency to prevent serial buffer overflow)
  if (acquisition_active) {
    static unsigned long last_progress = 0;
    if (millis() - last_progress > 1000) {
      Serial.print("DEBUG: Acquisition progress: ");
      Serial.print(acq_index);
      if (required_samples > 0) {
        Serial.print("/");
        Serial.print(required_samples);
        Serial.print(" samples (");
        Serial.print((float)acq_index / required_samples * 100.0, 1);
        Serial.print("%)");
      } else {
        Serial.print(" samples");
      }
      if (acquisition_start_time > 0) {
        Serial.print(", elapsed=");
        Serial.print((millis() - acquisition_start_time) / 1000.0, 1);
        Serial.print("s");
      }
      Serial.print(", adc.avail=");
      Serial.println(adc_all.available());
      Serial.flush();
      last_progress = millis();
    }
  }
  
  // Check if acquisition just completed
  static bool was_acquiring = false;
  if (was_acquiring && !acquisition_active && adc_initialized) {
    // Acquisition just finished - stop ADC
    adc_all.stop();
    output_active = false;
    current_state = STATE_IDLE;
    required_samples = 0;
    acquisition_start_time = 0;
    Serial.println("ACK: Acquisition complete");
    Serial.flush();  // Ensure message is sent
    was_acquiring = false;
  } else if (acquisition_active) {
    was_acquiring = true;
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

