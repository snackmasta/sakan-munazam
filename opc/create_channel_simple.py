#!/usr/bin/env python3
"""
Simple script to create a new channel in KEPServer
"""

import requests
import json

class SimpleKEPChannel:
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
            print("\nTroubleshooting:")
            print("1. Make sure KEPServerEX is running")
            print("2. Verify Configuration API is enabled in KEPServer settings")
            print("3. Check if port 57412 is correct")
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
                return False
            else:
                print(f"✗ Failed to create channel. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating channel: {str(e)}")
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
                            print(f"  - {channel['common.ALLTYPES_NAME']}")
                        elif isinstance(channel, str):
                            print(f"  - {channel}")
                else:
                    print("No existing channels found.")
            else:
                print("Could not retrieve existing channels.")
        except Exception as e:
            print(f"Error listing channels: {str(e)}")

def main():
    print("KEPServer Channel Creator")
    print("=" * 25)
    
    # Initialize KEPServer connection
    kep = SimpleKEPChannel()
    
    # Check connection first
    if not kep.check_connection():
        print("\nCannot proceed without a valid connection to KEPServer.")
        return
    
    # List existing channels
    kep.list_existing_channels()
    
    # Get channel name from user
    print("\nCreate New Channel:")
    channel_name = input("Enter channel name (or press Enter for 'TestChannel'): ").strip()
    if not channel_name:
        channel_name = "TestChannel"
    
    # Get driver type from user
    print("\nAvailable drivers:")
    print("1. Simulator (default)")
    print("2. Modbus TCP/IP")
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
        print("\nNext steps:")
        print("1. You can now add devices to this channel")
        print("2. Configure device settings as needed")
        print("3. Add tags to devices for data points")
    else:
        print(f"\n❌ Failed to create channel '{channel_name}'")

if __name__ == "__main__":
    main()
