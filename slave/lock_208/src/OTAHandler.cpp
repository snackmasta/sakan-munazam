#include "OTAHandler.h"
#include <WiFiUdp.h>

OTAHandler::OTAHandler(const char* serverAddress, int serverPort, const char* deviceId, const char* currentVersion) 
    : _serverAddress(serverAddress), 
      _serverPort(serverPort), 
      _deviceId(deviceId), 
      _currentVersion(currentVersion) {
}

bool OTAHandler::begin() {
    Serial.println("[OTA] Handler initialized");
    return true;
}

bool OTAHandler::initWiFi(const char* ssid, const char* password) {
    _ssid = ssid;
    _password = password;
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(_ssid, _password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) { // 10 second timeout
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("\nWiFi connection failed!");
        return false;
    }
    
    Serial.println("\nConnected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    return true;
}

void OTAHandler::checkForUpdates() {
    Serial.println("[OTA] Checking for firmware updates...");
    delay(1000); // Give WiFi connection time to stabilize
    
    WiFiClient client;
    HTTPClient http;
    
    String versionUrl = String("http://") + _serverAddress + ":" + _serverPort + "/version?deviceId=" + _deviceId;
    Serial.print("[OTA] Version check URL: ");
    Serial.println(versionUrl);
    
    if (!http.begin(client, versionUrl)) {
        Serial.println("[OTA] HTTP Begin failed");
        return;
    }
    
    int httpCode = http.GET();
    Serial.print("[OTA] HTTP GET code: ");
    Serial.println(httpCode);
    
    if (httpCode != HTTP_CODE_OK) {
        Serial.print("[OTA] Version check failed. HTTP code: ");
        Serial.println(httpCode);
        http.end();
        client.stop();
        delay(100);
        return;
    }
    
    String payload = http.getString();
    http.end();
    delay(100);
    
    if (payload.length() == 0) {
        Serial.println("[OTA] Empty payload received");
        client.stop();
        return;
    }
    
    Serial.print("[OTA] Version payload: ");
    Serial.println(payload);
    
    String latestVersion = getVersionFromPayload(payload);
    if (latestVersion.length() == 0) {
        Serial.println("[OTA] Failed to parse version from payload");
        client.stop();
        return;
    }
    
    Serial.print("[OTA] Latest version on server: ");
    Serial.println(latestVersion);
    Serial.print("[OTA] Current firmware version: ");
    Serial.println(_currentVersion);
    
    if (latestVersion != _currentVersion) {
        Serial.println("[OTA] New firmware available. Starting OTA update...");
        String firmwareUrl = String("http://") + _serverAddress + ":" + _serverPort + "/firmware?deviceId=" + _deviceId;
        Serial.print("[OTA] Firmware download URL: ");
        Serial.println(firmwareUrl);

        ESPhttpUpdate.rebootOnUpdate(true);
        // --- OTA Progress Reporting via UDP ---
        static WiFiUDP udp;
        auto progressCb = [&](size_t progress, size_t total) {
            int percent = (progress * 100) / total;
            char msg[64];
            snprintf(msg, sizeof(msg), "OTA_PROGRESS:%s:%d", _deviceId, percent);
            udp.beginPacket(IPAddress(192,168,137,1), 4210);
            udp.write((uint8_t*)msg, strlen(msg));
            udp.endPacket();
        };
        ESPhttpUpdate.onProgress(progressCb);
        // --- End OTA Progress Reporting ---
        t_httpUpdate_return ret = ESPhttpUpdate.update(client, firmwareUrl, _currentVersion);
        
        switch (ret) {
            case HTTP_UPDATE_FAILED:
                Serial.printf("[OTA] HTTP_UPDATE_FAILED Error (%d): %s\n", 
                            ESPhttpUpdate.getLastError(), 
                            ESPhttpUpdate.getLastErrorString().c_str());
                break;
            case HTTP_UPDATE_NO_UPDATES:
                Serial.println("[OTA] No updates available.");
                break;
            case HTTP_UPDATE_OK:
                Serial.println("[OTA] Update successful! Rebooting...");
                break;
        }
    } else {
        Serial.println("[OTA] Firmware is up to date.");
    }
    
    client.stop();
    delay(100);
}

String OTAHandler::getVersionFromPayload(const String& payload) {
    int idx = payload.indexOf(":");
    if (idx > 0) {
        int start = payload.indexOf('"', idx + 1) + 1;
        int end = payload.indexOf('"', start);
        return payload.substring(start, end);
    }
    return "";
}
