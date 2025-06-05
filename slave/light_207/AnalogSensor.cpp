#include "AnalogSensor.h"

AnalogSensor::AnalogSensor(uint8_t pin, int inMin, int inMax, int outMin, int outMax)
  : analogPin(pin), inMin(inMin), inMax(inMax), outMin(outMin), outMax(outMax) {}

void AnalogSensor::begin() {
  // No pinMode needed for analog inputs on ESP8266
}

int AnalogSensor::readRaw() {
#if defined(ESP8266)
  return analogRead(A0); // ESP8266 only supports A0
#else
  return analogRead(analogPin);
#endif
}

float AnalogSensor::readVoltage() {
  int raw = readRaw();
  return (3.3 * raw) / 1023.0;
}

int AnalogSensor::readCalibrated() {
  int raw = readRaw();
  return map(raw, inMin, inMax, outMin, outMax);
}

void AnalogSensor::setCalibration(int newInMin, int newInMax, int newOutMin, int newOutMax) {
  inMin = newInMin;
  inMax = newInMax;
  outMin = newOutMin;
  outMax = newOutMax;
}

float AnalogSensor::readLux(float rFixed, float a, float b) {
  float vOut = readVoltage();
  if (vOut <= 0.0 || vOut >= 3.3) return -1.0; // Avoid divide-by-zero or invalid values

  float rLDR = rFixed * ((3.3 - vOut) / vOut);
  float lux = a * pow((1.0 / rLDR), b);
  return lux;
}
