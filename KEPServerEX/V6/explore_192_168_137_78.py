from opcua import Client, ua
import time

# OPC UA server endpoint
ENDPOINT = "opc.tcp://192.168.100.115:49320"

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
    # Discover endpoints
    discovery_client = Client(ENDPOINT)
    endpoints = discovery_client.connect_and_get_server_endpoints()
    print("Discovered endpoints:")
    for ep in endpoints:
        print(f"  Endpoint: {ep.EndpointUrl}, Security: {ep.SecurityPolicyUri}, Mode: {ep.SecurityMode}")
    discovery_client.disconnect()
except Exception as e:
    print(f"Endpoint discovery failed: {e}")

client = Client(ENDPOINT)

try:
    client.connect()
    print(f"Connected to OPC UA server at {ENDPOINT}")
    time.sleep(1)

    # Print namespaces
    namespaces = client.get_namespace_array()
    print("Namespaces:")
    for idx, ns in enumerate(namespaces):
        print(f"  [{idx}] {ns}")

    # Browse root folder
    print("\nBrowsing RootFolder:")
    root = client.get_root_node()
    browse_node(root, max_depth=2)

    # Browse Objects folder
    print("\nBrowsing Objects folder:")
    objects = client.get_objects_node()
    browse_node(objects, max_depth=2)

    # List available channels
    print("\nListing available channels:")
    try:
        for child in objects.get_children():
            display_name = child.get_display_name().Text
            node_id = child.nodeid
            print(f"Channel: {display_name}, NodeId: {node_id}")
    except Exception as e:
        print(f"Error listing channels: {e}")

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
