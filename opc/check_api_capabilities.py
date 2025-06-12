#!/usr/bin/env python3
"""
Check KEPServer API permissions and capabilities
"""

import requests
import json

def check_api_capabilities():
    base_url = "http://localhost:57412/config"
    auth = ("Administrator", "")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("KEPServer API Capability Check")
    print("=" * 30)
    
    # Check project info
    print("1. Project Information:")
    try:
        response = requests.get(f"{base_url}/v1/project", headers=headers, auth=auth)
        if response.status_code == 200:
            project_info = response.json()
            print(f"✓ Project accessible")
            print(f"Project data: {json.dumps(project_info, indent=2)}")
        else:
            print(f"✗ Project not accessible: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check what HTTP methods are allowed on devices endpoint
    print("\n2. Testing HTTP Methods on Devices Endpoint:")
    channel_name = "Data Type Examples"
    devices_url = f"{base_url}/v1/project/channels/{channel_name}/devices"
    
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
    for method in methods:
        try:
            if method == 'GET':
                response = requests.get(devices_url, headers=headers, auth=auth)
            elif method == 'POST':
                response = requests.post(devices_url, headers=headers, json={}, auth=auth)
            elif method == 'OPTIONS':
                response = requests.options(devices_url, headers=headers, auth=auth)
            else:
                continue  # Skip other methods for safety
                
            print(f"  {method}: {response.status_code}")
            if method == 'OPTIONS' and response.status_code == 200:
                print(f"    Allowed methods: {response.headers.get('Allow', 'Not specified')}")
                
        except Exception as e:
            print(f"  {method}: Error - {e}")
    
    # Check if we can read existing devices (this should work)
    print(f"\n3. Reading Existing Devices:")
    try:
        response = requests.get(devices_url, headers=headers, auth=auth)
        if response.status_code == 200:
            devices = response.json()
            print(f"✓ Can read devices: {len(devices) if devices else 0} devices found")
        else:
            print(f"✗ Cannot read devices: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check API version or server info
    print(f"\n4. API Version/Server Info:")
    try:
        # Try to get server info
        response = requests.get(f"{base_url}/v1", headers=headers, auth=auth)
        print(f"API root status: {response.status_code}")
        if response.status_code == 200:
            print(f"API root response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check if there's a different endpoint for device creation
    print(f"\n5. Testing Alternative Endpoints:")
    alt_endpoints = [
        f"{base_url}/v1/project/channels/{channel_name}/device",  # singular
        f"{base_url}/project/channels/{channel_name}/devices",    # no v1
        f"{base_url}/config/v1/project/channels/{channel_name}/devices",  # different path
    ]
    
    for endpoint in alt_endpoints:
        try:
            response = requests.post(endpoint, headers=headers, json={"common.ALLTYPES_NAME": "test"}, auth=auth)
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")

if __name__ == "__main__":
    check_api_capabilities()
