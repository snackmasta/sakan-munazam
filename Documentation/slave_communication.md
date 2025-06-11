# Slave Device Communication Analysis

## Overview

Each slave device (Light_207, Light_208, Lock_207, Lock_208) participates in a networked system involving a Web Interface, OTA Server (Node.js), Master Server (Python), and KEPServer/OPC. Communication occurs over HTTP and UDP protocols, with specific roles for each component.

---

## Light Controllers (light_207, light_208)

### Incoming Communication

- **From OTA Server:**  
  - Protocol: HTTP  
  - Purpose: OTA updates, configuration, or commands.

- **From Master Server:**  
  - Protocol: UDP  
  - Purpose: Real-time control commands, status requests, or event notifications.

### Outgoing Communication

- **To Master Server:**  
  - Protocol: UDP  
  - Purpose: Status updates, sensor data, or event responses.

---

## Lock Controllers (lock_207, lock_208)

### Incoming Communication

- **From OTA Server:**  
  - Protocol: HTTP  
  - Purpose: OTA updates, configuration, or commands.

- **From Master Server:**  
  - Protocol: UDP  
  - Purpose: Real-time control commands, status requests, or event notifications.

### Outgoing Communication

- **To Master Server:**  
  - Protocol: UDP  
  - Purpose: Status updates, access logs, or event responses.

---

## Communication Flow Summary

- **OTA Server → Slaves:**  
  - HTTP for firmware updates and configuration.

- **Master Server ↔ Slaves:**  
  - UDP for real-time control and status exchange (bidirectional).

- **Web Interface:**  
  - Interacts with OTA Server and Master Server via HTTP/UDP relay, but not directly with slaves.

---

## Diagram Reference

See `current communication.mmd` for a visual representation of these interactions.
