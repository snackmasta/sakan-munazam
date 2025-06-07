"""
OPC Server Configuration

This module contains configuration settings for the OPC server including:
- Server connection parameters
- Tag definitions
- Data access settings
"""

# Server Configuration
OPC_SERVER_NAME = "Kepware.KEPServerEX.V6"
UPDATE_RATE = 100  # milliseconds

# Tag Groups
TAG_GROUPS = {
    "LIGHTS": "Lights",
    "LOCKS": "Locks",
    "SENSORS": "Sensors"
}

# Default values
DEFAULT_READ_TIMEOUT = 1000  # milliseconds
DEFAULT_WRITE_TIMEOUT = 1000  # milliseconds
