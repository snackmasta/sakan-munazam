from opcua import Client, ua

def browse_namespace():
    client = Client("opc.tcp://127.0.0.1:49320")
    try:
        client.connect()
        print("Connected to KEPserver")
        
        # Get root node
        root = client.get_root_node()
        
        # Get namespace array
        print("\nNamespace array:")
        ns_array = client.get_namespace_array()
        for idx, ns in enumerate(ns_array):
            print(f"ns={idx}: {ns}")
            
        # Browse Objects folder
        objects = root.get_child(["Objects"])
        print("\nObjects folder contents:")
        for child in objects.get_children():
            print(f"\nNode: {child}")
            try:
                # Get node class
                node_class = child.get_node_class()
                print(f"Class: {node_class}")
                
                # Get browse name
                browse_name = child.get_browse_name()
                print(f"BrowseName: {browse_name}")
                
                # Get display name
                display_name = child.get_display_name()
                print(f"DisplayName: {display_name}")
                
                # List methods if this is a folder
                try:
                    print("Child nodes:")
                    for subchild in child.get_children():
                        print(f"  - {subchild}")
                        # Try to get methods
                        if "Method" in str(subchild.get_node_class()):
                            print(f"    Method name: {subchild.get_browse_name()}")
                except:
                    pass
            except Exception as e:
                print(f"Error getting node details: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    browse_namespace()
