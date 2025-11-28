/* -------------------------------------------------------------------------- */
/* FILE NAME:   test-analog-control-stm32.ino
   DESCRIPTION: Real-time control loop test program for Arduino Giga R1 WiFi
                Tests control loop implementation using STM32H7 hardware timers.
                Purpose: Verify real-time servo control loop with synchronized ADC/DAC.
                
                Features:
                - Single DAC output on A12 (DAC0)
                - Six ADC inputs on A0, A1, A2, A3, A4, A5
                - Control loop: sine wave output (frequency = SAMPLE_RATE / 20)
                - Hardware-timed synchronized ADC and DAC operation
                - Timer interrupt-based single-sample acquisition
                - Adjustable sample rate (default 2000 Hz)
                - CSV output to serial for plotting
   LICENSE:     See project LICENSE file
   NOTE:        Uses mbed Ticker for hardware-timed interrupts and direct ADC/DAC access
/* -------------------------------------------------------------------------- */

#include <mbed.h>

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define SAMPLE_RATE 20        // Hz (adjustable - change this value to test different rates)
#define DURATION_SEC 0.1       // Acquisition duration in seconds
#define TOTAL_SAMPLES ((uint32_t)(SAMPLE_RATE * DURATION_SEC))

#define DAC0_PIN A12           // DAC0 on Arduino Giga R1 WiFi
#define NUM_ADC_CHANNELS 6     // Number of ADC channels (A0-A5)

// ADC channel pins
#define ADC_PIN_0 A0
#define ADC_PIN_1 A1
#define ADC_PIN_2 A2
#define ADC_PIN_3 A3
#define ADC_PIN_4 A4
#define ADC_PIN_5 A5

// ============================================================================
// Global Variables
// ============================================================================

// mbed Ticker instance for hardware-timed interrupts
mbed::Ticker sample_ticker;

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
volatile bool control_loop_active = false;  // Combined flag for ADC and DAC

// ============================================================================
// Timer Interrupt Service Routine
// ============================================================================

void TimerISR() {
  // Only process if control loop is active and not complete
  if (!control_loop_active || acquisition_complete) {
    return;
  }
  
  // Check if we've collected enough samples
  if (sample_index >= TOTAL_SAMPLES) {
    acquisition_complete = true;
    return;
  }
  
  // ========================================================================
  // ADC Processing (first) - acquire input voltages (6 channels)
  // ========================================================================
  // Read all 6 ADC channels sequentially
  // Note: analogRead() on STM32H7 is relatively fast but not hardware-timed
  // For true hardware timing, we'd need direct register access, but this
  // approach works well for moderate sample rates
  
  uint16_t adc_ch0_value = analogRead(ADC_PIN_0);  // Channel 0 (A0)
  uint16_t adc_ch1_value = analogRead(ADC_PIN_1);  // Channel 1 (A1)
  uint16_t adc_ch2_value = analogRead(ADC_PIN_2);  // Channel 2 (A2)
  uint16_t adc_ch3_value = analogRead(ADC_PIN_3);  // Channel 3 (A3)
  uint16_t adc_ch4_value = analogRead(ADC_PIN_4);  // Channel 4 (A4)
  uint16_t adc_ch5_value = analogRead(ADC_PIN_5);  // Channel 5 (A5)
  
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
  
  // ========================================================================
  // Control Calculation (second) - calculate output voltage
  // ========================================================================
  // Generate sine wave: frequency = SAMPLE_RATE / 20 Hz
  // Sine wave from 0V to 3.3V (centered at 1.65V)
  float frequency = (float)SAMPLE_RATE / 20.0;  // Hz
  float time = (float)sample_index / (float)SAMPLE_RATE;  // seconds
  float output_voltage = 1.65 + 1.65 * sin(2.0 * PI * frequency * time);
  // Clamp output to valid DAC range (0-3.3V) as safety measure
  output_voltage = constrain(output_voltage, 0.0, 3.3);
  
  // Save output voltage
  output_voltage_buffer[sample_index] = output_voltage;
  
  // ========================================================================
  // DAC Processing (third) - output calculated voltage
  // ========================================================================
  // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit DAC)
  uint16_t dac_value = (uint16_t)(output_voltage * 4095.0 / 3.3);
  dac_value = constrain(dac_value, 0, 4095);
  
  // Write directly to DAC (single sample, no buffering)
  // Note: analogWrite() on STM32H7 with DAC pin writes directly to hardware
  analogWrite(DAC0_PIN, dac_value);
  
  // Increment sample index
  sample_index++;
  
  // Check if acquisition is complete
  if (sample_index >= TOTAL_SAMPLES) {
    acquisition_complete = true;
  }
}

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
  Serial.println("STM32 Hardware-Timed Control Loop");
  Serial.println("========================================");
  Serial.print("Sample Rate: ");
  Serial.print(SAMPLE_RATE);
  Serial.println(" Hz");
  Serial.print("Duration: ");
  Serial.print(DURATION_SEC);
  Serial.println(" seconds");
  Serial.print("Total Samples: ");
  Serial.println(TOTAL_SAMPLES);
  Serial.println("Initializing mbed Ticker...");
  
  // Set ADC resolution to 12 bits (0-4095)
  analogReadResolution(12);
  
  // Set DAC resolution to 12 bits (0-4095)
  analogWriteResolution(12);
  
  // Note: Ticker will be attached in loop() when 'c' command is received
  // Calculate period in microseconds: period_us = 1000000 / SAMPLE_RATE
  // This will be done when starting the control loop
  
  Serial.println("mbed Ticker ready. Send 'c' to start control loop.");
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    // Clear any remaining characters in buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
    
    // Handle "c" command to start control loop
    if ((command == 'c' || command == 'C') && !control_loop_active) {
      // Reset acquisition state variables
      sample_index = 0;
      acquisition_complete = false;
      
      // Start control loop
      control_loop_active = true;
      
      // Attach Ticker with period in microseconds
      // Period = 1000000 microseconds / SAMPLE_RATE Hz
      uint32_t period_us = 1000000 / SAMPLE_RATE;
      sample_ticker.attach_us(TimerISR, period_us);
      
      Serial.println("Control loop started! mbed Ticker running.");
    }
  }
  
  // Check if acquisition is complete
  if (acquisition_complete && control_loop_active) {
    // Stop Ticker
    sample_ticker.detach();
    control_loop_active = false;
    
    // Print data once
    static bool data_printed = false;
    
    if (!data_printed) {
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
      Serial.println("Send 'c' to start a new control loop.");
      
      data_printed = true;
    }
    
    // Check for new commands
    if (Serial.available() > 0) {
      char command = Serial.read();
      // Clear any remaining characters in buffer
      while (Serial.available() > 0) {
        Serial.read();
      }
      
      // Handle "c" command to start new control loop
      if ((command == 'c' || command == 'C') && !control_loop_active) {
        // Reset for new acquisition
        data_printed = false;
        sample_index = 0;
        acquisition_complete = false;
        
        // Start control loop
        control_loop_active = true;
        
        // Attach Ticker with period in microseconds
        uint32_t period_us = 1000000 / SAMPLE_RATE;
        sample_ticker.attach_us(TimerISR, period_us);
        
        Serial.println("Control loop started! mbed Ticker running.");
      }
    } else {
      // Do nothing - wait for command
      delay(1000);
    }
  } else if (!control_loop_active) {
    // Do nothing - wait for command
    delay(100);
  }
}
