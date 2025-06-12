#include "OTAHandler.h"
#include "WiFiUDPHandler.h"
#include "AnalogSensor.h"
#include <ESP8266WiFi.h>

// OTA Update Configuration
#define OTA_SERVER "192.168.137.1"
#define OTA_PORT 5000
#define CURRENT_VERSION "1.0.26"
#define DEVICE_ID "light_208"

// WiFi credentials
const char* ssid = "ALICE";
const char* password = "@channel";

// Pin definitions
const int LDR_PIN = A0;       // Analog input for LDR
const int LIGHT_PIN = 15;     // D8/GPIO15 for PWM output
const int LED_PIN = LED_BUILTIN;

// Light control parameters
// #define TARGET_LUX 500.0    // Target light level in lux
// float targetLux = 500.0;    // Target light level in lux
int targetLDR = 500;    // Target raw LDR value
#define PWM_MIN 0
#define PWM_MAX 1023
#define LDR_FIXED_R 10000.0 // 10k fixed resistor in voltage divider

bool lightState = false;     // Current state of the light
int currentPWM = 0;         // Current PWM value
bool autoMode = true; // true = AUTO, false = MANUAL

OTAHandler otaHandler(OTA_SERVER, OTA_PORT, DEVICE_ID, CURRENT_VERSION);
WiFiUDPHandler udpHandler(ssid, password);
AnalogSensor ldrSensor(LDR_PIN);

// Status variables
unsigned long lastBlink = 0;
const long blinkInterval = 1000;  // Blink every second
bool ledState = false;

unsigned long lastUDPBroadcast = 0;
const long udpBroadcastInterval = 500;  // Broadcast every 5 seconds

unsigned long lastLightAdjust = 0;
const long lightAdjustInterval = 100;  // Adjust light every 100ms

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
    Serial.print("[CALIBRATION] Loaded. Degree: ");
    Serial.print(ldrSensor.getCalibrationDegree());
    Serial.print(" Coeffs: ");
    for (int i = 0; i < 4; ++i) {
        Serial.print(ldrSensor.getCalibrationCoeff(i)); Serial.print(" ");
    }
    Serial.println();
    
    // Initialize UDP and OTA handlers
    udpHandler.begin();
    otaHandler.begin();
    otaHandler.checkForUpdates();
    
    Serial.println("Device ready for OTA updates and UDP communication.");
    Serial.println("Current version: " + String(CURRENT_VERSION));
    Serial.println("Device ID: " + String(DEVICE_ID));
}

void handleCalibrationCommand(String message) {
    // Format: CAL:degree:coeff0:coeff1:coeff2:coeff3
    float coeffs[4] = {0};
    int lastPos = 4;
    int nextPos;
    int degree = 1;
    for (int i = 0; i < 5; ++i) {
        nextPos = message.indexOf(':', lastPos);
        String val = (i < 4) ? message.substring(lastPos, nextPos) : message.substring(lastPos);
        if (i == 0) degree = val.toInt();
        else coeffs[i-1] = val.toFloat();
        lastPos = nextPos + 1;
    }
    ldrSensor.setCalibrationCoeffs(coeffs, degree);
    Serial.print("[CALIBRATION] Set. Degree: ");
    Serial.print(degree);
    Serial.print(" Coeffs: ");
    for (int i = 0; i <= degree; ++i) {
        Serial.print(coeffs[i]); Serial.print(" ");
    }
    Serial.println();
    // Immediately save and print confirmation
    ldrSensor.saveCalibration();
    Serial.println("[CALIBRATION] Saved to EEPROM.");
}

void handleUDPMessage(String message) {
    Serial.print("Received command: ");
    Serial.println(message);
    if (message == "ON") {
        lightState = true;
    } else if (message == "OFF") {
        lightState = false;
        analogWrite(LIGHT_PIN, 0);
        currentPWM = 0;
        // Send OFF status back to master
        String status = String(DEVICE_ID) + ":OFF:0:0:0";
        IPAddress masterIP(192,168,137,1); // Set to your master server IP
        uint16_t masterPort = 4210;        // Set to your master server UDP port
        udpHandler.sendTo(status.c_str(), masterIP, masterPort);
    } else if (message == "PWM_MANUAL") {
        autoMode = false;
        Serial.println("Switched to MANUAL PWM mode");
    } else if (message == "PWM_AUTO") {
        // When switching to AUTO, use the current raw LDR as the new target
        int raw = ldrSensor.readRaw();
        targetLDR = raw;
        autoMode = true;
        Serial.print("Switched to AUTO PWM mode, new targetLDR: ");
        Serial.println(targetLDR);
    } else if (message.startsWith("PWM:")) {
        if (!autoMode) {
            int pwmVal = message.substring(4).toInt();
            currentPWM = constrain(pwmVal, PWM_MIN, PWM_MAX);
            analogWrite(LIGHT_PIN, currentPWM);
            Serial.print("Manual PWM set to: ");
            Serial.println(currentPWM);
        }
    } else if (message.startsWith("CAL:")) {
        handleCalibrationCommand(message);
    }
}

void handleMeshCommand(String message) {
    // Format: target_ip:command:ttl
    int sep1 = message.indexOf(":");
    int sep2 = message.indexOf(":", sep1 + 1);
    if (sep1 == -1 || sep2 == -1) return;
    String targetIpStr = message.substring(0, sep1);
    String cmd = message.substring(sep1 + 1, sep2);
    int ttl = message.substring(sep2 + 1).toInt();
    IPAddress myIp = WiFi.localIP();
    IPAddress targetIp;
    if (!targetIp.fromString(targetIpStr)) return;
    if (myIp == targetIp) {
        handleUDPMessage(cmd);
    } else if (ttl > 0) {
        // Relay to target IP, decrement TTL
        String relayMsg = targetIpStr + ":" + cmd + ":" + String(ttl - 1);
        Serial.print("[MESH RELAY] Relaying to ");
        Serial.print(targetIp);
        Serial.print(" with TTL ");
        Serial.println(ttl - 1);
        udpHandler.sendTo(relayMsg.c_str(), targetIp, 4210);
    } else {
        Serial.println("[MESH RELAY] TTL expired, not relaying.");
    }
}

void adjustLight() {
    if (!lightState) return;
    if (autoMode) {
        int raw = ldrSensor.readRaw();
        // Debug output
        Serial.print("Raw: ");
        Serial.print(raw);
        // Simple proportional control using raw LDR
        int error = targetLDR - raw;
        int adjustment = error * 0.5;  // Adjust sensitivity with this multiplier
        currentPWM = constrain(currentPWM + adjustment, PWM_MIN, PWM_MAX);
        analogWrite(LIGHT_PIN, currentPWM);
        Serial.print(" PWM: ");
        Serial.println(currentPWM);
    } else {
        // Manual mode: PWM set directly, nothing to do here
        Serial.print("Manual mode PWM: ");
        Serial.println(currentPWM);
    }
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
        if (lightState) { // Only send data when running
            int raw = ldrSensor.readRaw();
            float currentLux = ldrSensor.calibratedLux(raw);
            if (currentLux < 0) currentLux = ldrSensor.readLux(LDR_FIXED_R);
            // Debug: Print calibration coefficients and calculation
            Serial.print("[DEBUG] Calibration degree: ");
            Serial.println(ldrSensor.getCalibrationDegree());
            Serial.print("[DEBUG] Calibration coeffs: ");
            for (int i = 0; i <= ldrSensor.getCalibrationDegree(); ++i) {
                Serial.print(ldrSensor.getCalibrationCoeff(i)); Serial.print(" ");
            }
            Serial.println();
            Serial.print("[DEBUG] Raw: "); Serial.print(raw);
            Serial.print("  Calculated Lux: "); Serial.println(currentLux, 4);
            // Show formula used
            Serial.print("[DEBUG] Formula: lux = ");
            for (int i = 0; i <= ldrSensor.getCalibrationDegree(); ++i) {
                if (i > 0) Serial.print(" + ");
                Serial.print(ldrSensor.getCalibrationCoeff(i));
                if (i == 1) Serial.print("*raw");
                else if (i > 1) {
                    Serial.print("*raw^"); Serial.print(i);
                }
            }
            Serial.println();
            float expectedLux = 0.0f;
            for (int i = 0; i <= ldrSensor.getCalibrationDegree(); ++i) {
                expectedLux += ldrSensor.getCalibrationCoeff(i) * pow(raw, i);
            }
            Serial.print("[DEBUG] Formula result for raw ");
            Serial.print(raw); Serial.print(": ");
            Serial.println(expectedLux, 4);
            String status = String(DEVICE_ID) + ":" + 
                           (lightState ? "ON" : "OFF") + ":" +
                           String(currentLux, 1) + ":" +
                           String(currentPWM) + ":" +
                           String(raw);
            // Send UDP only to master, not broadcast
            IPAddress masterIP(192,168,137,1); // Set to your master server IP
            uint16_t masterPort = 4210;        // Set to your master server UDP port
            udpHandler.sendTo(status.c_str(), masterIP, masterPort);
        }
    }

    // Check for incoming UDP messages (process all available)
    while (true) {
        String response = udpHandler.receiveResponses(10);
        if (response.length() == 0) break;
        Serial.print("[DEBUG] Raw UDP received: ");
        Serial.println(response);
        if (response.startsWith("PWM:") && !autoMode) {
            int pwmVal = response.substring(4).toInt();
            currentPWM = constrain(pwmVal, PWM_MIN, PWM_MAX);
            analogWrite(LIGHT_PIN, currentPWM);
            Serial.print("[DEBUG] Manual override PWM: ");
            Serial.println(currentPWM);
        }
        // Mesh command format: ip:cmd:ttl (should have exactly two colons)
        int firstColon = response.indexOf(':');
        int secondColon = response.indexOf(':', firstColon + 1);
        int thirdColon = response.indexOf(':', secondColon + 1);
        if (firstColon > 0 && secondColon > firstColon && thirdColon == -1) {
            handleMeshCommand(response);
        } else {
            handleUDPMessage(response);
        }
    }
}
