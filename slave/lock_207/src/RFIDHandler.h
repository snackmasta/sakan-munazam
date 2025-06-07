#ifndef RFIDHANDLER_H
#define RFIDHANDLER_H

#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 0
#define SS_PIN  2

void initializeRFID();
bool isCardDetected();
String getCardUID();

#endif
