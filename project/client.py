import socket, threading, os
from random import randint
from datetime import datetime

from message import message as msg_lib
from constants import ADDR, BUFFER_SIZE, FORMAT

class Client:
    def __init__(self):
        self.rq_num = -1
        self.host = socket.gethostbyname(socket.gethostname())
        self.tcp_port = 10000

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP Socket

        self.get_port_num()
        self.start() # Need to start on a thread because client needs to listen, talk to server & talk to other clients

    def get_rq_num(self):
        self.rq_num = (self.rq_num + 1) % 8
        return self.rq_num

    def get_port_num(self):
        self.tcp_port = randint(10000, 65535)

    def print_log(self, msg: str):
        date_time = datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        print('[{}] {}'.format(date_time, msg))

    def start(self):
        self.print_log('Starting Client...')
        self.tcp_socket.bind((self.host, self.tcp_port)) # Need to check if port number already exists
        self.print_log('Client is listening on {}:{}'.format(self.host, self.tcp_port))

        try:
            self.tcp_socket.listen()

            while(True):
                conn, addr = self.tcp_socket.accept()
                new_client_thread = threading.Thread(target=self.handle_request, args=(conn, addr))
                new_client_thread.daemon = True
                new_client_thread.start()

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.print_log('Client is shutting down...')
        self.udp_socket.close()
        self.tcp_socket.close()

    def handle_request(self, conn: socket.socket, addr):
        self.print_log('New connection from {}:{}'.format(addr[0], addr[1]))

        try:
            data = conn.recv(1024) # Need to determine buffer size
            data = data.decode(FORMAT)
            # Read all data
            # Use data

        except OSError as err:
            self.print_log('ERROR: {}'.format(err))

        finally:
            conn.close()
            self.print_log('Connection {}:{} closed'.format(addr[0], addr[1]))

    def send_to_udp_server(self, request):
        self.udp_socket.sendto(request, ADDR)

        try:
            response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            self.udp_socket.settimeout(3.0)
            self.print_log('Server Response\n{}\n'.format(response.decode(FORMAT)))
        
        except socket.timeout:
            self.print_log('Connection timeout. Request not received, send again')

    def register(self, name):
        self.print_log('Sending register request...')
        paylaod = {
            'ACTION': 'REGISTER',
            'RQ#': self.get_rq_num(), # Do circular cycle of numbers 0 - 7
            'NAME': name, # Have user register name (store in .init file) **Name needs to be unique
            'IP_ADDRESS': self.host,
            'UDP_SOCKET': '', # UDP socket number it can be reached at by the server
            'TCP_SOCKET': self.tcp_port # TCP socket number to be used for file transfer with peers
        }

        request = msg_lib.create_request('REGISTER', paylaod)
        self.send_to_udp_server(request)

    def de_register(self, name):
        self.print_log('Sending de-register request...')
        paylaod = {
            'ACTION': 'DE-REGISTER',
            'RQ#': self.get_rq_num(),
            'NAME': name, 
        }

        request = msg_lib.create_request('DE-REGISTER', paylaod)
        self.send_to_udp_server(request)

    def publish(self, list: list[str]):
        self.print_log('Sending publish request...')
        paylaod = {
            'ACTION': 'PUBLISH',
            'RQ#': self.get_rq_num(),
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('PUBLISH', paylaod)
        self.send_to_udp_server(request)

    def remove(self, list: list[str]):
        self.print_log('Sending remove request...')
        paylaod = {
            'ACTION': 'REMOVE',
            'RQ#':  self.get_rq_num(),
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('REMOVE', paylaod)
        self.send_to_udp_server(request)
    
    def retrieve_all(self):
        self.print_log('Sending retrieve all request...')
        paylaod = {
            'ACTION': 'RETRIEVE-ALL',
            'RQ#':  self.get_rq_num()
        }

        request = msg_lib.create_request('RETRIEVE-ALL', paylaod)
        self.send_to_udp_server(request)

    def retrieve_infot(self, name):
        self.print_log('Sending retrieve info request...')
        paylaod = {
            'ACTION': 'RETRIEVE-INFO',
            'RQ#':  self.get_rq_num(),
            'NAME': name
        }

        request = msg_lib.create_request('RETRIEVE-INFO', paylaod)
        self.send_to_udp_server(request)

    def search_file(self, file_name):
        self.print_log('Sending search file request...')
        paylaod = {
            'ACTION': 'SEARCH-FILE',
            'RQ#':  self.get_rq_num(),
            'FILE_NAME': file_name
        }

        request = msg_lib.create_request('SEARCH-FILE', paylaod)
        self.send_to_udp_server(request)

    def update_contact(self, ip_address: str, udp_socket: int, tcp_socket: int):
        pass

    def download(self):
        pass


# Get file names to client wants to share to public
def get_files():
    return os.listdir('./shared_folder')

def main():
    client = Client()
    client.register('TEST-HOST')
    client.de_register('TEST-HOST')
    client.publish(get_files())

if __name__ == "__main__":
    main()
