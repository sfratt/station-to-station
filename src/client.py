import socket, threading, os, json
from random import randint
from datetime import datetime
import tkinter as tk
from tkinter.constants import DISABLED, NORMAL

from message import message as msg_lib
from models.constants import ADDR, BUFFER_SIZE, FORMAT, HEADER_SIZE

class Client:
    def __init__(self):
        
        gui_thread = threading.Thread(target=self.gui, args=())
        #gui_thread.daemon = True
        gui_thread.start()
        
        self.rq_num = -1
        self.host = socket.gethostbyname(socket.gethostname())
        self.tcp_port = 10000

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP Socket

        self.get_tcp_port_num()
        client_listening_thread = threading.Thread(target=self.start_tcp_server, args=())
        client_listening_thread.daemon = True
        client_listening_thread.start()
        

    def get_rq_num(self):
        self.rq_num = (self.rq_num + 1) % 8
        return self.rq_num

    def get_tcp_port_num(self):
        self.tcp_port = randint(10000, 65535)

    def print_log(self, msg: str):
        date_time = datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        print('[{}] {}'.format(date_time, msg))
        self.insert_log('[{}] {}'.format(date_time, msg))

    def start_tcp_server(self):
        self.print_log('Starting Client...')
        is_bound = False
        while (not is_bound):
            try:
                self.tcp_socket.bind((self.host, self.tcp_port))
                is_bound = True

            except OSError:
                self.get_tcp_port_num()

        self.print_log('Client is listening on {}:{}'.format(self.host, self.tcp_port))
        self.tcp_socket.listen()

        while (True):
            conn, addr = self.tcp_socket.accept()
            new_client_thread = threading.Thread(target=self.handle_download_request, args=(conn, addr))
            new_client_thread.daemon = True
            new_client_thread.start()

    def stop_tcp_server(self):
        self.print_log('Client is shutting down...')
        self.udp_socket.close()
        self.tcp_socket.close()

    def handle_download_request(self, conn: socket.socket, addr):
        self.print_log('New connection from {}:{}'.format(addr[0], addr[1]))

        try:
            data = conn.recv(HEADER_SIZE).decode(FORMAT)
            header = msg_lib.extract_headers(data)
            content_length = header['content-length']

            data = conn.recv(content_length).decode(FORMAT)
            body = json.loads(data)
            self.print_log('Client Request\nHeader: {}\nBody: {}\n'.format(header, body))

        except OSError as err:
            self.print_log('ERROR: {}'.format(err))

        self.print_log('Starting download...')
        chunk_num = 0
        file_name = body['FILE_NAME']
        path = os.path.join('..\shared_folder', file_name)
        self.print_log('Reading file from {}'.format(path))
        
        try:
            with open(path, 'r') as file:
                while (True):
                    chunk = file.read(200)

                    if (not chunk):
                        break

                    payload = {
                        'RQ#': body['RQ#'],
                        'FILE_NAME': file_name,
                        'CHUNK#': chunk_num,
                        'TEXT': chunk
                    }

                    if (len(chunk) < 200):
                        self.print_log('Sending final chunk # {}'.format(chunk_num))
                        response = msg_lib.create_request('FILE-END', payload)
                    else:
                        self.print_log('Sending chunk # {}'.format(chunk_num))
                        response = msg_lib.create_request('FILE', payload)

                    conn.send(response)
                    chunk_num += 1
            
            self.print_log('Download complete')

        except Exception as err:
            self.print_log('Download Error\nReason: {}'.format(err))
            payload = {
                'STATUS': 'DOWNLOAD-ERROR',
                'RQ#': body['RQ#'],
                'REASON': str(err)
            }
            response = msg_lib.create_response(payload, 500)
            conn.send(response)

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
        payload = {
            'ACTION': 'REGISTER',
            'RQ#': self.get_rq_num(), # Do circular cycle of numbers 0 - 7
            'NAME': name, # Have user register name (store in .init file) **Name needs to be unique
            'IP_ADDRESS': self.host,
            'UDP_SOCKET': None, # UDP socket number it can be reached at by the server
            'TCP_SOCKET': self.tcp_port # TCP socket number to be used for file transfer with peers
        }

        request = msg_lib.create_request('REGISTER', payload)
        self.send_to_udp_server(request)

    def de_register(self, name):
        self.print_log('Sending de-register request...')
        payload = {
            'ACTION': 'DE-REGISTER',
            'RQ#': self.get_rq_num(),
            'NAME': name, 
        }

        request = msg_lib.create_request('DE-REGISTER', payload)
        self.send_to_udp_server(request)

    def publish(self, list: list[str]):
        self.print_log('Sending publish request...')
        payload = {
            'ACTION': 'PUBLISH',
            'RQ#': self.get_rq_num(),
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('PUBLISH', payload)
        self.send_to_udp_server(request)

    def remove(self, list: list[str]):
        self.print_log('Sending remove request...')
        payload = {
            'ACTION': 'REMOVE',
            'RQ#':  self.get_rq_num(),
            'NAME': socket.gethostname(),
            'LIST_OF_FILES': list 
        }

        request = msg_lib.create_request('REMOVE', payload)
        self.send_to_udp_server(request)
    
    def retrieve_all(self):
        self.print_log('Sending retrieve all request...')
        payload = {
            'ACTION': 'RETRIEVE-ALL',
            'RQ#':  self.get_rq_num()
        }

        request = msg_lib.create_request('RETRIEVE-ALL', payload)
        self.send_to_udp_server(request)

    def retrieve_info(self, name):
        self.print_log('Sending retrieve info request...')
        payload = {
            'ACTION': 'RETRIEVE-INFO',
            'RQ#':  self.get_rq_num(),
            'NAME': name
        }

        request = msg_lib.create_request('RETRIEVE-INFO', payload)
        self.send_to_udp_server(request)

    def search_file(self, file_name):
        self.print_log('Sending search file request...')
        payload = {
            'ACTION': 'SEARCH-FILE',
            'RQ#':  self.get_rq_num(),
            'FILE_NAME': file_name
        }

        request = msg_lib.create_request('SEARCH-FILE', payload)
        self.send_to_udp_server(request)

    def update_contact(self, ip_address: str, udp_socket: int, tcp_socket: int):
        pass
    
    def insert_log(self,msg):
        self.log_text.configure(state=NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.configure(state=DISABLED)

    def download(self, host, port, file_name):
        download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.print_log('Download socket created')

        try:
            self.print_log('Connecting to {}:{} for file download'.format(host, port))
            download_socket.connect((host, port))

            payload = {
                'RQ#': self.get_rq_num(),
                'FILE_NAME': file_name
            }

            request = msg_lib.create_request('DOWNLOAD', payload)
            download_socket.send(request)
            
            # Handle Response of Files
            self.print_log('Downloading...')
            chunk_dict = {}

            while (True):
                data = download_socket.recv(HEADER_SIZE).decode(FORMAT)
                method_call = msg_lib.extract_method(data)
                header = msg_lib.extract_headers(data)
                content_length = header['content-length']

                data = download_socket.recv(content_length).decode(FORMAT)
                body = json.loads(data)
                self.print_log('Incoming file chunk: {}'.format(body))

                if ('STATUS' in body and body['STATUS'] == 'DOWNLOAD-ERROR'):
                    self.print_log('DOWNLOAD-ERROR: {}'.format(body['REASON']))
                    return

                chunk_num = body['CHUNK#']
                chunk = body['TEXT']
                chunk_dict[chunk_num] = chunk

                if (method_call == 'file_end'):
                    total_chunk_num = body['CHUNK#']
                    break
            
            # Assemble File
            path = os.path.join('..\downloads', file_name)
            self.print_log('Assembling file to {}'.format(path))

            with open(path, 'w') as file:
                for i in range(total_chunk_num + 1):
                    file.write(chunk_dict[i])

            self.print_log('Download complete')

        except OSError as err:
            self.print_log('ERROR: {}'.format(err))

        finally:
            download_socket.close()
            self.print_log('Connection {}:{} closed'.format(host, port))
            
    def gui(self):
        window = tk.Tk()
        window.geometry("900x800")
        window.resizable(False, False)

        label = tk.Label(text="Name").place(x=0, y=0)
        entry = tk.Entry(window, width=40)
        entry.place(x=50, y=0)

        tk.Button(window, text="Register", command=lambda: self.register(entry.get())).place(x=0, y=25)
        tk.Button(window, text="Deregister", command=self.de_register).place(x=55, y=25)
        tk.Button(window, text="Func1", command=self.register).place(x=120, y=25)

        scroll = tk.Scrollbar(window)

        self.log_text = tk.Text(window, height=45, width=110, state=DISABLED)
        self.log_text.place(x=0, y=50)
        
        # Need to start running the Client() when the UI starts

        window.mainloop()



# ***** FOR TESTING *****

# Get file names to client wants to share to public
def get_files():
    return os.listdir('./shared_folder')

# Temp cmd line menu
def print_options():
    return '''*****CLIENT*****

Please select the function you would like to perform:
1. Register
2. De-register
3. Publish
4. Remove
5. Retrieve all
6. Retrieve info
7. Search file
8. Update Contact
9. Download

Press 0 to close client\n'''

def main():
    client = Client()

    

    #client.stop_tcp_server()
    #print('Exit Client Program')

if __name__ == "__main__":
   main()
