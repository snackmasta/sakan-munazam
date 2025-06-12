#ifndef ANALOG_SENSOR_H
#define ANALOG_SENSOR_H

#include <Arduino.h>
#include <EEPROM.h>

class AnalogSensor {
public:
  AnalogSensor(uint8_t pin, int inMin = 0, int inMax = 1023, int outMin = 0, int outMax = 100);

  void begin();

  int readRaw();                      // Raw ADC value
  float readVoltage();               // Voltage (0 - 3.3V)
  int readCalibrated();              // Mapped calibrated value
  float readLux(float rFixed, float a = 500.0, float b = 1.4); // Estimated lux
  void loadCalibration();
  void saveCalibration();
  void setCalibrationCoeffs(float* coeffs, uint8_t degree);
  float calibratedLux(int raw);

  void setCalibration(int inMin, int inMax, int outMin, int outMax);

  // --- Debug getters for calibration ---
  uint8_t getCalibrationDegree() const;
  float getCalibrationCoeff(uint8_t i) const;
  uint8_t getCalibrationCoeffCount() const;

private:
  uint8_t analogPin;
  int inMin, inMax, outMin, outMax;

  struct LDRCalibration {
    float coeffs[3]; // For quadratic: coeffs[0] + coeffs[1]*x + coeffs[2]*x^2
    uint8_t degree;  // 1=linear, 2=quadratic
    bool valid;
  } calibration;
};

#endif
