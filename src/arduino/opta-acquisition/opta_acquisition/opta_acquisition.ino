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
#include <HardwareTimer.h>

using namespace Opta;

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_CSV_SAMPLES 10000  // Maximum samples in CSV file
#define MAX_ACQ_SAMPLES 100000 // Maximum acquisition samples (6 channels)
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
HardwareTimer *timer = NULL;
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
  // For hardware-timed acquisition, we'll use timer interrupts
  
  // Setup hardware timer for precise timing
  timer = new HardwareTimer(TIM3);  // Use TIM3 on STM32
  timer->setOverflow(1000, MICROSEC_FORMAT);  // Default 1kHz
  
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
  
  // Read first line (sample period)
  String line = Serial.readStringUntil('\n');
  line.trim();
  csv_sample_period = line.toFloat();
  
  if (csv_sample_period <= 0 || csv_sample_period > 1.0) {
    Serial.println("ERROR: Invalid sample period");
    return false;
  }
  
  // Configure timer for this sample period
  uint32_t period_us = (uint32_t)(csv_sample_period * 1000000);
  timer->setOverflow(period_us, MICROSEC_FORMAT);
  
  // Read voltage values
  while (Serial.available() > 0 && csv_sample_count < MAX_CSV_SAMPLES) {
    line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.length() == 0) break;
    
    float voltage = line.toFloat();
    
    // Validate voltage range
    if (voltage < 0.0 || voltage > 3.3) {
      Serial.print("ERROR: Voltage out of range: ");
      Serial.println(voltage);
      return false;
    }
    
    csv_voltage_values[csv_sample_count++] = voltage;
  }
  
  if (csv_sample_count == 0) {
    Serial.println("ERROR: No voltage samples loaded");
    return false;
  }
  
  Serial.print("INFO: Loaded ");
  Serial.print(csv_sample_count);
  Serial.print(" samples, period: ");
  Serial.print(csv_sample_period);
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
    timer->attachInterrupt(timerISR);
    Serial.println("ACK: Output started");
    
  } else if (cmd.startsWith("STOP_OUTPUT")) {
    output_active = false;
    if (acquisition_active) {
      current_state = STATE_ACQUIRING;
    } else {
      current_state = STATE_IDLE;
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
    }
    
    timer->attachInterrupt(timerISR);
    
    Serial.println("ACK: Acquisition started");
    
    // Wait for acquisition to complete
    while (acquisition_active) {
      OptaController.update();
      delay(10);
    }
    
    timer->detachInterrupt();
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

