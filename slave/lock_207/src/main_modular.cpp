#include "WiFiUDPHandler.h"
#include "LockControl.h"
#include "RFIDHandler.h"
#include "OTAHandler.h"
#include "LockCommandHandler.h"

// Configuration constants
#define OTA_SERVER "192.168.137.1"
#define OTA_PORT 5000
#define CURRENT_VERSION "1.0.13"
#define DEVICE_ID "lock_207"
#define LOCK_GPIO_PIN 15
#define MASTER_UDP_PORT 4210

// WiFi credentials
const char* ssid = "ALICE";
const char* password = "@channel";

// Component instances
WiFiUDPHandler udpHandler(ssid, password);
LockControl lockController(LOCK_GPIO_PIN);
OTAHandler otaHandler(OTA_SERVER, OTA_PORT, DEVICE_ID, CURRENT_VERSION);
IPAddress masterIp(192, 168, 137, 1);
LockCommandHandler commandHandler(&lockController, &udpHandler, DEVICE_ID, masterIp, MASTER_UDP_PORT);

void setup() {
    Serial.begin(115200);
    delay(100);
    
    // Initialize WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected!");
    
    // Initialize OTA and check for updates
    otaHandler.begin();
    otaHandler.checkForUpdates();
    
    delay(500); // Add delay before hardware initialization
    
    // Initialize hardware components
    SPI.begin();
    initializeRFID();
    udpHandler.begin();
    lockController.begin();
    
    Serial.println("ESP8266 ready. Waiting for commands...");
}

void loop() {
    // Check for RFID card and send UID to master if detected
    if (isCardDetected()) {
        String uid = getCardUID();
        String message = String(DEVICE_ID) + ":" + uid;
        Serial.println("Card detected: " + uid);
        Serial.println("Sending: " + message);
        
        udpHandler.sendTo(message.c_str(), masterIp, MASTER_UDP_PORT);
        delay(10);
    }

    // Listen for UDP commands
    String data = udpHandler.receiveResponses(100);
    if (data != "") {
        // Check if it's a mesh command (has colons)
        if (data.indexOf(":") > 0) {
            commandHandler.handleMeshCommand(data);
        } else {
            commandHandler.handleUDPMessage(data);
        }
    }

    delay(10); // Small delay to avoid busy loop
}
