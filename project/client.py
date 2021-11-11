import socket

from message import message as msg_lib

HOST = '127.0.0.1' # Localhost
PORT = 65341
ADDR = (HOST, PORT)

BUFFER_SIZE = 2048
FORMAT = 'utf-8'

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

    def publish(self, name, list: list[str]):
        print('[PUBLISH] Sending publish request...')
        paylaod = {
            'ACTION': 'PUBLISH',
            'RQ#': '',
            'NAME': name,
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('POST', '/publish', paylaod)
        self.send(request)

    def remove(self, name, list: list[str]):
        print('[REMOVE] Sending remove request...')
        paylaod = {
            'ACTION': 'REMOVE',
            'RQ#': '',
            'NAME': name,
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('POST', '/remove', paylaod)
        self.send(request)
    
    def retrieve_all(self):
        pass

    def retrieve_infot(self):
        pass

    def search_file(self):
        pass



def main():
    client = Client()
    client.register()
    client.de_register('TEST-HOST')

if __name__ == "__main__":
    main()
