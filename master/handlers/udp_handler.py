"""UDP server handler for device communication."""
import socket
from ..config.settings import UDP_PORT, BUFFER_SIZE, DEVICE_TYPE_LIGHT, CMD_UNLOCK, CMD_LOCK
from ..handlers.device_manager import DeviceManager
from ..utils.sql import is_access_allowed, is_user_id_valid
from .command_logger import log_command

class UDPHandler:
    def __init__(self, port=UDP_PORT, buffer_size=BUFFER_SIZE):
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.device_manager = DeviceManager()
        self.running = True

    def handle_light_message(self, device, parts):
        """Handle messages from light devices."""
        state = parts[1]
        device.update_state(state)
        if len(parts) >= 5:
            try:
                lux = float(parts[2])
                pwm = int(parts[3])
                raw_ldr = int(parts[4])
                device.update_light_data(lux, pwm, raw_ldr)
            except ValueError:
                pass
        elif len(parts) >= 4:
            try:
                lux = float(parts[2])
                pwm = int(parts[3])
                device.update_light_data(lux, pwm)
            except ValueError:
                pass

    def handle_lock_message(self, device, uid, addr):
        """Handle messages from lock devices."""
        uid = uid.strip()
        uid_without_colons = uid.replace(":", "")
        if len(uid_without_colons) == 14:  # 7 bytes of hex (14 characters)
            ip_address = addr[0]
            # Use UID with colons for DB check
            if not is_user_id_valid(uid):
                response = CMD_LOCK
                device.update_state("LOCKED")
            else:
                if is_access_allowed(uid, ip_address):
                    response = CMD_UNLOCK
                    device.update_state("UNLOCKED")
                else:
                    response = CMD_LOCK
                    device.update_state("LOCKED")
            self.sock.sendto(response.encode(), addr)
            log_command(device.device_id, response, addr)
        else:
            pass

    def handle_message(self, message, addr):
        """Handle incoming UDP messages."""
        parts = message.split(":")
        
        if len(parts) >= 2:
            device_id = parts[0]
            device_type = DEVICE_TYPE_LIGHT if "light" in device_id else "lock"
            device = self.device_manager.register_or_update_device(device_id, device_type, addr)
            
            if device_type == DEVICE_TYPE_LIGHT:
                self.handle_light_message(device, parts)
            else:
                # For lock devices, join all remaining parts as the UID
                uid = ":".join(parts[1:])
                self.handle_lock_message(device, uid, addr)

    def control_light(self, device_id, command):
        """Send control command to a light device."""
        device = self.device_manager.get_device(device_id)
        if device and device.device_type == DEVICE_TYPE_LIGHT:
            self.sock.sendto(command.encode(), device.addr)
            log_command(device_id, command, device.addr)
            print(f"[LIGHT] Sent {command} to {device_id}")
            return True
        return False

    def get_device_status(self):
        """Get status of all devices."""
        return self.device_manager.get_device_status()

    def stop(self):
        """Stop the UDP server."""
        self.running = False
        self.sock.close()
