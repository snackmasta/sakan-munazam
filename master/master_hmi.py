import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import matplotlib
import time
import threading
import socket
import json
from opcua import Client, ua
matplotlib.use('Agg')  # Use non-interactive backend for safety
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import queue

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
        self.gui_queue = queue.Queue()  # Thread-safe queue for GUI updates
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

        # Add Shutdown button
        shutdown_btn = tk.Button(self, text='Shutdown', bg='red', fg='white', font=('Arial', 12, 'bold'), command=self.shutdown)
        shutdown_btn.pack(pady=10, side='bottom')

        # Add LED indicators and alarm placeholders for each slave device
        self.led_vars = {}
        self.led_labels = {}
        self.led_indicators = {}
        self.alarm_canvases = {}
        self.ack_buttons = {}  # Store references to ACK buttons

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
            # Add ACK button for each alarm
            ack_btn = tk.Button(led_frame, text=f"ACK {dev}", command=lambda d=dev: self.ack_alarm(d))
            ack_btn.pack(side='left', padx=2)
            self.ack_buttons[dev] = ack_btn

        # Add maintenance indicators and reset buttons for each room
        self.maintenance_indicators = {}
        self.maintenance_reset_buttons = {}
        for room in ["207", "208"]:
            maint_frame = tk.Frame(self)
            maint_frame.pack(pady=2)
            maint_label = tk.Label(maint_frame, text=f"Room {room} Maintenance", width=18)
            maint_label.pack(side='left', padx=5)
            indicator = tk.Label(maint_frame, text="MAINT", width=6, relief='sunken', bg='gray', fg='white')
            indicator.pack(side='left', padx=5)
            self.maintenance_indicators[room] = indicator
            reset_btn = tk.Button(maint_frame, text=f"Reset {room}", command=lambda r=room: self.reset_maintenance(r))
            reset_btn.pack(side='left', padx=5)
            self.maintenance_reset_buttons[room] = reset_btn

        # Add LDR value StringVars for each light device
        self.ldr_vars = {}
        for dev in DEVICES:
            if DEVICES[dev]['type'] == 'light':
                self.ldr_vars[dev] = tk.StringVar(value='-')
        # If the GUI widgets for LDR exist, link them
        for dev in self.ldr_vars:
            ldr_widget_key = f'{dev}_ldr_value'
            if ldr_widget_key in self.widgets:
                self.widgets[ldr_widget_key].config(textvariable=self.ldr_vars[dev])

        # Add Lux value StringVars for each light device
        self.lux_vars = {}
        for dev in DEVICES:
            if DEVICES[dev]['type'] == 'light':
                self.lux_vars[dev] = tk.StringVar(value='-')
        # If the GUI widgets for Lux exist, link them
        for dev in self.lux_vars:
            lux_widget_key = f'{dev}_lux_value'
            if lux_widget_key in self.widgets:
                self.widgets[lux_widget_key].config(textvariable=self.lux_vars[dev])

        self.after(100, self.process_incoming_queue)
        self.after(100, self.process_gui_queue)  # Start polling the GUI queue

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

        # After building layout, set up periodic update for reservation listbox if present
        if 'reservation_listbox' in self.widgets and hasattr(self, 'update_reservation_listbox'):
            def periodic_update():
                self.update_reservation_listbox()
                self.after(60000, periodic_update)
            self.after(60000, periodic_update)

        # OPC UA client
        self.opc_client = None
        self.opc_connected = False
        self._opc_state_lock = threading.Lock()
        self._opc_state_snapshot = {}
        self._opc_thread = threading.Thread(target=self._opc_relay_thread, daemon=True)
        self._opc_thread.start()
        self._init_opcua_client()
        self._update_opc_state_snapshot()  # Initialize snapshot
        # self._start_opcua_relay_thread()  # Removed: no such method, thread already started

    def _init_opcua_client(self):
        try:
            self.opc_client = Client("opc.tcp://DESKTOP-97F20FJ:49320")
            self.opc_client.connect()
            self.opc_connected = True
            print("[HMI] Connected to OPC UA server.")
        except Exception as e:
            print(f"[HMI] OPC UA connection error: {e}")
            self.opc_connected = False

    def _update_opc_state_snapshot(self):
        """Update the thread-safe snapshot of HMI state for OPC relay."""
        state = {}
        for dev in self.led_vars:
            state[f'led_{dev}'] = 1 if self.led_vars[dev].get() in ('ON', 'UNLOCKED') else 0
        for dev, canvas in self.alarm_canvases.items():
            state[f'alarm_{dev}'] = getattr(canvas, '_json_alarm_state', 0)
        for room in self.maintenance_indicators:
            state[f'maintenance_{room}'] = 1 if self.maintenance_indicators[room].cget('bg') == 'orange' else 0
        # Add lux values for each light device
        if hasattr(self, 'lux_vars'):
            for dev in self.lux_vars:
                try:
                    lux_val = float(self.lux_vars[dev].get())
                except Exception:
                    lux_val = 0.0
                state[f'lux_{dev}'] = lux_val
        # Add PWM values for each light device (for OPC relay)
        if hasattr(self, 'pwm_vars'):
            for dev in self.pwm_vars:
                # dev: light_207, light_208
                state[f'pwm_{dev}'] = int(self.pwm_vars[dev]) if str(self.pwm_vars[dev]).isdigit() else 0
        with self._opc_state_lock:
            self._opc_state_snapshot = state.copy()

    def _opc_relay_thread(self):
        while True:
            with self._opc_state_lock:
                state = self._opc_state_snapshot.copy()
            for key, value in state.items():
                self._opc_write(key, value)
            time.sleep(0.01)  # 10ms, adjust as needed

    def _opc_write(self, key, value):
        TAG_MAP = {
            'led_lock_207': "ns=2;s=ROOM 207.Device1.led_lock_207",
            'led_lock_208': "ns=2;s=ROOM 207.Device1.led_lock_208",
            'led_light_207': "ns=2;s=ROOM 207.Device1.led_light_207",
            'led_light_208': "ns=2;s=ROOM 207.Device1.led_light_208",
            'alarm_lock_207': "ns=2;s=ROOM 207.Device1.alarm_lock_207",
            'alarm_lock_208': "ns=2;s=ROOM 207.Device1.alarm_lock_208",
            'alarm_light_207': "ns=2;s=ROOM 207.Device1.alarm_light_207",
            'alarm_light_208': "ns=2;s=ROOM 207.Device1.alarm_light_208",
            'maintenance_207': "ns=2;s=ROOM 207.Device1.maintenance_207",
            'maintenance_208': "ns=2;s=ROOM 207.Device1.maintenance_208",
            # Add OPC tags for lux values
            'lux_light_207': "ns=2;s=ROOM 207.Device1.lux_light_207",
            'lux_light_208': "ns=2;s=ROOM 207.Device1.lux_light_208",
            'pwm_light_207': "ns=2;s=ROOM 207.Device1.pwm_light_207",
            'pwm_light_208': "ns=2;s=ROOM 207.Device1.pwm_light_208",
        }
        if not self.opc_connected or key not in TAG_MAP:
            return
        try:
            node = self.opc_client.get_node(TAG_MAP[key])
            varianttype = node.get_data_type_as_variant_type()
            # For lux, always send as float
            if key.startswith('lux_'):
                v = float(value)
                node.set_value(ua.DataValue(ua.Variant(v, ua.VariantType.Float)))
                return
            if varianttype == ua.VariantType.Boolean:
                v = value
            elif varianttype == ua.VariantType.Byte:
                v = int(value) & 0xFF
            elif varianttype == ua.VariantType.Int16:
                v = int(value)
            elif varianttype == ua.VariantType.UInt16:
                v = int(value)
            elif varianttype == ua.VariantType.Int32:
                v = int(value)
            elif varianttype == ua.VariantType.UInt32:
                v = int(value)
            else:
                v = int(value)
            node.set_value(ua.DataValue(ua.Variant(v, varianttype)))
        except Exception as e:
            # Handle socket error and mark OPC as disconnected
            if hasattr(e, 'winerror') and e.winerror == 10038:
                print(f"[HMI] OPC UA client socket error (disconnected): {e}")
                self.opc_connected = False
            else:
                print(f"[HMI] Failed to write {key} to OPC: {e}")

    def send_command(self, device_name, command):
        try:
            self.network.send_command(device_name, command)
        except Exception as e:
            messagebox.showerror('Error', f"Failed to send command: {e}")

    def log(self, msg):
        from datetime import datetime
        from utils import sql
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_area.config(state='normal')
        self.log_area.insert('end', f"[{timestamp}] {msg}\n")
        self.log_area.see('end')
        self.log_area.config(state='disabled')
        try:
            sql.insert_outgoing_log(f"[{timestamp}] {msg}")
        except Exception as e:
            print(f"[HMI] Failed to record outgoing log: {e}")

    def log_incoming(self, msg_with_source): # Renamed to avoid confusion with internal msg variable
        from utils import sql
        self.incoming_log_area.config(state='normal')
        self.incoming_log_area.insert('end', msg_with_source + '\n')
        self.incoming_log_area.see('end')
        self.incoming_log_area.config(state='disabled')
        try:
            sql.insert_incoming_log(msg_with_source)
        except Exception as e:
            print(f"[HMI] Failed to record incoming log: {e}")

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

        # --- Parse PWM value from light incoming log ---
        try:
            # Format: device:STATE:LUX:PWM:LDR
            parts = original_msg_content.split(":")
            if len(parts) >= 4:
                dev = parts[0]
                if dev in self.lux_vars:  # Only for light devices
                    pwm_val = parts[3].strip()
                    if not hasattr(self, 'pwm_vars'):
                        self.pwm_vars = {}
                    self.pwm_vars[dev] = pwm_val
        except Exception as e:
            print(f"[HMI_DEBUG] Error parsing PWM from incoming log: {e}")

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
            self._update_opc_state_snapshot()
        except Exception as e:
            print(f"LED status update error: {e}")

    def _update_lux_from_msg(self, msg):
        # Update lux trend and also update LDR and Lux value boxes for each light
        self.lux_logic.update_lux_from_msg(msg, lambda: self.lux_logic.draw_lux_trend(self.lux_ax, self.lux_canvas))
        # Parse and update LDR and Lux values
        for dev in self.ldr_vars:
            if dev in msg:
                # Expecting format: device:STATE:LUX:PWM:LDR
                parts = msg.split(':')
                if len(parts) >= 5:
                    ldr_val = parts[4].strip()
                    self.ldr_vars[dev].set(ldr_val)
                if len(parts) >= 3:
                    lux_val = parts[2].strip()
                    if dev in self.lux_vars:
                        self.lux_vars[dev].set(lux_val)

    def _draw_lux_trend(self):
        self.lux_logic.draw_lux_trend(self.lux_ax, self.lux_canvas)

    def process_incoming_queue(self):
        self.network.process_incoming_queue()
        self.after(100, self.process_incoming_queue)

    def process_gui_queue(self):
        try:
            while True:
                func, args, kwargs = self.gui_queue.get_nowait()
                func(*args, **kwargs)
        except queue.Empty:
            pass
        self.after(50, self.process_gui_queue)  # Poll frequently

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

    def shutdown(self):
        """Properly shutdown the HMI, close threads/resources, and exit the application."""
        try:
            # Signal threads to stop
            self._stop_event.set()
            if hasattr(self, 'heartbeat_listener') and self.heartbeat_listener:
                self.heartbeat_listener.stop()
            # Stop OPC UA thread if running
            if hasattr(self, '_opc_thread') and self._opc_thread:
                if hasattr(self, '_opcua_thread_stop'):
                    self._opcua_thread_stop.set()
                self._opc_thread.join(timeout=1)
            # Disconnect OPC UA client if connected
            if hasattr(self, 'opc_client') and self.opc_client:
                try:
                    self.opc_client.disconnect()
                except Exception:
                    pass
        except Exception as e:
            print(f"[HMI] Error during shutdown: {e}")
        finally:
            self.quit()
            self.destroy()
            import sys
            sys.exit(0)

    def destroy(self):
        # Overridden to ensure shutdown is always called
        try:
            super().destroy()
        except Exception:
            pass

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

    def ack_alarm(self, device_name):
        """Acknowledge the alarm for a device. Turn on maintenance indicator for the room, no green ACK button."""
        try:
            # Send an ACK command to the device
            self.send_command(device_name, 'ACK')
            # Turn on maintenance indicator for the room
            for room in self.maintenance_indicators:
                if room in device_name:
                    self.set_maintenance(room, on=True)
            # No green ACK button, just keep the button as default
            if device_name in self.ack_buttons:
                ack_btn = self.ack_buttons[device_name]
                ack_btn.config(bg=self.cget('bg'), text=f'ACK {device_name}')
            if device_name in self.alarm_canvases:
                canvas = self.alarm_canvases[device_name]
                canvas._blinking = False  # Stop blinking
                canvas._acknowledged = True
                if canvas._blink_job:
                    canvas.after_cancel(canvas._blink_job)
                    canvas._blink_job = None
                # Set to solid red until heartbeat returns and reset is pressed
                canvas.itemconfig('all', fill='red')
            self._update_opc_state_snapshot()  # Update state after ACK
        except Exception as e:
            messagebox.showerror('Error', f"Failed to acknowledge alarm: {e}")

    def heartbeat_alarm_callback(self, device_name, alarm_on):
        """Callback function for heartbeat alarms."""
        def update_alarm_canvas():
            if device_name in self.alarm_canvases:
                canvas = self.alarm_canvases[device_name]
                if alarm_on:
                    # Heartbeat lost
                    if not getattr(canvas, '_acknowledged', False):
                        # Only start blinking if not already blinking
                        if not getattr(canvas, '_blinking', False):
                            canvas.start_blinking()
                else:
                    # Heartbeat is back: always clear alarm
                    canvas._acknowledged = False
                    if getattr(canvas, '_blinking', False):
                        canvas.stop_blinking()
                    canvas.itemconfig('all', fill='gray')
                self._update_opc_state_snapshot()  # Update state after alarm change
        # Instead of calling self.after directly, put the update in the queue
        self.gui_queue.put((update_alarm_canvas, (), {}))

    def reset_maintenance(self, room):
        self.set_maintenance(room, on=False)
        # Also clear alarm if heartbeat is back and ACK was pressed
        for dev in DEVICES:
            if room in dev and dev in self.alarm_canvases:
                canvas = self.alarm_canvases[dev]
                # Only clear if heartbeat is back and ACK was pressed
                if getattr(canvas, '_acknowledged', False):
                    canvas._acknowledged = False
                    canvas.stop_blinking()
                    canvas.itemconfig('all', fill='gray')
        self._update_opc_state_snapshot()  # Update state after reset
        self.log(f"Maintenance reset for Room {room}")

    def set_maintenance(self, room, on=True):
        if room in self.maintenance_indicators:
            indicator = self.maintenance_indicators[room]
            indicator.config(bg='orange' if on else 'gray')
            self._update_opc_state_snapshot()  # Update state after maintenance change

if __name__ == '__main__':
    app = MasterHMI()
    def listen_for_q():
        try:
            while True:
                key = sys.stdin.read(1)
                if key.lower() == 'q':
                    print('Detected "q" keypress. Shutting down...')
                    app.shutdown()
                    break
        except Exception:
            pass
    # Start the key listener in a background thread
    threading.Thread(target=listen_for_q, daemon=True).start()
    app.after(1000, app.show_server_log)  # Show last 50 incoming log lines from server.log after 1s
    app.mainloop()
