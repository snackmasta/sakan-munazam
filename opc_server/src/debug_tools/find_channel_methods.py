from opcua import Client, ua

def explore_kepserver():
    client = Client("opc.tcp://127.0.0.1:49320")
    try:
        client.connect()
        print("Connected to KEPserver")
        
        # Get root node and objects folder
        root = client.get_root_node()
        objects = root.get_child(["Objects"])
        
        # Try to find channel configuration method
        print("\nSearching for channel configuration methods...")
        
        # Search in different possible locations
        paths_to_try = [
            ["Project"],
            ["Project", "Methods"],
            ["Config"],
            ["Channel"],
            ["_System"],
            ["Server"]
        ]
        
        for path in paths_to_try:
            try:
                node = objects.get_child(path)
                print(f"\nFound node at path Objects/{'/'.join(path)}:")
                for child in node.get_children():
                    print(f"  - {child}")
                    # If this is a methods folder, list its contents
                    if "Methods" in str(child):
                        try:
                            for method in child.get_children():
                                print(f"    * {method}")
                        except:
                            pass
            except:
                print(f"Could not find path Objects/{'/'.join(path)}")
                
        # Try to find any nodes with 'Channel' in the name
        print("\nSearching for nodes containing 'Channel'...")
        for child in objects.get_children():
            if "Channel" in str(child):
                print(f"\nFound channel-related node: {child}")
                try:
                    for subchild in child.get_children():
                        print(f"  - {subchild}")
                except:
                    pass
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    explore_kepserver()
