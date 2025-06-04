// LockControl.h
#ifndef LOCK_CONTROL_H
#define LOCK_CONTROL_H

#include <Arduino.h> // Needed for pinMode and digitalWrite

class LockControl {
public:
    // Constructor: Takes the GPIO pin number as an argument
    LockControl(int pin);

    // Initializes the GPIO pin
    void begin();

    // Sets the lock to an unlocked state
    void unlock();

    // Sets the lock to a locked state
    void lock();

private:
    int _pin; // Stores the GPIO pin number
};

#endif // LOCK_CONTROL_H