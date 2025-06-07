from kepserver_config import KepserverConfigurator
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
        
        # Step 2: Create test channel and device
        print("\n2. Creating test channel and device...")
        channel_name = "TestChannel"
        device_name = "TestDevice"
        
        if not kepserver.create_channel(channel_name):
            print("Failed to create channel")
            return

        # Give KEPserver a moment to set up the channel
        time.sleep(2)
        
        if not kepserver.create_device(channel_name, device_name):
            print("Failed to create device")
            return

        # Give KEPserver a moment to set up the device
        time.sleep(2)
        
        # Step 3: Create test tags
        print("\n3. Creating test tags...")
        tags = [
            {"name": "TestValue", "type": "Float", "address": "R0", "description": "Test value"},
            {"name": "TestString", "type": "String", "address": "R1", "description": "Test string"},
            {"name": "TestBool", "type": "Boolean", "address": "R2", "description": "Test boolean"}
        ]
        
        for tag in tags:
            success = kepserver.create_tag(
                channel_name=channel_name,
                device_name=device_name,
                tag_name=tag["name"],
                data_type=tag["type"],
                address=tag["address"],
                description=tag["description"]
            )
            if not success:
                print(f"Failed to create tag {tag['name']}")
                return
            time.sleep(1)  # Give KEPserver time between tag creations
            
        # Give KEPserver a moment to set up all tags
        time.sleep(2)
            
        # Step 4: Test writing values
        print("\n4. Testing write operations...")
        test_values = {
            f"{channel_name}.{device_name}.TestValue": 123.45,
            f"{channel_name}.{device_name}.TestString": "Hello OPC",
            f"{channel_name}.{device_name}.TestBool": True
        }
        
        for tag_path, value in test_values.items():
            if not kepserver.write_tag_value(tag_path, value):
                print(f"Failed to write to {tag_path}")
                return
            time.sleep(1)  # Give KEPserver time between writes
            
        # Give KEPserver a moment to process all writes
        time.sleep(2)
            
        # Step 5: Test reading values back
        print("\n5. Testing read operations...")
        all_reads_successful = True
        for tag_path, expected_value in test_values.items():
            read_value = kepserver.read_tag_value(tag_path)
            if read_value is None:
                print(f"Failed to read from {tag_path}")
                all_reads_successful = False
            else:
                print(f"Read {tag_path}: {read_value} (Expected: {expected_value})")
            time.sleep(1)  # Give KEPserver time between reads
            
        if all_reads_successful:
            print("\nTest completed successfully!")
        else:
            print("\nTest completed with some read failures")
            
    except Exception as e:
        print(f"\nTest failed with error: {e}")
    finally:
        # Clean up
        kepserver.disconnect()

if __name__ == "__main__":
    test_kepserver()
