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
        headers = msg_lib.extract_headers(msg)
        body = msg_lib.extract_body(msg)

        api_call = msg_lib.extract_url(msg)[1:]
        response = getattr(self, api_call)(body)
        
        # 5. Handle response
        self.server.sendto(response, addr)

    def register(self, request: dict):
        # Connect to db 
        # Check if name already exists
        name_exists = False

        if(not name_exists):
            try:
                # Write to db (add new client)

                return msg_lib.create_response({
                    'RQ#': request['RQ#'],
                    'STATUS': 'REGISTERED'
                }, 200)

            except Exception as err:
                return msg_lib.create_response({
                    'RQ#': request['RQ#'],
                    'STATUS': 'REGISTER-FAILED',
                    'REASON': '[ERROR] {}'.format(err)
                }, 500)

        else:
            return msg_lib.create_response({
                'RQ#': request['RQ#'],
                'STATUS': 'REGISTER-DENIED',
                'REASON': '[ERROR] Client {} already exists'.format(request['NAME'])
            }, 500)

    def de_register(self, request):
        try:
            # Connect to db
            # Try to remove client name and all info
            # If no client exists, ignore 
            return msg_lib.create_response({
                'RQ#': request['RQ#'],
                'STATUS': 'DE-REGISTERED'
            }, 200)

        except Exception as err:
            return msg_lib.create_response({
                'RQ#': request['RQ#'],
                'STATUS': 'DE-REGISTER-FAILED',
                'REASON': '[ERROR] {}'.format(err)
            }, 500)
    
    def publish(self, request):
        pass

if __name__ == "__main__":
    Server().start()
