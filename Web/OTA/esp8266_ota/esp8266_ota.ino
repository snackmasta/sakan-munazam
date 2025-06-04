// Replace with your WiFi credentials and server IP
#define WIFI_SSID "Bu Ikah"
#define WIFI_PASSWORD "ganteng05"
#define OTA_SERVER "192.168.100.119" // e.g., "192.168.1.100"
#define OTA_PORT 3001
#define CURRENT_VERSION "1.0.1"
#define DEVICE_ID "esp1" // Change this for each device

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  checkForUpdates(); // Check for new firmware only once at every reboot
}

void loop() {
  // Your main code here
}

void checkForUpdates() {
  HTTPClient http;
  String versionUrl = String("http://") + OTA_SERVER + ":" + OTA_PORT + "/version?deviceId=" + DEVICE_ID;
  WiFiClient client;
  http.begin(client, versionUrl);
  int httpCode = http.GET();
  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    String latestVersion = getVersionFromPayload(payload);
    if (latestVersion != CURRENT_VERSION) {
      Serial.println("New firmware available. Starting OTA update...");
      String firmwareUrl = String("http://") + OTA_SERVER + ":" + OTA_PORT + "/firmware?deviceId=" + DEVICE_ID;
      t_httpUpdate_return ret = ESPhttpUpdate.update(client, firmwareUrl, CURRENT_VERSION);
      switch (ret) {
        case HTTP_UPDATE_FAILED:
          Serial.printf("HTTP_UPDATE_FAILED Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
          break;
        case HTTP_UPDATE_NO_UPDATES:
          Serial.println("No updates available.");
          break;
        case HTTP_UPDATE_OK:
          Serial.println("Update successful!");
          break;
      }
    } else {
      Serial.println("Firmware is up to date.");
    }
  } else {
    Serial.println("Failed to check version.");
  }
  http.end();
}

String getVersionFromPayload(const String& payload) {
  int idx = payload.indexOf(":");
  if (idx > 0) {
    int start = payload.indexOf('"', idx + 1) + 1;
    int end = payload.indexOf('"', start);
    return payload.substring(start, end);
  }
  return "";
}
