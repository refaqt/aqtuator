/*
 * Controllino Micro Control Loop with ODrive CAN Torque Output
 * 
 * Control loop that reads 4 analog inputs, calculates torque, and sends to ODrive S1 via CAN.
 * Uses hardware timers for precise timing at configurable sample rates.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Install Controllino board support in Arduino IDE
 * 2. CAN.h library is included with Controllino board support
 * 3. Connect CAN bus: CANH to CANH, CANL to CANL, common GND
 * 4. Add 120-ohm termination resistors at both ends of CAN bus
 * 5. Configure ODrive S1 node ID (default: 0) to match ODRIVE_NODE_ID constant
 * 6. Connect analog inputs A0-A3 to sensors (pins 26-29)
 * 
 * USAGE:
 * - Open Serial Monitor at 115200 baud
 * - Use SET_TIME,<seconds> to set duration (default: 5 seconds)
 * - Use SET_RATE,<hz> to set sample rate (default: 8000 Hz)
 * - Use SET_SCALE,<value> to set torque scaling factor (default: 1.0)
 * - Use SET_F,<value> to set frequency f in Hz (default: 10.0)
 * - Use S or s to start the control loop
 * 
 * NOTE: Serial communication is blocked during control loop execution.
 */

#include <CAN.h>
#include <math.h>

#ifdef ARDUINO_ARCH_RP2040
  #include <hardware/timer.h>
  #include <hardware/irq.h>
  #include <hardware/adc.h>
#endif

// ============================================================================
// Configuration Constants
// ============================================================================

#define SERIAL_BAUD 115200
#define ODRIVE_NODE_ID 0
#define CAN_BAUD_RATE 1000000  // 1 Mbps

// ODrive CAN message IDs (CANSimple protocol)
#define CAN_ID_SET_TORQUE 0x0E

// ADC pins (Controllino Micro - RP2040 GPIO26-29 are ADC0-3)
#define ADC_PIN_A0 26
#define ADC_PIN_A1 27
#define ADC_PIN_A2 28
#define ADC_PIN_A3 29

// Torque limits
#define TORQUE_MIN -2.0f
#define TORQUE_MAX 2.0f

// ============================================================================
// State Variables
// ============================================================================

volatile bool control_loop_active = false;
volatile bool serial_blocked = false;
bool completion_sent = false;

float control_duration_sec = 5.0;  // Default 5 seconds
uint32_t sample_rate_hz = 8000;     // Default 8000 Hz
float torque_scale = 0.0001;            // Default scaling factor
float frequency_hz = 10.0;           // Default frequency f: 10 Hz

unsigned long loop_start_time = 0;
volatile uint32_t sample_index = 0;        // Current sample index (for time calculation)
volatile float previous_adc_sum = 0.0f;    // Previous sum of ADC values for derivative
float sample_period = 0.0f;                // Sample period in seconds (1.0 / sample_rate_hz)

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

// ============================================================================
// Function Prototypes
// ============================================================================

void setupCAN();
void setupTimer();
void setupADC();
bool timerCallback(struct repeating_timer *t);
void timerISR();
void sendTorqueSetpoint(float torque);
void processCommand(String cmd);
float clampTorque(float torque);

// ============================================================================
// Setup Function
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(2000);  // Delay for Controllino stability
  Serial.flush();
  
  Serial.println("========================================");
  Serial.println("Controllino Micro Control Loop");
  Serial.println("========================================");
  Serial.flush();
  
  // Initialize CAN
  setupCAN();
  
  // Initialize ADC (RP2040)
  #ifdef ARDUINO_ARCH_RP2040
    setupADC();
  #endif
  
  Serial.println("INFO: System initialized");
  Serial.println("INFO: Ready for commands");
  Serial.println();
  // Initialize sample period
  sample_period = 1.0f / (float)sample_rate_hz;
  
  Serial.println("Commands:");
  Serial.println("  S or s - Start control loop");
  Serial.println("  SET_TIME,<seconds> - Set duration (default: 5.0)");
  Serial.println("  SET_RATE,<hz> - Set sample rate (default: 8000)");
  Serial.println("  SET_SCALE,<value> - Set torque scale (default: 1.0)");
  Serial.println("  SET_F,<value> - Set frequency f in Hz (default: 10.0)");
  Serial.flush();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Skip reading Serial if blocked during operation
  if (serial_blocked) {
    return;
  }
  
  // Check for completion notification
  if (!completion_sent && !control_loop_active && !serial_blocked) {
    Serial.println("ACK: Control loop complete");
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
// CAN Setup
// ============================================================================

void setupCAN() {
  Serial.print("Initializing CAN bus at ");
  Serial.print(CAN_BAUD_RATE);
  Serial.println(" bps...");
  
  #ifdef ARDUINO_ARCH_RP2040
    SPI1.setRX(PIN_SPI1_MISO);
    SPI1.setTX(PIN_SPI1_MOSI);
    SPI1.setSCK(PIN_SPI1_SCK);
  #endif
  
  if (!CAN.begin(CAN_BAUD_RATE)) {
    Serial.println("ERROR: CAN initialization failed!");
    Serial.println("Check CAN wiring and connections.");
    while (1) {
      delay(1000);
    }
  }
  Serial.println("CAN bus initialized successfully.");
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
  if (sample_rate_hz == 0) {
    Serial.println("ERROR: Sample rate not set");
    return;
  }
  
  #ifdef ARDUINO_ARCH_RP2040
    // Cancel existing timer if running
    if (timer_initialized) {
      cancel_repeating_timer(&timer);
      timer_initialized = false;
    }
    
    // Calculate sample interval in microseconds
    unsigned long sample_interval_us = 1000000UL / sample_rate_hz;
    
    // Use RP2040 hardware timer (alarm pool)
    // Negative delay means repeating timer
    int64_t delay_us = -((int64_t)sample_interval_us);
    
    if (add_repeating_timer_us(delay_us, timerCallback, NULL, &timer)) {
      timer_initialized = true;
      Serial.print("Hardware timer initialized: ");
      Serial.print(sample_rate_hz);
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
// Timer ISR - Control Loop
// ============================================================================

void timerISR() {
  if (!control_loop_active) {
    return;
  }
  
  // Check if duration has been exceeded
  unsigned long elapsed_ms = millis() - loop_start_time;
  if (elapsed_ms >= (unsigned long)(control_duration_sec * 1000.0f)) {
    // Duration exceeded - stop control loop
    sendTorqueSetpoint(0.0f);
    control_loop_active = false;
    serial_blocked = false;
    sample_index = 0;
    previous_adc_sum = 0.0f;
    return;
  }
  
  // Read ADC channels (hardware-timed)
  uint32_t adc_sum = 0;
  
  #ifdef ARDUINO_ARCH_RP2040
    for (int ch = 0; ch < 4; ch++) {
      uint8_t gpio_pin = adc_channels[ch];
      adc_select_input(gpio_pin - 26);  // GPIO26-29 map to ADC0-3
      uint16_t adc_raw = adc_read();    // 12-bit ADC: 0-4095
      adc_sum += adc_raw;
    }
  #else
    // Fallback: use analogRead (not hardware-timed, but works)
    adc_sum += analogRead(A0);
    adc_sum += analogRead(A1);
    adc_sum += analogRead(A2);
    adc_sum += analogRead(A3);
  #endif
  
  // Calculate derivative: dA = d(A0+A1+A2+A3)/dt
  float current_sum = (float)adc_sum;
  float dA = 0.0f;
  
  if (sample_index > 0) {
    // Calculate derivative: (current_sum - previous_sum) / sample_period
    dA = (current_sum - previous_adc_sum) / sample_period;
  }
  // First iteration: dA = 0 (no previous value)
  
  // Update previous_adc_sum for next iteration
  previous_adc_sum = current_sum;
  
  // Calculate time: t = sample_index * sample_period
  float t = (float)sample_index * sample_period;
  
  // Calculate torque: torque_scale * dA * sin(2*PI*frequency_hz*t)
  float output_torque = torque_scale * dA * sin(2.0f * PI * frequency_hz * t);
  
  // Increment sample index
  sample_index++;
  
  // Clamp torque to -2.0 to +2.0 Nm
  output_torque = clampTorque(output_torque);
  
  // Send torque command via CAN
  sendTorqueSetpoint(output_torque);
}

// ============================================================================
// Torque Clamping
// ============================================================================

float clampTorque(float torque) {
  if (torque < TORQUE_MIN) {
    return TORQUE_MIN;
  } else if (torque > TORQUE_MAX) {
    return TORQUE_MAX;
  }
  return torque;
}

// ============================================================================
// CAN Communication
// ============================================================================

void sendTorqueSetpoint(float torque) {
  // Calculate CAN ID: ODrive uses node_id in bits 5-7
  uint32_t canId = CAN_ID_SET_TORQUE + (ODRIVE_NODE_ID << 5);
  
  // Begin CAN packet
  CAN.beginPacket(canId);
  
  // Write torque (4 bytes, little-endian float)
  uint8_t* torqueBytes = (uint8_t*)&torque;
  CAN.write(torqueBytes[0]);
  CAN.write(torqueBytes[1]);
  CAN.write(torqueBytes[2]);
  CAN.write(torqueBytes[3]);
  
  // Write reserved bytes (4 bytes, set to 0)
  CAN.write(0);
  CAN.write(0);
  CAN.write(0);
  CAN.write(0);
  
  // End packet and send
  CAN.endPacket();
}

// ============================================================================
// Command Processing
// ============================================================================

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.equalsIgnoreCase("S")) {
    // Start control loop
    if (control_loop_active) {
      Serial.println("ERROR: Control loop already running");
      return;
    }
    
    // Cancel existing timer if running
    #ifdef ARDUINO_ARCH_RP2040
      if (timer_initialized) {
        cancel_repeating_timer(&timer);
        timer_initialized = false;
      }
    #endif
    
    // Setup timer with current sample rate
    setupTimer();
    
    if (!timer_initialized) {
      Serial.println("ERROR: Timer initialization failed");
      return;
    }
    
    // Start control loop
    loop_start_time = millis();
    sample_index = 0;           // Reset sample index
    previous_adc_sum = 0.0f;    // Reset previous sum
    control_loop_active = true;
    serial_blocked = true;
    completion_sent = false;
    
    Serial.println("ACK: Control loop started");
    Serial.flush();
    
  } else if (cmd.startsWith("SET_TIME")) {
    // Set duration: SET_TIME,<seconds>
    if (control_loop_active) {
      Serial.println("ERROR: Cannot change duration while control loop is running");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing duration value in SET_TIME command");
      return;
    }
    
    float duration = cmd.substring(comma_pos + 1).toFloat();
    if (duration <= 0) {
      Serial.println("ERROR: Invalid duration (must be > 0)");
      return;
    }
    
    control_duration_sec = duration;
    Serial.print("ACK: Duration set to ");
    Serial.print(control_duration_sec);
    Serial.println(" seconds");
    
  } else if (cmd.startsWith("SET_RATE")) {
    // Set sample rate: SET_RATE,<hz>
    if (control_loop_active) {
      Serial.println("ERROR: Cannot change sample rate while control loop is running");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing rate value in SET_RATE command");
      return;
    }
    
    uint32_t rate = cmd.substring(comma_pos + 1).toInt();
    if (rate == 0 || rate > 50000) {
      Serial.println("ERROR: Invalid sample rate (must be > 0 and <= 50000)");
      return;
    }
    
    sample_rate_hz = rate;
    // Recalculate sample period
    sample_period = 1.0f / (float)sample_rate_hz;
    
    Serial.print("ACK: Sample rate set to ");
    Serial.print(sample_rate_hz);
    Serial.println(" Hz");
    
    // Reinitialize timer if it was already initialized
    if (timer_initialized) {
      setupTimer();
    }
    
  } else if (cmd.startsWith("SET_SCALE")) {
    // Set torque scale: SET_SCALE,<value>
    if (control_loop_active) {
      Serial.println("ERROR: Cannot change torque scale while control loop is running");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing scale value in SET_SCALE command");
      return;
    }
    
    float scale = cmd.substring(comma_pos + 1).toFloat();
    if (isnan(scale) || isinf(scale)) {
      Serial.println("ERROR: Invalid torque scale value");
      return;
    }
    
    torque_scale = scale;
    Serial.print("ACK: Torque scale set to ");
    Serial.println(torque_scale);
    
  } else if (cmd.startsWith("SET_F")) {
    // Set frequency: SET_F,<value>
    if (control_loop_active) {
      Serial.println("ERROR: Cannot change frequency while control loop is running");
      return;
    }
    
    int comma_pos = cmd.indexOf(',');
    if (comma_pos < 0) {
      Serial.println("ERROR: Missing frequency value in SET_F command");
      return;
    }
    
    float freq = cmd.substring(comma_pos + 1).toFloat();
    if (isnan(freq) || isinf(freq) || freq < 0) {
      Serial.println("ERROR: Invalid frequency value (must be >= 0)");
      return;
    }
    
    frequency_hz = freq;
    Serial.print("ACK: Frequency set to ");
    Serial.print(frequency_hz);
    Serial.println(" Hz");
    
  } else if (cmd.length() > 0) {
    Serial.print("ERROR: Unknown command: ");
    Serial.println(cmd);
  }
}

