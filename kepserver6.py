from opcua import Client, ua

# Connect using no security
client = Client("opc.tcp://127.0.0.1:49320")

try:
    client.connect()
    print("Connected to OPC UA server")

    root = client.get_root_node()
    print("Root node is: ", root)

    # Browse to your node
    objects = client.get_objects_node()
    print("Children of Objects node:")
    for child in objects.get_children():
        print(child, child.get_browse_name())

    # Try to get 'Channel1' node in namespace 2
    try:
        channel1 = objects.get_child(["2:Channel1"])
        print("Found Channel1 node:", channel1)
        print("Children of Channel1 node:")
        for child in channel1.get_children():
            print(child, child.get_browse_name())
            # Check for Device1
            if child.get_browse_name().Name == "Device1":
                device1 = child
                print("Found Device1 node:", device1)
                print("Tags inside Device1:")
                tag1 = device1.get_child(["2:Tag1"])
                tag2 = device1.get_child(["2:Tag2"])
                print("Tag1 node:", tag1)
                print("Tag2 node:", tag2)

                import time
                print("Realtime updating Tag1 and Tag2 values (press Ctrl+C to stop):")
                while True:
                    try:
                        val1 = tag1.get_value()
                        val2 = tag2.get_value()
                        print(f"Tag1: {val1} | Tag2: {val2}")
                        time.sleep(1)  # Update every second
                    except KeyboardInterrupt:
                        print("Stopped realtime update.")
                        break
    except Exception as e:
        print("Could not find 'Channel1':", e)

except Exception as e:
    print("Error:", e)
finally:
    try:
        client.disconnect()
        print("Disconnected")
    except Exception as e:
        print("Disconnect error:", e)
