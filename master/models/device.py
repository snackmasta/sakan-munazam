"""Device model class."""
from datetime import datetime

class Device:
    def __init__(self, device_id, device_type, addr):
        self.device_id = device_id
        self.device_type = device_type
        self.addr = addr
        self.state = "UNKNOWN"
        self.last_update = datetime.now()
        # Additional attributes for lights
        self.current_lux = 0.0
        self.pwm_value = 0
        self.raw_ldr = 0  # New: raw LDR value

    def update_state(self, state):
        """Update device state and timestamp."""
        self.state = state
        self.last_update = datetime.now()

    def update_light_data(self, lux, pwm, raw_ldr=None):
        """Update light-specific data."""
        self.current_lux = lux
        self.pwm_value = pwm
        if raw_ldr is not None:
            self.raw_ldr = raw_ldr

    def to_dict(self):
        """Convert device to dictionary for status display."""
        data = {
            "state": self.state,
            "last_update": self.last_update.strftime("%H:%M:%S")
        }
        if self.device_type == "light":
            data.update({
                "current_lux": f"{self.current_lux:.1f}",
                "pwm_value": str(self.pwm_value),
                "raw_ldr": str(self.raw_ldr)  # New: raw LDR value
            })
        return data
