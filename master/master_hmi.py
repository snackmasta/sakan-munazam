import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading
import queue
import os

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
