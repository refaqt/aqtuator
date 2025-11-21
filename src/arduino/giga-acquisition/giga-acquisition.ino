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
#define MAX_ACQ_SAMPLES 10000  // Maximum acquisition samples (6 channels)
                                // Memory constraint: ~480 KB (20000 × 6 channels × 4 bytes/float)
                                // Maximum acquisition duration = MAX_ACQ_SAMPLES / sample_rate
                                // Example: At 1 kHz = 20 seconds, at 10 kHz = 2 seconds
                                // See specifications_giga.md "Memory Management" section
#define DAC0_PIN A12          // DAC0 on Arduino Giga R1 WiFi (A12 is DAC0 channel)
#define INPUT_CHANNELS 6       // A0-A5 on Arduino Giga R1 WiFi

// AdvancedAnalog library configuration
#define ADC_BUFFER_SIZE 32     // DMA buffer size for ADC
#define ADC_QUEUE_SIZE 32      // Queue size for ADC
#define DAC_BUFFER_SIZE 32     // DMA buffer size for DAC
#define DAC_QUEUE_SIZE 32      // Queue size for DAC

// AdvancedAnalog ADC instances (multi-channel configuration)
// Arduino Giga R1 WiFi has 3 ADCs, but we use only ADC1 and ADC2 for hardware compatibility
// For synchronized timing, group channels by ADC:
// - A0, A1, A2 → ADC1 (3 channels)
// - A3, A4, A5 → ADC2 (3 channels)
AdvancedADC adc1(A0, A1, A2);  // ADC1 with channels A0, A1, A2
AdvancedADC adc2(A3, A4, A5);  // ADC2 with channels A3, A4, A5

// AdvancedAnalog DAC instance
AdvancedDAC dac_output(DAC0_PIN);

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
uint32_t required_samples = 0;  // Required samples for current acquisition (0 = use buffer limit)
unsigned long acquisition_start_time = 0;  // Start time of current acquisition

// AdvancedAnalog state
bool adc_initialized = false;
bool dac_initialized = false;
uint32_t current_sample_rate = 1000;  // Current sample rate in Hz (default 1kHz)

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
  // Initialize 2 multi-channel ADC instances (ADC1, ADC2)
  // ADC1 handles 3 channels (A0, A1, A2), ADC2 handles 3 channels (A3, A4, A5)
  // Use start=false to prevent immediate sampling - will start when START_ACQUISITION is called
  if (!adc1.begin(AN_RESOLUTION_12, sample_rate, ADC_BUFFER_SIZE, ADC_QUEUE_SIZE, false)) {
    Serial.println("ERROR: Failed to initialize ADC1 (A0, A1, A2)");
    return false;
  }
  if (!adc2.begin(AN_RESOLUTION_12, sample_rate, ADC_BUFFER_SIZE, ADC_QUEUE_SIZE, false)) {
    Serial.println("ERROR: Failed to initialize ADC2 (A3, A4, A5)");
    adc1.stop();  // Clean up on failure
    return false;
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
  // Stop all ADC instances
  adc1.stop();
  adc2.stop();
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
        adc1.stop();
        adc2.stop();
      }
      // Wait a bit for ADCs to fully stop
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
    
    // Ensure ADCs are stopped before starting (in case they were left running)
    adc1.stop();
    adc2.stop();
    delay(50);  // Give ADCs time to fully stop
    
    // Start ADC sampling (ADCs were initialized with start=false, so we need to start them now)
    // start() requires sample_rate parameter
    if (!adc1.start(current_sample_rate) || !adc2.start(current_sample_rate)) {
      Serial.println("ERROR: Failed to start ADC sampling");
      // Clean up on failure
      adc1.stop();
      adc2.stop();
      return;
    }
    
    // Debug: Verify ADCs started
    Serial.print("DEBUG: ADC1 started, available()=");
    Serial.println(adc1.available());
    Serial.print("DEBUG: ADC2 started, available()=");
    Serial.println(adc2.available());
    Serial.print("DEBUG: Sample rate=");
    Serial.print(current_sample_rate);
    Serial.println(" Hz");
    
    if (output_active) {
      current_state = STATE_ACQUIRING;
    } else {
      // Start output at the same time
      if (!dac_initialized) {
        Serial.println("ERROR: DAC not initialized. Please load CSV file first.");
        // Stop ADCs if DAC is not ready
        adc1.stop();
        adc2.stop();
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
      adc1.stop();
      adc2.stop();
      Serial.println("DEBUG: ADCs stopped");
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

// Process DAC output (called from loop())
// AdvancedAnalog handles timing via DMA, so we just need to keep the buffer filled
void processDACOutput() {
  if (!dac_initialized || csv_sample_count == 0 || !output_active) {
    return;
  }
  
  // Check if DAC has a buffer available for writing
  if (dac_output.available() > 0) {
    // Get a SampleBuffer from the DAC queue
    SampleBuffer buf = dac_output.dequeue();
    
    if (buf) {
      // Fill the buffer with CSV voltage values
      for (size_t i = 0; i < buf.size(); i++) {
        float voltage = csv_voltage_values[output_index];
        // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit DAC)
        uint16_t dac_value = (uint16_t)(voltage * 4095.0 / 3.3);
        dac_value = constrain(dac_value, 0, 4095);
        buf[i] = dac_value;
        
        // Advance to next CSV sample (cyclic)
        output_index = (output_index + 1) % csv_sample_count;
      }
      
      // Write the filled buffer to DAC (DMA transfer happens automatically)
      dac_output.write(buf);
      // Note: buf.release() is handled automatically by the library after write()
    }
  }
}

// Process ADC acquisition (called from loop())
// AdvancedAnalog handles timing via DMA, so we read from DMA buffers
// Multi-channel data is interleaved in SampleBuffer (ch0, ch1, ch2, ch0, ch1, ch2, ...)
void processADCAcquisition() {
  // Debug: Periodic status output
  static unsigned long last_debug = 0;
  static uint32_t last_acq_index = 0;
  static unsigned long last_data_time = 0;
  
  if (!adc_initialized || !acquisition_active || acq_index >= MAX_ACQ_SAMPLES) {
    if (millis() - last_debug > 2000) {
      Serial.print("DEBUG: processADCAcquisition() - adc_initialized=");
      Serial.print(adc_initialized);
      Serial.print(", acquisition_active=");
      Serial.print(acquisition_active);
      Serial.print(", acq_index=");
      Serial.print(acq_index);
      Serial.print("/");
      Serial.println(MAX_ACQ_SAMPLES);
      last_debug = millis();
    }
    return;
  }
  
  // Check if both ADC instances have data available
  int adc1_avail = adc1.available();
  int adc2_avail = adc2.available();
  
  // Debug: Print status every second
  if (millis() - last_debug > 1000) {
    Serial.print("DEBUG: adc1.available()=");
    Serial.print(adc1_avail);
    Serial.print(", adc2.available()=");
    Serial.print(adc2_avail);
    Serial.print(", acq_index=");
    Serial.print(acq_index);
    Serial.print(", samples/sec=");
    Serial.println(acq_index - last_acq_index);
    last_acq_index = acq_index;
    last_debug = millis();
    
    if (adc1_avail == 0 && adc2_avail == 0) {
      Serial.println("WARNING: Both ADCs have no data available!");
    } else if (adc1_avail == 0) {
      Serial.println("WARNING: ADC1 has no data available!");
    } else if (adc2_avail == 0) {
      Serial.println("WARNING: ADC2 has no data available!");
    }
  }
  
  if (adc1_avail > 0 && adc2_avail > 0) {
    // Read SampleBuffer from each ADC instance
    SampleBuffer buf1 = adc1.read();
    SampleBuffer buf2 = adc2.read();
    
    if (buf1 && buf2) {
      // Process samples from each buffer
      // Buffer 1 (ADC1): [A0, A1, A2, A0, A1, A2, ...] (3 channels interleaved)
      // Buffer 2 (ADC2): [A3, A4, A5, A3, A4, A5, ...] (3 channels interleaved)
      // We need to extract samples in sync across both ADCs
      
      size_t samples_to_process = min(buf1.size() / 3, buf2.size() / 3);
      samples_to_process = min(samples_to_process, (size_t)(MAX_ACQ_SAMPLES - acq_index));
      
      // Debug: Print buffer info occasionally
      if (millis() - last_data_time > 5000) {
        Serial.print("DEBUG: Buffer sizes - buf1.size()=");
        Serial.print(buf1.size());
        Serial.print(", buf2.size()=");
        Serial.print(buf2.size());
        Serial.print(", samples_to_process=");
        Serial.println(samples_to_process);
        last_data_time = millis();
      }
      
      if (samples_to_process == 0) {
        Serial.println("WARNING: samples_to_process is 0 - buffer size issue?");
        Serial.print("  buf1.size()=");
        Serial.print(buf1.size());
        Serial.print(", buf2.size()=");
        Serial.print(buf2.size());
        Serial.print(", buf1.size()/3=");
        Serial.print(buf1.size() / 3);
        Serial.print(", buf2.size()/3=");
        Serial.println(buf2.size() / 3);
        buf1.release();
        buf2.release();
        return;
      }
      
      for (size_t i = 0; i < samples_to_process; i++) {
        if (acq_index >= MAX_ACQ_SAMPLES) {
          break;
        }
        
        float *sample_ptr = &acq_buffer[acq_index * 6];
        
        // Extract interleaved channel data from each buffer
        // Buffer 1 (ADC1): A0, A1, A2 at indices i*3, i*3+1, i*3+2
        uint16_t adc1_ch0 = buf1[i * 3];      // A0
        uint16_t adc1_ch1 = buf1[i * 3 + 1];  // A1
        uint16_t adc1_ch2 = buf1[i * 3 + 2];  // A2
        
        // Buffer 2 (ADC2): A3, A4, A5 at indices i*3, i*3+1, i*3+2
        uint16_t adc2_ch0 = buf2[i * 3];      // A3
        uint16_t adc2_ch1 = buf2[i * 3 + 1];  // A4
        uint16_t adc2_ch2 = buf2[i * 3 + 2];  // A5
        
        // Convert ADC values (0-4095) to voltage (0-3.3V)
        sample_ptr[0] = adc1_ch0 * 3.3 / 4095.0;  // A0
        sample_ptr[1] = adc1_ch1 * 3.3 / 4095.0;  // A1
        sample_ptr[2] = adc1_ch2 * 3.3 / 4095.0;  // A2
        sample_ptr[3] = adc2_ch0 * 3.3 / 4095.0;  // A3
        sample_ptr[4] = adc2_ch1 * 3.3 / 4095.0;  // A4
        sample_ptr[5] = adc2_ch2 * 3.3 / 4095.0;  // A5
        
        acq_index++;
        acq_sample_count = acq_index;
        
        if (acq_index >= MAX_ACQ_SAMPLES) {
          acquisition_active = false;
          // Stop ADC sampling when buffer is full
          adc1.stop();
          adc2.stop();
          current_state = STATE_IDLE;
          Serial.println("DEBUG: Acquisition stopped - buffer full");
          break;
        }
      }
      
      // Release buffers back to the memory pool
      buf1.release();
      buf2.release();
    } else {
      Serial.println("WARNING: Failed to read buffers from ADCs");
      if (!buf1) Serial.println("  buf1 is invalid");
      if (!buf2) Serial.println("  buf2 is invalid");
    }
  }
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Process DAC output (AdvancedAnalog handles timing via DMA)
  if (output_active && current_state != STATE_TRANSFERRING && dac_initialized) {
    processDACOutput();
  }
  
  // Process ADC acquisition (AdvancedAnalog handles timing via DMA)
  if (acquisition_active && adc_initialized) {
    processADCAcquisition();
    
    // Check for duration-based completion
    if (required_samples > 0 && acq_index >= required_samples) {
      acquisition_active = false;
      Serial.println("DEBUG: Acquisition completed - reached required samples");
    }
    
    // Progress reporting (reduced frequency to prevent serial buffer overflow)
    static unsigned long last_progress = 0;
    if (millis() - last_progress > 1000) {  // Changed from 200ms to 1000ms to reduce serial traffic
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
      Serial.print(", adc1.avail=");
      Serial.print(adc1.available());
      Serial.print(", adc2.avail=");
      Serial.println(adc2.available());
      Serial.flush();  // Ensure progress message is sent
      last_progress = millis();
    }
  }
  
  // Check if acquisition just completed
  static bool was_acquiring = false;
  if (was_acquiring && !acquisition_active && adc_initialized) {
    // Acquisition just finished (either by duration, buffer full, or STOP command)
    // Note: ADCs are already stopped by STOP_ACQUISITION handler or processADCAcquisition()
    // But we stop them here too to be safe (stop() is safe to call multiple times)
    adc1.stop();
    adc2.stop();
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

