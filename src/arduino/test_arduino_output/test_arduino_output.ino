/* -------------------------------------------------------------------------- */
/* FILE NAME:   test_arduino_output.ino
   DESCRIPTION: Standalone test program to verify 5kHz output capability
                on Arduino Opta with A0602 expansion board.
                Outputs pattern: 0V, 1V, 0V, 2V, 0V, 3.3V (cycling)
   LICENSE:     See project LICENSE file
/* -------------------------------------------------------------------------- */

#include "OptaBlue.h"
#include "mbed.h"

using namespace Opta;

// ============================================================================
// Configuration and Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define OUTPUT_CHANNEL 0       // O1 on A0602 expansion board
#define TEST_PERIOD 3.000     // 5kHz = 0.0002s period

// Test voltage pattern: 0V, 1V, 0V, 2V, 0V, 3.3V (cycling)
const float test_voltages[] = {0.0, 1.0, 2.0, 3.0, 2.0, 1.0};
const uint8_t pattern_size = sizeof(test_voltages) / sizeof(test_voltages[0]);

// Timing
mbed::Ticker timer;
uint8_t pattern_index = 0;
uint32_t output_count = 0;
bool test_running = false;

// A0602 expansion board reference
int8_t expansion_index = -1;

// Pending tick counter for producer-consumer pattern
volatile uint32_t pending_output_ticks = 0;

// ============================================================================
// Timer Interrupt Service Routine
// ============================================================================

void timerISR() {
  // Minimal ISR - just increment counter (takes ~1µs)
  if (test_running) {
    pending_output_ticks++;
  }
}

// ============================================================================
// Setup
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(1000);  // Wait for serial to initialize
  
  Serial.println("========================================");
  Serial.println("Arduino Opta 5kHz Output Test");
  Serial.println("========================================");
  
  // Initialize Opta controller
  OptaController.begin();
  delay(100);  // Give time for expansion detection
  
  // Find A0602 analog expansion board
  for (int i = 0; i < OptaController.getExpansionNum(); i++) {
    if (OptaController.getExpansionType(i) == EXPANSION_OPTA_ANALOG) {
      expansion_index = i;
      break;
    }
  }
  
  if (expansion_index == -1) {
    Serial.println("ERROR: No A0602 analog expansion board found!");
    Serial.println("Please connect the A0602 expansion board and reset.");
    while (1) {
      delay(1000);  // Halt - wait for reset
    }
  }
  
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
  
  Serial.println("INFO: Output channel initialized");
  Serial.print("INFO: Test pattern: ");
  for (uint8_t i = 0; i < pattern_size; i++) {
    Serial.print(test_voltages[i]);
    Serial.print("V");
    if (i < pattern_size - 1) Serial.print(", ");
  }
  Serial.println();
  
  Serial.print("INFO: Test period: ");
  Serial.print(TEST_PERIOD * 1000.0);
  Serial.print("ms (");
  Serial.print(1.0 / TEST_PERIOD);
  Serial.println("Hz)");
  
  // Start the test
  Serial.println("INFO: Starting 5kHz output test in 2 seconds...");
  delay(2000);
  
  test_running = true;
  output_count = 0;
  pattern_index = 0;
  
  // Attach timer interrupt
  timer.attach(&timerISR, TEST_PERIOD);
  
  Serial.println("INFO: Test started! Output is running at 5kHz.");
  Serial.println("INFO: Pattern: 0V -> 1V -> 0V -> 2V -> 0V -> 3.3V (cycling)");
  Serial.println("INFO: Use oscilloscope or multimeter to verify output.");
  Serial.println("INFO: Press reset to stop.");
}

// ============================================================================
// Helper Functions
// ============================================================================

// Process one output frame (called from loop())
static inline void processOneOutputFrame() {
  if (expansion_index >= 0) {
    AnalogExpansion exp = OptaController.getExpansion(expansion_index);
    if (exp) {
      // Get current voltage from pattern
      float voltage = test_voltages[pattern_index];
      
      // Convert voltage (0-3.3V) to DAC value (0-4095 for 12-bit)
      uint16_t dac_value = (uint16_t)(voltage * 8191.0 / 11.0);
      dac_value = constrain(dac_value, 0, 8191);
      
      // Set DAC output
      exp.setDac(OUTPUT_CHANNEL, dac_value);
      
      // Move to next pattern value (cycling)
      pattern_index = (pattern_index + 1) % pattern_size;
      
      // Count outputs for statistics
      output_count++;
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
    if (test_running) {
      processOneOutputFrame();
    }
  }
  
  // Print statistics every 5 seconds
  static unsigned long last_print = 0;
  unsigned long now = millis();
  
  if (now - last_print >= 5000) {
    last_print = now;
    
    Serial.print("INFO: Output count: ");
    Serial.print(output_count);
    Serial.print(" (");
    Serial.print(output_count / 5.0);  // Approximate rate over 5 seconds
    Serial.println(" outputs/second)");
    
    // Reset counter for next period
    output_count = 0;
  }
  
  // Small delay to prevent tight loop
  delay(10);  // Reduced from 100ms to allow faster tick processing
}
