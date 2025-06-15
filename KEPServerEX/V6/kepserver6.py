from opcua import Client, ua
import time

# Try to discover endpoints first
try:
    discovery_client = Client("opc.tcp://DESKTOP-97F20FJ:49320")
    endpoints = discovery_client.connect_and_get_server_endpoints()
    print("Discovered endpoints:")
    for ep in endpoints:
        print(f"  Endpoint: {ep.EndpointUrl}, Security: {ep.SecurityPolicyUri}, Mode: {ep.SecurityMode}")
    discovery_client.disconnect()
except Exception as e:
    print(f"Endpoint discovery failed: {e}")

# Now try to connect as before
client = Client("opc.tcp://DESKTOP-97F20FJ:49320")

try:
    client.connect()
    # Print tags under ROOM 207/Device1, including data type
    try:
        objects = client.get_objects_node()
        room207 = objects.get_child(["2:ROOM 207"])
        device1 = room207.get_child(["2:Device1"])
        for tag in device1.get_children():
            tag_name = tag.get_display_name().Text
            tag_nodeid = tag.nodeid
            try:
                tag_value = tag.get_value()
                tag_datatype = tag.get_data_type_as_variant_type().name
            except Exception as e:
                tag_value = f"Error reading value: {e}"
                tag_datatype = "Unknown"
            print(f"Tag: {tag_name}, NodeId: {tag_nodeid}, Value: {tag_value}, DataType: {tag_datatype}")
    except Exception as e:
        pass  # Suppress all other output
finally:
    try:
        client.disconnect()
    except Exception:
        pass
