import socket, os

from message import message as msg_lib
from constants import ADDR, BUFFER_SIZE, FORMAT

class Client:
    def __init__(self):
        self.rq_num = -1
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        # self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP Socket

    def get_rq_num(self):
        self.rq_num = (self.rq_num + 1) % 8
        return self.rq_num

    def send(self, request):
        self.udp_socket.sendto(request, ADDR)

        try:
            response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            self.udp_socket.settimeout(3.0)
            print('[SERVER RESPONSE]\n{}\n'.format(response.decode(FORMAT)))
        
        except socket.timeout:
            print('[TIMEOUT] Connection timeout...')

    def register(self, name):
        print('[REGISTER] Sending register request...')
        paylaod = {
            'ACTION': 'REGISTER',
            'RQ#': self.get_rq_num(), # Do circular cycle of numbers 0 - 7
            'NAME': name, # Have user register name (store in .init file) **Name needs to be unique
            'IP_ADDRESS': socket.gethostbyname(socket.gethostname()),
            'UDP_SOCKET': '', # UDP socket number it can be reached at by the server
            'TCP_SOCKET': '' # TCP socket number to be used for file transfer with peers
        }

        request = msg_lib.create_request('REGISTER', paylaod)
        self.send(request)

    def de_register(self, name):
        print('[DE-REGISTER] Sending de-register request...')
        paylaod = {
            'ACTION': 'DE-REGISTER',
            'RQ#': self.get_rq_num(),
            'NAME': name, 
        }

        request = msg_lib.create_request('DE-REGISTER', paylaod)
        self.send(request)

    def publish(self, list: list[str]):
        print('[PUBLISH] Sending publish request...')
        paylaod = {
            'ACTION': 'PUBLISH',
            'RQ#': self.get_rq_num(),
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('PUBLISH', paylaod)
        self.send(request)

    def remove(self, list: list[str]):
        print('[REMOVE] Sending remove request...')
        paylaod = {
            'ACTION': 'REMOVE',
            'RQ#':  self.get_rq_num(),
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('REMOVE', paylaod)
        self.send(request)
    
    def retrieve_all(self):
        print('[RETRIEVE-ALL] Sending retrieve all request...')
        paylaod = {
            'ACTION': 'RETRIEVE-ALL',
            'RQ#':  self.get_rq_num()
        }

        request = msg_lib.create_request('RETRIEVE-ALL', paylaod)
        self.send(request)

    def retrieve_infot(self, name):
        print('[RETRIEVE-INFO] Sending retrieve info request...')
        paylaod = {
            'ACTION': 'RETRIEVE-INFO',
            'RQ#':  self.get_rq_num(),
            'NAME': name
        }

        request = msg_lib.create_request('RETRIEVE-INFO', paylaod)
        self.send(request)

    def search_file(self, file_name):
        print('[SEARCH-FILE] Sending search file request...')
        paylaod = {
            'ACTION': 'SEARCH-FILE',
            'RQ#':  self.get_rq_num(),
            'FILE_NAME': file_name
        }

        request = msg_lib.create_request('SEARCH-FILE', paylaod)
        self.send(request)

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
