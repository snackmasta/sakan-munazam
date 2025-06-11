# System Communication Topology

## Overview

This document describes the communication topology of the sakan-munazam system, including all major components and their interactions.

## Components

- **Master Server** (Python): Handles device management, UDP communication, and access control.
- **Slave Devices** (ESP8266/Arduino): Includes light and lock controllers, each with unique device IDs.
- **OTA Server** (Node.js): Manages firmware updates for slave devices.
- **KEPServer/OPC**: Provides industrial protocol integration and channel management.
- **Web Interface**: For OTA management and device monitoring.

## Communication Flows

### 1. Master ↔ Slave Devices

- **Protocol**: UDP
- **Direction**: Bidirectional
- **Purpose**: Device state reporting, control commands, and access events.
- **Details**:
  - Slaves send status and event messages to the master via UDP.
  - Master sends control commands (e.g., ON/OFF, LOCK/UNLOCK) to slaves via UDP.
  - Device registration and address updates are managed dynamically.

### 2. Slave Devices ↔ OTA Server

- **Protocol**: HTTP
- **Direction**: Slave-initiated
- **Purpose**: Firmware version check and binary download.
- **Details**:
  - On boot or scheduled interval, each device checks the OTA server for new firmware.
  - If a new version is available, the device downloads and installs the update.

### 3. Master ↔ KEPServer/OPC

- **Protocol**: HTTP (REST API)
- **Direction**: Master-initiated
- **Purpose**: Channel creation, configuration, and monitoring.
- **Details**:
  - Master scripts can create and manage channels via KEPServer REST API.
  - Device and tag configuration is typically manual due to KEPServer limitations.

### 4. Web Interface ↔ OTA Server

- **Protocol**: HTTP
- **Direction**: User-initiated
- **Purpose**: Device management, firmware upload, and monitoring.

### 5. Web Interface ↔ Devices (via UDP Relay)

- **Protocol**: HTTP (to server) + UDP (to device)
- **Direction**: User-initiated
- **Purpose**: Relays control commands from the web interface to devices using UDP relay endpoints.

## Network Layout

- All devices and servers are typically on the same local network (e.g., 192.168.137.x).
- Each slave device is assigned a static or DHCP IP address.
- UDP port 4210 is used for device communication.
- OTA server runs on port 5000.

## Example Message Flows

- **Device Status Update**: `light_207:ON:450.0:512:300` (UDP from device to master)
- **Control Command**: `ON` or `OFF` (UDP from master to device)
- **OTA Version Check**: `GET /version?deviceId=light_207` (HTTP from device to OTA server)

## Security Considerations

- UDP communication is not encrypted; use a secure network.
- OTA server should be protected from unauthorized access.
- Device IDs and firmware versions should be managed securely.

---

This topology ensures modular, scalable, and maintainable communication between all system components.
