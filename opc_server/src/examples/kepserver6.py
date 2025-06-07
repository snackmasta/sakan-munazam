from kepserver_config import KepserverConfigurator

# Create KEPserver configurator instance
kepserver = KepserverConfigurator("opc.tcp://127.0.0.1:49320")

try:
    # Connect to KEPserver
    if kepserver.connect():
        # Example: Create a new channel and device
        channel_name = "Room_207"
        device_name = "Lock_207"
        
        # Create tags in the device
        kepserver.create_tag(
            channel_name=channel_name,
            device_name=device_name,
            tag_name="Status",
            data_type="String",
            address="400001",
            description="Lock status (LOCKED/UNLOCKED)"
        )
        
        kepserver.create_tag(
            channel_name=channel_name,
            device_name=device_name,
            tag_name="LastAccess",
            data_type="String",
            address="400002",
            description="Timestamp of last access"
        )
        
        # Write and read tag values
        tag_path = f"{channel_name}.{device_name}.Status"
        kepserver.write_tag_value(tag_path, "LOCKED")
        
        # Read the value back
        status = kepserver.read_tag_value(tag_path)

except Exception as e:
    print("Error:", e)
finally:
    try:
        client.disconnect()
        print("Disconnected")
    except Exception as e:
        print("Disconnect error:", e)
