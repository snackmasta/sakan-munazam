"""Main application entry point."""
import threading
import socket
from master.handlers.udp_handler import UDPHandler
from master.utils.ui_handler import UIHandler
from master.config.settings import UDP_PORT, BUFFER_SIZE, CMD_ON, CMD_OFF

def input_listener(udp_handler):
    """Handle user input in a separate thread."""
    UIHandler.print_help()
    
    while udp_handler.running:
        cmd = input().strip().split()
        if not cmd:
            continue
            
        if cmd[0].upper() == "E":
            udp_handler.stop()
            break
        elif cmd[0].lower() == "status":
            status = udp_handler.get_device_status()
            UIHandler.print_status_table(status["lights"], status["locks"])
        elif len(cmd) == 3 and cmd[0].lower() == "light":
            device_id = cmd[1]
            command = cmd[2].upper()
            if command in [CMD_ON, CMD_OFF]:
                if udp_handler.control_light(device_id, command):
                    print(f"Command sent to {device_id}")
                else:
                    print(f"Device {device_id} not found or not a light")
            else:
                print(f"Invalid command. Use {CMD_ON} or {CMD_OFF}")
        else:
            UIHandler.print_help()

def main():
    """Main application entry point."""
    print("[INFO] Starting Sakan Munazam Master Server...")
    
    # Initialize UDP handler
    udp_handler = UDPHandler(UDP_PORT, BUFFER_SIZE)
    print(f"[INFO] Listening on UDP port {UDP_PORT}...")
    
    # Start input listener thread
    input_thread = threading.Thread(
        target=input_listener,
        args=(udp_handler,),
        daemon=True
    )
    input_thread.start()
    
    # Main UDP listening loop
    try:
        while udp_handler.running:
            try:
                udp_handler.sock.settimeout(1.0)
                data, addr = udp_handler.sock.recvfrom(BUFFER_SIZE)
                message = data.decode().strip()
                print(f"[RECV] From {addr}: {message}")
                udp_handler.handle_message(message, addr)
            except socket.timeout:
                continue
            except OSError:
                break
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        udp_handler.stop()

if __name__ == "__main__":
    main()
