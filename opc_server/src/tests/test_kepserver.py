from ..core.kepserver_config import KepserverConfigurator
import time

def test_kepserver():
    # Create KEPserver configurator instance
    kepserver = KepserverConfigurator()
    
    try:
        # Step 1: Connect to KEPserver
        print("\n1. Testing connection...")
        if not kepserver.connect():
            print("Failed to connect to KEPserver")
            return
        
        # Step 2: Verify existing channels
        print("\n2. Verifying existing channels...")
        channels = ["Room_207", "Room_208"]
        
        for channel_name in channels:
            print(f"\nTesting channel: {channel_name}")
            if kepserver.verify_channel(channel_name):
                # Get and verify devices in the channel
                print(f"\nGetting devices for channel {channel_name}...")
                devices = kepserver.get_channel_devices(channel_name)
                
                for device_name in devices:
                    print(f"\nVerifying device: {device_name}")
                    if kepserver.verify_device(channel_name, device_name):
                        # Get and test tags in the device
                        print(f"\nGetting tags for device {device_name}...")
                        tags = kepserver.get_device_tags(channel_name, device_name)
                        
                        for tag_name in tags:
                            print(f"\nTesting tag: {tag_name}")
                            # Try reading the tag
                            value = kepserver.read_tag(channel_name, device_name, tag_name)
                            
                            if value is not None:
                                print(f"Successfully read value: {value}")
                                # Try writing the same value back
                                if kepserver.write_tag(channel_name, device_name, tag_name, value):
                                    print("Successfully wrote value back to tag")
                                else:
                                    print("Failed to write value to tag (might be read-only)")
                            else:
                                print("Failed to read tag value")
                    else:
                        print(f"Device {device_name} does not exist in channel {channel_name}")
            else:
                print(f"Channel {channel_name} does not exist")
                    
    finally:
        # Disconnect from KEPserver
        print("\nDisconnecting from KEPserver...")
        kepserver.disconnect()

if __name__ == "__main__":
    test_kepserver()
