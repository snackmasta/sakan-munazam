"""Main application entry point."""
import threading
import socket
from master.handlers.udp_handler import UDPHandler
from master.utils.ui_handler import UIHandler
from master.config.settings import UDP_PORT, BUFFER_SIZE, CMD_ON, CMD_OFF
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

def input_listener(udp_handler, session):
    """Handle user input in a separate thread using prompt_toolkit."""
    UIHandler.print_help()
    while udp_handler.running:
        with patch_stdout():
            try:
                cmd = session.prompt('> ').strip().split()
            except (EOFError, KeyboardInterrupt):
                udp_handler.stop()
                break
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
    import logging
    logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(message)s')
    print("[INFO] Starting Sakan Munazam Master Server...")
    udp_handler = UDPHandler(UDP_PORT, BUFFER_SIZE)
    print(f"[INFO] Listening on UDP port {UDP_PORT}...")
    session = PromptSession()
    input_thread = threading.Thread(
        target=input_listener,
        args=(udp_handler, session),
        daemon=True
    )
    input_thread.start()
    try:
        import time
        last_status = None
        while udp_handler.running:
            try:
                udp_handler.sock.settimeout(0.2)
                data, addr = udp_handler.sock.recvfrom(BUFFER_SIZE)
                message = data.decode().strip()
                # Log to file instead of printing
                logging.info(f"[RECV] From {addr}: {message}")
                udp_handler.handle_message(message, addr)  # Remove log_to_file argument
            except socket.timeout:
                pass
            except OSError:
                break
            status = udp_handler.get_device_status()
            if status != last_status:
                UIHandler.print_status_table(status["lights"], status["locks"])
                last_status = status
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        udp_handler.stop()

if __name__ == "__main__":
    main()
