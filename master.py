import socket
import threading
from sql import is_access_allowed
import json
from datetime import datetime

UDP_PORT = 4210
BUFFER_SIZE = 1024

class Device:
    def __init__(self, device_id, device_type, addr):
        self.device_id = device_id
        self.device_type = device_type  # 'light' or 'lock'
        self.addr = addr
        self.state = "UNKNOWN"
        self.last_update = datetime.now()
        # Additional attributes for lights
        self.current_lux = 0.0
        self.pwm_value = 0

class UDPSocketServer:
    def __init__(self, port, buffer_size):
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.devices = {}  # Track devices by their IDs
        self.running = True
        print(f"[INFO] Listening on UDP port {self.port}...")

    def listen(self):
        while self.running:
            try:
                self.sock.settimeout(1.0)
                data, addr = self.sock.recvfrom(self.buffer_size)
                message = data.decode().strip()
                print(f"[RECV] From {addr}: {message}")
                self.handle_message(message, addr)
            except socket.timeout:
                continue
            except OSError:
                break

    def handle_message(self, message, addr):
        parts = message.split(":")
        
        # Handle different message formats
        if len(parts) >= 2:  # Device status message
            device_id = parts[0]
            state = parts[1]
            
            # Determine device type from ID
            device_type = "light" if "light" in device_id else "lock"
            
            # Create or update device
            if device_id not in self.devices:
                self.devices[device_id] = Device(device_id, device_type, addr)
            
            device = self.devices[device_id]
            device.addr = addr  # Update address in case it changed
            device.last_update = datetime.now()
            
            if device_type == "light":
                # Handle light status: "light_20X:ON/OFF:current_lux:pwm_value"
                device.state = state
                if len(parts) >= 4:
                    try:
                        device.current_lux = float(parts[2])
                        device.pwm_value = int(parts[3])
                    except ValueError:
                        pass
                print(f"[LIGHT] {device_id} - State: {state}, Lux: {device.current_lux}, PWM: {device.pwm_value}")
                
            else:  # Lock device
                # Check access for lock messages (assuming message is user_id)
                if len(message.strip()) == 8:  # RFID card format
                    user_id = message.strip()
                    ip_address = addr[0]
                    if is_access_allowed(user_id, ip_address):
                        response = "UNLOCK"
                        device.state = "UNLOCKED"
                    else:
                        response = "LOCK"
                        device.state = "LOCKED"
                    self.sock.sendto(response.encode(), addr)
                    print(f"[LOCK] {device_id} - State: {device.state}, Response: {response}")

    def control_light(self, device_id, command):
        """Control a light device: ON or OFF"""
        if device_id in self.devices and self.devices[device_id].device_type == "light":
            device = self.devices[device_id]
            self.sock.sendto(command.encode(), device.addr)
            print(f"[LIGHT] Sent {command} to {device_id}")
            return True
        return False

    def get_device_status(self):
        """Get status of all devices"""
        lights = []
        locks = []
        
        for device_id, device in self.devices.items():
            last_update = device.last_update.strftime("%H:%M:%S")
            
            if device.device_type == "light":
                lights.append((
                    device_id,
                    device.state,
                    f"{device.current_lux:.1f}",
                    str(device.pwm_value),
                    last_update
                ))
            else:
                locks.append((
                    device_id,
                    device.state,
                    last_update
                ))
                
        return {"lights": sorted(lights), "locks": sorted(locks)}

    def stop(self):
        self.running = False
        self.sock.close()
        print("[INFO] UDP server stopped.")

def print_status_table(lights, locks):
    # Clear previous lines (not scrolling)
    print("\033[H\033[J")  # Clear screen
    
    # Print header
    print("\n=== Device Status ===")
    
    # Print lights table
    if lights:
        print("\nLights:")
        print("┌─────────────┬──────┬─────────┬─────────┬──────────┐")
        print("│ Device ID   │State │ Lux     │ PWM     │ Updated  │")
        print("├─────────────┼──────┼─────────┼─────────┼──────────┤")
        for device in lights:
            print(f"│ {device[0]:<11}│{device[1]:<6}│{device[2]:>8} │{device[3]:>8} │ {device[4]} │")
        print("└─────────────┴──────┴─────────┴─────────┴──────────┘")
    
    # Print locks table
    if locks:
        print("\nLocks:")
        print("┌─────────────┬──────────┬──────────┐")
        print("│ Device ID   │ State    │ Updated  │")
        print("├─────────────┼──────────┼──────────┤")
        for device in locks:
            print(f"│ {device[0]:<11}│{device[1]:<9} │ {device[2]} │")
        print("└─────────────┴──────────┴──────────┘")

def input_listener(server):
    print("Commands:")
    print("- 'status': Show all device statuses")
    print("- 'light <device_id> <ON/OFF>': Control light")
    print("- 'E': Exit server")
    
    while server.running:
        cmd = input().strip().split()
        if not cmd:
            continue
            
        if cmd[0].upper() == "E":
            server.stop()
            break
        elif cmd[0].lower() == "status":
            status = server.get_device_status()
            print_status_table(status["lights"], status["locks"])
        elif len(cmd) == 3 and cmd[0].lower() == "light":
            device_id = cmd[1]
            command = cmd[2].upper()
            if command in ["ON", "OFF"]:
                if server.control_light(device_id, command):
                    print(f"Command sent to {device_id}")
                else:
                    print(f"Device {device_id} not found or not a light")
            else:
                print("Invalid command. Use ON or OFF")
        else:
            print("Invalid command. Use 'status', 'light <device_id> <ON/OFF>', or 'E'")

if __name__ == "__main__":
    server = UDPSocketServer(UDP_PORT, BUFFER_SIZE)
    input_thread = threading.Thread(target=input_listener, args=(server,), daemon=True)
    input_thread.start()
    server.listen()