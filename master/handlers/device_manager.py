"""Device manager for handling device registry and operations."""
from ..models.device import Device
from ..config.settings import DEVICE_TYPE_LIGHT, DEVICE_TYPE_LOCK

class DeviceManager:
    def __init__(self):
        self.devices = {}

    def register_or_update_device(self, device_id, device_type, addr):
        """Register a new device or update existing one."""
        if device_id not in self.devices:
            self.devices[device_id] = Device(device_id, device_type, addr)
        device = self.devices[device_id]
        device.addr = addr  # Update address in case it changed
        return device

    def get_device(self, device_id):
        """Get a device by ID."""
        return self.devices.get(device_id)

    def get_device_status(self):
        """Get status of all devices."""
        lights = []
        locks = []
        
        for device_id, device in self.devices.items():
            if device.device_type == DEVICE_TYPE_LIGHT:
                lights.append((
                    device_id,
                    device.state,
                    device.to_dict()["current_lux"],
                    device.to_dict()["pwm_value"],
                    device.to_dict()["last_update"]
                ))
            else:
                locks.append((
                    device_id,
                    device.state,
                    device.to_dict()["last_update"]
                ))
                
        return {
            "lights": sorted(lights),
            "locks": sorted(locks)
        }
