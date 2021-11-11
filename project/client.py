import socket

from message import message as msg_lib

HOST = '127.0.0.1' # Localhost
PORT = 65341
ADDR = (HOST, PORT)

BUFFER_SIZE = 4096
FORMAT = 'utf-8'

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket

    def send(self, request):
        self.client.sendto(request, ADDR)
        response, addr = self.client.recvfrom(BUFFER_SIZE)
        print('[SERVER RESPONSE] {}\r\n'.format(response.decode(FORMAT)))

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
            'RQ#': '123', # DONT UNDERSTAND THIS FIELD
            'NAME': name, 
        }

        request = msg_lib.create_request('POST', '/de_register', paylaod)
        self.send(request)

    def publish(self):
        pass

    def remove(self):
        pass
    
    def retrieve_all(self):
        pass

    def retrieve_infot(self):
        pass

    def search_file(self):
        pass

if __name__ == "__main__":
    Client().register()
    Client().de_register('TEST-HOST')
