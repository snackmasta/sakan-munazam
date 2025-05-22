import socket

UDP_PORT = 4210
BUFFER_SIZE = 1024

class UDPSocketServer:
    def __init__(self, port, buffer_size):
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        print(f"[INFO] Listening on UDP port {self.port}...")

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(self.buffer_size)
            print(f"[RECV] From {addr}: {data.decode()}")
            self.handle_message(data, addr)

    def handle_message(self, data, addr):
        # Respond with "UNLOCK" if data is "E3BA4B0E", else "LOCK"
        message = data.decode().strip()
        if message == "E3BA4B0E":
            response = "UNLOCK"
        else:
            response = "LOCK"
        self.sock.sendto(response.encode(), addr)
        print(f"[SEND] Sent reply '{response}' to {addr}")

if __name__ == "__main__":
    server = UDPSocketServer(UDP_PORT, BUFFER_SIZE)
    server.listen()