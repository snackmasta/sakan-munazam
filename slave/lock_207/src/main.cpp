#include "WiFiUDPHandler.h"
#include "LockControl.h"
#include "RFIDHandler.h"
#include "OTAHandler.h"

// OTA Update Configuration
#define OTA_SERVER "192.168.137.1"
#define OTA_PORT 5000
#define CURRENT_VERSION "1.0.12"
#define DEVICE_ID "lock_207"

const char* ssid = "ALICE";
const char* password = "@channel";

// Define the GPIO pin for the lock control
#define LOCK_GPIO_PIN 15
#define MASTER_UDP_PORT 4210

WiFiUDPHandler udpHandler(ssid, password);
LockControl lockController(LOCK_GPIO_PIN);
OTAHandler otaHandler(OTA_SERVER, OTA_PORT, DEVICE_ID, CURRENT_VERSION);

// Define master IP as IPAddress object
IPAddress masterIp(192,168,137,1);

void setup() {
    Serial.begin(115200);
    delay(100);
    
    // Initialize WiFi and check for updates
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected!");
    
    otaHandler.begin();
    otaHandler.checkForUpdates();
    
    delay(500); // Add delay before hardware initialization
    
    // Initialize hardware and other modules
    SPI.begin();
    initializeRFID();
    udpHandler.begin();
    lockController.begin();
    
    Serial.println("ESP8266 ready. Waiting for commands...");
}

void handleUDPMessage(String message);

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

void handleUDPMessage(String message) {
    Serial.print("Received command: ");
    Serial.println(message);
    if (message == "UNLOCK") {
        lockController.unlock();
    } else if (message == "LOCK") {
        lockController.lock();
    } else {
        Serial.println("Unknown command received.");
    }
}

void loop() {
    // 1. Check for card and send UID to master if detected
    if (isCardDetected()) {
        String uid = getCardUID();
        String message = String(DEVICE_ID) + ":" + uid;
        Serial.println("Card detected: " + uid);
        Serial.println("Sending: " + message);
        
        // Send UDP message directly to master (unicast, not broadcast)
        udpHandler.sendTo(message.c_str(), masterIp, MASTER_UDP_PORT);
        delay(10);
    }

    // 2. Always listen for UDP responses
    String data = udpHandler.receiveResponses(100); // Use a short timeout for responsiveness
    if (data != "") {
        // Mesh command: device_id:command
        if (data.indexOf(":") > 0) {
            handleMeshCommand(data);
        } else {
            handleUDPMessage(data);
        }
    }

    delay(10); // Small delay to avoid busy loop
}