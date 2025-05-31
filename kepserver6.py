from opcua import Client

client = Client("opc.tcp://127.0.0.1:49320")

try:
    client.connect()
    print("Connected to OPC UA server")

    # Directly get Tag1 node (adjust the path if needed)
    tag1 = client.get_node("ns=2;s=Channel1.Device1.Tag1")

    import time
    print("Realtime updating Tag1 value (press Ctrl+C to stop):")
    while True:
        try:
            val1 = tag1.get_value()
            print(f"Tag1: {val1}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped realtime update.")
            break

except Exception as e:
    print("Error:", e)
finally:
    try:
        client.disconnect()
        print("Disconnected")
    except Exception as e:
        print("Disconnect error:", e)
