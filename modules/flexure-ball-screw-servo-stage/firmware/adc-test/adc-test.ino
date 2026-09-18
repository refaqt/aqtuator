/*
 * Controllino Micro ADC Test Program
 * 
 * Tests acquisition of 6 analog inputs:
 * - DI0-DI3: 4 analog inputs at 8kHz using RP2040 hardware ADC (adc_read)
 * - AI0-AI1: 2 analog inputs at 8kHz using MCP3564RT ADC (analogRead) - testing if it blocks
 * 
 * Uses hardware timer interrupt for precise 8kHz timing (125µs interval).
 * Acquires 100 samples and outputs to Serial Plotter format.
 * Start acquisition by typing 'S' in Serial Monitor.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Install Controllino board support in Arduino IDE
 * 2. Connect analog inputs to DI0-DI3 and AI0-AI1
 * 3. Open Serial Monitor at 115200 baud
 * 4. Type 'S' to start acquisition
 * 5. Open Serial Plotter to view results
 */

/* #include <Controllino.h>  /* Usage of CONTROLLINO library allows you to use CONTROLLINO_xx aliases */

#include <Arduino.h>

#ifdef ARDUINO_ARCH_RP2040
  #include <hardware/timer.h>
  #include <hardware/irq.h>
  #include <hardware/adc.h>
  #include <pico/time.h>
#endif

// ============================================================================
// Configuration Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define SAMPLE_RATE_HZ 8000
#define SAMPLE_INTERVAL_US (1000000UL / SAMPLE_RATE_HZ)  // 125 µs for 8kHz
#define NUM_SAMPLES 100
#define NUM_CHANNELS 6  // DI0, DI1, DI2, DI3, AI0, AI1

// Enable/disable sampling of CONTROLLINO_MICRO_AIx channels (AI0, AI1)
// Set to false to compare timing without the slower MCP3564RT ADC channels
#define ENABLE_AI_CHANNELS false

// GPIO pins for DI0-DI3 (RP2040 hardware ADC channels 0-3)
// RP2040 ADC channels: GPIO26-29 are ADC0-3
// Mapping: DI0=A0=GPIO26=ADC0, DI1=A1=GPIO27=ADC1, DI2=A2=GPIO28=ADC2, DI3=A3=GPIO29=ADC3
#define GPIO_DI0 26
#define GPIO_DI1 27
#define GPIO_DI2 28
#define GPIO_DI3 29

// Analog input pins for AI0-AI1 (MCP3564RT ADC via Controllino library)
// Using CONTROLLINO_A4 and CONTROLLINO_A5 as per Controllino library convention
// Reference: https://github.com/CONTROLLINO-PLC/CONTROLLINO_Library/blob/master/examples/Common/AnalogInputs/AnalogInputs.ino
#define PIN_AI0 CONTROLLINO_MICRO_AI4  // AI0 - MCP3564RT ADC channel
#define PIN_AI1 CONTROLLINO_MICRO_AI5  // AI1 - MCP3564RT ADC channel

// ============================================================================
// State Machine
// ============================================================================

enum State {
  STATE_IDLE,
  STATE_ACQUIRING,
  STATE_COMPLETE
};

volatile State current_state = STATE_IDLE;

// ============================================================================
// Data Storage
// ============================================================================

// Storage for 100 samples × 6 channels
volatile float sample_buffer[NUM_SAMPLES][NUM_CHANNELS];
volatile uint32_t sample_index = 0;
volatile bool acquisition_active = false;

// ============================================================================
// Timing Diagnostics
// ============================================================================

#ifdef ARDUINO_ARCH_RP2040
  // Timing variables (volatile for ISR access)
  volatile uint64_t isr_start_time = 0;
  volatile uint64_t previous_isr_time = 0;
  volatile uint64_t analog_read_start_time = 0;
  
  // Timing data storage (one per sample)
  volatile uint32_t isr_execution_time_us[NUM_SAMPLES];      // Total ISR execution time
  volatile uint32_t analog_read_time_us[NUM_SAMPLES];        // Time for analogRead() calls
  volatile uint32_t inter_interval_us[NUM_SAMPLES];         // Time between interrupts
  
  // Statistics
  volatile uint32_t missed_interrupt_count = 0;
  #define MISSED_INTERRUPT_THRESHOLD_US 150  // Intervals > 150µs indicate blocking
#endif

// ============================================================================
// Hardware Timer (RP2040)
// ============================================================================

#ifdef ARDUINO_ARCH_RP2040
  struct repeating_timer timer;
  bool timer_initialized = false;
  
  // ADC channel mapping for DI0-DI3
  // GPIO26-29 map to ADC channels 0-3
  uint8_t adc_channel_map[4] = {0, 1, 2, 3};  // DI0->ADC0, DI1->ADC1, etc.
#endif

// ============================================================================
// Function Prototypes
// ============================================================================

void setupADC();
void setupTimer();
bool timerCallback(struct repeating_timer *t);
void timerISR();
void outputToSerialPlotter();
void outputTimingStatistics();

// ============================================================================
// Setup Function
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(2000);  // Wait for Serial Monitor to open
  Serial.flush();
  
  Serial.println("========================================");
  Serial.println("Controllino Micro ADC Test");
  Serial.println("========================================");
  Serial.print("Sample Rate: ");
  Serial.print(SAMPLE_RATE_HZ);
  Serial.println(" Hz");
  Serial.print("Samples to acquire: ");
  Serial.println(NUM_SAMPLES);
  Serial.print("Sample interval: ");
  Serial.print(SAMPLE_INTERVAL_US);
  Serial.println(" µs");
  Serial.println();
  
  // Initialize RP2040 ADC for DI0-DI3
  #ifdef ARDUINO_ARCH_RP2040
    setupADC();
  #endif
  
  // Configure AI0-AI1 as analog inputs (MCP3564RT ADC via Controllino library)
  #if ENABLE_AI_CHANNELS
    pinMode(PIN_AI0, INPUT);
    pinMode(PIN_AI1, INPUT);
    Serial.println("AI channels (AI0, AI1): ENABLED");
  #else
    Serial.println("AI channels (AI0, AI1): DISABLED");
  #endif
  
  // Initialize timer (will be started when 'S' is received)
  #ifdef ARDUINO_ARCH_RP2040
    setupTimer();
  #endif
  
  Serial.println("Ready. Type 'S' in Serial Monitor to start acquisition.");
  Serial.println("Then open Serial Plotter to view results.");
  Serial.flush();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Check for 'S' command to start acquisition
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if ((cmd == 'S' || cmd == 's') && current_state == STATE_IDLE) {
      // Reset acquisition state
      sample_index = 0;
      acquisition_active = true;
      current_state = STATE_ACQUIRING;
      
      // Reset timing variables
      #ifdef ARDUINO_ARCH_RP2040
        previous_isr_time = 0;
        missed_interrupt_count = 0;
      #endif
      
      Serial.println("Starting acquisition...");
      Serial.flush();
      
      // Start the timer
      #ifdef ARDUINO_ARCH_RP2040
        if (!timer_initialized) {
          setupTimer();
        }
      #endif
    }
  }
  
  // Check if acquisition is complete
  if (current_state == STATE_COMPLETE) {
    // Stop timer
    #ifdef ARDUINO_ARCH_RP2040
      if (timer_initialized) {
        cancel_repeating_timer(&timer);
        timer_initialized = false;
      }
    #endif
    
    acquisition_active = false;
    
    // Output data to Serial Plotter
    outputToSerialPlotter();
    
    // Output timing statistics
    outputTimingStatistics();
    
    // Reset state
    current_state = STATE_IDLE;
    sample_index = 0;
    
    Serial.println();
    Serial.println("Acquisition complete. Type 'S' to start again.");
    Serial.flush();
  }
}

// ============================================================================
// ADC Setup (RP2040)
// ============================================================================

void setupADC() {
  #ifdef ARDUINO_ARCH_RP2040
    adc_init();
    
    // Initialize GPIO pins for DI0-DI3 as ADC inputs
    adc_gpio_init(GPIO_DI0);
    adc_gpio_init(GPIO_DI1);
    adc_gpio_init(GPIO_DI2);
    adc_gpio_init(GPIO_DI3);
    
    Serial.println("RP2040 ADC initialized for DI0-DI3 (GPIO26-29)");
  #endif
}

// ============================================================================
// Timer Setup
// ============================================================================

void setupTimer() {
  #ifdef ARDUINO_ARCH_RP2040
    // Cancel existing timer if running
    if (timer_initialized) {
      cancel_repeating_timer(&timer);
      timer_initialized = false;
    }
    
    // Use RP2040 hardware timer (alarm pool)
    // Negative delay means repeating timer
    int64_t delay_us = -((int64_t)SAMPLE_INTERVAL_US);
    
    if (add_repeating_timer_us(delay_us, timerCallback, NULL, &timer)) {
      timer_initialized = true;
      Serial.print("Hardware timer initialized: ");
      Serial.print(SAMPLE_RATE_HZ);
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
  if (!acquisition_active || sample_index >= NUM_SAMPLES) {
    if (sample_index >= NUM_SAMPLES) {
      current_state = STATE_COMPLETE;
    }
    return;
  }
  
  #ifdef ARDUINO_ARCH_RP2040
    // Capture start time of ISR
    isr_start_time = time_us_64();
    
    // Calculate inter-interrupt interval (time since previous ISR)
    if (previous_isr_time > 0) {
      uint64_t interval = isr_start_time - previous_isr_time;
      inter_interval_us[sample_index] = (uint32_t)interval;
      
      // Detect missed interrupts (intervals significantly longer than expected)
      if (interval > MISSED_INTERRUPT_THRESHOLD_US) {
        missed_interrupt_count++;
      }
    } else {
      // First interrupt - no interval to measure
      inter_interval_us[sample_index] = 0;
    }
    previous_isr_time = isr_start_time;
  #endif
  
  // Read DI0-DI3 using RP2040 hardware ADC (fast, ~2-3µs per channel)
  #ifdef ARDUINO_ARCH_RP2040
    // DI0 (GPIO26, ADC channel 0)
    adc_select_input(adc_channel_map[0]);
    uint16_t di0_raw = adc_read();
    sample_buffer[sample_index][0] = (float)di0_raw * 3.3f / 4095.0f;
    
    // DI1 (GPIO27, ADC channel 1)
    adc_select_input(adc_channel_map[1]);
    uint16_t di1_raw = adc_read();
    sample_buffer[sample_index][1] = (float)di1_raw * 3.3f / 4095.0f;
    
    // DI2 (GPIO28, ADC channel 2)
    adc_select_input(adc_channel_map[2]);
    uint16_t di2_raw = adc_read();
    sample_buffer[sample_index][2] = (float)di2_raw * 3.3f / 4095.0f;
    
    // DI3 (GPIO29, ADC channel 3)
    adc_select_input(adc_channel_map[3]);
    uint16_t di3_raw = adc_read();
    sample_buffer[sample_index][3] = (float)di3_raw * 3.3f / 4095.0f;
  #else
    // Fallback: use analogRead (not hardware-timed)
    sample_buffer[sample_index][0] = analogRead(A0) * 3.3f / 4095.0f;
    sample_buffer[sample_index][1] = analogRead(A1) * 3.3f / 4095.0f;
    sample_buffer[sample_index][2] = analogRead(A2) * 3.3f / 4095.0f;
    sample_buffer[sample_index][3] = analogRead(A3) * 3.3f / 4095.0f;
  #endif
  
  // Read AI0-AI1 using analogRead() (MCP3564RT ADC via Controllino library)
  // This may block or return stale values at 8kHz (max ADC rate is 1.15kHz)
  // Measure time taken by analogRead() calls to detect blocking
  #if ENABLE_AI_CHANNELS
    #ifdef ARDUINO_ARCH_RP2040
      analog_read_start_time = time_us_64();
    #endif
    
    uint32_t ai0_raw = analogRead(PIN_AI0);
    uint32_t ai1_raw = analogRead(PIN_AI1);
    
    #ifdef ARDUINO_ARCH_RP2040
      uint64_t analog_read_end_time = time_us_64();
      analog_read_time_us[sample_index] = (uint32_t)(analog_read_end_time - analog_read_start_time);
    #endif
    
    // Convert to voltage
    // If 24-bit: 0-16777215 -> 0-3.3V
    // If 12-bit: 0-4095 -> 0-3.3V
    // Try 24-bit first, if values seem too small, use 12-bit
    if (ai0_raw > 4095) {
      // Likely 24-bit
      sample_buffer[sample_index][4] = (float)ai0_raw * 3.3f / 16777215.0f;
      sample_buffer[sample_index][5] = (float)ai1_raw * 3.3f / 16777215.0f;
    } else {
      // Likely 12-bit
      sample_buffer[sample_index][4] = (float)ai0_raw * 3.3f / 4095.0f;
      sample_buffer[sample_index][5] = (float)ai1_raw * 3.3f / 4095.0f;
    }
  #else
    // AI channels disabled - set to 0 and no timing measurement
    sample_buffer[sample_index][4] = 0.0f;
    sample_buffer[sample_index][5] = 0.0f;
    #ifdef ARDUINO_ARCH_RP2040
      analog_read_time_us[sample_index] = 0;
    #endif
  #endif
  
  #ifdef ARDUINO_ARCH_RP2040
    // Calculate total ISR execution time
    uint64_t isr_end_time = time_us_64();
    isr_execution_time_us[sample_index] = (uint32_t)(isr_end_time - isr_start_time);
  #endif
  
  sample_index++;
  
  // Check if we've collected all samples
  if (sample_index >= NUM_SAMPLES) {
    current_state = STATE_COMPLETE;
  }
}

// ============================================================================
// Serial Plotter Output
// ============================================================================

void outputToSerialPlotter() {
  // Output header for Serial Plotter
  #if ENABLE_AI_CHANNELS
    Serial.println("DI0,DI1,DI2,DI3,AI0,AI1");
  #else
    Serial.println("DI0,DI1,DI2,DI3");
  #endif
  
  // Output all samples
  for (uint32_t i = 0; i < NUM_SAMPLES; i++) {
    Serial.print(sample_buffer[i][0], 4);  // DI0
    Serial.print(",");
    Serial.print(sample_buffer[i][1], 4);  // DI1
    Serial.print(",");
    Serial.print(sample_buffer[i][2], 4);  // DI2
    Serial.print(",");
    Serial.print(sample_buffer[i][3], 4);  // DI3
    #if ENABLE_AI_CHANNELS
      Serial.print(",");
      Serial.print(sample_buffer[i][4], 4);  // AI0
      Serial.print(",");
      Serial.println(sample_buffer[i][5], 4);  // AI1
    #else
      Serial.println();
    #endif
  }
  
  Serial.flush();
}

// ============================================================================
// Timing Statistics Output
// ============================================================================

void outputTimingStatistics() {
  #ifdef ARDUINO_ARCH_RP2040
    Serial.println();
    Serial.println("========================================");
    Serial.println("Timing Diagnostics");
    Serial.println("========================================");
    
    // Calculate statistics for ISR execution time
    uint32_t isr_min = UINT32_MAX;
    uint32_t isr_max = 0;
    uint64_t isr_sum = 0;
    
    // Calculate statistics for analogRead() time
    uint32_t analog_min = UINT32_MAX;
    uint32_t analog_max = 0;
    uint64_t analog_sum = 0;
    
    // Calculate statistics for inter-interrupt intervals
    uint32_t interval_min = UINT32_MAX;
    uint32_t interval_max = 0;
    uint64_t interval_sum = 0;
    uint32_t valid_intervals = 0;  // Skip first sample (no previous interval)
    
    for (uint32_t i = 0; i < NUM_SAMPLES; i++) {
      // ISR execution time statistics
      if (isr_execution_time_us[i] < isr_min) isr_min = isr_execution_time_us[i];
      if (isr_execution_time_us[i] > isr_max) isr_max = isr_execution_time_us[i];
      isr_sum += isr_execution_time_us[i];
      
      // analogRead() time statistics (only if AI channels enabled)
      #if ENABLE_AI_CHANNELS
        if (analog_read_time_us[i] < analog_min) analog_min = analog_read_time_us[i];
        if (analog_read_time_us[i] > analog_max) analog_max = analog_read_time_us[i];
        analog_sum += analog_read_time_us[i];
      #endif
      
      // Inter-interrupt interval statistics (skip first sample)
      if (i > 0 && inter_interval_us[i] > 0) {
        if (inter_interval_us[i] < interval_min) interval_min = inter_interval_us[i];
        if (inter_interval_us[i] > interval_max) interval_max = inter_interval_us[i];
        interval_sum += inter_interval_us[i];
        valid_intervals++;
      }
    }
    
    // Print ISR execution time statistics
    Serial.println("ISR Execution Time (total):");
    Serial.print("  Min: ");
    Serial.print(isr_min);
    Serial.println(" µs");
    Serial.print("  Max: ");
    Serial.print(isr_max);
    Serial.println(" µs");
    Serial.print("  Avg: ");
    Serial.print((float)isr_sum / NUM_SAMPLES, 2);
    Serial.println(" µs");
    Serial.println();
    
    // Print analogRead() time statistics (only if AI channels enabled)
    #if ENABLE_AI_CHANNELS
      Serial.println("analogRead() Time (AI0 + AI1):");
      Serial.print("  Min: ");
      Serial.print(analog_min);
      Serial.println(" µs");
      Serial.print("  Max: ");
      Serial.print(analog_max);
      Serial.println(" µs");
      Serial.print("  Avg: ");
      Serial.print((float)analog_sum / NUM_SAMPLES, 2);
      Serial.println(" µs");
      Serial.println();
    #else
      Serial.println("analogRead() Time (AI0 + AI1):");
      Serial.println("  DISABLED (AI channels not sampled)");
      Serial.println();
    #endif
    
    // Print inter-interrupt interval statistics
    if (valid_intervals > 0) {
      Serial.println("Inter-Interrupt Interval:");
      Serial.print("  Expected: ");
      Serial.print(SAMPLE_INTERVAL_US);
      Serial.println(" µs");
      Serial.print("  Min: ");
      Serial.print(interval_min);
      Serial.println(" µs");
      Serial.print("  Max: ");
      Serial.print(interval_max);
      Serial.println(" µs");
      Serial.print("  Avg: ");
      Serial.print((float)interval_sum / valid_intervals, 2);
      Serial.println(" µs");
      Serial.println();
    }
    
    // Print missed interrupt statistics
    Serial.println("Missed Interrupts:");
    Serial.print("  Count: ");
    Serial.print(missed_interrupt_count);
    Serial.print(" / ");
    Serial.print(valid_intervals);
    Serial.print(" (");
    if (valid_intervals > 0) {
      Serial.print((float)missed_interrupt_count * 100.0f / valid_intervals, 2);
    } else {
      Serial.print("0.00");
    }
    Serial.println("%)");
    Serial.print("  Threshold: > ");
    Serial.print(MISSED_INTERRUPT_THRESHOLD_US);
    Serial.println(" µs");
    Serial.println();
    
    // Warning if blocking detected
    #if ENABLE_AI_CHANNELS
      if (missed_interrupt_count > 0) {
        Serial.println("*** WARNING: Blocking detected! ***");
        Serial.print("analogRead() is taking too long (max: ");
        Serial.print(analog_max);
        Serial.println(" µs)");
        Serial.println("Timer interrupts are being missed.");
        Serial.println("Consider reducing sample rate or using non-blocking ADC.");
      } else if (analog_max > SAMPLE_INTERVAL_US) {
        Serial.println("*** WARNING: analogRead() time exceeds sample interval! ***");
        Serial.print("Max analogRead() time: ");
        Serial.print(analog_max);
        Serial.print(" µs > Sample interval: ");
        Serial.print(SAMPLE_INTERVAL_US);
        Serial.println(" µs");
        Serial.println("This will cause timing issues even if interrupts aren't missed.");
      } else {
        Serial.println("Timing OK: No blocking detected.");
      }
    #else
      if (missed_interrupt_count > 0) {
        Serial.println("*** WARNING: Blocking detected! ***");
        Serial.println("Timer interrupts are being missed (not related to analogRead()).");
      } else {
        Serial.println("Timing OK: No blocking detected.");
      }
    #endif
    
    Serial.println("========================================");
    Serial.println();
    
    // Display individual sample timing data
    Serial.println("Individual Sample Timing Data:");
    #if ENABLE_AI_CHANNELS
      Serial.println("Sample | ISR Time (µs) | analogRead (µs) | Interval (µs)");
      Serial.println("-------|---------------|-----------------|---------------");
    #else
      Serial.println("Sample | ISR Time (µs) | Interval (µs)");
      Serial.println("-------|---------------|---------------");
    #endif
    
    for (uint32_t i = 0; i < NUM_SAMPLES; i++) {
      Serial.print(i);
      Serial.print("      | ");
      Serial.print(isr_execution_time_us[i]);
      Serial.print("           | ");
      #if ENABLE_AI_CHANNELS
        Serial.print(analog_read_time_us[i]);
        Serial.print("              | ");
      #endif
      if (i == 0) {
        Serial.println("N/A (first)");
      } else {
        Serial.println(inter_interval_us[i]);
      }
    }
    
    Serial.println();
    Serial.println("========================================");
    Serial.flush();
  #else
    Serial.println("Timing diagnostics not available for this board.");
  #endif
}

