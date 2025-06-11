import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import matplotlib
import time
import threading
matplotlib.use('Agg')  # Use non-interactive backend for safety
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from utils import sql
from network import MasterNetworkHandler
from gui import HMIWidgets

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
        self.lux_data = []  # Store recent lux values for trend
        self.max_lux_points = 40  # Number of points to show in trend
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
            show_user_ids_cb=self.show_user_ids
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
        self.after(100, self.process_incoming_queue)

    def send_command(self, device_name, command):
        try:
            self.network.send_command(device_name, command)
        except Exception as e:
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
        allowed = sql.is_access_allowed(user_id, ip_address)
        if allowed:
            messagebox.showinfo('Access', f'User {user_id} is allowed for {ip_address}')
        else:
            messagebox.showwarning('Access', f'User {user_id} is NOT allowed for {ip_address}')

if __name__ == '__main__':
    app = MasterHMI()
    app.show_server_log()  # Show last 50 incoming log lines from server.log on startup
    app.mainloop()
