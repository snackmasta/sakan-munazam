#ifndef OTA_HANDLER_H
#define OTA_HANDLER_H

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>

class OTAHandler {
public:
    OTAHandler(const char* serverAddress, int serverPort, const char* deviceId, const char* currentVersion);
    bool begin();
    void checkForUpdates();

private:
    bool initWiFi(const char* ssid, const char* password);
    String getVersionFromPayload(const String& payload);

    const char* _serverAddress;
    int _serverPort;
    const char* _deviceId;
    const char* _currentVersion;
    const char* _ssid;
    const char* _password;
};

#endif // OTA_HANDLER_H
