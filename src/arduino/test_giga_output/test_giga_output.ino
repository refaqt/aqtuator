/* -------------------------------------------------------------------------- */
/* FILE NAME:   test_giga_output.ino
   DESCRIPTION: Minimal test program to generate 5kHz output signal
                on Arduino Giga R1 WiFi.
                Simplest possible code to isolate Mbed OS crash issues.
   LICENSE:     See project LICENSE file
/* -------------------------------------------------------------------------- */

#include "mbed.h"

// ============================================================================
// Configuration and Constants
// ============================================================================

#define DAC0_PIN A0            // DAC0 on Arduino Giga R1 WiFi (physical pin A0)
#define PERIOD 0.1           // 5kHz = 0.0002s period

// ============================================================================
// Global Variables
// ============================================================================

mbed::Ticker timer;
volatile bool output_state = false;

// ============================================================================
// Timer Interrupt Service Routine
// ============================================================================

void timerISR() {
  output_state = !output_state;
  analogWrite(DAC0_PIN, output_state ? 2048 : 0);
}

// ============================================================================
// Setup
// ============================================================================

void setup() {
  pinMode(DAC0_PIN, OUTPUT);
  timer.attach(&timerISR, PERIOD);
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  delay(1000);
}
