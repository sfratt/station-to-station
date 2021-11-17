import socket, threading
from datetime import datetime

from message import message as msg_lib
from models.constants import BUFFER_SIZE, FORMAT, HOST, PORT
from data.client_store import ClientStore
from models.client_dto import ClientDto

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        self.socket_lock = threading.Lock()

    def print_log(self, msg: str):
        date_time = datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        print('[{}] {}'.format(date_time, msg))

    def start(self):
        self.print_log('Starting Server...')
        self.server_socket.bind((self.host, self.port))
        self.print_log('Server is listening on {}:{}'.format(self.host, self.port))
        
        try:
            while(True):
                try:
                    data, addr = self.server_socket.recvfrom(BUFFER_SIZE)
                    thread = threading.Thread(target=self.handle_request, args=(data, addr))
                    thread.daemon = True
                    thread.start()

                except OSError as err:
                    self.print_log('ERROR: {}'.format(err))

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.print_log('Server is shutting down...')
        self.server_socket.close()

    def handle_request(self, data: bytes, addr):
        data = data.decode(FORMAT)
        self.print_log('New connection from {}:{}'.format(addr[0], addr[1]))
        self.print_log('Client request:\n{}\n'.format(data))

        with self.socket_lock:
            headers = msg_lib.extract_headers(data)
            body = msg_lib.extract_body(data)

            try:
                method_call = msg_lib.extract_method(data)
                response = getattr(self, method_call)(body, addr)
            
            except AttributeError:
                response = self.invalid_request(body)

            # 5. Handle response
            try:
                self.print_log('Responding to request')
                self.server_socket.sendto(response, addr)

            except TypeError:
                self.print_log('Ignoring request')
                pass

    def invalid_request(self):
        return msg_lib.create_response({
            'STATUS': 'ERROR',
            'REASON': '[ERROR] Invalid request'
        }, 500) 

    def register(self, request: dict, client_addr):
        client_dto = ClientDto(request['NAME'], request['IP_ADDRESS'], client_addr[1], request['TCP_SOCKET'])
        
        with ClientStore() as db:
            try:
                db.add_client(client_dto)
                return msg_lib.create_response({
                    'RQ#': request['RQ#'],
                    'STATUS': 'REGISTERED'
                }, 200)

            except Exception as err:
                return msg_lib.create_response({
                    'RQ#': request['RQ#'],
                    'STATUS': 'REGISTER-DENIED',
                    'REASON': '[ERROR] {}'.format(err)
                }, 500)

    def de_register(self, request, client_addr):
        # De-register should delete all data that belows to client as well as client itself 
        # ERROR: Currently you can de-register a non registered name
        client_dto = ClientDto(request['NAME'], None, None, None)
        
        with ClientStore() as db:
            try:
                db.delete_client(client_dto)
                return msg_lib.create_response({
                    'RQ#': request['RQ#'],
                    'STATUS': 'DE-REGISTERED'
                }, 200)

            except Exception as err:
                self.print_log('Name is not registered')
                return None
    
    # def publish(self, request, client_addr):
    #     for i in range(1000000000):
    #         pass



def main():
    server = Server(HOST, PORT)
    server.start()

if __name__ == "__main__":
    main()
