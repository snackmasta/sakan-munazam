import threading
import time

class AlarmStateListener(threading.Thread):
    """
    Listens for changes in alarm, ACK, maintenance, and reset states for devices/rooms.
    Callbacks are triggered on state changes.
    """
    def __init__(self, get_state_callback, on_alarm=None, on_ack=None, on_maintenance=None, on_reset=None, poll_interval=0.2):
        """
        get_state_callback: function returning dict with keys: device/room, values: dict with keys 'alarm', 'ack', 'maintenance', 'reset'
        on_alarm: function(device, state)
        on_ack: function(device, state)
        on_maintenance: function(room, state)
        on_reset: function(room, state)
        poll_interval: polling interval in seconds
        """
        super().__init__(daemon=True)
        self.get_state_callback = get_state_callback
        self.on_alarm = on_alarm
        self.on_ack = on_ack
        self.on_maintenance = on_maintenance
        self.on_reset = on_reset
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._last_state = {}

    def run(self):
        while not self._stop_event.is_set():
            state = self.get_state_callback()
            for key, vals in state.items():
                prev = self._last_state.get(key, {})
                # Alarm
                if 'alarm' in vals and vals['alarm'] != prev.get('alarm'):
                    if self.on_alarm:
                        self.on_alarm(key, vals['alarm'])
                # ACK
                if 'ack' in vals and vals['ack'] != prev.get('ack'):
                    if self.on_ack:
                        self.on_ack(key, vals['ack'])
                # Maintenance
                if 'maintenance' in vals and vals['maintenance'] != prev.get('maintenance'):
                    if self.on_maintenance:
                        self.on_maintenance(key, vals['maintenance'])
                # Reset
                if 'reset' in vals and vals['reset'] != prev.get('reset'):
                    if self.on_reset:
                        self.on_reset(key, vals['reset'])
                self._last_state[key] = vals.copy()
            time.sleep(self.poll_interval)

    def stop(self):
        self._stop_event.set()
