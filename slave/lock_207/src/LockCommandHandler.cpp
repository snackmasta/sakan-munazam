#include "LockCommandHandler.h"

LockCommandHandler::LockCommandHandler(LockControl* lockCtrl, WiFiUDPHandler* udpHandler, 
                                       const char* deviceId, IPAddress masterIp, uint16_t masterPort)
    : lockController(lockCtrl), udpHandler(udpHandler), 
      deviceId(deviceId), masterIp(masterIp), masterPort(masterPort) {
}

void LockCommandHandler::handleUDPMessage(String message) {
    Serial.print("Received command: ");
    Serial.println(message);
    
    if (message == "UNLOCK") {
        lockController->unlock();
        String statusMsg = String(deviceId) + ":UNLOCKED";
        udpHandler->sendTo(statusMsg.c_str(), masterIp, masterPort);
    } else if (message == "LOCK") {
        lockController->lock();
        String statusMsg = String(deviceId) + ":LOCKED";
        udpHandler->sendTo(statusMsg.c_str(), masterIp, masterPort);
    } else {
        Serial.println("Unknown command received.");
    }
}

void LockCommandHandler::handleMeshCommand(String message) {
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
        udpHandler->sendTo(relayMsg.c_str(), targetIp, 4210);
    } else {
        Serial.println("[MESH RELAY] TTL expired, not relaying.");
    }
}
