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

bool do_en = true;
unsigned long enableDoTimer = 0;
unsigned long digitalAnalogTimer = 0;

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
}

void loop(void) {
  // I/O handling every 500 ms
  if ((millis() - digitalAnalogTimer) > 500)
  {
    digitalAnalogTimer = millis();

    // Analog read AI0-AI5
    Serial.print("AI0:");
    Serial.print(analogRead(CONTROLLINO_MICRO_AI0));
    Serial.print(" | AI1:");
    Serial.print(analogRead(CONTROLLINO_MICRO_AI1));
    Serial.print(" | AI2:");
    Serial.print(analogRead(CONTROLLINO_MICRO_AI2));
    Serial.print(" | AI3:");
    Serial.print(analogRead(CONTROLLINO_MICRO_AI3));
    Serial.print(" | AI4:");
    Serial.print(analogRead(CONTROLLINO_MICRO_AI4));
    Serial.print(" | AI5:");
    Serial.print(analogRead(CONTROLLINO_MICRO_AI5));

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
