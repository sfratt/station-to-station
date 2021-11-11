import socket, os

from message import message as msg_lib
from constants import ADDR, BUFFER_SIZE, FORMAT

class Client:
    def __init__(self):
        self.upd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        # self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP Socket

    def send(self, request):
        self.upd_socket.sendto(request, ADDR)
        response, addr = self.upd_socket.recvfrom(BUFFER_SIZE)
        print('[SERVER RESPONSE]\n{}\n'.format(response.decode(FORMAT)))

    def register(self):
        print('[REGISTER] Sending register request...')
        paylaod = {
            'ACTION': 'REGISTER',
            'RQ#': '123', # DONT UNDERSTAND THIS FIELD
            'NAME': socket.gethostname(), # Name needs to be unique
            'IP_ADDRESS': socket.gethostbyname(socket.gethostname()),
            'UDP_SOCKET': '', # UDP socket number it can be reached at by the server
            'TCP_SOCKET': '' # TCP socket number to be used for file transfer with peers
        }

        request = msg_lib.create_request('POST', '/register', paylaod)
        self.send(request)

    def de_register(self, name):
        print('[DE-REGISTER] Sending de-register request...')
        paylaod = {
            'ACTION': 'DE-REGISTER',
            'RQ#': '',
            'NAME': name, 
        }

        request = msg_lib.create_request('POST', '/de-register', paylaod)
        self.send(request)

    def publish(self, list: list[str]):
        print('[PUBLISH] Sending publish request...')
        paylaod = {
            'ACTION': 'PUBLISH',
            'RQ#': '',
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('POST', '/publish', paylaod)
        self.send(request)

    def remove(self, list: list[str]):
        print('[REMOVE] Sending remove request...')
        paylaod = {
            'ACTION': 'REMOVE',
            'RQ#': '',
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('POST', '/remove', paylaod)
        self.send(request)
    
    def retrieve_all(self):
        print('[RETRIEVE-ALL] Sending retrieve all request...')
        paylaod = {
            'ACTION': 'RETRIEVE-ALL',
            'RQ#': ''
        }

        request = msg_lib.create_request('GET', '/retrieve-all', paylaod)
        self.send(request)

    def retrieve_infot(self, name):
        print('[RETRIEVE-INFOT] Sending retrieve info request...')
        paylaod = {
            'ACTION': 'RETRIEVE-INFOT',
            'RQ#': '',
            'NAME': name
        }

        request = msg_lib.create_request('GET', '/retrieve-info', paylaod)
        self.send(request)

    def search_file(self, file_name):
        print('[SEARCH-FILE] Sending search file request...')
        paylaod = {
            'ACTION': 'SEARCH-FILE',
            'RQ#': '',
            'FILE_NAME': file_name
        }

        request = msg_lib.create_request('GET', '/search-file', paylaod)
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
    client.register()
    client.de_register('TEST-HOST')
    client.publish(get_files())

if __name__ == "__main__":
    main()
