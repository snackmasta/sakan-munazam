#include "RFIDHandler.h"

MFRC522 rfid(SS_PIN, RST_PIN);

void initializeRFID() {
  rfid.PCD_Init();
}

bool isCardDetected() {
  return rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial();
}

String getCardUID() {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      uid += "0"; // Add leading zero if byte is less than 0x10
    }
    uid += String(rfid.uid.uidByte[i], HEX); // Add the hex representation of the byte
    if (i < rfid.uid.size - 1) { // Add a colon if it's not the last byte
      uid += ":";
    }
  }
// uid will now be in the format "04:3D:84:BA:EA:68:80"
  uid.toUpperCase();
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  return uid;
}
