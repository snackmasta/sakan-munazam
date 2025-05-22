import socket
import threading

UDP_PORT = 4210
BUFFER_SIZE = 1024

class UDPSocketServer:
    def __init__(self, port, buffer_size):
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.devices = {}  # Track device states by address
        self.running = True
        print(f"[INFO] Listening on UDP port {self.port}...")

    def listen(self):
        while self.running:
            try:
                self.sock.settimeout(1.0)
                data, addr = self.sock.recvfrom(self.buffer_size)
                print(f"[RECV] From {addr}: {data.decode()}")
                self.handle_message(data, addr)
            except socket.timeout:
                continue
            except OSError:
                break

    def handle_message(self, data, addr):
        # Respond with "UNLOCK" if data is "E3BA4B0E", else "LOCK"
        message = data.decode().strip()
        if message == "E3BA4B0E":
            response = "UNLOCK"
            self.devices[addr] = "UNLOCKED"
        else:
            response = "LOCK"
            self.devices[addr] = "LOCKED"
        self.sock.sendto(response.encode(), addr)
        print(f"[SEND] Sent reply '{response}' to {addr}")
        print(f"[STATE] Devices: {self.devices}")

    def stop(self):
        self.running = False
        self.sock.close()
        print("[INFO] UDP server stopped.")

def input_listener(server):
    while server.running:
        key = input()
        if key.strip().upper() == "E":
            server.stop()
            break

if __name__ == "__main__":
    server = UDPSocketServer(UDP_PORT, BUFFER_SIZE)
    input_thread = threading.Thread(target=input_listener, args=(server,), daemon=True)
    input_thread.start()
    server.listen()