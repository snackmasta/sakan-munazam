#!/usr/bin/env python3
"""
Final solution: Update the create_channel.py to work with the limitations
"""

import requests
import json

class KEPServerManager:
    def __init__(self, host="localhost", config_port=57412, username="Administrator", password=""):
        self.base_url = f"http://{host}:{config_port}/config"
        self.auth = (username, password)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def check_connection(self):
        """Test connection to KEPServer Configuration API"""
        try:
            url = f"{self.base_url}/v1/project"
            print(f"Testing connection to: {url}")
            response = requests.get(url, headers=self.headers, auth=self.auth, timeout=5)
            if response.status_code == 200:
                print("✓ Successfully connected to KEPServer Configuration API!")
                return True
            else:
                print(f"✗ Connection failed with status code: {response.status_code}")
                if response.status_code == 401:
                    print("  Authentication failed - check username/password")
                return False
        except requests.exceptions.ConnectionError:
            print("✗ Connection failed: KEPServer might not be running or Configuration API not enabled")
            return False
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False
    
    def create_channel(self, channel_name, driver_id="Simulator"):
        """Create a new channel in KEPServer"""
        try:
            url = f"{self.base_url}/v1/project/channels"
            data = {
                "common.ALLTYPES_NAME": channel_name,
                "servermain.MULTIPLE_TYPES_DEVICE_DRIVER": driver_id
            }
            
            print(f"Creating channel '{channel_name}' with driver '{driver_id}'...")
            response = requests.post(url, headers=self.headers, json=data, auth=self.auth)
            
            if response.status_code == 201:
                print(f"✓ Channel '{channel_name}' created successfully!")
                return True
            elif response.status_code == 409:
                print(f"⚠ Channel '{channel_name}' already exists")
                return True
            else:
                print(f"✗ Failed to create channel. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating channel: {str(e)}")
            return False
    
    def check_device_creation_capability(self):
        """Check if device creation is supported"""
        print("\n--- Checking Device Creation Capability ---")
        
        # Test with a known channel
        test_channel = "Data Type Examples"
        url = f"{self.base_url}/v1/project/channels/{test_channel}/devices"
        
        test_data = {
            "common.ALLTYPES_NAME": "APITest",
            "servermain.DEVICE_ID_STRING": "999"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=test_data, auth=self.auth)
            
            if response.status_code == 201:
                print("✓ Device creation is supported via REST API")
                # Clean up test device
                delete_url = f"{url}/APITest"
                requests.delete(delete_url, headers=self.headers, auth=self.auth)
                return True
            elif response.status_code == 400:
                print("✗ Device creation not supported via REST API")
                print("   This KEPServer version/license may not support device creation via REST")
                print("   Devices need to be created manually through KEPServer Administrator")
                return False
            else:
                print(f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error testing device creation: {e}")
            return False
    
    def list_existing_channels(self):
        """List all existing channels"""
        try:
            url = f"{self.base_url}/v1/project/channels"
            response = requests.get(url, headers=self.headers, auth=self.auth, timeout=5)
            
            if response.status_code == 200:
                channels = response.json()
                if channels:
                    print("\nExisting channels:")
                    for channel in channels:
                        if isinstance(channel, dict) and "common.ALLTYPES_NAME" in channel:
                            channel_name = channel['common.ALLTYPES_NAME']
                            print(f"  - {channel_name}")
                            
                            # List devices in this channel
                            self.list_devices_in_channel(channel_name)
                        elif isinstance(channel, str):
                            print(f"  - {channel}")
                    return [ch.get('common.ALLTYPES_NAME', ch) if isinstance(ch, dict) else ch for ch in channels]
                else:
                    print("No existing channels found.")
                    return []
            else:
                print("Could not retrieve existing channels.")
                return []
        except Exception as e:
            print(f"Error listing channels: {str(e)}")
            return []
    
    def list_devices_in_channel(self, channel_name):
        """List devices in a specific channel"""
        try:
            url = f"{self.base_url}/v1/project/channels/{channel_name}/devices"
            response = requests.get(url, headers=self.headers, auth=self.auth, timeout=3)
            
            if response.status_code == 200:
                devices = response.json()
                if devices:
                    print(f"    Devices: {', '.join([d.get('common.ALLTYPES_NAME', str(d)) if isinstance(d, dict) else str(d) for d in devices])}")
                else:
                    print(f"    Devices: None")
            
        except Exception as e:
            pass  # Silently fail for listing

def main():
    print("KEPServer Channel Creator & Device Information")
    print("=" * 50)
    
    # Initialize KEPServer connection
    kep = KEPServerManager()
    
    # Check connection first
    if not kep.check_connection():
        print("\nCannot proceed without a valid connection to KEPServer.")
        return
    
    # Check device creation capability
    device_creation_supported = kep.check_device_creation_capability()
    
    # List existing channels and devices
    kep.list_existing_channels()
    
    # Get channel name from user
    print("\nCreate New Channel:")
    channel_name = input("Enter channel name (or press Enter for 'TestChannel'): ").strip()
    if not channel_name:
        channel_name = "TestChannel"
    
    # Get driver type from user
    print("\nAvailable drivers:")
    print("1. Simulator (default)")
    print("2. Modbus TCP/IP Ethernet")
    print("3. OPC UA Client")
    print("4. Other (specify)")
    
    driver_choice = input("Select driver (1-4, or press Enter for Simulator): ").strip()
    
    driver_map = {
        "1": "Simulator",
        "2": "Modbus TCP/IP Ethernet",
        "3": "OPC UA Client",
        "": "Simulator"
    }
    
    if driver_choice in driver_map:
        driver_id = driver_map[driver_choice]
    elif driver_choice == "4":
        driver_id = input("Enter driver name: ").strip()
        if not driver_id:
            driver_id = "Simulator"
    else:
        driver_id = "Simulator"
    
    # Create the channel
    print(f"\nAttempting to create channel...")
    success = kep.create_channel(channel_name, driver_id)
    
    if success:
        print(f"\n🎉 Channel '{channel_name}' has been created successfully!")
        
        if not device_creation_supported:
            print("\n📋 Next Steps (Manual Configuration Required):")
            print("Since device creation via REST API is not supported, you'll need to:")
            print("1. Open KEPServer Administrator")
            print(f"2. Navigate to the '{channel_name}' channel")
            print("3. Right-click and select 'New Device'")
            print("4. Configure device properties manually")
            print("5. Add tags to the device as needed")
            print("\nAlternatively:")
            print("- Use KEPServer Configuration Client")
            print("- Import configuration from OPF files")
            print("- Use KEPServer's built-in wizards")
        else:
            print("\n✅ Device creation via REST API is supported!")
            print("You can now use the enhanced scripts to create devices and tags.")
        
        print(f"\n📊 Channel Summary:")
        print(f"   Name: {channel_name}")
        print(f"   Driver: {driver_id}")
        print(f"   REST API: Channel ✅, Device ❌, Tags ❌")
        
    else:
        print(f"\n❌ Failed to create channel '{channel_name}'")

if __name__ == "__main__":
    main()
