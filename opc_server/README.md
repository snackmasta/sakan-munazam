# OPC Server Implementation

This repository contains the implementation of OPC UA communication with KEPserver EX 6.

## Project Structure

```
opc_server/
├── src/
│   ├── core/                  # Core implementation
│   │   ├── kepserver_config.py  # Main KEPserver configuration class
│   │   ├── opc_handler.py       # OPC UA communication handler
│   │   └── __init__.py
│   ├── debug_tools/          # Debug and exploration tools
│   │   ├── browse_namespace.py
│   │   ├── explore_nodes.py
│   │   ├── find_channel_methods.py
│   │   ├── check_nodes.py
│   │   └── browse_server.py
│   ├── tests/               # Test files
│   │   ├── test_kepserver.py
│   │   └── test_kepserver_new.py
│   └── examples/           # Example implementations
│       ├── kepserver6.py
│       ├── kepserver_config_new.py
│       └── kepserver_config_new2.py
└── config/                # Configuration files
    └── settings.py
```

## Components

### Core Implementation
- `kepserver_config.py`: Main class for interacting with KEPserver EX 6
- `opc_handler.py`: Handles OPC UA communication

### Debug Tools
- `browse_namespace.py`: Tool for exploring the OPC UA namespace
- `explore_nodes.py`: Detailed node inspection tool
- `find_channel_methods.py`: Discovers available methods
- `check_nodes.py`: Node validation tool
- `browse_server.py`: Server exploration utility

### Tests
- `test_kepserver.py`: Main test suite
- `test_kepserver_new.py`: Additional tests

### Examples
Contains example implementations and variations of the KEPserver configuration

## Usage

1. Core functionality is implemented in the `core` directory
2. For development and debugging, use tools in the `debug_tools` directory
3. Run tests from the `tests` directory
4. Check `examples` for implementation examples

## Current Features

- Channel verification
- Device listing and verification
- Tag operations (create, read, write)
- Namespace browsing
- Connection to existing channels (Room_207, Room_208)
- Support for existing devices (Lock_207, Lock_208, Lux_207, Lux_208)
