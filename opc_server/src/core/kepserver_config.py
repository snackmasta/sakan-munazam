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
            
    def verify_channel(self, channel_name: str) -> bool:
        """
        Verify if a channel exists in KEPserver
        
        Args:
            channel_name (str): Name of the channel to verify
            
        Returns:
            bool: True if channel exists, False otherwise
        """
        try:
            # Get the root node
            root = self.client.get_root_node()
            
            # Try to get the channel under _System/ChannelNames
            channel_path = ["Objects", "_System", "ChannelNames", channel_name]
            channel_node = root.get_child(channel_path)
            if channel_node:
                print(f"Channel '{channel_name}' exists")
                return True
            
            # If not found in ChannelNames, try Project/Channels
            try:
                channel_path = ["Objects", "Project", "Channels", channel_name]
                channel_node = root.get_child(channel_path)
                if channel_node:
                    print(f"Channel '{channel_name}' exists")
                    return True
            except:
                pass
                
            return False
        except Exception as e:
            print(f"Error verifying channel: {e}")
            return False
            
    def create_channel(self, channel_name: str) -> bool:
        """
        Verify existing channel in KEPserver. This method no longer creates channels
        as we're working with pre-configured channels.
        
        Args:
            channel_name (str): Name of the channel to verify
            
        Returns:
            bool: True if channel exists, False otherwise
        """
        return self.verify_channel(channel_name)

    def get_channel_devices(self, channel_name: str) -> list:
        """
        Get a list of devices in the specified channel
        
        Args:
            channel_name (str): Name of the channel
            
        Returns:
            list: List of device names in the channel
        """
        devices = []
        try:
            # Get the root node
            root = self.client.get_root_node()
            
            # Try getting devices from Project/Channels path
            try:
                channel_path = ["Objects", "Project", "Channels", channel_name]
                channel_node = root.get_child(channel_path)
                devices_node = channel_node.get_child(["Devices"])
                for device in devices_node.get_children():
                    devices.append(device.get_browse_name().Name)
            except:
                pass
                
            if devices:
                print(f"Found devices in channel '{channel_name}': {devices}")
            else:
                print(f"No devices found in channel '{channel_name}'")
                
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

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
        
    def verify_device(self, channel_name: str, device_name: str) -> bool:
        """
        Verify if a device exists in the specified channel
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device to verify
            
        Returns:
            bool: True if device exists, False otherwise
        """
        devices = self.get_channel_devices(channel_name)
        exists = device_name in devices
        if exists:
            print(f"Device '{device_name}' exists in channel '{channel_name}'")
        else:
            print(f"Device '{device_name}' not found in channel '{channel_name}'")
        return exists

    def get_device_tags(self, channel_name: str, device_name: str) -> list:
        """
        Get a list of tags in the specified device
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device
            
        Returns:
            list: List of tag names in the device
        """
        tags = []
        try:
            # Get the root node
            root = self.client.get_root_node()
            
            # Try getting tags from Project/Channels path
            try:
                device_path = ["Objects", "Project", "Channels", channel_name, "Devices", device_name]
                device_node = root.get_child(device_path)
                tags_node = device_node.get_child(["Tags"])
                for tag in tags_node.get_children():
                    tags.append(tag.get_browse_name().Name)
            except:
                pass
                
            if tags:
                print(f"Found tags in device '{device_name}': {tags}")
            else:
                print(f"No tags found in device '{device_name}'")
                
            return tags
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []

    def verify_tag(self, channel_name: str, device_name: str, tag_name: str) -> bool:
        """
        Verify if a tag exists in the specified device
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device
            tag_name (str): Name of the tag to verify
            
        Returns:
            bool: True if tag exists, False otherwise
        """
        tags = self.get_device_tags(channel_name, device_name)
        exists = tag_name in tags
        if exists:
            print(f"Tag '{tag_name}' exists in device '{device_name}'")
        else:
            print(f"Tag '{tag_name}' not found in device '{device_name}'")
        return exists

    def read_tag(self, channel_name: str, device_name: str, tag_name: str) -> Optional[Any]:
        """
        Read a value from a tag
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device
            tag_name (str): Name of the tag to read
            
        Returns:
            Any: The tag value if successful, None otherwise
        """
        try:
            tag_path = f"{channel_name}.{device_name}.{tag_name}"
            tag_node = self.client.get_node(f"ns=2;s={tag_path}")
            value = tag_node.get_value()
            print(f"Successfully read value {value} from tag {tag_path}")
            return value
        except Exception as e:
            print(f"Failed to read tag value: {e}")
            return None

    def write_tag(self, channel_name: str, device_name: str, tag_name: str, value: Any) -> bool:
        """
        Write a value to a tag
        
        Args:
            channel_name (str): Name of the channel
            device_name (str): Name of the device
            tag_name (str): Name of the tag to write to
            value: Value to write to the tag
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            tag_path = f"{channel_name}.{device_name}.{tag_name}"
            tag_node = self.client.get_node(f"ns=2;s={tag_path}")
            tag_node.set_value(value)
            print(f"Successfully wrote value {value} to tag {tag_path}")
            return True
        except Exception as e:
            print(f"Failed to write tag value: {e}")
            return False
