import socket

HOST = '127.0.0.1' # Localhost
PORT = 65341
ADDR = (HOST, PORT)

BUFFER_SIZE = 1024
FORMAT = 'utf-8'

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket

    def send(self, msg):
        print('[SENDING DATA] Client sending data...')
        self.client.sendto(msg.encode(FORMAT), ADDR)

        response, addr = self.client.recvfrom(BUFFER_SIZE)
        print('[SERVER RESPONSE] %s' %(response.decode(FORMAT)))


if __name__ == "__main__":
    Client().send('Hello Server! Im a new client')
