from opcua import Client, ua
import time

# Try to discover endpoints first
try:
    discovery_client = Client("opc.tcp://ALICE:49320")
    endpoints = discovery_client.connect_and_get_server_endpoints()
    print("Discovered endpoints:")
    for ep in endpoints:
        print(f"  Endpoint: {ep.EndpointUrl}, Security: {ep.SecurityPolicyUri}, Mode: {ep.SecurityMode}")
    discovery_client.disconnect()
except Exception as e:
    print(f"Endpoint discovery failed: {e}")

# Now try to connect as before
client = Client("opc.tcp://ALICE:49320")

def browse_node(node, level=0, max_depth=2):
    indent = "  " * level
    try:
        print(f"{indent}- NodeId: {node.nodeid}, DisplayName: {node.get_display_name().Text}, Class: {node.get_node_class()}")
        if level < max_depth:
            for child in node.get_children():
                browse_node(child, level + 1, max_depth)
    except Exception as e:
        print(f"{indent}Error browsing node: {e}")

try:
    client.connect()
    print("Connected to OPC UA server")
    time.sleep(1)  # Give the server a moment

    # Print namespaces
    namespaces = client.get_namespace_array()
    print("Namespaces:")
    for idx, ns in enumerate(namespaces):
        print(f"  [{idx}] {ns}")

    # Browse root folder
    print("\nBrowsing RootFolder:")
    root = client.get_root_node()
    browse_node(root, max_depth=2)

    # Optionally, browse Objects folder for more details
    print("\nBrowsing Objects folder:")
    objects = client.get_objects_node()
    browse_node(objects, max_depth=2)

    # Browse Objects folder for channels
    print("\nListing available channels:")
    objects = client.get_objects_node()
    try:
        for child in objects.get_children():
            display_name = child.get_display_name().Text
            node_id = child.nodeid
            print(f"Channel: {display_name}, NodeId: {node_id}")
    except Exception as e:
        print(f"Error listing channels: {e}")

    # List all tags under ROOM 207/Device1
    print("\nListing tags under ROOM 207/Device1:")
    try:
        room207 = objects.get_child(["2:ROOM 207"])
        device1 = room207.get_child(["2:Device1"])
        for tag in device1.get_children():
            tag_name = tag.get_display_name().Text
            tag_nodeid = tag.nodeid
            try:
                tag_value = tag.get_value()
            except Exception as e:
                tag_value = f"Error reading value: {e}"
            print(f"Tag: {tag_name}, NodeId: {tag_nodeid}, Value: {tag_value}")
    except Exception as e:
        print(f"Error listing tags under ROOM 207/Device1: {e}")

    # List and write to all tags under ROOM 207/Device1
    print("\nWriting value to all tags under ROOM 207/Device1:")
    try:
        room207 = objects.get_child(["2:ROOM 207"])
        device1 = room207.get_child(["2:Device1"])
        for tag in device1.get_children():
            tag_name = tag.get_display_name().Text
            tag_nodeid = tag.nodeid
            try:
                tag_value = tag.get_value()
                # Determine new value based on type
                datatype = tag.get_data_type_as_variant_type()
                if datatype.name == 'Boolean':
                    new_value = not bool(tag_value)
                elif datatype.name in ['Int16', 'Int32', 'Int64', 'UInt16', 'UInt32', 'UInt64', 'Byte', 'SByte', 'Double', 'Float']:
                    new_value = (tag_value + 1) if isinstance(tag_value, (int, float)) else 1
                else:
                    new_value = tag_value
                tag.set_value(ua.DataValue(ua.Variant(new_value, datatype)))
                print(f"Tag: {tag_name}, NodeId: {tag_nodeid}, Old Value: {tag_value}, New Value: {new_value}")
            except Exception as e:
                print(f"Tag: {tag_name}, NodeId: {tag_nodeid}, Error writing value: {e}")
    except Exception as e:
        print(f"Error writing tags under ROOM 207/Device1: {e}")

except Exception as e:
    import traceback
    print("Error:", e)
    traceback.print_exc()
finally:
    try:
        client.disconnect()
        print("Disconnected")
    except Exception as e:
        print("Disconnect error:", e)
