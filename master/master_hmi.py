import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading
import queue
import os
import matplotlib
import time
matplotlib.use('Agg')  # Use non-interactive backend for safety
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from utils import sql

# Device info (update as needed)
DEVICES = {
    'lock_207': {'ip': '192.168.137.250', 'port': 4210, 'type': 'lock'},
    'lock_208': {'ip': '192.168.137.249', 'port': 4210, 'type': 'lock'},
    'light_207': {'ip': '192.168.137.248', 'port': 4210, 'type': 'light'},
    'light_208': {'ip': '192.168.137.247', 'port': 4210, 'type': 'light'},
}

class MasterHMI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Master HMI')
        self.geometry('800x600')
        self.create_widgets()
        self.incoming_queue = queue.Queue()
        self.udp_listen_port = 4210  # Use a different port than outgoing if needed
        self._stop_event = threading.Event()
        self.udp_thread = threading.Thread(target=self.listen_udp, daemon=True)
        self.udp_thread.start()
        self.after(100, self.process_incoming_queue)
        self.lux_data = []  # Store recent lux values for trend
        self.max_lux_points = 40  # Number of points to show in trend

    def create_widgets(self):
        # Main layout: left (controls), right (trend), bottom (logs)
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True)

        # Left panel: Device controls
        left_panel = tk.LabelFrame(main_frame, text="Device Controls", font=("Arial", 10, "bold"), padx=8, pady=8)
        left_panel.grid(row=0, column=0, sticky='nsw', padx=8, pady=8)
        lock_frame = tk.LabelFrame(left_panel, text="Locks", font=("Arial", 9, "bold"), padx=4, pady=4)
        lock_frame.pack(fill='x', pady=(0,8))
        light_frame = tk.LabelFrame(left_panel, text="Lights", font=("Arial", 9, "bold"), padx=4, pady=4)
        light_frame.pack(fill='x')
        for name, info in DEVICES.items():
            if info['type'] == 'lock':
                frame = tk.Frame(lock_frame)
                frame.pack(fill='x', pady=2)
                tk.Label(frame, text=name, width=10, anchor='w').pack(side='left')
                tk.Button(frame, text='LOCK', width=7, command=lambda n=name: self.send_command(n, 'LOCK')).pack(side='left', padx=2)
                tk.Button(frame, text='UNLOCK', width=7, command=lambda n=name: self.send_command(n, 'UNLOCK')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST LOCK', width=14, command=lambda n=name: self.broadcast_mesh_command(n, 'LOCK')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST UNLOCK', width=14, command=lambda n=name: self.broadcast_mesh_command(n, 'UNLOCK')).pack(side='left', padx=2)
            elif info['type'] == 'light':
                frame = tk.Frame(light_frame)
                frame.pack(fill='x', pady=2)
                tk.Label(frame, text=name, width=10, anchor='w').pack(side='left')
                tk.Button(frame, text='ON', width=7, command=lambda n=name: self.send_command(n, 'ON')).pack(side='left', padx=2)
                tk.Button(frame, text='OFF', width=7, command=lambda n=name: self.send_command(n, 'OFF')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST ON', width=12, command=lambda n=name: self.broadcast_mesh_command(n, 'ON')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST OFF', width=12, command=lambda n=name: self.broadcast_mesh_command(n, 'OFF')).pack(side='left', padx=2)

        # Right panel: Trend chart
        right_panel = tk.LabelFrame(main_frame, text="Trend Visualization", font=("Arial", 10, "bold"), padx=8, pady=8)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=8, pady=8)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        tk.Label(right_panel, text="Lux Trend", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=(5,0))
        self.lux_fig = Figure(figsize=(3.5, 1.5), dpi=90)
        self.lux_ax = self.lux_fig.add_subplot(111)
        self.lux_canvas = FigureCanvasTkAgg(self.lux_fig, master=right_panel)
        self.lux_canvas_widget = self.lux_canvas.get_tk_widget()
        self.lux_canvas_widget.pack(padx=5, pady=5, fill='both', expand=True)

        # Bottom panel: Logs
        bottom_panel = tk.LabelFrame(self, text="Logs", font=("Arial", 10, "bold"), padx=8, pady=8)
        bottom_panel.pack(fill='x', padx=8, pady=(0,8), side='bottom')
        log_frame = tk.Frame(bottom_panel)
        log_frame.pack(fill='x')
        # Outgoing log
        out_frame = tk.Frame(log_frame)
        out_frame.pack(side='left', fill='both', expand=True, padx=(0,8))
        tk.Label(out_frame, text='Outgoing Log', font=("Arial", 9, "bold")).pack(anchor='w')
        self.log_area = scrolledtext.ScrolledText(out_frame, width=40, height=7, state='disabled')
        self.log_area.pack(fill='both', expand=True)
        # Incoming log
        in_frame = tk.Frame(log_frame)
        in_frame.pack(side='left', fill='both', expand=True)
        tk.Label(in_frame, text='Incoming Log', font=("Arial", 9, "bold")).pack(anchor='w')
        self.incoming_log_area = scrolledtext.ScrolledText(in_frame, width=40, height=7, state='disabled')
        self.incoming_log_area.pack(fill='both', expand=True)

        # Add SQL DB controls
        db_frame = tk.LabelFrame(self, text="SQL DB Tools", font=("Arial", 10, "bold"), padx=8, pady=8)
        db_frame.pack(fill='x', padx=8, pady=(0,8), side='bottom')
        tk.Button(db_frame, text='Show All User IDs', command=self.show_user_ids).pack(side='left', padx=4)
        tk.Label(db_frame, text='Check Access for User ID:').pack(side='left', padx=4)
        self.user_id_entry = tk.Entry(db_frame, width=12)
        self.user_id_entry.pack(side='left', padx=2)
        tk.Label(db_frame, text='IP:').pack(side='left', padx=2)
        self.ip_entry = tk.Entry(db_frame, width=15)
        self.ip_entry.pack(side='left', padx=2)
        tk.Button(db_frame, text='Check Access', command=lambda: self.check_user_access(self.user_id_entry.get(), self.ip_entry.get())).pack(side='left', padx=4)

    def send_command(self, device_name, command):
        info = DEVICES[device_name]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(command.encode(), (info['ip'], info['port']))
            self.log(f"Sent {command} to {device_name} at {info['ip']}:{info['port']}")
        except Exception as e:
            self.log(f"Error sending to {device_name}: {e}")
            messagebox.showerror('Error', f"Failed to send command: {e}")

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert('end', msg + '\n')
        self.log_area.see('end')
        self.log_area.config(state='disabled')

    def log_incoming(self, msg):
        self.incoming_log_area.config(state='normal')
        self.incoming_log_area.insert('end', msg + '\n')
        self.incoming_log_area.see('end')
        self.incoming_log_area.config(state='disabled')
        # Parse lux value from incoming data and update trend
        self._update_lux_from_msg(msg)

    def _update_lux_from_msg(self, msg):
        # Only treat the part with a decimal as lux, color by device
        try:
            color = 'blue'  # default
            dev = None
            if 'light_207' in msg:
                color = 'red'
                dev = 'light_207'
            elif 'light_208' in msg:
                color = 'blue'
                dev = 'light_208'
            if 'light_' in msg:
                parts = msg.split(':')
                for part in parts:
                    part = part.strip()
                    if '.' in part:
                        try:
                            lux = float(part)
                            # Store (lux, color, dev) for matplotlib separation
                            self.lux_data.append((lux, color, dev))
                            if len(self.lux_data) > self.max_lux_points:
                                self.lux_data = self.lux_data[-self.max_lux_points:]
                            self._draw_lux_trend()
                            break
                        except ValueError:
                            continue
        except Exception:
            pass

    def _draw_lux_trend(self):
        self.lux_ax.clear()
        if not self.lux_data:
            self.lux_canvas.draw()
            return
        # Separate data by device
        data_207 = [(i, lux) for i, (lux, color, dev) in enumerate([(v[0], v[1], v[2] if len(v) > 2 else None) for v in self.lux_data]) if dev == 'light_207']
        data_208 = [(i, lux) for i, (lux, color, dev) in enumerate([(v[0], v[1], v[2] if len(v) > 2 else None) for v in self.lux_data]) if dev == 'light_208']
        if data_207:
            x_207, y_207 = zip(*data_207)
            self.lux_ax.plot(x_207, y_207, color='red', label='light_207')
        if data_208:
            x_208, y_208 = zip(*data_208)
            self.lux_ax.plot(x_208, y_208, color='blue', label='light_208')
        self.lux_ax.set_ylabel('Lux')
        self.lux_ax.set_xlabel('Sample')
        self.lux_ax.legend(loc='upper right', fontsize=8)
        self.lux_ax.grid(True, linestyle='--', alpha=0.5)
        self.lux_fig.tight_layout()
        self.lux_canvas.draw()

    def listen_udp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.udp_listen_port))
        sock.settimeout(1.0)
        while not self._stop_event.is_set():
            try:
                data, addr = sock.recvfrom(1024)
                msg = f"From {addr}: {data.decode(errors='replace')}"
                self.incoming_queue.put(msg)

                # --- Automatic UID/IP matching and unlock broadcast ---
                try:
                    # Expecting format: device_id:UID (for lock devices)
                    parts = data.decode(errors='replace').strip().split(":")
                    if len(parts) >= 2:
                        device_id = parts[0]
                        uid = ":".join(parts[1:])
                        # Only for lock devices
                        if device_id.startswith("lock_"):
                            ip_address = addr[0]
                            # Check access
                            if sql.is_access_allowed(uid, ip_address):
                                # Find the device in DEVICES by IP
                                for name, info in DEVICES.items():
                                    if info['ip'] == ip_address and info['type'] == 'lock':
                                        # Send mesh UNLOCK broadcast for this lock
                                        self.broadcast_mesh_command(name, 'UNLOCK')
                                        self.log(f"[AUTO] UID {uid} allowed for {ip_address}, sent UNLOCK broadcast.")
                                        break
                except Exception as e:
                    self.log(f"[AUTO] Error in auto-unlock: {e}")
                # --- End automatic matching ---
            except socket.timeout:
                continue
            except Exception as e:
                self.incoming_queue.put(f"UDP Listen error: {e}")
        sock.close()

    def process_incoming_queue(self):
        while not self.incoming_queue.empty():
            msg = self.incoming_queue.get()
            self.log_incoming(msg)
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
        super().destroy()

    def broadcast_mesh_command(self, target_device, command):
        # Send mesh command as IP:COMMAND:TTL
        info = DEVICES[target_device]
        target_ip = info['ip']
        mesh_message = f"{target_ip}:{command}:3"  # TTL=3 (or adjust as needed)
        try:
            for name, info in DEVICES.items():
                if info['type'] in ('light', 'lock'):
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.sendto(mesh_message.encode(), (info['ip'], info['port']))
                        time.sleep(0.01)
            self.log(f"Unicast mesh command to all: {mesh_message}")
        except Exception as e:
            self.log(f"Error unicasting mesh command: {e}")
            messagebox.showerror('Error', f"Failed to unicast mesh command: {e}")

    def show_user_ids(self):
        user_ids = sql.get_all_user_ids()
        msg = 'User IDs in DB:\n' + '\n'.join(user_ids)
        messagebox.showinfo('User IDs', msg)

    def check_user_access(self, user_id, ip_address):
        allowed = sql.is_access_allowed(user_id, ip_address)
        if allowed:
            messagebox.showinfo('Access', f'User {user_id} is allowed for {ip_address}')
        else:
            messagebox.showwarning('Access', f'User {user_id} is NOT allowed for {ip_address}')

if __name__ == '__main__':
    app = MasterHMI()
    app.show_server_log()  # Show last 50 incoming log lines from server.log on startup
    app.mainloop()
