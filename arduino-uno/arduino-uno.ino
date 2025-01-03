
/* This file contains code borrowed from https://github.com/DFRobor/DFRobot_AS3935, licensed under MIT. */

#include "DFRobot_AS3935_I2C.h"

volatile int8_t AS3935IsrTrig = 0;

#if defined(ESP32) || defined(ESP8266)
#define IRQ_PIN       0
#else
#define IRQ_PIN       2
#endif

// Antenna tuning capcitance (must be integer multiple of 8, 8 - 120 pf)
#define AS3935_CAPACITANCE   96

// Indoor/outdoor mode selection
#define AS3935_INDOORS       0
#define AS3935_OUTDOORS      1
#define AS3935_MODE          AS3935_INDOORS

// Enable/disable disturber detection
#define AS3935_DIST_DIS      0
#define AS3935_DIST_EN       1
#define AS3935_DIST          AS3935_DIST_EN

// I2C address
#define AS3935_I2C_ADDR      AS3935_ADD3

#define TESTING   false

void AS3935_ISR();

DFRobot_AS3935_I2C  lightning0((uint8_t)IRQ_PIN, (uint8_t)AS3935_I2C_ADDR);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("# THOR Lighting Node - Lightning Sensor");

  while (lightning0.begin() != 0) {
    Serial.print(".");
  }
  lightning0.defInit();

  lightning0.manualCal(AS3935_CAPACITANCE, AS3935_MODE, AS3935_DIST);
}

void loop() {
  if (TESTING) {
      uint8_t lightningDistKm = 14;
      uint32_t lightningEnergyVal = 83;

      Serial.print("~LIGHTNING;DISTANCE:");
      Serial.print(lightningDistKm);
      Serial.print(";ENERGY:");
      Serial.print(lightningEnergyVal);
      Serial.println("");
    delay(2500);
  } else {
    while (AS3935IsrTrig == 0) {delay(1);}
    delay(5);

    AS3935IsrTrig = 0;

    uint8_t intSrc = lightning0.getInterruptSrc();
      if (intSrc == 1){
      uint8_t lightningDistKm = lightning0.getLightningDistKm();
      uint32_t lightningEnergyVal = lightning0.getStrikeEnergyRaw();

      Serial.print("~LIGHTNING;DISTANCE:");
      Serial.print(lightningDistKm);
      Serial.print(";ENERGY:");
      Serial.print(lightningEnergyVal);
      Serial.println("");
    }else if (intSrc == 3){
      Serial.println("~NOISY");
    }
  }
}
