// LockControl.cpp
#include "LockControl.h"

// Constructor implementation
LockControl::LockControl(int pin) : _pin(pin) {
    // Constructor simply stores the pin number
    // pinMode and initial state setting will be done in begin()
}

// begin() method implementation
void LockControl::begin() {
    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW); // Default to locked state on startup
    Serial.print("LockControl initialized on GPIO: ");
    Serial.println(_pin);
}

// unlock() method implementation
void LockControl::unlock() {
    digitalWrite(_pin, HIGH);
    Serial.println("Lock state: UNLOCKED");
}

// lock() method implementation
void LockControl::lock() {
    digitalWrite(_pin, LOW);
    Serial.println("Lock state: LOCKED");
}