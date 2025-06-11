import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket

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
        self.geometry('500x400')
        self.create_widgets()

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
        self.log_area = scrolledtext.ScrolledText(self, width=60, height=10, state='disabled')
        self.log_area.grid(row=row, column=0, padx=10, pady=10)

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

if __name__ == '__main__':
    app = MasterHMI()
    app.mainloop()
