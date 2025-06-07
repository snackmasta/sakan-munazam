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
        Create a new channel in KEPserver using Project node
        
        Args:
            channel_name (str): Name of the channel to create
        """
        try:
            # Get the Project node to create the channel
            root = self.client.get_root_node()
            project_node = root.get_child(["Objects", "Project"])
            
            # Create the channel
            create_channel = project_node.get_child(["Methods", "CreateChannel"])
            create_channel.call(channel_name)
            print(f"Created channel '{channel_name}'")
            
            # Give KEPserver a moment to create the channel
            time.sleep(1)
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
            # Get the Project node to create the device
            root = self.client.get_root_node()
            project_node = root.get_child(["Objects", "Project"])
            
            # Create the device
            create_device = project_node.get_child(["Methods", "CreateDevice"])
            create_device.call([channel_name, device_name])
            print(f"Created device '{device_name}' in channel '{channel_name}'")
            
            # Give KEPserver a moment to create the device
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"Failed to create device: {e}")
            return False

    def create_tag(self, channel_name: str, device_name: str, tag_name: str, 
                  data_type: str = "Float", address: str = "400001", 
                  description: str = "") -> bool:
        """
        Create a new tag in the specified device
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device to add tag to
            tag_name (str): Name of the tag to create
            data_type (str): Data type for the tag (Float, Boolean, String, etc.)
            address (str): Tag address (e.g., 400001 for Modbus)
            description (str): Tag description
        """
        try:
            # Get the Project node to create the tag
            root = self.client.get_root_node()
            project_node = root.get_child(["Objects", "Project"])
            
            # Create the tag
            create_tag = project_node.get_child(["Methods", "CreateTag"])
            create_tag.call([channel_name, device_name, tag_name])
            print(f"Created tag '{tag_name}' in device '{device_name}'")
            
            # Give KEPserver a moment to create the tag
            time.sleep(1)
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
