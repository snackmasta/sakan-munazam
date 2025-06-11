import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading
import queue
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for safety
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.geometry('600x500')
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
        row = 0
        for name, info in DEVICES.items():
            frame = tk.Frame(self)
            frame.grid(row=row, column=0, padx=10, pady=5, sticky='w')
            tk.Label(frame, text=name).pack(side='left')
            if info['type'] == 'lock':
                tk.Button(frame, text='LOCK', command=lambda n=name: self.send_command(n, 'LOCK')).pack(side='left', padx=5)
                tk.Button(frame, text='UNLOCK', command=lambda n=name: self.send_command(n, 'UNLOCK')).pack(side='left', padx=5)
            elif info['type'] == 'light':
                tk.Button(frame, text='ON', command=lambda n=name: self.send_command(n, 'ON')).pack(side='left', padx=5)
                tk.Button(frame, text='OFF', command=lambda n=name: self.send_command(n, 'OFF')).pack(side='left', padx=5)
            row += 1
        self.log_area = scrolledtext.ScrolledText(self, width=60, height=7, state='disabled')
        self.log_area.grid(row=row, column=0, padx=10, pady=5)
        row += 1
        self.incoming_log_area = scrolledtext.ScrolledText(self, width=60, height=7, state='disabled')
        self.incoming_log_area.grid(row=row, column=0, padx=10, pady=5)
        tk.Label(self, text='Outgoing Log').grid(row=row-1, column=1, sticky='nw')
        tk.Label(self, text='Incoming Log').grid(row=row, column=1, sticky='nw')
        # Trend summary (add lux trend chart placeholder)
        trend_frame = tk.LabelFrame(self, text="Trend Summary Table", font=("Arial", 10, "bold"), bg="#f0f0f0")
        trend_frame.grid(row=row+1, column=0, padx=10, pady=5, sticky='ew')
        tk.Label(trend_frame, text="Lux Trend", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=5, pady=(5,0))
        # Remove old Canvas, add matplotlib Figure
        self.lux_fig = Figure(figsize=(2.8, 1.2), dpi=80)
        self.lux_ax = self.lux_fig.add_subplot(111)
        self.lux_canvas = FigureCanvasTkAgg(self.lux_fig, master=trend_frame)
        self.lux_canvas_widget = self.lux_canvas.get_tk_widget()
        self.lux_canvas_widget.pack(padx=5, pady=5)

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

if __name__ == '__main__':
    app = MasterHMI()
    app.show_server_log()  # Show last 50 incoming log lines from server.log on startup
    app.mainloop()
