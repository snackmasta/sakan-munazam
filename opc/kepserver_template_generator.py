#!/usr/bin/env python3
"""
KEPServer Configuration Template Generator
Creates standardized configuration files and provides setup guidance
"""

import json
import os
from datetime import datetime

class KEPConfigTemplateGenerator:
    def __init__(self):
        self.templates = {
            "modbus_plc": {
                "description": "Standard Modbus TCP PLC Configuration",
                "channel": {
                    "driver": "Modbus TCP/IP Ethernet",
                    "properties": {
                        "Network Adapter": "Default",
                        "Ethernet Encap": "Ethernet",
                        "Request Timeout": 1000,
                        "Fail After": 3
                    }
                },
                "devices": [
                    {
                        "name": "PLC_{id}",
                        "id": "{id}",
                        "ip_address": "192.168.1.{ip_last}",
                        "port": 502,
                        "tags": [
                            {"name": "Status", "address": "40001", "type": "Boolean", "description": "PLC Status"},
                            {"name": "Temperature", "address": "40002", "type": "Float", "description": "Process Temperature"},
                            {"name": "Pressure", "address": "40003", "type": "Float", "description": "Process Pressure"},
                            {"name": "FlowRate", "address": "40004", "type": "Float", "description": "Flow Rate"},
                            {"name": "SetPoint", "address": "40005", "type": "Float", "description": "Temperature Setpoint", "access": "Read/Write"}
                        ]
                    }
                ]
            },
            "simulator_test": {
                "description": "Simulator for Testing and Development",
                "channel": {
                    "driver": "Simulator",
                    "properties": {
                        "Update Rate": 1000
                    }
                },
                "devices": [
                    {
                        "name": "TestDevice_{id}",
                        "id": "{id}",
                        "tags": [
                            {"name": "Counter", "address": "R0", "type": "DWord", "description": "Incrementing Counter"},
                            {"name": "RandomFloat", "address": "R1", "type": "Float", "description": "Random Float Value"},
                            {"name": "Toggle", "address": "R2", "type": "Boolean", "description": "Boolean Toggle"},
                            {"name": "Sine_Wave", "address": "R3", "type": "Float", "description": "Sine Wave Generator"},
                            {"name": "UserInput", "address": "R4", "type": "Word", "description": "User Input Value", "access": "Read/Write"}
                        ]
                    }
                ]
            },
            "opc_ua_client": {
                "description": "OPC UA Client Configuration",
                "channel": {
                    "driver": "OPC UA Client",
                    "properties": {
                        "Endpoint URL": "opc.tcp://{server_ip}:4840",
                        "Security Policy": "None",
                        "Message Mode": "None",
                        "Update Rate": 1000
                    }
                },
                "devices": [
                    {
                        "name": "OPC_Server_{id}",
                        "id": "{id}",
                        "tags": [
                            {"name": "ServerStatus", "address": "ns=0;i=2256", "type": "DWord", "description": "Server State"},
                            {"name": "CurrentTime", "address": "ns=0;i=2258", "type": "Date", "description": "Server Current Time"},
                            {"name": "ProcessVar1", "address": "ns=2;s=ProcessValue1", "type": "Float", "description": "Process Variable 1"},
                            {"name": "ProcessVar2", "address": "ns=2;s=ProcessValue2", "type": "Float", "description": "Process Variable 2"}
                        ]
                    }
                ]
            }
        }
    
    def generate_setup_guide(self, template_name, channel_name, **kwargs):
        """Generate a step-by-step setup guide for a specific template"""
        if template_name not in self.templates:
            print(f"Template '{template_name}' not found!")
            return None
            
        template = self.templates[template_name]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"setup_guide_{template_name}_{timestamp}.md"
        
        guide_content = self._generate_guide_content(template, channel_name, **kwargs)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"Setup guide created: {filename}")
        return filename
    
    def _generate_guide_content(self, template, channel_name, **kwargs):
        """Generate the markdown content for setup guide"""
        content = f"""# KEPServer Setup Guide - {template['description']}

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview
This guide will help you set up a KEPServer configuration for: **{template['description']}**

---

## Step 1: Create Channel (Automated)

Run the channel creation script:
```bash
python create_channel_final.py
```

**Channel Configuration:**
- **Name**: `{channel_name}`
- **Driver**: `{template['channel']['driver']}`

---

## Step 2: Configure Channel Properties (Manual)

1. Open KEPServer Administrator
2. Right-click on channel `{channel_name}` → Properties
3. Configure the following properties:

"""
        
        # Add channel properties
        for prop, value in template['channel'].get('properties', {}).items():
            content += f"   - **{prop}**: `{value}`\n"
        
        content += "\n---\n\n## Step 3: Create Devices (Manual)\n\n"
        
        # Add device instructions
        for i, device in enumerate(template['devices'], 1):
            device_name = device['name'].format(id=i, **kwargs)
            device_id = device['id'].format(id=i, **kwargs)
            
            content += f"### Device {i}: {device_name}\n\n"
            content += f"1. Right-click channel `{channel_name}` → New Device\n"
            content += f"2. Configure device properties:\n"
            content += f"   - **Name**: `{device_name}`\n"
            content += f"   - **Device ID**: `{device_id}`\n"
            
            # Add device-specific properties
            if 'ip_address' in device:
                ip = device['ip_address'].format(**kwargs)
                content += f"   - **IP Address**: `{ip}`\n"
            if 'port' in device:
                content += f"   - **Port**: `{device['port']}`\n"
            
            content += f"\n---\n\n## Step 4: Create Tags for {device_name} (Manual)\n\n"
            content += f"For each tag, right-click device `{device_name}` → New Tag:\n\n"
            
            for tag in device['tags']:
                content += f"### Tag: {tag['name']}\n"
                content += f"- **Address**: `{tag['address']}`\n"
                content += f"- **Data Type**: `{tag['type']}`\n"
                content += f"- **Description**: `{tag['description']}`\n"
                if 'access' in tag:
                    content += f"- **Access Rights**: `{tag['access']}`\n"
                content += "\n"
        
        content += """
---

## Step 5: Test Configuration

1. **Check Connection**: Verify all devices show "Connected" status
2. **Test Tag Values**: Use KEPServer Administrator to view live tag values
3. **Write Test**: If applicable, test writing to Read/Write tags

---

## Step 6: Client Connection

Use this connection information for OPC clients:

**OPC Server Details:**
- **Server Name**: `KEPware.KEPServerEx.V6`
- **Host**: `localhost` (or KEPServer machine IP)
- **Port**: `7392` (OPC DA) or `49320` (OPC UA)

**Sample Tag Addresses:**
"""
        
        # Add sample tag addresses for OPC clients
        for device in template['devices']:
            device_name = device['name'].format(id=1, **kwargs)
            content += f"\n**{device_name}:**\n"
            for tag in device['tags'][:3]:  # Show first 3 tags as examples
                content += f"- `{channel_name}.{device_name}.{tag['name']}`\n"
        
        content += """
---

## Troubleshooting

### Common Issues:
1. **Device Not Connected**: Check IP addresses and network connectivity
2. **Tag Values Not Updating**: Verify addressing and data types
3. **OPC Client Connection Failed**: Check Windows firewall and DCOM settings

### Testing Tools:
- KEPServer Administrator (built-in)
- OPC Expert (Matrikon)
- UaExpert (Unified Automation)

---

## Configuration Backup

**Important:** Save your configuration!
1. File → Export → Save as OPF file
2. Store in version control
3. Document any custom changes

"""
        
        return content
    
    def list_templates(self):
        """List all available templates"""
        print("Available KEPServer Configuration Templates:")
        print("=" * 50)
        for name, template in self.templates.items():
            print(f"📋 {name}")
            print(f"   Description: {template['description']}")
            print(f"   Driver: {template['channel']['driver']}")
            print(f"   Devices: {len(template['devices'])}")
            print()
    
    def generate_json_template(self, template_name, output_file=None):
        """Generate a JSON configuration template file"""
        if template_name not in self.templates:
            print(f"Template '{template_name}' not found!")
            return None
          if not output_file:
            output_file = f"template_{template_name}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates[template_name], f, indent=2)
        
        print(f"JSON template created: {output_file}")
        return output_file

def main():
    generator = KEPConfigTemplateGenerator()
    
    print("KEPServer Configuration Template Generator")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List available templates")
        print("2. Generate setup guide")
        print("3. Generate JSON template")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            generator.list_templates()
            
        elif choice == "2":
            generator.list_templates()
            template_name = input("\nEnter template name: ").strip()
            channel_name = input("Enter channel name: ").strip()
            
            # Get additional parameters based on template
            kwargs = {}
            if template_name == "modbus_plc":
                ip_base = input("Enter IP base (e.g., 192.168.1): ").strip() or "192.168.1"
                kwargs['ip_last'] = "100"  # Default
            elif template_name == "opc_ua_client":
                server_ip = input("Enter OPC UA server IP: ").strip() or "localhost"
                kwargs['server_ip'] = server_ip
            
            guide_file = generator.generate_setup_guide(template_name, channel_name, **kwargs)
            if guide_file:
                print(f"\n✅ Setup guide created: {guide_file}")
                
        elif choice == "3":
            generator.list_templates()
            template_name = input("\nEnter template name: ").strip()
            output_file = input("Enter output filename (or press Enter for default): ").strip()
            
            json_file = generator.generate_json_template(template_name, output_file or None)
            if json_file:
                print(f"\n✅ JSON template created: {json_file}")
                
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
