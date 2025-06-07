from opcua import Client, ua
import time
import sys
import os

def browse_server():
    # Set up logging to file
    log_path = os.path.join(os.path.dirname(__file__), 'browse_server.log')
    sys.stdout = open(log_path, 'w')
    sys.stderr = sys.stdout
    
    client = Client("opc.tcp://127.0.0.1:49320")
    try:
        client.connect()
        print("Connected to KEPserver")
        
        # Get root node
        root = client.get_root_node()
        print("\nRoot node:", root)
        print("\nRoot node children:")
        for child in root.get_children():
            print(f"Node: {child}")
            
        # Get Objects node
        objects = root.get_child(["Objects"])
        print("\nObjects node children:")
        for child in objects.get_children():
            print(f"Node: {child}")
            try:
                for subchild in child.get_children():
                    print(f"  - {subchild}")
            except:
                pass
        
        # Try to find specific nodes
        for path in [
            ["Objects", "Server"],
            ["Objects", "Project"],
            ["Objects", "Config"],
            ["Objects", "IOConfig"]
        ]:
            try:
                node = root.get_child(path)
                print(f"\nFound {'.'.join(path)}:")
                for child in node.get_children():
                    print(f"  - {child}")
            except Exception as e:
                print(f"\nCould not find {'.'.join(path)}: {e}")
        
    finally:        client.disconnect()
        print("\nDisconnected")
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

if __name__ == "__main__":
    browse_server()
