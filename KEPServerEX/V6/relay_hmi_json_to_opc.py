import time
import json
from opcua import Client, ua
import os

# OPC UA server endpoint (update as needed)
OPC_SERVER_URL = "opc.tcp://192.168.100.115:49320"
# Path to the real-time HMI state JSON
JSON_PATH = os.path.join(os.path.dirname(__file__), '../../master/hmi_state.json')

# Map JSON keys to OPC UA tag node IDs (update as needed)
TAG_MAP = {
    # Example mappings (update to match your OPC UA server's tag structure)
    'led_lock_207': "ns=2;s=ROOM 207.Device1.led_lock_207",
    'led_lock_208': "ns=2;s=ROOM 207.Device1.led_lock_208",
    'led_light_207': "ns=2;s=ROOM 207.Device1.led_light_207",
    'led_light_208': "ns=2;s=ROOM 207.Device1.led_light_208",
    'alarm_lock_207': "ns=2;s=ROOM 207.Device1.alarm_lock_207",
    'alarm_lock_208': "ns=2;s=ROOM 207.Device1.alarm_lock_208",
    'alarm_light_207': "ns=2;s=ROOM 207.Device1.alarm_light_207",
    'alarm_light_208': "ns=2;s=ROOM 207.Device1.alarm_light_208",
    'maintenance_207': "ns=2;s=ROOM 207.Device1.maintenance_207",
    'maintenance_208': "ns=2;s=ROOM 207.Device1.maintenance_208",
    # Add more mappings as needed
}

def relay_json_to_opc():
    client = Client(OPC_SERVER_URL)
    last_state = None
    try:
        client.connect()
        print("Connected to OPC UA server.")
        while True:
            try:
                with open(JSON_PATH, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            except Exception as e:
                print(f"Failed to read JSON: {e}")
                time.sleep(0.01)
                continue
            for key, value in state.items():
                if key in TAG_MAP:
                    try:
                        node = client.get_node(TAG_MAP[key])
                        varianttype = node.get_data_type_as_variant_type()
                        # Write value as-is for Boolean (should be 0 or 1), or int for others
                        if varianttype == ua.VariantType.Boolean:
                            v = value
                        elif varianttype == ua.VariantType.Byte:
                            v = int(value) & 0xFF
                        elif varianttype == ua.VariantType.Int16:
                            v = int(value)
                        elif varianttype == ua.VariantType.UInt16:
                            v = int(value)
                        elif varianttype == ua.VariantType.Int32:
                            v = int(value)
                        elif varianttype == ua.VariantType.UInt32:
                            v = int(value)
                        else:
                            v = int(value)
                        node.set_value(ua.DataValue(ua.Variant(v, varianttype)))
                    except Exception as e:
                        print(f"Failed to write {key} to OPC: {e}")
            # No sleep for true real-time relay
    except Exception as e:
        print(f"OPC UA connection error: {e}")
    finally:
        try:
            client.disconnect()
        except:
            pass
        print("Disconnected from OPC UA server.")

if __name__ == "__main__":
    relay_json_to_opc()
