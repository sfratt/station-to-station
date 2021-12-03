import socket, threading, sys, time
from datetime import datetime
from collections import defaultdict

from message import message as msg_lib
from models.constants import BUFFER_SIZE, FORMAT
from data.client_store import ClientStore
from data.store import StoreException
from models.client_dto import ClientDto
from models.file_dto import FileDto

class Server:

    def __init__(self, host, port):
        """
        Initializes the server by creating a UDP socket and a new database if the
        database does not exist.
        """

        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Socket
        self.clients_rq_num_dict = defaultdict(list)

        with ClientStore() as db:
            try:
                db.create_tables()
                db.complete()
            except:
                pass # DB already created, do nothing

    def print_log(self, msg: str):
        """
        Attaches timestamp to message and prints to terminal.
        """
        date_time = datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        print('[{}] {}'.format(date_time, msg))

    def start_server(self):
        """
        Infinite loop to listen for incoming requests from clients.
        Each request is handled on a new thread.
        """

        self.print_log('Starting Server...')
        self.server_socket.bind((self.host, self.port))
        self.print_log('Server is listening on {}:{}'.format(self.host, self.port))

        while (True):
            try:
                request, client_addr = self.server_socket.recvfrom(BUFFER_SIZE)
                new_request_thread = threading.Thread(target=self.handle_request, args=(request, client_addr))
                new_request_thread.start()
                new_request_thread.join()

            except OSError as err:
                self.print_log('ERROR: {}'.format(err))

    def stop_server(self):
        """
        Close server's UDP socket.
        """
        self.print_log('Server is shutting down...')
        self.server_socket.close()

    def handle_request(self, request: bytes, client_addr):
        """
        Read client's request and call corresponding function to that method. If method is not found response with an invalid request. 
        If response is empty just ignore request and do not send a response. All duplicate requests (RQ#) are ignored.
        """

        request = request.decode(FORMAT)
        self.print_log('New request from {}:{}'.format(client_addr[0], client_addr[1]))
        self.print_log('Client Request\n{}\n'.format(request))

        headers = msg_lib.extract_headers(request)
        body = msg_lib.extract_body(request)

        try:
            # Check for duplicate requests and ignore
            if (body['RQ#'] in self.clients_rq_num_dict[f'{client_addr[0]}:{client_addr[1]}']):
                self.print_log('Request RQ# {} already received from {}, ignoring request...'.format(body['RQ#'], client_addr[0]))
                return

            # Save in memory all clients RQ#
            self.clients_rq_num_dict[f'{client_addr[0]}:{client_addr[1]}'].append(body['RQ#'])

            method_call = msg_lib.extract_method(request)
            response = getattr(self, method_call)(body, client_addr) # Call function based on method in request header
        
        except AttributeError:
            response = self.invalid_request() # Invalid request if method is not found 

        try:
            self.server_socket.sendto(response, client_addr)
            self.print_log('Responding to request RQ# {} from {}'.format(body['RQ#'], client_addr[0]))

        except TypeError:
            self.print_log('Ignoring request RQ# {} from {}'.format(body['RQ#'], client_addr[0]))
            pass

    def invalid_request(self):
        return msg_lib.create_response({
            'STATUS': 'ERROR',
            'REASON': 'Invalid request'
        }, 500) 

    def register(self, data: dict, client_addr):
        client_dto = ClientDto(data['NAME'], data['IP_ADDRESS'], client_addr[1], data['TCP_SOCKET'])
        
        with ClientStore() as db:
            try:
                self.print_log('Adding client to database')
                db.register_client(client_dto)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'REGISTERED'
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'REGISTER-DENIED',
                    'REASON': '{}'.format(err)
                }, 500)

    def de_register(self, data: dict, client_addr):
        client_name = data['NAME']
        
        with ClientStore() as db:
            try:
                self.print_log('Removing client from database')
                db.deregister_client(client_name)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'DE-REGISTERED'
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'DE-REGISTER-ERROR',
                    'REASON': '{}'.format(err)
                }, 500)
    
    def publish(self, data: dict, client_addr):
        file_dto = FileDto(data['NAME'], data['LIST_OF_FILES']) 
        
        with ClientStore() as db:
            try:
                self.print_log('Publishing list of files to database')
                db.publish_files(file_dto)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'PUBLISHED'
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'PUBLISH-DENIED',
                    'REASON': '{}'.format(err)
                }, 500)

    def remove(self, data: dict, client_addr):
        file_dto = FileDto(data['NAME'], data['LIST_OF_FILES'])
        
        with ClientStore() as db:
            try:
                self.print_log('Removing list of files from database')
                db.remove_files(file_dto)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'REMOVED'
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'REMOVED-DENIED',
                    'REASON': '{}'.format(err)
                }, 500)

    def retrieve_all(self, data: dict, client_addr):
        client_name = data['NAME']

        with ClientStore() as db:
            try:
                self.print_log('Retrieving list of all clients from database')
                all_clients = db.retrieve_all(client_name)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'RETRIEVED-ALL',
                    'CLIENTS': [{'NAME': col[0], 'IP_ADDRESS': col[1], 'TCP_SOCKET': col[2], 'LIST_OF_FILES': col[3]} for col in all_clients]
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'RETRIEVE-ERROR',
                    'REASON': '{}'.format(err)
                }, 500)

    def retrieve_info(self, data: dict, client_addr):
        client_name = data['NAME']
        search_name = data['SEARCH_NAME']
        
        with ClientStore() as db:
            try:
                self.print_log('Retrieving info of client {} from database'.format(search_name))
                client = db.retrieve_info(client_name, search_name)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'RETRIEVED-INFO',
                    'NAME': client[0],
                    'IP_ADDRESS': client[1],
                    'TCP_SOCKET': client[2],
                    'LIST_OF_FILES': client[3]
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'RETRIEVE-ERROR',
                    'REASON': '{}'.format(err)
                }, 500)

    def search_file(self, data: dict, client_addr):
        client_name = data['NAME']
        file_name = data['FILE_NAME']
        
        with ClientStore() as db:
            try:
                self.print_log('Searching for file {} in database'.format(file_name))
                clients = db.search_file(client_name, file_name)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'FILE-FOUND',
                    'CLIENTS': [{'NAME': col[0], 'IP_ADDRESS': col[1], 'TCP_SOCKET': col[2]} for col in clients]
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'SEARCH-ERROR',
                    'REASON': '{}'.format(err)
                }, 500)

    def update_contact(self, data: dict, client_addr):
        client_dto = ClientDto(data['NAME'], data['IP_ADDRESS'], client_addr[1], data['TCP_SOCKET'])
        
        with ClientStore() as db:
            try:
                self.print_log('Adding client to database')
                db.update_client(client_dto)
                db.complete()
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'UPDATE-CONFIRMED',
                    'NAME': client_dto.name,
                    'IP_ADDRESS': client_dto.ip_address,
                    'UDP_SOCKET': client_dto.udp_socket,
                    'TCP_SOCKET': client_dto.tcp_socket
                }, 200)

            except StoreException as err:
                self.print_log('[ERROR] {}'.format(err))
                return msg_lib.create_response({
                    'RQ#': data['RQ#'],
                    'STATUS': 'UPDATE-DENIED',
                    'REASON': '{}'.format(err)
                }, 500)



def main():
    server.start_server()

if __name__ == "__main__":
    ip_address = socket.gethostbyname(socket.gethostname())
    server = Server(ip_address, 9000)

    try:
        thread = threading.Thread(target=main)
        thread.daemon = True
        thread.start()
        while (True):
            pass

    except KeyboardInterrupt:
        pass
    finally:
            server.stop_server()
            sys.exit()
