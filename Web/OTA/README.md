# OTA ESP8266 Firmware Update System

## Node.js OTA Server

1. Place your compiled ESP8266 firmware binary as `firmware.bin` in this folder.
2. Run the server:
   ```powershell
   npm install express
   node server.js
   ```
3. The server exposes:
   - `/version?deviceId=<DEVICE_ID>` (returns latest firmware version for the device)
   - `/firmware?deviceId=<DEVICE_ID>` (serves the firmware binary for the device)

## ESP8266 Arduino Sketch

- Edit `esp8266_ota.ino` and set your WiFi credentials, the server's IP address, and a unique `DEVICE_ID` for each ESP8266.
- Flash the sketch to your ESP8266.
- On boot, the device checks for updates and performs OTA if a new version is available for its `DEVICE_ID`.

## Workflow

1. Update the `deviceFirmware` map in `server.js` with the correct version and binary filename for each device.
2. Place the corresponding firmware binary (e.g., `firmware_esp1.bin`, `firmware_esp2.bin`) in the server folder.
3. Devices will auto-update on next boot if a new version is available for their `DEVICE_ID`.

---

**Note:**
- The ESP8266 must be able to reach the server on your network.
- Use the Arduino IDE or PlatformIO to compile and export your firmware as the correct binary filename for each device (e.g., `firmware_esp1.bin`).
