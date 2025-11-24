/* -------------------------------------------------------------------------- */
/* FILE NAME:   test_analog_io.ino
   DESCRIPTION: Minimal diagnostic test program for Arduino Giga R1 WiFi
                Tests basic DAC output and ADC acquisition using AdvancedAnalog library.
                Purpose: Identify cause of Arduino error state (red LED flashing).
                
                Features:
                - Single DAC output on A12 (DAC0)
                - Six ADC inputs on A0, A1, A2, A3, A4, A5
                - Output sequence: 0V, 1V, 0V, 2V, 0V, 3V (repeating)
                - Adjustable sample rate (default 100 Hz)
                - 1 second acquisition duration
                - CSV output to serial for plotting
   LICENSE:     See project LICENSE file
   NOTE:        Uses Arduino_AdvancedAnalog library
/* -------------------------------------------------------------------------- */

#include <Arduino_AdvancedAnalog.h>

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define SAMPLE_RATE 10000        // Hz (adjustable - change this value to test different rates)
#define DURATION_SEC 0.1       // Acquisition duration in seconds
#define TOTAL_SAMPLES ((uint32_t)(SAMPLE_RATE * DURATION_SEC))

#define DAC0_PIN A12           // DAC0 on Arduino Giga R1 WiFi
#define NUM_ADC_CHANNELS 6     // Number of ADC channels (A0-A5)

// AdvancedAnalog library configuration
#define BUFFER_SIZE 32         // DMA buffer size
#define QUEUE_SIZE 32          // Queue size

// Output voltage sequence (repeating pattern)
float output_sequence[] = {0.0, 1.0, 0.0, 2.0, 0.0, 3.0};
uint32_t output_sequence_size = 6;

// ============================================================================
// Global Variables
// ============================================================================

// AdvancedAnalog instances
AdvancedDAC dac_output(DAC0_PIN);
AdvancedADC adc_input(A0, A1, A2, A3, A4, A5);  // 6-channel ADC

// Data storage buffers
float output_voltage_buffer[TOTAL_SAMPLES];
float input_voltage_buffer_0[TOTAL_SAMPLES];  // Channel 0 (A0)
float input_voltage_buffer_1[TOTAL_SAMPLES];  // Channel 1 (A1)
float input_voltage_buffer_2[TOTAL_SAMPLES];  // Channel 2 (A2)
float input_voltage_buffer_3[TOTAL_SAMPLES];  // Channel 3 (A3)
float input_voltage_buffer_4[TOTAL_SAMPLES];  // Channel 4 (A4)
float input_voltage_buffer_5[TOTAL_SAMPLES];  // Channel 5 (A5)

// Acquisition state
volatile uint32_t sample_index = 0;
volatile bool acquisition_complete = false;

// Output state
uint32_t output_index = 0;

// Temporary storage for voltage values from DAC buffer
static float dac_voltage_buffer[BUFFER_SIZE];
static uint32_t dac_voltage_count = 0;

// ============================================================================
// Setup
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  
  // Wait for serial connection (optional - remove if not using serial monitor)
  while (!Serial && millis() < 5000) {
    delay(10);
  }
  
  Serial.println("========================================");
  Serial.println("Analog I/O Test Program");
  Serial.println("========================================");
  Serial.print("Sample Rate: ");
  Serial.print(SAMPLE_RATE);
  Serial.println(" Hz");
  Serial.print("Duration: ");
  Serial.print(DURATION_SEC);
  Serial.println(" seconds");
  Serial.print("Total Samples: ");
  Serial.println(TOTAL_SAMPLES);
  Serial.println("Initializing DAC and ADC...");
  
  // Initialize DAC
  if (!dac_output.begin(AN_RESOLUTION_12, SAMPLE_RATE, BUFFER_SIZE, QUEUE_SIZE)) {
    Serial.println("ERROR: Failed to initialize DAC!");
    while (1) {
      delay(1000);
    }
  }
  
  // Initialize ADC (start=false - we'll start it manually)
  if (!adc_input.begin(AN_RESOLUTION_12, SAMPLE_RATE, BUFFER_SIZE, QUEUE_SIZE, false)) {
    Serial.println("ERROR: Failed to initialize ADC!");
    while (1) {
      delay(1000);
    }
  }
  
  Serial.println("DAC and ADC initialized successfully");
  Serial.println("Starting acquisition in 1 second...");
  delay(1000);
  
  // Reset buffers
  sample_index = 0;
  output_index = 0;
  acquisition_complete = false;
  
  // Start both DAC and ADC simultaneously
  Serial.println("Starting DAC and ADC...");
  
  if (!adc_input.start(SAMPLE_RATE)) {
    Serial.println("ERROR: Failed to start ADC!");
    while (1) {
      delay(1000);
    }
  }
  
  Serial.println("Acquisition started!");
  Serial.println("Acquiring data...");
}

// ============================================================================
// Combined Analog I/O Processing
// ============================================================================

void processAnalogIO() {
  // ========================================================================
  // DAC Processing (first) - output voltage sequence
  // ========================================================================
  if (dac_output.available() > 0) {
    SampleBuffer dac_buf = dac_output.dequeue();
    
    if (dac_buf) {
      // Reset voltage count for this buffer
      dac_voltage_count = 0;
      
      // Fill buffer with output sequence values
      for (size_t i = 0; i < dac_buf.size(); i++) {
        // Get voltage from sequence (cyclic)
        float voltage = output_sequence[output_index];
        
        // Store voltage for later use with ADC samples
        if (dac_voltage_count < BUFFER_SIZE) {
          dac_voltage_buffer[dac_voltage_count++] = voltage;
        }
        
        // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit DAC)
        uint16_t dac_value = (uint16_t)(voltage * 4095.0 / 3.3);
        dac_value = constrain(dac_value, 0, 4095);
        dac_buf[i] = dac_value;
        
        // Advance to next sequence value (cyclic)
        output_index = (output_index + 1) % output_sequence_size;
      }
      
      // Write filled buffer to DAC (DMA transfer happens automatically)
      dac_output.write(dac_buf);
      // Note: dac_buf.release() is handled automatically by the library
    }
  }
  
  // ========================================================================
  // ADC Processing (second) - acquire input voltages (6 channels)
  // ========================================================================
  if (adc_input.available() > 0 && sample_index < TOTAL_SAMPLES) {
    SampleBuffer adc_buf = adc_input.read();
    
    if (adc_buf) {
      // Check buffer size (must be multiple of 6 for 6 channels)
      if (adc_buf.size() % NUM_ADC_CHANNELS != 0) {
        adc_buf.release();
        return;
      }
      
      // Process samples from buffer
      // Buffer format: [ch0, ch1, ch2, ch3, ch4, ch5, ch0, ch1, ...] (6 channels interleaved)
      size_t samples_to_process = adc_buf.size() / NUM_ADC_CHANNELS;
      samples_to_process = min(samples_to_process, (size_t)(TOTAL_SAMPLES - sample_index));
      
      for (size_t i = 0; i < samples_to_process; i++) {
        if (sample_index >= TOTAL_SAMPLES) {
          break;
        }
        
        // Extract interleaved channel data from buffer
        // Buffer: ch0, ch1, ch2, ch3, ch4, ch5 at indices i*6, i*6+1, ..., i*6+5
        uint16_t adc_ch0_value = adc_buf[i * NUM_ADC_CHANNELS + 0];  // Channel 0 (A0)
        uint16_t adc_ch1_value = adc_buf[i * NUM_ADC_CHANNELS + 1];  // Channel 1 (A1)
        uint16_t adc_ch2_value = adc_buf[i * NUM_ADC_CHANNELS + 2];  // Channel 2 (A2)
        uint16_t adc_ch3_value = adc_buf[i * NUM_ADC_CHANNELS + 3];  // Channel 3 (A3)
        uint16_t adc_ch4_value = adc_buf[i * NUM_ADC_CHANNELS + 4];  // Channel 4 (A4)
        uint16_t adc_ch5_value = adc_buf[i * NUM_ADC_CHANNELS + 5];  // Channel 5 (A5)
        
        // Convert ADC values (0-4095) to voltage (0-3.3V)
        float input_voltage_0 = adc_ch0_value * 3.3 / 4095.0;  // Channel 0 (A0)
        float input_voltage_1 = adc_ch1_value * 3.3 / 4095.0;  // Channel 1 (A1)
        float input_voltage_2 = adc_ch2_value * 3.3 / 4095.0;  // Channel 2 (A2)
        float input_voltage_3 = adc_ch3_value * 3.3 / 4095.0;  // Channel 3 (A3)
        float input_voltage_4 = adc_ch4_value * 3.3 / 4095.0;  // Channel 4 (A4)
        float input_voltage_5 = adc_ch5_value * 3.3 / 4095.0;  // Channel 5 (A5)
        
        // Save input voltages
        input_voltage_buffer_0[sample_index] = input_voltage_0;
        input_voltage_buffer_1[sample_index] = input_voltage_1;
        input_voltage_buffer_2[sample_index] = input_voltage_2;
        input_voltage_buffer_3[sample_index] = input_voltage_3;
        input_voltage_buffer_4[sample_index] = input_voltage_4;
        input_voltage_buffer_5[sample_index] = input_voltage_5;
        
        // Save corresponding output voltage
        if (i < dac_voltage_count) {
          output_voltage_buffer[sample_index] = dac_voltage_buffer[i];
        } else {
          // No corresponding voltage (shouldn't happen if buffers are same size)
          output_voltage_buffer[sample_index] = 0.0;
        }
        
        sample_index++;
        
        if (sample_index >= TOTAL_SAMPLES) {
          acquisition_complete = true;
          break;
        }
      }
      
      // Release buffer back to memory pool
      adc_buf.release();
      
      // Reset voltage count after processing
      dac_voltage_count = 0;
    }
  }
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Process analog I/O while acquiring
  if (!acquisition_complete) {
    processAnalogIO();
  } else {
    // Acquisition complete - print data once
    static bool data_printed = false;
    
    if (!data_printed) {
      // Stop DAC and ADC
      dac_output.stop();
      adc_input.stop();
      
      Serial.println("Acquisition complete!");
      Serial.println("Printing data in CSV format...");
      Serial.println();
      
      // Print CSV header
      Serial.println("time,output_voltage,input_voltage_A0,input_voltage_A1,input_voltage_A2,input_voltage_A3,input_voltage_A4,input_voltage_A5");
      
      // Print data rows
      float time_step = 1.0 / SAMPLE_RATE;
      for (uint32_t i = 0; i < sample_index; i++) {
        float time = i * time_step;
        Serial.print(time, 4);
        Serial.print(",");
        Serial.print(output_voltage_buffer[i], 4);
        Serial.print(",");
        Serial.print(input_voltage_buffer_0[i], 4);
        Serial.print(",");
        Serial.print(input_voltage_buffer_1[i], 4);
        Serial.print(",");
        Serial.print(input_voltage_buffer_2[i], 4);
        Serial.print(",");
        Serial.print(input_voltage_buffer_3[i], 4);
        Serial.print(",");
        Serial.print(input_voltage_buffer_4[i], 4);
        Serial.print(",");
        Serial.println(input_voltage_buffer_5[i], 4);
      }
      
      Serial.println();
      Serial.println("Data printing complete!");
      Serial.println("Reset Arduino to run test again.");
      
      data_printed = true;
    }
    
    // Do nothing - wait for reset
    delay(1000);
  }
}

