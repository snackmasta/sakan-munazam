from opcua import Client

def check_nodes():
    client = Client("opc.tcp://127.0.0.1:49320")
    try:
        client.connect()
        print("Connected to KEPserver")
        
        # Get root node
        root = client.get_root_node()
        objects = root.get_child(["Objects"])
        
        # Try to get the channel creation method
        config = objects.get_child(["Config"])
        print("\nMethods in Config:")
        try:
            methods = config.get_children()
            for method in methods:
                print(f"Method: {method}")
                try:
                    if hasattr(method, 'get_children'):
                        for child in method.get_children():
                            print(f"  Child: {child}")
                except:
                    pass
        except Exception as e:
            print(f"Error browsing Config: {e}")
            
        # Try browsing server info
        server = objects.get_child(["Server"])
        print("\nServer info:")
        try:
            for child in server.get_children():
                print(f"Node: {child}")
        except Exception as e:
            print(f"Error browsing Server: {e}")
            
    finally:
        client.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    check_nodes()
