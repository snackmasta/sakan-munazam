#include "OTAHandler.h"
#include "WiFiUDPHandler.h"
#include "AnalogSensor.h"
#include <ESP8266WiFi.h>

// OTA Update Configuration
#define OTA_SERVER "192.168.137.1"
#define OTA_PORT 5000
#define CURRENT_VERSION "1.0.0"
#define DEVICE_ID "light_207"

// WiFi credentials
const char* ssid = "ALICE";
const char* password = "@channel";

// Pin definitions
const int LDR_PIN = A0;       // Analog input for LDR
const int LIGHT_PIN = 15;     // D8/GPIO15 for PWM output
const int LED_PIN = LED_BUILTIN;

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
    
    // Initialize UDP and OTA handlers
    udpHandler.begin();
    otaHandler.begin();
    otaHandler.checkForUpdates();
    
    Serial.println("Device ready for OTA updates and UDP communication.");
    Serial.println("Current version: " + String(CURRENT_VERSION));
    Serial.println("Device ID: " + String(DEVICE_ID));
}

void handleUDPMessage(String message) {
    if (message == "ON") {
        lightState = true;
    } else if (message == "OFF") {
        lightState = false;
        analogWrite(LIGHT_PIN, 0);
        currentPWM = 0;
    }
}

void adjustLight() {
    if (!lightState) return;  // Don't adjust if light is off
    
    float currentLux = ldrSensor.readLux(LDR_FIXED_R);
    if (currentLux < 0) return;  // Invalid reading
    
    // Simple proportional control
    float error = TARGET_LUX - currentLux;
    int adjustment = error * 0.5;  // Adjust sensitivity with this multiplier
    
    currentPWM = constrain(currentPWM + adjustment, PWM_MIN, PWM_MAX);
    analogWrite(LIGHT_PIN, currentPWM);
    
    // Debug output
    Serial.print("Lux: ");
    Serial.print(currentLux);
    Serial.print(" PWM: ");
    Serial.println(currentPWM);
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
        float currentLux = ldrSensor.readLux(LDR_FIXED_R);
        String status = String(DEVICE_ID) + ":" + 
                       (lightState ? "ON" : "OFF") + ":" +
                       String(currentLux, 1) + ":" +
                       String(currentPWM);
        udpHandler.sendBroadcast(status.c_str());
    }

    // Check for incoming UDP messages
    String response = udpHandler.receiveResponses(10);
    if (response.length() > 0) {
        handleUDPMessage(response);
    }

    delay(10);  // Small delay to avoid busy loop
}
