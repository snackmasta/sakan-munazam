from opcua import Client, ua
import time
import os

log_file = None

def write_log(msg):
    global log_file
    print(msg)
    if log_file:
        log_file.write(msg + "\n")
        log_file.flush()

def browse_all_nodes(node, level=0):
    """Recursively browse all nodes"""    indent = "  " * level
    write_log(f"{indent}Node: {node}")
    try:
        attrs = node.get_attributes([ua.AttributeIds.DisplayName, ua.AttributeIds.BrowseName])
        for attr in attrs:
            if attr.StatusCode.is_good():
                if isinstance(attr.Value.Value, ua.LocalizedText):
                    write_log(f"{indent}  DisplayName: {attr.Value.Value.Text}")
                else:
                    write_log(f"{indent}  BrowseName: {attr.Value.Value}")
    except:
        pass
        
    try:
        for child in node.get_children():
            browse_all_nodes(child, level + 1)
    except Exception as e:
        print(f"{indent}  Error browsing children: {e}")

def explore_server():
    client = Client("opc.tcp://127.0.0.1:49320")
    try:
        client.connect()
        print("Connected to KEPserver")
        
        # Get root node
        root = client.get_root_node()
        print("\nExploring from root node:")
        browse_all_nodes(root)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    explore_server()
