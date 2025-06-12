# KEPServer Configuration Guide

## Overview
This guide covers both automated (via REST API) and manual configuration methods for KEPServer.

## What Works via REST API ✅
- **Channel Creation**: Fully supported
- **Channel Management**: Read, update, delete operations
- **Project Information**: Retrieving server status and configuration

## What Requires Manual Configuration ❌
- **Device Creation**: Not supported in current KEPServer version/license
- **Tag Creation**: Not supported via REST API
- **Complex device properties**: Must be configured through GUI

---

## Automated Channel Creation

### Quick Start
```bash
python create_channel_final.py
```

### Features
- Connection testing and validation
- Interactive channel creation
- Driver selection (Simulator, Modbus, OPC UA, etc.)
- Capability detection for device creation
- Error handling and user guidance

### Supported Drivers
- Simulator (for testing)
- Modbus TCP/IP Ethernet
- OPC UA Client
- Custom drivers (user-specified)

---

## Manual Device and Tag Configuration

### Method 1: KEPServer Administrator (Recommended)
1. **Open KEPServer Administrator**
2. **Navigate to your channel** (created via script)
3. **Create Device:**
   - Right-click channel → "New Device"
   - Configure device properties (ID, description, etc.)
   - Set communication parameters
4. **Add Tags:**
   - Right-click device → "New Tag"
   - Configure tag properties (address, data type, etc.)

### Method 2: KEPServer Configuration Client
1. Use KEPServer's Configuration Client for bulk operations
2. Import/export configurations
3. Better for large-scale deployments

### Method 3: OPF File Import
1. Create OPF (OPC Project File) configuration files
2. Import via KEPServer Administrator
3. Useful for standardized configurations

---

## Complete Workflow Example

### Step 1: Automated Channel Creation
```bash
# Run the channel creation script
python create_channel_final.py

# Example output:
# ✓ Successfully connected to KEPServer Configuration API!
# ✓ Channel 'ProductionLine1' created successfully!
```

### Step 2: Manual Device Configuration
1. Open KEPServer Administrator
2. Expand "ProductionLine1" channel
3. Right-click → "New Device"
4. Configure:
   - **Name**: "PLC001"
   - **Device ID**: "1"
   - **Description**: "Main Production PLC"

### Step 3: Manual Tag Creation
1. Right-click "PLC001" device → "New Tag"
2. Configure each tag:
   - **Name**: "Temperature"
   - **Address**: "40001"
   - **Data Type**: "Float"
   - **Access**: "Read/Write"

---

## Alternative Solutions

### 1. KEPServer EX Configuration API
- Some versions support more extensive REST operations
- Check KEPServer documentation for your specific version
- May require different licensing

### 2. OPC Client Approach
- Connect as OPC client to read/write data
- Use existing manually configured devices
- Focus on data exchange rather than configuration

### 3. Batch Configuration Scripts
- Create standardized OPF files
- Use KEPServer's import functionality
- Version control your configurations

---

## Troubleshooting

### Common Issues
1. **400 Bad Request for Device Creation**
   - Expected behavior with current KEPServer version
   - Use manual configuration methods

2. **401 Authentication Failed**
   - Check username/password in script
   - Verify KEPServer security settings

3. **Connection Refused**
   - Ensure KEPServer is running
   - Check if Configuration API is enabled
   - Verify port 57412 is accessible

### Testing Your Setup
```bash
# Test connection only
python check_api_capabilities.py

# Test with minimal channel creation
python create_channel_simple.py
```

---

## Script Reference

### Available Scripts
- `create_channel_final.py` - Complete solution with guidance
- `create_channel_simple.py` - Basic channel creation only
- `create_channel_enhanced.py` - Full-featured (devices won't work)
- `check_api_capabilities.py` - API testing and diagnostics

### Configuration
```python
# Default settings in scripts
host = "localhost"
config_port = 57412
username = "Administrator"
password = ""  # Set your password here
```

---

## Best Practices

### 1. Channel Organization
- Use descriptive channel names
- Group related devices in same channel
- Choose appropriate drivers for your hardware

### 2. Device Configuration
- Use consistent naming conventions
- Document device IDs and addresses
- Test communication before production

### 3. Tag Management
- Use meaningful tag names
- Set appropriate data types
- Consider polling rates and performance

### 4. Backup and Version Control
- Export configurations regularly
- Save OPF files in version control
- Document changes and configurations

---

## Future Enhancements

### Potential Improvements
1. **OPF File Generation**: Create scripts to generate configuration files
2. **Device Templates**: Standardized device configurations
3. **Bulk Operations**: Mass tag creation tools
4. **Configuration Validation**: Automated testing of setups

### Integration Options
- **SCADA Systems**: Connect to HMI/SCADA platforms
- **Databases**: Log data to SQL databases
- **Cloud Services**: Push data to IoT platforms
- **APIs**: Create custom REST endpoints for data access
