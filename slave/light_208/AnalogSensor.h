#ifndef ANALOG_SENSOR_H
#define ANALOG_SENSOR_H

#include <Arduino.h>

class AnalogSensor {
public:
  AnalogSensor(uint8_t pin, int inMin = 0, int inMax = 1023, int outMin = 0, int outMax = 100);

  void begin();

  int readRaw();                      // Raw ADC value
  float readVoltage();               // Voltage (0 - 3.3V)
  int readCalibrated();              // Mapped calibrated value
  float readLux(float rFixed, float a = 500.0, float b = 1.4); // Estimated lux

  void setCalibration(int inMin, int inMax, int outMin, int outMax);

private:
  uint8_t analogPin;
  int inMin, inMax, outMin, outMax;
};

#endif
