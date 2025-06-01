from opcua import Client, ua

client = Client("opc.tcp://127.0.0.1:49320")

try:
    client.connect()
    print("Connected to OPC UA server")

    # Get Tag1 and Tag2 nodes
    tag1 = client.get_node("ns=2;s=Channel1.Device1.Tag1")
    tag2 = client.get_node("ns=2;s=Channel1.Device1.Tag2")

    # Read value from Tag1
    val1 = tag1.get_value()
    print(f"Tag1 value: {val1}")

    # Get Tag2 data type
    tag2_datatype = tag2.get_data_type_as_variant_type()
    print(f"Tag2 expects data type: {tag2_datatype}")

    # Write value to Tag2 with correct data type
    tag2.set_value(ua.DataValue(ua.Variant(val1, tag2_datatype)))
    print(f"Wrote value {val1} to Tag2")

except Exception as e:
    print("Error:", e)
finally:
    try:
        client.disconnect()
        print("Disconnected")
    except Exception as e:
        print("Disconnect error:", e)
