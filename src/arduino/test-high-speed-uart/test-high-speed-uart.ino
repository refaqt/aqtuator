 
#include <ODriveUART.h>
#include <mbed.h>
// #include <SoftwareSerial.h>

// Documentation for this example can be found here:
// https://docs.odriverobotics.com/v/latest/guides/arduino-uart-guide.html


////////////////////////////////
// Set up serial pins to the ODrive
////////////////////////////////

// Below are some sample configurations.
// You can comment out the default one and uncomment the one you wish to use.
// You can of course use something different if you like
// Don't forget to also connect ODrive ISOVDD and ISOGND to Arduino 3.3V/5V and GND.

// Arduino without spare serial ports (such as Arduino UNO) have to use software serial.
// Note that this is implemented poorly and can lead to wrong data sent or read.
// pin 8: RX - connect to ODrive TX
// pin 9: TX - connect to ODrive RX
// SoftwareSerial odrive_serial(8, 9);
// unsigned long baudrate = 115200; // Must match what you configure on the ODrive (see docs for details)

// Teensy 3 and 4 (all versions) - Serial1
// pin 0: RX - connect to ODrive TX
// pin 1: TX - connect to ODrive RX
// See https://www.pjrc.com/teensy/td_uart.html for other options on Teensy
HardwareSerial& odrive_serial = Serial1;
int baudrate = 115200; // Must match what you configure on the ODrive (see docs for details)

// Arduino Mega or Due - Serial1
// pin 19: RX - connect to ODrive TX
// pin 18: TX - connect to ODrive RX
// See https://www.arduino.cc/reference/en/language/functions/communication/serial/ for other options
// HardwareSerial& odrive_serial = Serial1;
// int baudrate = 115200; // Must match what you configure on the ODrive (see docs for details)


ODriveUART odrive(odrive_serial);

// Timer interrupt for accurate 5000Hz update rate
mbed::Ticker controlTimer;

// Sinewave parameters
const float SINE_FREQUENCY = 500.0f;  // 500Hz sinewave
const float SINE_AMPLITUDE = 0.05f;   // 0.001 Nm torque amplitude
const float UPDATE_RATE = 5000.0f;    // 5000Hz update rate (200 microseconds)

// Timing variables
volatile unsigned long startTime = 0;
volatile float elapsedTime = 0.0f;

// Interrupt service routine - called at 5000Hz
void controlInterrupt() {
  // Calculate time in seconds since start
  elapsedTime = (micros() - startTime) * 1e-6f;
  
  // Calculate phase: 2*PI*frequency*time
  float phase = TWO_PI * SINE_FREQUENCY * elapsedTime;
  
  // Calculate torque: amplitude * sin(phase)
  float torque = SINE_AMPLITUDE * sin(phase);
  
  // Send torque command
  odrive.setTorque(torque);
}

void setup() {
  odrive_serial.begin(baudrate);

  Serial.begin(115200); // Serial to PC
  
  delay(2000); // Longer delay for Arduino GIGA/mbed Serial initialization
  
  Serial.println("Starting setup...");

  Serial.println("Waiting for ODrive...");
  unsigned long waitStartTime = millis();
  const unsigned long TIMEOUT_MS = 10000; // 10 second timeout
  unsigned long lastStatusTime = 0;
  
  while (odrive.getState() == AXIS_STATE_UNDEFINED) {
    unsigned long currentTime = millis();
    
    // Print status every second
    if (currentTime - lastStatusTime >= 1000) {
      Serial.print("Still waiting for ODrive... (");
      Serial.print((currentTime - waitStartTime) / 1000);
      Serial.println("s)");
      lastStatusTime = currentTime;
    }
    
    // Check for timeout
    if (currentTime - waitStartTime >= TIMEOUT_MS) {
      Serial.println("ERROR: Timeout waiting for ODrive!");
      Serial.println("Please check ODrive connection and power.");
      while(1) { delay(1000); } // Halt execution
    }
    
    delay(100);
  }

  Serial.println("found ODrive");
  
  Serial.print("DC voltage: ");
  Serial.println(odrive.getParameterAsFloat("vbus_voltage"));
  
  Serial.println("Setting control mode to torque control...");
  // Set control mode to torque control BEFORE enabling closed loop
  odrive.setParameter("controller.config.control_mode", 2); // 2 = CONTROL_MODE_TORQUE_CONTROL
  delay(100);
  Serial.println("Control mode set to torque control");
  
  Serial.println("Enabling closed loop control...");
  unsigned long controlStartTime = millis();
  const unsigned long CONTROL_TIMEOUT_MS = 10000; // 10 second timeout
  unsigned long lastControlStatusTime = 0;
  
  while (odrive.getState() != AXIS_STATE_CLOSED_LOOP_CONTROL) {
    unsigned long currentTime = millis();
    
    // Print status every second
    if (currentTime - lastControlStatusTime >= 1000) {
      Serial.print("Still enabling closed loop control... (");
      Serial.print((currentTime - controlStartTime) / 1000);
      Serial.println("s)");
      lastControlStatusTime = currentTime;
    }
    
    // Check for timeout
    if (currentTime - controlStartTime >= CONTROL_TIMEOUT_MS) {
      Serial.println("ERROR: Timeout enabling closed loop control!");
      Serial.println("Please check ODrive configuration and errors.");
      while(1) { delay(1000); } // Halt execution
    }
    
    odrive.clearErrors();
    odrive.setState(AXIS_STATE_CLOSED_LOOP_CONTROL);
    delay(100);
  }
  
  Serial.println("ODrive running in torque control mode!");
  
  // Initialize timing
  startTime = micros();
  
  // Ensure all Serial messages are sent before starting high-frequency timer
  Serial.flush();
  delay(10); // Small delay to ensure Serial buffer is fully flushed
  
  Serial.println("High-speed torque control loop started at 5000Hz");
  Serial.flush(); // Final flush before starting timer
  
  // Start timer interrupt at 5000Hz (200 microseconds)
  controlTimer.attach_us(controlInterrupt, 200); // 200 microseconds = 5000Hz
}

void loop() {
  // Control loop runs in interrupt, so main loop can be empty
  // or used for other low-priority tasks
  delay(1000);
}
