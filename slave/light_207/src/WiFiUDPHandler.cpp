#include "WiFiUDPHandler.h"

WiFiUDPHandler::WiFiUDPHandler(const char* ssid, const char* password, int port)
  : _ssid(ssid), _password(password), _port(port) {}

void WiFiUDPHandler::begin() {
  connectWithDHCP();

  IPAddress dhcp_gateway = WiFi.gatewayIP();
  IPAddress dhcp_subnet = WiFi.subnetMask();

  IPAddress static_ip = dhcp_gateway;
  static_ip[3] = 248;  // decrement from the first slave

  WiFi.disconnect();
  delay(1000);
  WiFi.config(static_ip, dhcp_gateway, dhcp_subnet);
  connectWithStaticIP();

  _udp.begin(_port);
}

void WiFiUDPHandler::connectWithDHCP() {
  WiFi.begin(_ssid, _password);
  Serial.print("Connecting to WiFi (DHCP)");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected with DHCP.");
  Serial.print("DHCP IP: ");
  Serial.println(WiFi.localIP());
}

void WiFiUDPHandler::connectWithStaticIP() {
  WiFi.begin(_ssid, _password);
  Serial.println("Reconnecting using static IP...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected with static IP.");
  Serial.print("Static IP: ");
  Serial.println(WiFi.localIP());
}

void WiFiUDPHandler::sendBroadcast(const char* message) {
  _udp.beginPacket("255.255.255.255", _port);
  _udp.print(message);
  _udp.endPacket();
}

void WiFiUDPHandler::sendTo(const char* message, IPAddress ip, uint16_t port) {
    _udp.beginPacket(ip, port);
    _udp.print(message);
    _udp.endPacket();
}

String WiFiUDPHandler::receiveResponses(unsigned long timeoutMs) {
  unsigned long start = millis();
  while (millis() - start < timeoutMs) {
    int packetSize = _udp.parsePacket();
    if (packetSize) {
      char incomingBuffer[255];
      int len = _udp.read(incomingBuffer, 255);
      if (len > 0) {
        incomingBuffer[len] = '\0';
        return String(incomingBuffer);
      }
    }
    delay(10);
  }
  return "";
}
