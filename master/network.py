import socket
import threading
import queue
import time
from utils import sql
from threading import Timer

class MasterNetworkHandler:
    def __init__(self, devices, udp_listen_port, log_callback, incoming_callback, stop_event=None, hmi_ref=None):
        self.devices = devices
        self.udp_listen_port = udp_listen_port
        self.log_callback = log_callback  # function to log outgoing
        self.incoming_callback = incoming_callback  # function to log incoming
        self.incoming_queue = queue.Queue()
        self._stop_event = stop_event or threading.Event()
        self.hmi_ref = hmi_ref  # Reference to MasterHMI for auto light logic
        self.udp_thread = threading.Thread(target=self.listen_udp, daemon=True)
        self.udp_thread.start()

    def send_command(self, device_name, command):
        info = self.devices[device_name]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(command.encode(), (info['ip'], info['port']))
            self.log_callback(f"Sent {command} to {device_name} at {info['ip']}:{info['port']}")
        except Exception as e:
            self.log_callback(f"Error sending to {device_name}: {e}")
            raise

    def broadcast_mesh_command(self, target_device, command):
        info = self.devices[target_device]
        target_ip = info['ip']
        mesh_message = f"{target_ip}:{command}:3"  # TTL=3 (or adjust as needed)
        try:
            for name, info in self.devices.items():
                if info['type'] in ('light', 'lock'):
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.sendto(mesh_message.encode(), (info['ip'], info['port']))
                        time.sleep(0.01)
            self.log_callback(f"Unicast mesh command to all: {mesh_message}")
        except Exception as e:
            self.log_callback(f"Error unicasting mesh command: {e}")
            raise

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
                    parts = data.decode(errors='replace').strip().split(":")
                    if len(parts) >= 2:
                        device_id = parts[0]
                        uid = ":".join(parts[1:])
                        if device_id.startswith("lock_"):
                            ip_address = addr[0]
                            if sql.is_access_allowed(uid, ip_address):
                                for name, info in self.devices.items():
                                    if info['ip'] == ip_address and info['type'] == 'lock':
                                        # --- NEW: Call HMI auto reservation logic ---
                                        if self.hmi_ref:
                                            # 10 seconds reservation, can be changed
                                            self.hmi_ref.auto_reservation_light_unlock(name, reservation_seconds=10)
                                        else:
                                            # Fallback: just unlock/lock as before
                                            self.broadcast_mesh_command(name, 'UNLOCK')
                                            self.log_callback(f"[AUTO] UID {uid} allowed for {ip_address}, sent UNLOCK broadcast.")
                                            Timer(2.0, lambda: self.broadcast_mesh_command(name, 'LOCK')).start()
                                        break
                except Exception as e:
                    self.log_callback(f"[AUTO] Error in auto-unlock: {e}")
                # --- End automatic matching ---
            except socket.timeout:
                continue
            except Exception as e:
                self.incoming_queue.put(f"UDP Listen error: {e}")
        sock.close()

    def process_incoming_queue(self):
        while not self.incoming_queue.empty():
            msg = self.incoming_queue.get()
            self.incoming_callback(msg)
