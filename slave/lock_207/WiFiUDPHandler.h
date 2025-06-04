#ifndef WIFI_UDP_HANDLER_H
#define WIFI_UDP_HANDLER_H

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

class WiFiUDPHandler {
  public:
    WiFiUDPHandler(const char* ssid, const char* password, int port = 4210);
    void begin();
    void sendBroadcast(const char* message);
    String receiveResponses(unsigned long timeoutMs = 3000);

  private:
    const char* _ssid;
    const char* _password;
    int _port;
    WiFiUDP _udp;

    void connectWithDHCP();
    void connectWithStaticIP();
};

#endif
