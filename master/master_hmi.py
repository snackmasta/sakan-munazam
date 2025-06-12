import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import matplotlib
import time
import threading
import socket
matplotlib.use('Agg')  # Use non-interactive backend for safety
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from utils import sql
from network import MasterNetworkHandler
from gui import HMIWidgets
from logic import LuxTrendLogic
from alarm_placeholder import create_alarm_placeholder  # Import the alarm placeholder module
from reservation_manager import ReservationManager

# Device info (update as needed)
DEVICES = {
    'lock_207': {'ip': '192.168.137.250', 'port': 4210, 'type': 'lock'},
    'lock_208': {'ip': '192.168.137.249', 'port': 4210, 'type': 'lock'},
    'light_207': {'ip': '192.168.137.248', 'port': 4210, 'type': 'light'},
    'light_208': {'ip': '192.168.137.247', 'port': 4210, 'type': 'light'},
}

class HeartbeatListener(threading.Thread):
    def __init__(self, device_names, alarm_callback, port=4220, timeout=1.0):
        super().__init__(daemon=True)
        self.device_names = device_names
        self.alarm_callback = alarm_callback  # function(device_name, alarm_on: bool)
        self.port = port
        self.timeout = timeout
        self.last_heartbeat = {dev: time.time() for dev in device_names}
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.sock.settimeout(0.2)

    def run(self):
        while self.running:
            now = time.time()
            # Check for lost heartbeat
            for dev, last in self.last_heartbeat.items():
                if now - last > self.timeout:
                    self.alarm_callback(dev, True)
                else:
                    self.alarm_callback(dev, False)
            # Listen for heartbeats
            try:
                data, addr = self.sock.recvfrom(128)
                msg = data.decode(errors='replace').strip()
                # Expecting: device_id:HEARTBEAT
                if msg.endswith(":HEARTBEAT"):
                    dev = msg.split(":")[0]
                    if dev in self.last_heartbeat:
                        self.last_heartbeat[dev] = time.time()
            except socket.timeout:
                continue
            except Exception:
                continue

    def stop(self):
        self.running = False
        self.sock.close()

class MasterHMI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Master HMI')
        self.geometry('800x600')
        self.lux_logic = LuxTrendLogic(max_lux_points=75)
        self._stop_event = threading.Event()
        # Networking handler
        self.network = MasterNetworkHandler(
            devices=DEVICES,
            udp_listen_port=4210,
            log_callback=self.log,
            incoming_callback=self.log_incoming,
            stop_event=self._stop_event
        )
        # GUI widgets
        self.widgets = HMIWidgets(
            master=self,
            devices=DEVICES,
            send_command_cb=self.send_command,
            broadcast_cb=self.broadcast_mesh_command,
            check_user_access_cb=self.check_user_access,
            show_user_ids_cb=self.show_user_ids,
            set_pwm_cb=self.set_pwm,
            set_max_lux_cb=self.set_max_lux_limit
        ).build_layout()
        # Assign widget references
        self.log_area = self.widgets['log_area']
        self.incoming_log_area = self.widgets['incoming_log_area']
        self.lux_fig = self.widgets['lux_fig']
        self.lux_ax = self.widgets['lux_ax']
        self.lux_canvas = self.widgets['lux_canvas']
        self.lux_canvas_widget = self.widgets['lux_canvas_widget']
        self.user_id_entry = self.widgets['user_id_entry']
        self.ip_entry = self.widgets['ip_entry']

        # Add LED indicators and alarm placeholders for each slave device
        self.led_vars = {}
        self.led_labels = {}
        self.led_indicators = {}
        self.alarm_canvases = {}

        led_frame = tk.Frame(self)
        led_frame.pack(pady=5)
        for dev in DEVICES:
            var = tk.StringVar(value='OFF')
            self.led_vars[dev] = var
            led_label = tk.Label(led_frame, text=dev, width=10)
            led_label.pack(side='left', padx=5)
            self.led_labels[dev] = led_label
            led_indicator = tk.Label(led_frame, textvariable=var, width=4, relief='sunken', bg='gray', fg='white')
            led_indicator.pack(side='left', padx=5)
            self.led_indicators[dev] = led_indicator

            # Add circular alarm placeholder
            alarm_canvas = create_alarm_placeholder(led_frame)
            alarm_canvas.pack(side='left', padx=5)
            self.alarm_canvases[dev] = alarm_canvas

        self.after(100, self.process_incoming_queue)

        # Start heartbeat listener
        self.heartbeat_listener = HeartbeatListener(DEVICES.keys(), self.heartbeat_alarm_callback)
        self.heartbeat_listener.start()

        # Map locks to their corresponding lights (update as needed)
        self.lock_to_light = {
            'lock_207': 'light_207',
            'lock_208': 'light_208',
        }
        self.devices = DEVICES  # <-- Fix: make devices available as self.devices
        self.reservation_manager = ReservationManager(self.lock_to_light, DEVICES)
        # Track which lights are ON due to reservation
        self.reserved_lights_on = {}
        # Start periodic reservation check
        self.after(1000, self.periodic_reservation_check)

    def send_command(self, device_name, command):
        try:
            self.network.send_command(device_name, command)
        except Exception as e:
            messagebox.showerror('Error', f"Failed to send command: {e}")

    def log(self, msg):
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_area.config(state='normal')
        self.log_area.insert('end', f"[{timestamp}] {msg}\n")
        self.log_area.see('end')
        self.log_area.config(state='disabled')

    def log_incoming(self, msg_with_source): # Renamed to avoid confusion with internal msg variable
        self.incoming_log_area.config(state='normal')
        self.incoming_log_area.insert('end', msg_with_source + '\n')
        self.incoming_log_area.see('end')
        self.incoming_log_area.config(state='disabled')

        original_msg_content = ""
        source_ip = None

        try:
            # Parse "From ('IP', PORT): CONTENT"
            if msg_with_source.startswith("From (") and "): " in msg_with_source:
                parts = msg_with_source.split("): ", 1)
                source_info = parts[0] # "From ('IP', PORT)"
                original_msg_content = parts[1]

                source_ip_str = source_info.split("('")[1].split("',")[0]
                source_ip = source_ip_str # Store the IP of the sender
            else:
                original_msg_content = msg_with_source
                # source_ip remains None if not in "From..." format

            # --- One-Time Access Check ---
            if source_ip and original_msg_content:
                content_parts = original_msg_content.split(':', 1) # Split only on the first colon, e.g., "lock_208" and "04:47:43:12:7A:6A:80"
                
                if len(content_parts) == 2:
                    device_name_from_msg = content_parts[0]
                    potential_uid = content_parts[1]
                    
                    actual_device_name_for_ip = None
                    for dev_key, dev_info in self.devices.items():
                        if dev_info['ip'] == source_ip and dev_info['type'] == 'lock':
                            actual_device_name_for_ip = dev_key
                            break
                    
                    if actual_device_name_for_ip and device_name_from_msg == actual_device_name_for_ip:
                        # Heuristic: UID has multiple colons (e.g., MAC address format) and is not a simple status.
                        is_likely_uid = potential_uid.count(':') >= 5 and not any(status_keyword in potential_uid for status_keyword in ['ON', 'OFF', 'LOCKED', 'UNLOCKED', 'PWM'])

                        if is_likely_uid:
                            print(f"[HMI_DEBUG] Incoming UID for one-time access check: device='{actual_device_name_for_ip}', uid='{potential_uid}', source_ip='{source_ip}'")
                            # Call reservation_manager's check_user_access directly.
                            # The boolean return is not used here to show a messagebox for this automatic flow.
                            self.reservation_manager.check_user_access(
                                user_id=potential_uid,
                                ip_address=source_ip, # IP of the lock device that sent the UID
                                send_command=self.send_command
                            )
                            # Do not pass this specific UID message to _update_led_status if it was handled as one-time access.
                            # Let further status changes (like UNLOCKED after command) be handled normally.
                            # However, to prevent _update_led_status from misinterpreting it, we can return early or pass a modified message.
                            # For now, let _update_led_status run; it should ignore this format.

        except Exception as e:
            print(f"[HMI_DEBUG] Error in log_incoming parsing for one-time access: {e}, Original message: {msg_with_source}")

        # Determine message content for downstream handlers (_update_led_status, _update_lux_from_msg)
        msg_for_downstream_handlers = original_msg_content if original_msg_content else msg_with_source
        
        self._update_led_status(msg_for_downstream_handlers)
        self._update_lux_from_msg(msg_for_downstream_handlers)

    def periodic_reservation_check(self):
        self.reservation_manager.check_reservation_expiry(self.send_command)
        self.after(1000, self.periodic_reservation_check)

    def _update_led_status(self, msg):
        # Expecting format: From (...): device_id:STATE:...
        try:
            # Extract the actual message part after the last colon
            if ":" in msg:
                parts = msg.split(": ", 1)
                if len(parts) == 2:
                    msg = parts[1]
            for dev in DEVICES:
                indicator = self.led_indicators[dev]
                if msg.startswith(dev + ':ON') or msg.startswith(dev + ':UNLOCKED'):
                    self.led_vars[dev].set('ON' if 'light' in dev else 'UNLOCKED')
                    indicator.config(bg='green')
                    if dev in self.lock_to_light and msg.startswith(dev + ':UNLOCKED'):
                        light_dev = self.lock_to_light[dev]
                        reserved, _ = self.reservation_manager.is_room_reserved_for_device(dev)
                        if reserved:
                            self.send_command(light_dev, 'ON')
                            self.reservation_manager.reserved_lights_on[light_dev] = True
                elif msg.startswith(dev + ':OFF') or msg.startswith(dev + ':LOCKED'):
                    self.led_vars[dev].set('OFF' if 'light' in dev else 'LOCKED')
                    indicator.config(bg='gray')
        except Exception as e:
            print(f"LED status update error: {e}")

    def _update_lux_from_msg(self, msg):
        self.lux_logic.update_lux_from_msg(msg, lambda: self.lux_logic.draw_lux_trend(self.lux_ax, self.lux_canvas))

    def _draw_lux_trend(self):
        self.lux_logic.draw_lux_trend(self.lux_ax, self.lux_canvas)

    def process_incoming_queue(self):
        self.network.process_incoming_queue()
        self.after(100, self.process_incoming_queue)

    def tail_server_log(self, log_path="../server.log", n=20):
        """Read the last n lines from the server.log file and display them in the incoming log area."""
        if not os.path.isabs(log_path):
            log_path = os.path.abspath(log_path)
        if not os.path.exists(log_path):
            self.log_incoming("server.log not found.")
            return
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-n:]
        for line in lines:
            if "[RECV]" in line:
                self.log_incoming(line.strip())

    def show_server_log(self):
        self.incoming_log_area.config(state='normal')
        self.incoming_log_area.delete('1.0', 'end')
        self.incoming_log_area.config(state='disabled')
        self.tail_server_log(log_path="server.log", n=50)

    def destroy(self):
        self._stop_event.set()
        self.heartbeat_listener.stop()
        super().destroy()

    def broadcast_mesh_command(self, target_device, command):
        try:
            self.network.broadcast_mesh_command(target_device, command)
        except Exception as e:
            messagebox.showerror('Error', f"Failed to unicast mesh command: {e}")

    def show_user_ids(self):
        user_ids = sql.get_all_user_ids()
        msg = 'User IDs in DB:\n' + '\n'.join(user_ids)
        messagebox.showinfo('User IDs', msg)

    def check_user_access(self, user_id, ip_address):
        allowed = self.reservation_manager.check_user_access(user_id, ip_address, send_command=self.send_command)
        if allowed:
            messagebox.showinfo('Access', f'User {user_id} is allowed for {ip_address}')
        else:
            messagebox.showwarning('Access', f'User {user_id} is NOT allowed for {ip_address}')

    def set_pwm(self, device_name, pwm_value):
        """Send PWM value to the specified light device."""
        try:
            self.send_command(device_name, f'PWM:{pwm_value}')
        except Exception as e:
            messagebox.showerror('Error', f"Failed to set PWM: {e}")

    def set_max_lux_limit(self, limit):
        """Set the maximum lux limit for the trend chart"""
        try:
            if limit < 10 or limit > 1000:
                messagebox.showwarning('Warning', 'Max lux limit should be between 10 and 1000')
                return
            self.lux_logic.set_max_lux_limit(limit)
            # Update the GUI entry field if it exists
            if 'max_lux_entry' in self.widgets:
                max_lux_entry = self.widgets['max_lux_entry']
                max_lux_entry.delete(0, 'end')
                max_lux_entry.insert(0, str(limit))
            # Redraw the chart with new limits
            self.lux_logic.draw_lux_trend(self.lux_ax, self.lux_canvas)
            self.log(f"Max lux limit set to {limit}")
        except ValueError:
            messagebox.showerror('Error', 'Invalid max lux limit value')
        except Exception as e:
            messagebox.showerror('Error', f"Failed to set max lux limit: {e}")

    def heartbeat_alarm_callback(self, device_name, alarm_on):
        """Callback function for heartbeat alarms."""
        if alarm_on:
            # Turn on the alarm placeholder (red)
            if device_name in self.alarm_canvases:
                canvas = self.alarm_canvases[device_name]
                canvas.delete("all")
                canvas.create_oval(2, 2, 18, 18, fill='red', outline='black')
        else:
            # Turn off the alarm placeholder (gray)
            if device_name in self.alarm_canvases:
                canvas = self.alarm_canvases[device_name]
                canvas.delete("all")
                canvas.create_oval(2, 2, 18, 18, fill='gray', outline='black')

if __name__ == '__main__':
    app = MasterHMI()
    app.show_server_log()  # Show last 50 incoming log lines from server.log on startup
    app.mainloop()
