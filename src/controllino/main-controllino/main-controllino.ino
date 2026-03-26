/*
 * Controllino Micro ODrive PWM Multisine Control and Data Acquisition
 * 
 * Synchronized command output via PWM (RC-filtered analog) and analog input acquisition.
 * Uses hardware timers for precise timing.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Install Controllino board support in Arduino IDE
 * 2. Connect Controllino PWM output (D0) through RC filter to ODrive GPIO1 (analog input)
 * 3. Connect analog inputs A0-A3 to sensors
 * 
 * USAGE:
 * - Open Serial Monitor at 115200 baud
 * - Upload CSV file with UPLOAD_CSV command
 * - Use START_OUTPUT,<duration> for testing (PWM output only)
 * - Use START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay> for full operation
 * 
 * NOTE: Serial communication is blocked during torque output for maximum performance.
 */

#ifdef ARDUINO_ARCH_RP2040
  #include <hardware/timer.h>
  #include <hardware/irq.h>
  #include <hardware/adc.h>
#endif

// ============================================================================
// Configuration Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define MAX_CSV_SAMPLES 2000   // Maximum samples in CSV file (20 KB)
#define MAX_ACQ_SAMPLES 4000   // Maximum acquisition samples (5 channels: 4 inputs + output_voltage)
                                // Memory: 4000 × 5 × 4 bytes = 80 KB
                                // Total: CSV (20 KB) + Acquisition (80 KB) = 100 KB (RP2040 has 264KB RAM)

// PWM output pin (Controllino MICRO: D0 / GPIO0 header)
#define PWM_OUTPUT_PIN D0

// PWM configuration (mirrors test-pwm-output defaults)
#define SYS_CLOCK_HZ 125000000UL
#define PWM_RESOLUTION_BITS 9
#define PWM_TOP ((1u << PWM_RESOLUTION_BITS) - 1u)
#define PWM_FREQ_HZ (SYS_CLOCK_HZ / ((uint32_t)PWM_TOP + 1u))

// Clamp: never exceed 0.84 of maximum PWM value (per requirement)
#define PWM_MAX_FRAC 0.84f

// ODrive GPIO1 analog mapping (used to convert CSV "torque" sample into analog voltage)
// Voltage mapping is assumed 0..3.3V on ODrive GPIO1.
#define ODRIVE_GPIO1_MIN_TORQUE (-3.874f)
#define ODRIVE_GPIO1_MAX_TORQUE (2.0f)
#define ODRIVE_GPIO1_VREF (3.3f)

// ODrive GPIO1 has a pull-up to 5V. Together with the RC series resistance,
// this means PWM=0% does not yield 0V at the ODrive pin. We must compensate
// when converting a desired ODrive-pin voltage to a PWM duty cycle.
#define ODRIVE_GPIO1_PULLUP_OHMS (2700.0f)
#define RC_SERIES_OHMS (720.0f)
#define ODRIVE_GPIO1_PULLUP_V (5.0f)

// ADC pins (Controllino Micro - check pin mapping)
// RP2040 ADC channels: GPIO26-29 are ADC0-3
// Controllino Micro A0-A3 mapping: hardware-timed ADC channels
#define ADC_PIN_A0 26
#define ADC_PIN_A1 27
#define ADC_PIN_A2 28
#define ADC_PIN_A3 29

// Analog input scaling (A0-A3)
// Note: RP2040 ADC is 12-bit (0..4095). In this project we scale those counts
// to an external full-scale of 0..25.8 V (e.g. due to front-end scaling/divider).
#define A0A3_FULL_SCALE_V (25.8f)
#define RP2040_ADC_MAX_COUNTS (4095.0f)

// ============================================================================
// State Machine
// ============================================================================

enum State {
  STATE_IDLE,
  STATE_OUTPUTTING,
  STATE_ACQUIRING,
  STATE_TRANSFERRING
};

State current_state = STATE_IDLE;

// ============================================================================
// CSV Data Storage
// ============================================================================

float csv_torque_values[MAX_CSV_SAMPLES];
uint32_t csv_sample_count = 0;
float csv_sample_period = 0.001;  // Default 1kHz
uint32_t csv_sample_rate_hz = 1000;

// ============================================================================
// Acquisition Data Storage
// ============================================================================

float acq_buffer[MAX_ACQ_SAMPLES * 5];  // 5 channels: A0-A3, output_voltage_command
uint32_t acq_sample_count = 0;
volatile uint32_t acq_index = 0;
float acq_sample_period = 0.001;

// ============================================================================
// Operation Control
// ============================================================================

volatile bool torque_output_active = false;
volatile bool acquisition_active = false;
volatile bool serial_blocked = false;
bool parsing_csv = false;
bool completion_sent = false;
bool is_test_output_mode = false;  // True for START_OUTPUT, false for START_IDENTIFICATION

// Timing control
volatile uint32_t csv_index = 0;  // Current position in CSV for cyclic playback
volatile unsigned long sample_interval_us = 0;
volatile unsigned long last_sample_time_us = 0;

// Acquisition timing
uint32_t required_acq_samples = 0;
unsigned long acquisition_start_time = 0;
unsigned long acquisition_delay_ms = 0;
unsigned long output_start_time = 0;
unsigned long output_duration_ms = 0;

// ============================================================================
// Hardware Timer (RP2040)
// ============================================================================

#ifdef ARDUINO_ARCH_RP2040
  struct repeating_timer timer;
  bool timer_initialized = false;
  
  // ADC configuration
  bool adc_initialized = false;
  uint8_t adc_channels[4] = {ADC_PIN_A0, ADC_PIN_A1, ADC_PIN_A2, ADC_PIN_A3};
#endif

// PWM update handoff (timer ISR -> loop)
static volatile bool pwm_update_pending = false;
static volatile uint16_t pwm_duty_pending = 0;
static volatile float output_voltage_pending = 0.0f;

// ============================================================================
// Function Prototypes
// ============================================================================

void setupTimer();
void setupADC();
bool timerCallback(struct repeating_timer *t);
void timerISR();
bool parseCSVFromSerial(uint32_t expected_lines);
void processCommand(String cmd);
void printStatus();

static inline float clampf(float x, float lo, float hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}

static inline float torqueToOdriveGpio1Voltage(float torque) {
  const float span = (ODRIVE_GPIO1_MAX_TORQUE - ODRIVE_GPIO1_MIN_TORQUE);
  if (span == 0.0f) return 0.0f;
  float norm = (torque - ODRIVE_GPIO1_MIN_TORQUE) / span; // 0..1 ideally
  norm = clampf(norm, 0.0f, 1.0f);
  return norm * ODRIVE_GPIO1_VREF;
}

static inline float odriveGpio1VoltageToPwmVoltage(float v_pin) {
  const float Rs = RC_SERIES_OHMS;
  const float Rp = ODRIVE_GPIO1_PULLUP_OHMS;
  const float Vp = ODRIVE_GPIO1_PULLUP_V;

  v_pin = clampf(v_pin, 0.0f, ODRIVE_GPIO1_VREF);

  if (Rs <= 0.0f || Rp <= 0.0f) {
    // Fallback: best effort without divider compensation
    return v_pin;
  }

  const float g_sum = (1.0f / Rs) + (1.0f / Rp);
  if (g_sum <= 0.0f) return 0.0f;

  // Invert: V_pin = (V_pwm/Rs + Vp/Rp) / (1/Rs + 1/Rp)
  float v_pwm = Rs * (v_pin * g_sum - (Vp / Rp));
  return clampf(v_pwm, 0.0f, ODRIVE_GPIO1_VREF);
}

static inline uint16_t voltageToPwmDuty(float v) {
  v = clampf(v, 0.0f, ODRIVE_GPIO1_VREF);
  float duty_f = (v / ODRIVE_GPIO1_VREF) * (float)PWM_TOP;
  float max_duty = PWM_MAX_FRAC * (float)PWM_TOP;
  if (duty_f > max_duty) duty_f = max_duty;
  if (duty_f < 0.0f) duty_f = 0.0f;
  return (uint16_t)(duty_f + 0.5f);
}

// ============================================================================
// Setup Function
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(2000);  // Longer delay for Controllino stability
  Serial.flush();
  
  Serial.println("========================================");
  Serial.println("Controllino Micro ODrive Control");
  Serial.println("========================================");
  Serial.flush();

  // Initialize PWM output (D0 -> RC filter -> ODrive GPIO1)
  pinMode(PWM_OUTPUT_PIN, OUTPUT);
  analogWriteFreq(PWM_FREQ_HZ);
  analogWriteRange(PWM_TOP);
  analogWrite(PWM_OUTPUT_PIN, 0);
  pwm_update_pending = false;
  
  // Initialize ADC (RP2040)
  #ifdef ARDUINO_ARCH_RP2040
    setupADC();
  #endif
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
  Serial.println();
  Serial.println("Commands:");
  Serial.println("  UPLOAD_CSV,<num_lines>");
  Serial.println("  START_OUTPUT,<duration>");
  Serial.println("  START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>");
  Serial.println("  GET_DATA");
  Serial.println("  GET_STATUS");
  Serial.flush();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Always apply latest PWM update, even while serial is blocked.
  if (pwm_update_pending) {
    noInterrupts();
    const uint16_t duty = pwm_duty_pending;
    pwm_update_pending = false;
    interrupts();
    analogWrite(PWM_OUTPUT_PIN, (int)duty);
  }

  // Skip reading Serial if parsing CSV
  if (parsing_csv) {
    delay(1);
    return;
  }
  
  // Skip reading Serial if blocked during operation
  if (serial_blocked) {
    // Don't set completion_sent here - wait until serial is unblocked
    // The completion message will be sent when serial_blocked becomes false
    return;
  }
  
  // Check for test output completion (START_OUTPUT mode)
  if (is_test_output_mode && !completion_sent && !torque_output_active && !serial_blocked && current_state == STATE_IDLE) {
    Serial.println("ACK: Output complete");
    Serial.flush();
    completion_sent = true;
    is_test_output_mode = false;  // Reset flag
  }
  
  // Check for acquisition completion notification (START_IDENTIFICATION mode)
  if (!is_test_output_mode && !completion_sent && acq_sample_count > 0 && !acquisition_active && !torque_output_active && !serial_blocked) {
    Serial.println("ACK: Acquisition complete");
    Serial.flush();
    completion_sent = true;
  }
  
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }
}

// ============================================================================
// ADC Setup (RP2040)
// ============================================================================

void setupADC() {
  #ifdef ARDUINO_ARCH_RP2040
    adc_init();
    // Configure ADC pins (will be read in ISR)
    for (int i = 0; i < 4; i++) {
      adc_gpio_init(adc_channels[i]);
    }
    adc_initialized = true;
    Serial.println("ADC initialized (hardware-timed via timer ISR)");
  #endif
}

// ============================================================================
// Timer Setup
// ============================================================================

void setupTimer() {
  if (csv_sample_rate_hz == 0) {
    Serial.println("ERROR: Sample rate not set");
    return;
  }
  
  sample_interval_us = 1000000UL / csv_sample_rate_hz;
  
  #ifdef ARDUINO_ARCH_RP2040
    // Cancel existing timer if running
    if (timer_initialized) {
      cancel_repeating_timer(&timer);
      timer_initialized = false;
    }
    
    // Use RP2040 hardware timer (alarm pool)
    // Negative delay means repeating timer
    int64_t delay_us = -((int64_t)sample_interval_us);
    
    if (add_repeating_timer_us(delay_us, timerCallback, NULL, &timer)) {
      timer_initialized = true;
      Serial.print("Hardware timer initialized: ");
      Serial.print(csv_sample_rate_hz);
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
  unsigned long current_time_us = micros();
  last_sample_time_us = current_time_us;
  
  float current_torque = 0.0f;
  float current_output_voltage = 0.0f;
  
  // ========================================================================
  // Command Output (if active): CSV torque -> ODrive GPIO1 voltage -> PWM duty
  // ========================================================================
  if (torque_output_active && csv_sample_count > 0) {
    // Get torque value from CSV (cyclic playback)
    current_torque = csv_torque_values[csv_index];
    csv_index = (csv_index + 1) % csv_sample_count;
    
    // Torque (Nm) -> desired ODrive GPIO1 pin voltage (0..3.3V)
    current_output_voltage = torqueToOdriveGpio1Voltage(current_torque);
    // Compensate for pull-up divider to get required PWM-side voltage (0..3.3V)
    float pwm_voltage = odriveGpio1VoltageToPwmVoltage(current_output_voltage);
    uint16_t duty = voltageToPwmDuty(pwm_voltage);
    pwm_duty_pending = duty;
    output_voltage_pending = current_output_voltage;
    pwm_update_pending = true;
    
    // Check if output duration expired (for START_OUTPUT test mode)
    if (output_duration_ms > 0 && is_test_output_mode) {
      unsigned long elapsed = millis() - output_start_time;
      if (elapsed >= output_duration_ms) {
        // Set output to zero before stopping
        pwm_duty_pending = 0;
        output_voltage_pending = 0.0f;
        pwm_update_pending = true;
        
        torque_output_active = false;
        output_duration_ms = 0;
        serial_blocked = false;  // Unblock serial to send completion message
        
        // Note: Serial.println cannot be called from ISR context
        // Completion message will be sent from loop() function
        current_state = STATE_IDLE;
      }
    }
  }
  
  // ========================================================================
  // Check if acquisition should start (after delay)
  // ========================================================================
  if (torque_output_active && !acquisition_active && required_acq_samples > 0) {
    unsigned long elapsed = millis() - output_start_time;
    if (elapsed >= acquisition_delay_ms) {
      // Delay has passed - start acquisition
      acquisition_active = true;
      acq_index = 0;
      acq_sample_count = 0;
      current_state = STATE_ACQUIRING;
    }
  }
  
  // ========================================================================
  // Acquisition (if active)
  // ========================================================================
  if (acquisition_active && acq_index < MAX_ACQ_SAMPLES) {
    float *sample_ptr = &acq_buffer[acq_index * 5];
    
    // Read ADC channels (hardware-timed) - only 4 channels (A0-A3)
    #ifdef ARDUINO_ARCH_RP2040
      // RP2040 has 4 ADC inputs (GPIO26-29), read A0-A3 using hardware-timed adc_read()
      for (int ch = 0; ch < 4; ch++) {
        uint8_t gpio_pin = adc_channels[ch];
        // All pins are valid ADC inputs (GPIO26-29 map to ADC0-3)
        adc_select_input(gpio_pin - 26);
        uint16_t adc_raw = adc_read();
        // Convert ADC counts to scaled input voltage (0..A0A3_FULL_SCALE_V)
        sample_ptr[ch] = (float)adc_raw * A0A3_FULL_SCALE_V / RP2040_ADC_MAX_COUNTS;
      }
    #else
      // Fallback: use analogRead (not hardware-timed, but works)
      sample_ptr[0] = analogRead(A0) * A0A3_FULL_SCALE_V / RP2040_ADC_MAX_COUNTS;
      sample_ptr[1] = analogRead(A1) * A0A3_FULL_SCALE_V / RP2040_ADC_MAX_COUNTS;
      sample_ptr[2] = analogRead(A2) * A0A3_FULL_SCALE_V / RP2040_ADC_MAX_COUNTS;
      sample_ptr[3] = analogRead(A3) * A0A3_FULL_SCALE_V / RP2040_ADC_MAX_COUNTS;
    #endif
    
    // Store commanded output voltage (what we're trying to drive into ODrive GPIO1)
    // This is derived from the CSV "torque" sample via the ODrive analog mapping.
    sample_ptr[4] = current_output_voltage;
    
    acq_index++;
    acq_sample_count = acq_index;
    
    // Check if acquisition duration reached
    if (required_acq_samples > 0 && acq_index >= required_acq_samples) {
      acquisition_active = false;
      
      // Set output to zero after acquisition completes
      pwm_duty_pending = 0;
      output_voltage_pending = 0.0f;
      pwm_update_pending = true;
      
      torque_output_active = false;
      serial_blocked = false;  // Unblock serial to send completion message
      
      // Note: Serial.println cannot be called from ISR context
      // Completion message will be sent from loop() function
      current_state = STATE_IDLE;
    } else if (acq_index >= MAX_ACQ_SAMPLES) {
      // Buffer limit reached
      acquisition_active = false;
      
      // Set output to zero
      pwm_duty_pending = 0;
      output_voltage_pending = 0.0f;
      pwm_update_pending = true;
      
      torque_output_active = false;
      serial_blocked = false;
      
      // Note: Serial.println cannot be called from ISR context
      // Completion message will be sent from loop() function
      current_state = STATE_IDLE;
    }
  }
}

// ============================================================================
// CSV Upload Protocol (based on giga-acquisition.ino)
// ============================================================================

bool parseCSVFromSerial(uint32_t expected_lines) {
  csv_sample_count = 0;
  bool sample_period_extracted = false;
  float first_time = -1.0;
  float second_time = -1.0;
  const unsigned long timeout_per_line_ms = 5000;  // 5 seconds max per line
  
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
    
    if (line.length() == 0) continue;
    
    // Skip header comment lines (starting with #)
    if (line.startsWith("#")) {
      // Try to extract sample period from metadata header
      // Format: "# fs: 8000.0 Hz" or "# fs: 8000.000000 Hz"
      int fs_pos = line.indexOf("fs:");
      if (fs_pos >= 0) {
        // Extract everything after "fs:"
        int fs_start = fs_pos + 3;  // Position after "fs:"
        String fs_str = line.substring(fs_start);
        fs_str.trim();
        
        // Find "Hz" (case-insensitive search)
        String fs_str_lower = fs_str;
        fs_str_lower.toLowerCase();
        int hz_pos = fs_str_lower.indexOf("hz");
        if (hz_pos > 0) {
          // Extract the number part from original string
          fs_str = fs_str.substring(0, hz_pos);
          fs_str.trim();
          float fs = fs_str.toFloat();
          if (fs > 0 && fs < 1000000) {
            csv_sample_period = 1.0 / fs;
            csv_sample_rate_hz = (uint32_t)(fs + 0.5f);  // Round to nearest integer
            sample_period_extracted = true;
            Serial.print("INFO: Extracted sample rate from header: ");
            Serial.print(csv_sample_rate_hz);
            Serial.println(" Hz");
          }
        }
      }
      continue;
    }
    
    // Skip CSV header row
    if (line.equalsIgnoreCase("Time_s,Signal") || line.equalsIgnoreCase("Time_s,Torque")) {
      continue;
    }
    
    // Parse data rows (comma-separated: time, torque)
    int comma_pos = line.indexOf(',');
    if (comma_pos > 0) {
      String time_str = line.substring(0, comma_pos);
      String torque_str = line.substring(comma_pos + 1);
      time_str.trim();
      torque_str.trim();
      
      float time_val = time_str.toFloat();
      float torque = torque_str.toFloat();
      
      // Validate parsed values
      if (isnan(time_val) || isnan(torque) || isinf(time_val) || isinf(torque)) {
        continue;
      }
      
      // Store first two time values to calculate sample period if not extracted
      if (first_time < 0 && time_val >= 0) {
        first_time = time_val;
      } else if (second_time < 0 && !sample_period_extracted && time_val > first_time) {
        second_time = time_val;
        if (second_time > first_time && second_time - first_time < 10.0) {
          csv_sample_period = second_time - first_time;
          float calculated_rate = 1.0 / csv_sample_period;
          csv_sample_rate_hz = (uint32_t)(calculated_rate + 0.5f);  // Round to nearest integer
          sample_period_extracted = true;
        }
      }
      
      // Store torque value (no range validation - torque can be positive or negative)
      csv_torque_values[csv_sample_count++] = torque;
    } else {
      // Fallback: try to parse as single value
      float torque = line.toFloat();
      if (!isnan(torque) && !isinf(torque)) {
        csv_torque_values[csv_sample_count++] = torque;
        if (!sample_period_extracted && csv_sample_count == 2) {
          csv_sample_period = 0.001;  // Default 1kHz
          csv_sample_rate_hz = 1000;
          sample_period_extracted = true;
        }
      }
    }
  }
  
  // Validate sample period - use fallback if extraction failed
  if (!sample_period_extracted) {
    if (csv_sample_count > 0) {
      csv_sample_period = 0.001;  // Default 1kHz
      csv_sample_rate_hz = 1000;
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
    Serial.println("ERROR: No samples loaded");
    return false;
  }
  
  Serial.print("INFO: Loaded ");
  Serial.print(csv_sample_count);
  Serial.print(" samples, period: ");
  Serial.print(csv_sample_period, 6);
  Serial.print("s (");
  Serial.print(csv_sample_rate_hz);
  Serial.println(" Hz)");
  
  // Initialize timer with CSV sample rate
  setupTimer();
  
  return true;
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("UPLOAD_CSV")) {
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
    while (Serial.available() > 0) {
      Serial.read();
    }
    Serial.println("READY");
    Serial.flush();
    
    if (parseCSVFromSerial(expected_lines)) {
      Serial.println("ACK: CSV loaded");
    } else {
      Serial.println("NACK: CSV load failed");
    }
    
    // Clear any leftover data from serial buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
    parsing_csv = false;  // Clear flag when done
    
  } else if (cmd.startsWith("START_OUTPUT")) {
    // Testing command: START_OUTPUT,<duration>
    if (csv_sample_count == 0) {
      Serial.println("ERROR: No CSV file loaded");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing duration in START_OUTPUT command");
      return;
    }
    
    float duration = cmd.substring(comma_pos + 1).toFloat();
    if (duration <= 0) {
      Serial.println("ERROR: Invalid duration");
      return;
    }
    
    // Prepare all state variables first
    output_duration_ms = (unsigned long)(duration * 1000.0f);
    output_start_time = millis();
    csv_index = 0;
    current_state = STATE_OUTPUTTING;
    is_test_output_mode = true;  // Mark as test output mode
    completion_sent = false;  // Reset completion flag
    
    // Send ACK BEFORE starting timer and blocking serial
    Serial.println("ACK: Output started");
    Serial.flush();
    
    // Now start the timer and block serial
    torque_output_active = true;
    serial_blocked = true;  // Block serial during output
    
  } else if (cmd.startsWith("START_IDENTIFICATION")) {
    // Main command: START_IDENTIFICATION,<acquisition_duration>,<acquisition_start_delay>
    if (csv_sample_count == 0) {
      Serial.println("ERROR: No CSV file loaded");
      return;
    }
    
    int comma1 = cmd.indexOf(',');
    int comma2 = cmd.indexOf(',', comma1 + 1);
    
    if (comma1 < 0 || comma2 < 0) {
      Serial.println("ERROR: Missing parameters in START_IDENTIFICATION command");
      return;
    }
    
    float acq_duration = cmd.substring(comma1 + 1, comma2).toFloat();
    float acq_delay = cmd.substring(comma2 + 1).toFloat();
    
    if (acq_duration <= 0 || acq_delay < 0) {
      Serial.println("ERROR: Invalid parameters");
      return;
    }
    
    // Calculate required samples
    required_acq_samples = (uint32_t)(acq_duration / csv_sample_period);
    if (required_acq_samples > MAX_ACQ_SAMPLES) {
      Serial.print("ERROR: Acquisition duration too long. Maximum: ");
      Serial.print((float)MAX_ACQ_SAMPLES * csv_sample_period);
      Serial.println(" seconds");
      return;
    }
    
    // Reset acquisition state
    acq_index = 0;
    acq_sample_count = 0;
    acq_sample_period = csv_sample_period;
    completion_sent = false;
    
    // Prepare all state variables
    csv_index = 0;
    output_start_time = millis();
    acquisition_delay_ms = (unsigned long)(acq_delay * 1000.0f);
    acquisition_start_time = output_start_time + acquisition_delay_ms;
    current_state = STATE_OUTPUTTING;
    is_test_output_mode = false;  // Mark as identification mode (not test output)
    output_duration_ms = 0;  // No duration limit for identification mode
    
    // Send ACK BEFORE starting timer and blocking serial
    Serial.println("ACK: Identification started");
    Serial.flush();
    
    // Now start the timer and block serial
    torque_output_active = true;
    acquisition_active = false;  // Will be activated after delay
    serial_blocked = true;  // Block serial during operation
    
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
  Serial.print(5);  // 5 channels: A0-A3, output_voltage_command
    Serial.println();
    
    // Send data samples (text format)
    for (uint32_t i = 0; i < acq_sample_count; i++) {
      float *sample_ptr = &acq_buffer[i * 5];
      
      Serial.print(sample_ptr[0], 4);  // A0
      for (int ch = 1; ch < 5; ch++) {  // A1-A3, output_voltage_command
        Serial.print(",");
        Serial.print(sample_ptr[ch], 4);
      }
      Serial.println();
      
      // Small delay to prevent serial buffer overflow
      if (i % 100 == 0) delay(1);
    }
    
    Serial.println("DATA_END");
    current_state = STATE_IDLE;
    
  } else if (cmd.startsWith("GET_STATUS")) {
    printStatus();
    
  } else if (cmd.length() > 0) {
    Serial.print("ERROR: Unknown command: ");
    Serial.println(cmd);
  }
}

// ============================================================================
// Status Printing
// ============================================================================

void printStatus() {
  Serial.println("\n========================================");
  Serial.println("Current Status:");
  Serial.println("========================================");
  Serial.print("State: ");
  switch (current_state) {
    case STATE_IDLE: Serial.println("IDLE"); break;
    case STATE_OUTPUTTING: Serial.println("OUTPUTTING"); break;
    case STATE_ACQUIRING: Serial.println("ACQUIRING"); break;
    case STATE_TRANSFERRING: Serial.println("TRANSFERRING"); break;
  }
  Serial.print("CSV Samples: ");
  Serial.println(csv_sample_count);
  Serial.print("CSV Sample Rate: ");
  Serial.print(csv_sample_rate_hz);
  Serial.println(" Hz");
  Serial.print("CSV Sample Period: ");
  Serial.print(csv_sample_period, 6);
  Serial.println(" s");
  Serial.print("Acquisition Samples: ");
  Serial.println(acq_sample_count);
  Serial.print("Torque Output: ");
  Serial.println(torque_output_active ? "ACTIVE" : "INACTIVE");
  Serial.print("Acquisition: ");
  Serial.println(acquisition_active ? "ACTIVE" : "INACTIVE");
  Serial.print("Serial Blocked: ");
  Serial.println(serial_blocked ? "YES" : "NO");
  Serial.println("========================================\n");
}

