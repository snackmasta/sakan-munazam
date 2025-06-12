#include "AnalogSensor.h"
#include <EEPROM.h>

#define EEPROM_CALIB_ADDR 0

AnalogSensor::AnalogSensor(uint8_t pin, int inMin, int inMax, int outMin, int outMax)
  : analogPin(pin), inMin(inMin), inMax(inMax), outMin(outMin), outMax(outMax) {}

void AnalogSensor::begin() {
  // No pinMode needed for analog inputs on ESP8266
  loadCalibration();
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

void AnalogSensor::loadCalibration() {
  EEPROM.begin(64);
  EEPROM.get(EEPROM_CALIB_ADDR, calibration);
  if (calibration.degree < 1 || calibration.degree > 3) calibration.valid = false;
}

void AnalogSensor::saveCalibration() {
  EEPROM.begin(64);
  EEPROM.put(EEPROM_CALIB_ADDR, calibration);
  EEPROM.commit();
}

// --- Debug getters for calibration ---
uint8_t AnalogSensor::getCalibrationDegree() const {
  return calibration.degree;
}

float AnalogSensor::getCalibrationCoeff(uint8_t i) const {
  if (i < 4) return calibration.coeffs[i];
  return 0.0f;
}

uint8_t AnalogSensor::getCalibrationCoeffCount() const {
  return calibration.degree;
}

void AnalogSensor::setCalibrationCoeffs(float* coeffs, uint8_t degree) {
  calibration.degree = degree;
  for (int i = 0; i < 4; ++i) calibration.coeffs[i] = (i < degree+1) ? coeffs[i] : 0.0f;
  calibration.valid = true;
  saveCalibration();
}

float AnalogSensor::calibratedLux(int raw) {
  if (!calibration.valid) return -1.0f;
  float lux = 0.0f;
  float x = raw;
  for (int i = 0; i <= calibration.degree; ++i) {
    lux += calibration.coeffs[i] * pow(x, i);
  }
  return lux;
}

float AnalogSensor::readLux(float rFixed, float a, float b) {
  // Use calibrated value for lux calculation
  int calibrated = readCalibrated();
  float vOut = (3.3 * calibrated) / 1023.0;
  if (vOut <= 0.0 || vOut >= 3.3) return -1.0; // Avoid divide-by-zero or invalid values
  float rLDR = rFixed * ((3.3 - vOut) / vOut);
  float lux = a * pow((1.0 / rLDR), b);
  return lux;
}
