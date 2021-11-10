import socket, threading

from message import message as msg_lib

HOST = '127.0.0.1' # Localhost
PORT = 65341
ADDR = (HOST, PORT)

BUFFER_SIZE = 4096
FORMAT = 'utf-8'

class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        
    def start(self):
        print('[STARTING SERVER] Server is starting...')
        self.server.bind(ADDR)
        print('[LISTENING] Server is listening on {}:{}'.format(HOST, PORT))
        
        while(True):
            try:
                msg, addr = self.server.recvfrom(BUFFER_SIZE)
                thread = threading.Thread(target=self.handle_request, args=(msg, addr))
                thread.start()

            except OSError as err:
                print('[ERROR] %s' %(str(err)))

    def handle_request(self, msg: bytes, addr):
        msg = msg.decode(FORMAT)
        print('[NEW CONNECTION] {}:{} connected'.format(addr[0], addr[1]))
        print('[CLIENT MESSAGE] {}\r\n'.format(msg))

        # 1. Read & Extract Headers
        # 2. Read & Extract Request Body
        # 3. Read URL & run corresponding fuction
        # 4. Peform the action (aka read or write to db)
        # 5. Handle response

        payload = {
            'RQ#': '123',
            'STATUS': '',
        }
        response = msg_lib.create_response(payload, 200)
        self.server.sendto(response, addr)

    def register(self):
        pass

if __name__ == "__main__":
    Server().start()
