import socket, threading

HOST = '127.0.0.1' # Localhost
PORT = 65341
ADDR = (HOST, PORT)

BUFFER_SIZE = 1024
FORMAT = 'utf-8'

class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        
    def start(self):
        print('[STARTING SERVER] Server is starting...')
        self.server.bind(ADDR)
        print('[LISTENING] Server is listening on %s:%s' %(HOST, PORT))
        
        while(True):
            msg, addr = self.server.recvfrom(BUFFER_SIZE)
            thread = threading.Thread(target=self.handle_request, args=(msg, addr))
            thread.start()

    def handle_request(self, msg: bytes, addr):
        print('[NEW CONNECTION] %s:%s connected' %(addr[0], addr[1]))
        print('[CLIENT MESSAGE] %s' %(msg.decode(FORMAT)))
        self.handle_response(addr)

    def handle_response(self, addr):
        ack_msg = 'Acknowledging Message'
        self.server.sendto(ack_msg.encode(FORMAT), addr)

if __name__ == "__main__":
    Server().start()
