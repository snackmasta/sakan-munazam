#ifndef LOCK_COMMAND_HANDLER_H
#define LOCK_COMMAND_HANDLER_H

#include "LockControl.h"
#include "WiFiUDPHandler.h"
#include <ESP8266WiFi.h>

class LockCommandHandler {
public:
    LockCommandHandler(LockControl* lockCtrl, WiFiUDPHandler* udpHandler, 
                       const char* deviceId, IPAddress masterIp, uint16_t masterPort);
    
    void handleUDPMessage(String message);
    void handleMeshCommand(String message);

private:
    LockControl* lockController;
    WiFiUDPHandler* udpHandler;
    const char* deviceId;
    IPAddress masterIp;
    uint16_t masterPort;
};

#endif
