from opcua import Client, ua, Node
from typing import Optional, Dict, Any
import time

class KepserverConfigurator:
    def __init__(self, endpoint: str = "opc.tcp://127.0.0.1:49320"):
        self.endpoint = endpoint
        self.client = Client(endpoint)
        
    def connect(self) -> bool:
        """Connect to the KEPserver OPC UA server"""
        try:
            self.client.connect()
            print("Connected to KEPserver OPC UA server")
            # Give it a moment to establish connection
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Failed to connect to KEPserver: {e}")
            return False
            
    def disconnect(self) -> None:
        """Disconnect from the KEPserver OPC UA server"""
        try:
            self.client.disconnect()
            print("Disconnected from KEPserver")
        except Exception as e:
            print(f"Error disconnecting: {e}")

    def create_channel(self, channel_name: str) -> bool:
        """
        Create a new channel in KEPserver
        
        Args:
            channel_name (str): Name of the channel to create
        """
        try:
            # Get the root node
            root = self.client.get_root_node()
            
            # Try to get Server node to browse methods
            server = root.get_child(["Objects", "Server"])
            print("Available nodes under Server:")
            for child in server.get_children():
                print(f"Node: {child}")
            
            # Try to get IOConfig node
            config = root.get_child(["Objects", "IOConfig"])
            print("Available nodes under IOConfig:")
            for child in config.get_children():
                print(f"Node: {child}")
            
            # Try to browse root for all possible paths
            print("All nodes under Objects:")
            objects = root.get_child(["Objects"])
            for child in objects.get_children():
                print(f"Node: {child}")
            
            # Try a different path
            project = root.get_child(["Objects", "Project"])
            print("Available methods under Project:")
            methods = project.get_child(["Methods"])
            for child in methods.get_children():
                print(f"Method: {child}")
            
            # Attempt to create channel
            create_channel = methods.get_child("CreateChannel")
            create_channel.call(channel_name)
            print(f"Created channel '{channel_name}' successfully")
            
            return True
        except Exception as e:
            print(f"Failed to create channel: {e}")
            return False

    def create_device(self, channel_name: str, device_name: str, device_id: int = 1) -> bool:
        """
        Create a new device in the specified channel
        
        Args:
            channel_name (str): Name of the channel to create device in
            device_name (str): Name of the device to create
            device_id (int): Device ID number
        """
        try:
            # Get the root node
            root = self.client.get_root_node()
            
            # Try to get the Project node
            project = root.get_child(["Objects", "Project"])
            methods = project.get_child(["Methods"])
            
            # Create the device
            create_device = methods.get_child("CreateDevice")
            create_device.call([channel_name, device_name])
            print(f"Created device '{device_name}' in channel '{channel_name}'")
            
            return True
        except Exception as e:
            print(f"Failed to create device: {e}")
            return False

    def create_tag(self, channel_name: str, device_name: str, tag_name: str, 
                  data_type: str = "Float", address: str = "R0", 
                  description: str = "") -> bool:
        """
        Create a new tag in the specified device
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device to add tag to
            tag_name (str): Name of the tag to create
            data_type (str): Data type for the tag (Float, Boolean, String, etc.)
            address (str): Tag address (e.g., R0 for simulator)
            description (str): Tag description
        """
        try:
            # Get the root node
            root = self.client.get_root_node()
            
            # Get the Project node
            project = root.get_child(["Objects", "Project"])
            methods = project.get_child(["Methods"])
            
            # Create the tag
            create_tag = methods.get_child("CreateTag")
            create_tag.call([channel_name, device_name, tag_name])
            print(f"Created tag '{tag_name}' in device '{device_name}'")
            
            return True
        except Exception as e:
            print(f"Failed to create tag: {e}")
            return False

    def write_tag_value(self, tag_path: str, value: Any) -> bool:
        """
        Write a value to a tag
        
        Args:
            tag_path (str): Full path to the tag (e.g., 'Channel1.Device1.Tag1')
            value: Value to write to the tag
        """
        try:
            # Get the tag node
            tag_node = self.client.get_node(f"ns=2;s={tag_path}")
            tag_node.set_value(value)
            print(f"Successfully wrote value {value} to tag {tag_path}")
            return True
        except Exception as e:
            print(f"Failed to write value: {e}")
            return False

    def read_tag_value(self, tag_path: str) -> Optional[Any]:
        """
        Read a value from a tag
        
        Args:
            tag_path (str): Full path to the tag (e.g., 'Channel1.Device1.Tag1')
        """
        try:
            # Get the tag node
            tag_node = self.client.get_node(f"ns=2;s={tag_path}")
            value = tag_node.get_value()
            print(f"Successfully read value from {tag_path}")
            return value
        except Exception as e:
            print(f"Failed to read value: {e}")
            return None
