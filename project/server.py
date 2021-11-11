import socket, threading

from message import message as msg_lib
from constants import BUFFER_SIZE, FORMAT, HOST, PORT

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        self.socket_lock = threading.Lock()

    def start(self):
        print('[STARTING SERVER] Server is starting...')
        self.server_socket.bind((self.host, self.port))
        print('[LISTENING] Server is listening on {}:{}'.format(self.host, self.port))
        
        try:
            while(True):
                try:
                    data, addr = self.server_socket.recvfrom(BUFFER_SIZE)
                    thread = threading.Thread(target=self.handle_request, args=(data, addr))
                    thread.daemon = True
                    thread.start()

                except OSError as err:
                    print('[ERROR] %s' %(str(err)))

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print('[SHUTTING DOWN SERVER] Server is shutting down...')
        self.server_socket.close()

    def handle_request(self, data: bytes, addr):
        data = data.decode(FORMAT)
        print('[NEW CONNECTION] {}:{} connected'.format(addr[0], addr[1]))
        print('[CLIENT REQUEST]\n{}\n'.format(data))

        with self.socket_lock:
            # 1. Read & Extract Headers
            # 2. Read & Extract Request Body      
            # 3. Read URL & run corresponding fuction
            # 4. Peform the action (aka read or write to db)
            headers = msg_lib.extract_headers(data)
            body = msg_lib.extract_body(data)

            try:
                api_call = msg_lib.extract_url(data)[1:]
                response = getattr(self, api_call)(body)
            
            except AttributeError:
                response = self.invalid_request()

            # 5. Handle response
            self.server_socket.sendto(response, addr)

    def invalid_request(self):
        return msg_lib.create_response({
            'STATUS': 'ERROR',
            'REASON': '[ERROR] Invalid request'
        }, 500) 

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
    
    # def publish(self, request):
    #     pass



def main():
    server = Server(HOST, PORT)
    server.start()

if __name__ == "__main__":
    main()
