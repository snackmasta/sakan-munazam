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
                for tag in device1.get_children():
                    print(tag, tag.get_browse_name())  # Print both node and browse name
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
