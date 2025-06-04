#include "OTAHandler.h"
#include <ESP8266WiFi.h>

// OTA Update Configuration
#define OTA_SERVER "192.168.137.1"
#define OTA_PORT 5000
#define CURRENT_VERSION "1.0.0"  // Start with 1.0.0 for new devices
#define DEVICE_ID "new_device"   // Change this for each new device

// WiFi credentials
const char* ssid = "ALICE";
const char* password = "@channel";

OTAHandler otaHandler(OTA_SERVER, OTA_PORT, DEVICE_ID, CURRENT_VERSION);

// Status LED pin (built-in LED on most ESP8266 boards)
const int LED_PIN = LED_BUILTIN;
unsigned long lastBlink = 0;
const long blinkInterval = 1000;  // Blink every second
bool ledState = false;

void setup() {
    Serial.begin(115200);
    delay(100);
    
    // Setup status LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);  // LED off initially (ESP8266 LED is active LOW)
    
    // Initialize WiFi and check for updates
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));  // Blink LED while connecting
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    digitalWrite(LED_PIN, LOW);  // LED on when connected
    delay(1000);
    
    otaHandler.begin();
    otaHandler.checkForUpdates();
    
    Serial.println("Device ready for OTA updates.");
    Serial.println("Current version: " + String(CURRENT_VERSION));
    Serial.println("Device ID: " + String(DEVICE_ID));
}

void loop() {
    // Blink LED to show device is running
    unsigned long currentMillis = millis();
    if (currentMillis - lastBlink >= blinkInterval) {
        lastBlink = currentMillis;
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
    }

    // Add your custom code here
    // ...

    delay(10);  // Small delay to avoid busy loop
}
