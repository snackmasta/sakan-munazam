# Side-by-Side Code Comparison

## 🔄 Light Control Algorithm

### Calibration-Fix Branch ✅
```cpp
void adjustLight() {
    if (!lightState) return;
    int raw = ldrSensor.readRaw();
    float currentLux = ldrSensor.calibratedLux(raw);
    if (currentLux < 0) currentLux = ldrSensor.readLux(LDR_FIXED_R);

    // Debug output
    Serial.print("Raw: ");
    Serial.print(raw);
    Serial.print(" Lux: ");
    Serial.print(currentLux);

    // Simple proportional control using LUX
    float error = TARGET_LUX - currentLux;
    int adjustment = error * 0.5;
    currentPWM = constrain(currentPWM + adjustment, PWM_MIN, PWM_MAX);
    analogWrite(LIGHT_PIN, currentPWM);

    Serial.print(" PWM: ");
    Serial.println(currentPWM);
}
```

### Main Branch ❌
```cpp
void adjustLight() {
    if (!lightState || !autoMode) return;  // Additional mode check
    int raw = ldrSensor.readRaw();
    float currentLux = ldrSensor.calibratedLux(raw);
    if (currentLux < 0) currentLux = ldrSensor.readLux(LDR_FIXED_R);

    // Debug output with mode info
    Serial.print("Raw: ");
    Serial.print(raw);
    Serial.print(" Lux: ");
    Serial.print(currentLux);
    Serial.print(" Mode: ");
    Serial.print(autoMode ? "AUTO" : "MANUAL");

    if (autoMode) {
        // Uses RAW ADC values instead of LUX!
        float error = targetLDR - raw;  // ← Problem: raw vs lux mixing
        int adjustment = error * 0.5;
        currentPWM = constrain(currentPWM + adjustment, PWM_MIN, PWM_MAX);
        analogWrite(LIGHT_PIN, currentPWM);
    }

    Serial.print(" PWM: ");
    Serial.println(currentPWM);
}
```

---

## 🎛️ Variables & Configuration

### Calibration-Fix Branch ✅
```cpp
// Clean, focused configuration
#define CURRENT_VERSION "1.0.24"
#define TARGET_LUX 500.0    // Proper lux units
bool lightState = false;
int currentPWM = 0;
const long udpBroadcastInterval = 5000;  // 5 seconds
```

### Main Branch ❌
```cpp
// Mixed configuration with legacy code
#define CURRENT_VERSION "1.0.22"
// #define TARGET_LUX 500.0    // Commented out!
// float targetLux = 500.0;    // Commented out!
int targetLDR = 500;    // Raw ADC target - inconsistent
bool lightState = false;
int currentPWM = 0;
bool autoMode = true;   // Additional complexity
const long udpBroadcastInterval = 500;  // 0.5 seconds - too frequent
```

---

## 📡 UDP Message Handling

### Calibration-Fix Branch ✅
```cpp
void handleUDPMessage(String message) {
    if (message == "ON") {
        lightState = true;
    } else if (message == "OFF") {
        lightState = false;
        analogWrite(LIGHT_PIN, 0);
        currentPWM = 0;
    } else if (message.startsWith("CAL:")) {
        handleCalibrationCommand(message);
    }
    // Clean, simple, focused
}
```

### Main Branch ❌
```cpp
void handleUDPMessage(String message) {
    if (message == "ON") {
        lightState = true;
    } else if (message == "OFF") {
        lightState = false;
        analogWrite(LIGHT_PIN, 0);
        currentPWM = 0;
    } else if (message == "PWM_MANUAL") {
        autoMode = false;
        Serial.println("Switched to MANUAL PWM mode");
    } else if (message == "PWM_AUTO") {
        // Complex mode switching logic
        int raw = ldrSensor.readRaw();
        targetLDR = raw;
        autoMode = true;
        Serial.print("Switched to AUTO PWM mode, new targetLDR: ");
        Serial.println(targetLDR);
    } else if (message.startsWith("PWM:")) {
        if (!autoMode) {
            int pwmVal = message.substring(4).toInt();
            currentPWM = constrain(pwmVal, PWM_MIN, PWM_MAX);
            analogWrite(LIGHT_PIN, currentPWM);
        }
    } else if (message.startsWith("CAL:")) {
        handleCalibrationCommand(message);
    }
    // Complex, mode-dependent, harder to maintain
}

// Additional complexity: Mesh networking
void handleMeshCommand(String message) {
    // 40+ lines of complex mesh routing logic
    // TTL management, IP parsing, relay logic
    // Potential for loops and failures
}
```

---

## 🔧 Sensor Initialization

### Calibration-Fix Branch ✅
```cpp
void AnalogSensor::begin() {
    // No pinMode needed for analog inputs on ESP8266
    // Explicit calibration loading in main.cpp
}

// In main.cpp setup():
ldrSensor.begin();
ldrSensor.loadCalibration();  // Explicit control
```

### Main Branch ❌
```cpp
void AnalogSensor::begin() {
    // No pinMode needed for analog inputs on ESP8266
    loadCalibration();  // Auto-loads, less control
}

// In main.cpp setup():
ldrSensor.begin();  // Calibration loaded automatically
```

---

## 📊 Key Metrics Comparison

| Metric | Calibration-Fix | Main | Improvement |
|--------|----------------|------|-------------|
| **Code Lines** | 183 | 229 | 🟢 -20% |
| **Functions** | 4 main | 6 main | 🟢 -33% |
| **Network Traffic** | Every 5s | Every 0.5s | 🟢 -90% |
| **Control Modes** | 1 (unified) | 2 (manual/auto) | 🟢 -50% |
| **Command Types** | 3 core | 7+ extended | 🔴 +133% |
| **Accuracy** | Lux-based | ADC-based | 🟢 Better |

---

## 🎯 Critical Issues in Main Branch

### 1. **Unit Inconsistency** 🚨
```cpp
// Main branch mixes units inconsistently:
float currentLux = ldrSensor.calibratedLux(raw);  // Calculates lux
float error = targetLDR - raw;                    // But uses raw ADC!
```

### 2. **Network Flooding** 🚨
```cpp
// Broadcasts every 0.5 seconds = 120 messages per minute per device
const long udpBroadcastInterval = 500;  // Too frequent!
```

### 3. **Mode Complexity** ⚠️
```cpp
// Complex mode switching creates potential for confusion
if (!lightState || !autoMode) return;  // Double conditions
```

### 4. **Commented Dead Code** ⚠️
```cpp
// #define TARGET_LUX 500.0    // Why commented?
// float targetLux = 500.0;    // Unused variable
```

---

## ✅ Calibration-Fix Advantages

1. **Consistent Units**: Always uses lux for light measurement
2. **Simplified Logic**: Single mode, clear purpose
3. **Network Efficiency**: 10x less broadcast traffic
4. **Cleaner Code**: No dead code or commented sections
5. **Better Accuracy**: Proper calibrated sensor readings
6. **Easier Debugging**: Fewer variables and states
7. **Production Ready**: Stable, focused implementation

**Verdict: Calibration-Fix branch is significantly superior for production use.**
