# Light Slave Project Comparison

This directory contains versions of the light slave projects from different branches for comparison.

## Directory Structure

```
comparison/
├── calibration-fix-version/    # Latest calibration-fix branch
│   ├── light_207/
│   └── light_208/
├── main-version/               # Current main branch
│   ├── light_207/
│   └── light_208/
└── README.md                   # This file
```

## Key Differences Expected

### Calibration-Fix Branch Features:
- Enhanced LDR calibration system with polynomial regression
- Improved sensor reading accuracy
- Better light control algorithms
- Advanced calibration coefficient handling
- EEPROM-based calibration storage

### Main Branch Features:
- Standard LDR reading implementation
- Basic light control
- Simple calibration methods

## How to Compare

### Using VS Code:
1. Open VS Code
2. Install "Compare Folders" extension if not already installed
3. Right-click on `calibration-fix-version` → "Compare with Folder"
4. Select `main-version` folder
5. View side-by-side differences

### Using Git (from project root):
```bash
# Compare specific files between branches
git diff main..calibration-fix -- slave/light_207/src/main.cpp
git diff main..calibration-fix -- slave/light_207/src/AnalogSensor.cpp
git diff main..calibration-fix -- slave/light_208/src/main.cpp
git diff main..calibration-fix -- slave/light_208/src/AnalogSensor.cpp
```

### Using Command Line:
```bash
# Compare file differences
fc /B calibration-fix-version\light_207\src\main.cpp main-version\light_207\src\main.cpp
```

## Important Files to Compare

### Core Files:
- `src/main.cpp` - Main application logic
- `src/AnalogSensor.cpp` - Sensor reading implementation
- `src/AnalogSensor.h` - Sensor interface
- `platformio.ini` - Build configuration

### Focus Areas:
1. **Calibration Functions** - Look for enhanced calibration methods
2. **Sensor Reading** - Compare accuracy improvements
3. **Light Control** - Check for algorithm improvements
4. **EEPROM Usage** - Calibration data storage
5. **UDP Commands** - Any new calibration commands

## Version Information

- **Generated**: June 12, 2025
- **Calibration-Fix Branch**: Latest commits with enhanced calibration
- **Main Branch**: Current production version
- **Purpose**: Feature comparison and code review

## Next Steps

1. Review the differences in the key files
2. Test calibration improvements
3. Validate enhanced sensor accuracy
4. Consider merging beneficial changes
5. Update documentation as needed
