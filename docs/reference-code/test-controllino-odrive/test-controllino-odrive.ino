/*
 * Controllino Micro ODrive CAN Sine Wave Generator
 * 
 * Generates sine waves with user-configurable amplitude and frequency,
 * transmitting them as position or torque setpoints to ODrive S1 via CAN bus.
 * Uses hardware timers for precise 8kHz sampling (default, configurable).
 * 
 * SETUP INSTRUCTIONS:
 * 1. Install Controllino board support in Arduino IDE
 * 2. CAN.h library is included with Controllino board support
 * 3. Connect CAN bus: CANH to CANH, CANL to CANL, common GND
 * 4. Add 120-ohm termination resistors at both ends of CAN bus
 * 5. Configure ODrive S1 node ID (default: 0) to match ODRIVE_NODE_ID constant
 * 
 * USAGE:
 * - Open Serial Monitor at 115200 baud
 * - Use commands: SET_AMP, SET_FREQ, SET_MODE, SET_RATE, START, STOP, GET_STATUS
 * - Default: 1.0 revolution/Nm amplitude, 1.0 Hz frequency, 8kHz sample rate
 * 
 * NOTE: Once START is called, Serial command parsing is disabled for maximum performance.
 * To stop, use ODrive GUI to disable closed-loop control, then reset Controllino.
 */

#include <CAN.h>

// Configuration constants
#define DEFAULT_SAMPLE_RATE_HZ 8000
#define DEFAULT_AMPLITUDE 0.12f      // revolutions or Nm
#define DEFAULT_FREQUENCY 1.0f      // Hz
#define DEFAULT_MODE_POSITION false  // true = position, false = torque
#define ODRIVE_NODE_ID 0
#define CAN_BAUD_RATE 1000000

// ODrive CAN message IDs (CANSimple protocol)
#define CAN_ID_SET_POSITION 0x00B
#define CAN_ID_SET_TORQUE 0x0E
#define CAN_ID_SET_AXIS_STATE 0x007

// ODrive Axis States
#define AXIS_STATE_IDLE 1
#define AXIS_STATE_CLOSED_LOOP_CONTROL 8

// Global configuration variables
volatile float amplitude = DEFAULT_AMPLITUDE;
volatile float frequency = DEFAULT_FREQUENCY;
volatile bool modePosition = DEFAULT_MODE_POSITION;  // true = position, false = torque
volatile float sampleRateHz = DEFAULT_SAMPLE_RATE_HZ;
volatile bool running = false;

// Timing variables
volatile unsigned long sampleIntervalUs = 1000000UL / DEFAULT_SAMPLE_RATE_HZ;  // 125 us for 8kHz
volatile unsigned long lastSampleTimeUs = 0;
volatile float phaseIncrement = 0.0f;

// Timing verification
unsigned long lastTimingCheck = 0;
unsigned long lastActualInterval = 0;

// Hardware timer setup (RP2040)
#ifdef ARDUINO_ARCH_RP2040
  #include <hardware/timer.h>
  #include <hardware/irq.h>
  struct repeating_timer timer;
  bool timerInitialized = false;
#endif

// Function prototypes
void setupCAN();
void setupTimer();
void timerISR();
void sendPositionSetpoint(float position, float velocity);
void sendTorqueSetpoint(float torque);
void sendAxisState(uint8_t state);
void enterClosedLoopControl();
void exitClosedLoopControl();
void parseSerialCommand();
void printStatus();
void updatePhaseIncrement();

// Timer ISR callback for RP2040
#ifdef ARDUINO_ARCH_RP2040
bool timerCallback(struct repeating_timer *t) {
  timerISR();
  return true;  // Continue repeating
}
#endif

void setup() {
  Serial.begin(115200);
  delay(2000);  // Longer delay for Controllino stability
  Serial.flush();  // Ensure Serial is ready
  
  Serial.println("========================================");
  Serial.println("Controllino Micro ODrive CAN Sine Wave");
  Serial.println("========================================");
  Serial.flush();  // Ensure header is sent before proceeding
  
  // Initialize CAN
  setupCAN();
  
  // Initialize timer
  setupTimer();
  
  // Calculate initial phase increment
  updatePhaseIncrement();
  
  // Print initial status
  printStatus();
  Serial.println("\nCommands:");
  Serial.println("  SET_AMP <value>     - Set amplitude");
  Serial.println("  SET_FREQ <value>    - Set frequency (Hz)");
  Serial.println("  SET_MODE <pos|tor>  - Set mode (position/torque)");
  Serial.println("  SET_RATE <value>    - Set sample rate (Hz)");
  Serial.println("  START               - Start generation (disables Serial parsing)");
  Serial.println("  STOP                - Disabled during operation (use ODrive GUI + reset)");
  Serial.println("  GET_STATUS          - Show status");
  Serial.println();
  Serial.println("NOTE: Once START is called, all Serial operations stop for maximum");
  Serial.println("performance. Stop via ODrive GUI and reset Controllino to stop.");
  Serial.flush();
}

void loop() {
  // Only parse commands when NOT running (no interference during operation)
  if (!running) {
    parseSerialCommand();
  }
  
  // Software timing fallback (if hardware timer not available)
  if (!timerInitialized && running) {
    unsigned long currentTimeUs = micros();
    if (currentTimeUs - lastSampleTimeUs >= sampleIntervalUs) {
      lastSampleTimeUs = currentTimeUs;
      timerISR();  // Call ISR manually for software timing
    }
  }
  
  // No monitoring, no Serial operations when running
  // Pure high-frequency setpoint transmission only
}

void setupCAN() {
  Serial.print("Initializing CAN bus at ");
  Serial.print(CAN_BAUD_RATE);
  Serial.println(" bps...");
  
  // Configure SPI1 for CAN (RP2040)
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

void setupTimer() {
  Serial.print("Setting up hardware timer for ");
  Serial.print(sampleRateHz);
  Serial.println(" Hz sampling rate...");
  
#ifdef ARDUINO_ARCH_RP2040
  // Cancel existing timer if running
  if (timerInitialized) {
    cancel_repeating_timer(&timer);
    timerInitialized = false;
  }
  
  // Use RP2040 hardware timer (alarm pool)
  // Negative delay means repeating timer
  int64_t delay_us = -((int64_t)sampleIntervalUs);
  
  if (add_repeating_timer_us(delay_us, timerCallback, NULL, &timer)) {
    timerInitialized = true;
    Serial.println("Hardware timer initialized successfully.");
  } else {
    Serial.println("WARNING: Hardware timer initialization failed!");
    Serial.println("Falling back to software timing (less accurate).");
    timerInitialized = false;
    lastSampleTimeUs = micros();
  }
#else
  // For non-RP2040 boards, use software timing
  Serial.println("WARNING: Hardware timer not available for this board.");
  Serial.println("Using software timing (may have higher jitter).");
  timerInitialized = false;
  lastSampleTimeUs = micros();
#endif
}

void timerISR() {
  if (!running) {
    return;
  }
  
  unsigned long currentTimeUs = micros();
  
  // Calculate timing deviation (for verification)
  if (lastSampleTimeUs > 0) {
    lastActualInterval = currentTimeUs - lastSampleTimeUs;
  }
  lastSampleTimeUs = currentTimeUs;
  
  // Calculate sine wave value using phase accumulator for precise frequency
  static float phase = 0.0f;
  phase += phaseIncrement;
  if (phase >= TWO_PI) {
    phase -= TWO_PI;
  }
  
  float value = amplitude * sin(phase);
  
  // Send CAN message based on mode
  if (modePosition) {
    // Calculate velocity feedforward (derivative of sine wave: d/dt[A*sin(2πft)] = A*2πf*cos(2πft))
    float velocity = amplitude * frequency * TWO_PI * cos(phase);
    sendPositionSetpoint(value, velocity);
  } else {
    sendTorqueSetpoint(value);
  }
}

void sendPositionSetpoint(float position, float velocity) {
  // Calculate CAN ID: ODrive uses node_id in bits 5-7
  uint32_t canId = CAN_ID_SET_POSITION + (ODRIVE_NODE_ID << 5);
  
  // Begin CAN packet
  CAN.beginPacket(canId);
  
  // Write position (4 bytes, little-endian float)
  uint8_t* posBytes = (uint8_t*)&position;
  CAN.write(posBytes[0]);
  CAN.write(posBytes[1]);
  CAN.write(posBytes[2]);
  CAN.write(posBytes[3]);
  
  // Write velocity feedforward (4 bytes, little-endian float)
  uint8_t* velBytes = (uint8_t*)&velocity;
  CAN.write(velBytes[0]);
  CAN.write(velBytes[1]);
  CAN.write(velBytes[2]);
  CAN.write(velBytes[3]);
  
  // End packet and send
  CAN.endPacket();
}

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

void sendAxisState(uint8_t state) {
  // Calculate CAN ID: ODrive uses node_id in bits 5-7
  uint32_t canId = CAN_ID_SET_AXIS_STATE + (ODRIVE_NODE_ID << 5);
  
  // Begin CAN packet
  CAN.beginPacket(canId);
  
  // Write axis state (4 bytes, little-endian uint32)
  CAN.write((uint8_t)(state & 0xFF));
  CAN.write((uint8_t)((state >> 8) & 0xFF));
  CAN.write((uint8_t)((state >> 16) & 0xFF));
  CAN.write((uint8_t)((state >> 24) & 0xFF));
  
  // End packet and send
  CAN.endPacket();
}

void enterClosedLoopControl() {
  Serial.println("Entering closed-loop control state...");
  sendAxisState(AXIS_STATE_CLOSED_LOOP_CONTROL);
  delay(500);  // Give ODrive time to transition
}

void exitClosedLoopControl() {
  Serial.println("Exiting closed-loop control (returning to IDLE)...");
  sendAxisState(AXIS_STATE_IDLE);
  delay(100);
}

void parseSerialCommand() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    if (command.startsWith("SET_AMP")) {
      float val = command.substring(8).toFloat();
      if (val > 0) {
        noInterrupts();
        amplitude = val;
        interrupts();
        Serial.print("Amplitude set to: ");
        Serial.println(val);
      } else {
        Serial.println("ERROR: Invalid amplitude value");
      }
    }
    else if (command.startsWith("SET_FREQ")) {
      float val = command.substring(9).toFloat();
      if (val > 0 && val < sampleRateHz / 2) {  // Nyquist limit
        noInterrupts();
        frequency = val;
        updatePhaseIncrement();
        interrupts();
        Serial.print("Frequency set to: ");
        Serial.print(val);
        Serial.println(" Hz");
      } else {
        Serial.print("ERROR: Invalid frequency (must be > 0 and < ");
        Serial.print(sampleRateHz / 2);
        Serial.println(" Hz)");
      }
    }
    else if (command.startsWith("SET_MODE")) {
      String mode = command.substring(9);
      mode.trim();
      mode.toUpperCase();
      noInterrupts();
      if (mode == "POS" || mode == "POSITION") {
        modePosition = true;
        Serial.println("Mode set to: POSITION");
      } else if (mode == "TOR" || mode == "TORQUE") {
        modePosition = false;
        Serial.println("Mode set to: TORQUE");
      } else {
        Serial.println("ERROR: Invalid mode (use 'pos' or 'tor')");
      }
      interrupts();
    }
    else if (command.startsWith("SET_RATE")) {
      float val = command.substring(9).toFloat();
      if (val > 0 && val <= 20000) {  // Reasonable upper limit
        noInterrupts();
        sampleRateHz = val;
        sampleIntervalUs = 1000000UL / (unsigned long)val;
        updatePhaseIncrement();
        interrupts();
        
        // Reinitialize timer with new rate
        Serial.print("Sample rate set to: ");
        Serial.print(val);
        Serial.println(" Hz");
        Serial.println("Restarting timer...");
        setupTimer();
      } else {
        Serial.println("ERROR: Invalid sample rate (must be > 0 and <= 20000 Hz)");
      }
    }
    else if (command == "START") {
      // Enter closed-loop control state BEFORE sending setpoints
      enterClosedLoopControl();
      
      noInterrupts();
      running = true;
      lastSampleTimeUs = 0;  // Reset timing
      interrupts();
      Serial.println("Sine wave generation STARTED");
      Serial.println("NOTE: Serial command parsing now disabled for maximum performance.");
      Serial.println("To stop: Use ODrive GUI to disable closed-loop control, then reset Controllino.");
      Serial.flush();
    }
    else if (command == "STOP") {
      if (running) {
        Serial.println("ERROR: STOP command is disabled during operation.");
        Serial.println("Serial command parsing is disabled for maximum performance.");
        Serial.println("To stop: Use ODrive GUI to disable closed-loop control, then reset Controllino.");
      } else {
        Serial.println("Already stopped. Use START to begin generation.");
      }
    }
    else if (command == "GET_STATUS" || command == "STATUS") {
      printStatus();
    }
    else if (command.length() > 0) {
      Serial.print("Unknown command: ");
      Serial.println(command);
      Serial.println("Type a command or 'GET_STATUS' for help.");
    }
  }
}

void printStatus() {
  Serial.println("\n========================================");
  Serial.println("Current Configuration:");
  Serial.println("========================================");
  Serial.print("Amplitude: ");
  Serial.print(amplitude);
  Serial.println(modePosition ? " revolutions" : " Nm");
  Serial.print("Frequency: ");
  Serial.print(frequency);
  Serial.println(" Hz");
  Serial.print("Mode: ");
  Serial.println(modePosition ? "POSITION" : "TORQUE");
  Serial.print("Sample Rate: ");
  Serial.print(sampleRateHz);
  Serial.println(" Hz");
  Serial.print("Sample Interval: ");
  Serial.print(sampleIntervalUs);
  Serial.println(" us");
  Serial.print("ODrive Node ID: ");
  Serial.println(ODRIVE_NODE_ID);
  Serial.print("Status: ");
  Serial.println(running ? "RUNNING" : "STOPPED");
  Serial.print("Timer: ");
  Serial.println(timerInitialized ? "Hardware" : "Software");
  if (running && lastActualInterval > 0) {
    float deviationPercent = abs((long)lastActualInterval - (long)sampleIntervalUs) * 100.0f / sampleIntervalUs;
    Serial.print("Timing Deviation: ");
    Serial.print(deviationPercent, 2);
    Serial.println("%");
  }
  Serial.println("========================================\n");
}

void updatePhaseIncrement() {
  // Calculate phase increment per sample for precise frequency control
  // phaseIncrement = 2 * PI * frequency / sampleRateHz
  phaseIncrement = TWO_PI * frequency / sampleRateHz;
}
