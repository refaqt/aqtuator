/*
 * Copyright (c) 2023 CONTROLLINO GmbH.
 *
 * SPDX-License-Identifier: MIT
 */

 /**
  * \file IoTest.ino
  *
  * \brief Example of CONTROLLINO MICRO I/O usage
  * \author Pedro Marquez @pmmarquez, CONTROLLINO Firmware Team
  *
  * \note The resolution for analogAnalog read is set by default to 24 bits it can be changed with analogReadResolution(1..32)
  */

#include <Arduino.h>
#include <mcp3564.h>

bool do_en = true;
unsigned long enableDoTimer = 0;
unsigned long digitalAnalogTimer = 0;

// Controllino Micro core (controllino_rp2) exposes the MCP3564 instance as a global pointer
// (defined in the core's micro.cpp). Use this instead of inventing a new symbol.
extern mcp3564_t* dev_mcp3564;

// Helper to print which Vref source the MCP3564 is configured to use
static void printMcp3564VrefConfig() {
  if (!dev_mcp3564) {
    Serial.println("MCP3564: dev_mcp3564 is null (not initialized)");
    return;
  }

  uint8_t cfg0 = 0;
  mcp3564_err_code_t err = mcp3564_sread(dev_mcp3564, MCP3564_REG_CFG_0, &cfg0, 1);

  Serial.print("MCP3564 CFG0 = 0x");
  Serial.println(cfg0, HEX);

  if (err != 0) {
    Serial.print("mcp3564_sread error = ");
    Serial.println(err);
    return;
  }

  if (cfg0 & MCP3564_CFG_0_VREF_INT) {
    Serial.println("MCP3564 Vref source: INTERNAL (VREF_INT, ~2.4 V)");
  } else {
    Serial.println("MCP3564 Vref source: EXTERNAL (VREF_EXT)");
  }
}

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while (!Serial); // Wait for serial port to connect. Needed for native USB port only
  delay(3000);

  Serial.println("Initializing I/O ...");
  pinMode(CONTROLLINO_MICRO_DI0, INPUT); // Digital only input 0-11V LOW > 11V HIGH
  pinMode(CONTROLLINO_MICRO_DI1, INPUT); // Analog input
  pinMode(CONTROLLINO_MICRO_DI2, INPUT); // Analog input
  pinMode(CONTROLLINO_MICRO_DI3, INPUT); // Analog input
  pinMode(CONTROLLINO_MICRO_AI0, INPUT); // Analog input 23 bit resolution at default gain 0-24V
  pinMode(CONTROLLINO_MICRO_AI1, INPUT); // Analog input 23 bit resolution at default gain 0-24V
  pinMode(CONTROLLINO_MICRO_AI2, INPUT); // Analog input 23 bit resolution at default gain 0-24V
  pinMode(CONTROLLINO_MICRO_AI3, INPUT); // Analog input 23 bit resolution at default gain 0-24V
  pinMode(CONTROLLINO_MICRO_AI4, INPUT); // Analog input 23 bit resolution at default gain 0-24V
  pinMode(CONTROLLINO_MICRO_AI5, INPUT); // Analog input 23 bit resolution at default gain 0-24V

  if (dev_mcp3564) {
    // Set one global gain used by all ADC-backed channels.
    mcp3564_set_gain(dev_mcp3564, MCP3564_GAIN_X_2);
    // Print which Vref source is configured (internal vs external)
    printMcp3564VrefConfig();
  } else {
    Serial.println("WARNING: dev_mcp3564 is null; MCP3564 gain cannot be configured.");
  }
}

void loop(void) {
  // I/O handling every 500 ms
  if ((millis() - digitalAnalogTimer) > 500)
  {
    digitalAnalogTimer = millis();

    // Analog read AI0-AI5
    const int32_t ai0 = analogRead(CONTROLLINO_MICRO_AI0);
    const int32_t ai1 = analogRead(CONTROLLINO_MICRO_AI1);
    const int32_t ai2 = analogRead(CONTROLLINO_MICRO_AI2);
    const int32_t ai3 = analogRead(CONTROLLINO_MICRO_AI3);
    const int32_t ai4 = analogRead(CONTROLLINO_MICRO_AI4);
    const int32_t ai5 = analogRead(CONTROLLINO_MICRO_AI5);

    Serial.print("AI0:");
    Serial.print(ai0);
    Serial.print(" | AI1:");
    Serial.print(ai1);
    Serial.print(" | AI2:");
    Serial.print(ai2);
    Serial.print(" | AI3:");
    Serial.print(ai3);
    Serial.print(" | AI4:");
    Serial.print(ai4);
    Serial.print(" | AI5:");
    Serial.print(ai5);

    // Analog read DI0-DI3
    Serial.print(" | DI0:");
    Serial.println(analogRead(CONTROLLINO_MICRO_DI0));
    Serial.print(" | DI1:");
    Serial.println(analogRead(CONTROLLINO_MICRO_DI1));
    Serial.print(" | DI2:");
    Serial.println(analogRead(CONTROLLINO_MICRO_DI2));
    Serial.print(" | DI3:");
    Serial.println(analogRead(CONTROLLINO_MICRO_DI3));
  }
}
