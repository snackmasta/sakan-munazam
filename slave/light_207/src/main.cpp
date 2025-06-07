#include <Arduino.h>
#include "OTAHandler.h"
#include "WiFiUDPHandler.h"
#include "AnalogSensor.h"
#include <ESP8266WiFi.h>

// These are defined by build flags in platformio.ini
#ifndef DEVICE_ID
#define DEVICE_ID "light_207"
#endif

#ifndef CURRENT_VERSION
#define CURRENT_VERSION "1.0.5"
#endif

void setup();
void loop();

// Pin definitions
const int LDR_PIN = A0;       // Analog input for LDR
const int LIGHT_PIN = 15;     // D8/GPIO15 for PWM output
const int LED_PIN = LED_BUILTIN;

// WiFi credentials
const char* ssid = "ALICE";
const char* password = "@channel";

// OTA Update Configuration
#define OTA_SERVER "192.168.137.1"
#define OTA_PORT 5000

// Light control parameters
#define TARGET_LUX 500.0    // Target light level in lux
#define PWM_MIN 0
#define PWM_MAX 1023
#define LDR_FIXED_R 10000.0 // 10k fixed resistor in voltage divider

bool lightState = false;     // Current state of the light
int currentPWM = 0;         // Current PWM value

OTAHandler otaHandler(OTA_SERVER, OTA_PORT, DEVICE_ID, CURRENT_VERSION);
WiFiUDPHandler udpHandler(ssid, password);
AnalogSensor ldrSensor(LDR_PIN);

// Status variables
unsigned long lastBlink = 0;
const long blinkInterval = 1000;  // Blink every second
bool ledState = false;

unsigned long lastUDPBroadcast = 0;
const long udpBroadcastInterval = 5000;  // Broadcast every 5 seconds

unsigned long lastLightAdjust = 0;
const long lightAdjustInterval = 100;  // Adjust light every 100ms

void handleCalibrationCommand(String message) {
    // Format: CAL:degree:coeff0:coeff1:coeff2
    int parts[4];
    float coeffs[3] = {0};
    int lastPos = 4;
    int nextPos;
    int degree = 1;
    for (int i = 0; i < 4; ++i) {
        nextPos = message.indexOf(':', lastPos);
        String val = (i < 3) ? message.substring(lastPos, nextPos) : message.substring(lastPos);
        if (i == 0) degree = val.toInt();
        else coeffs[i-1] = val.toFloat();
        lastPos = nextPos + 1;
    }
    ldrSensor.setCalibrationCoeffs(coeffs, degree);
    Serial.print("Calibration set. Degree: ");
    Serial.print(degree);
    Serial.print(" Coeffs: ");
    for (int i = 0; i <= degree; ++i) {
        Serial.print(coeffs[i]); Serial.print(" ");
    }
    Serial.println();
}

void handleUDPMessage(String message) {
    if (message == "ON") {
        lightState = true;
    } else if (message == "OFF") {
        lightState = false;
        analogWrite(LIGHT_PIN, 0);
        currentPWM = 0;
    } else if (message.startsWith("CALIBRATE:")) {
        int params[4];
        int idx = 0;
        int lastPos = 10;
        for (int i = 0; i < 4; ++i) {
            int nextPos = message.indexOf(':', lastPos);
            if (nextPos == -1 && i < 3) return; // Invalid
            String val = (i < 3) ? message.substring(lastPos, nextPos) : message.substring(lastPos);
            params[i] = val.toInt();
            lastPos = nextPos + 1;
        }
        ldrSensor.setCalibration(params[0], params[1], params[2], params[3]);
        Serial.print("Calibration updated: ");
        Serial.print(params[0]); Serial.print(", ");
        Serial.print(params[1]); Serial.print(", ");
        Serial.print(params[2]); Serial.print(", ");
        Serial.println(params[3]);
    } else if (message.startsWith("CAL:")) {
        handleCalibrationCommand(message);
    }
}

void adjustLight() {
    if (!lightState) return;
    int raw = ldrSensor.readRaw();
    float currentLux = ldrSensor.calibratedLux(raw);
    if (currentLux < 0) currentLux = ldrSensor.readLux(LDR_FIXED_R);

    // Debug output
    Serial.print("Raw: ");
    Serial.print(raw);
    Serial.print(" Lux: ");
    Serial.print(currentLux);

    // Simple proportional control
    float error = TARGET_LUX - currentLux;
    int adjustment = error * 0.5;  // Adjust sensitivity with this multiplier

    currentPWM = constrain(currentPWM + adjustment, PWM_MIN, PWM_MAX);
    analogWrite(LIGHT_PIN, currentPWM);

    Serial.print(" PWM: ");
    Serial.println(currentPWM);
}

void setup() {
    Serial.begin(115200);
    delay(100);
    
    // Setup pins
    pinMode(LED_PIN, OUTPUT);
    pinMode(LIGHT_PIN, OUTPUT);
    analogWriteRange(1023);  // Set PWM range to 10 bits
    digitalWrite(LED_PIN, HIGH);   // LED off initially (ESP8266 LED is active LOW)
    analogWrite(LIGHT_PIN, 0);     // Light off initially
    
    ldrSensor.begin();
    ldrSensor.loadCalibration();
    
    // Initialize UDP and OTA handlers
    udpHandler.begin();
    otaHandler.begin();
    otaHandler.checkForUpdates();
    
    Serial.println("Device ready for OTA updates and UDP communication.");
    Serial.println("Current version: " + String(CURRENT_VERSION));
    Serial.println("Device ID: " + String(DEVICE_ID));
}

void loop() {
    unsigned long currentMillis = millis();
    
    // Blink LED to show device is running
    if (currentMillis - lastBlink >= blinkInterval) {
        lastBlink = currentMillis;
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
    }

    // Adjust light level
    if (currentMillis - lastLightAdjust >= lightAdjustInterval) {
        lastLightAdjust = currentMillis;
        adjustLight();
    }

    // Periodically broadcast device status
    if (currentMillis - lastUDPBroadcast >= udpBroadcastInterval) {
        lastUDPBroadcast = currentMillis;
        int raw = ldrSensor.readRaw();
        float currentLux = ldrSensor.calibratedLux(raw);
        if (currentLux < 0) currentLux = ldrSensor.readLux(LDR_FIXED_R);
        String status = String(DEVICE_ID) + ":" + 
                       (lightState ? "ON" : "OFF") + ":" +
                       String(currentLux, 1) + ":" +
                       String(currentPWM) + ":" +
                       String(raw);
        udpHandler.sendBroadcast(status.c_str());
    }

    // Check for incoming UDP messages
    String response = udpHandler.receiveResponses(10);
    if (response.length() > 0) {
        handleUDPMessage(response);
    }

    delay(10);  // Small delay to avoid busy loop
}
