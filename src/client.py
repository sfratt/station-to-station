import socket, threading, os, json
from random import randint
from datetime import datetime
import tkinter as tk
from tkinter.constants import DISABLED, NORMAL

from message import message as msg_lib
from models.constants import BUFFER_SIZE, FORMAT, HEADER_SIZE

class Client:
    def __init__(self):
        self.start_ui_lock = threading.Lock()
        
        self.start_ui_lock.acquire()
        gui_thread = threading.Thread(target=self.gui)
        gui_thread.start()
        
        self.client_name = ''
        self.rq_num = -1
        self.host = socket.gethostbyname(socket.gethostname())
        self.tcp_port = 10000

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP Socket

        self.get_tcp_port_num()
        self.start_ui_lock.acquire()
        client_listening_thread = threading.Thread(target=self.start_tcp_server, args=())
        client_listening_thread.daemon = True
        client_listening_thread.start()

    def get_rq_num(self):
        # self.rq_num = (self.rq_num + 1) % 8
        self.rq_num += 1
        return self.rq_num

    def get_tcp_port_num(self):
        self.tcp_port = randint(10000, 65535)

    def print_log(self, msg: str):
        date_time = datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        log  = '[{}] {}'.format(date_time, msg)
        self.insert_log(log)
        print(log)

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

    def stop_client(self):
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

                    payload = {
                        'RQ#': body['RQ#'],
                        'FILE_NAME': file_name,
                        'CHUNK#': chunk_num,
                        'TEXT': chunk
                    }

                    if (len(chunk) < 200 or not chunk): # Check for EOF
                        self.print_log('Sending final chunk # {}'.format(chunk_num))
                        response = msg_lib.create_request('FILE-END', payload)
                        conn.send(response)
                        break

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

    def connect_to_server(self, host, port):
        self.server_addr = (host, port)
        self.print_log('Connected to server {}:{}'.format(host, port))
        self.button_toggle("server") # TODO Do we block actions until register??

    def send_to_udp_server(self, current_rq_num: int, request: bytes):
        self.udp_socket.sendto(request, self.server_addr)
        self.udp_socket.settimeout(5)

        for i in range(3):
            try:
                while (True):
                    response = None
                    response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                    response = response.decode(FORMAT)
                    body = msg_lib.extract_body(response)

                    if ('RQ#' in body and body['RQ#'] == current_rq_num):
                        self.print_log('Server Response\n{}\n'.format(response))
                        if('STATUS' in body):
                            if (body['STATUS'] == 'REGISTER-DENIED' or body['STATUS'] == 'DE-REGISTERED' or body['STATUS'] == 'UPDATE-DENIED'):
                                self.client_name = ''
                        
                        self.button_toggle("enable")
                        self.display_client_name()
                        return

            except socket.timeout:
                self.print_log('Connection timeout. Sending again...')
                self.udp_socket.sendto(request, self.server_addr)

            except ConnectionError:
                self.print_log('ERROR : Server is unavailable')
                return

        if response is None:
            self.print_log('No response from the server')

    def register(self, name):
        if name == "":
            self.print_log("Name cannot be empty")
            return
        
        self.button_toggle("disable")
        self.client_name = name
        rq_num = self.get_rq_num()
        payload = {
            'RQ#': rq_num,
            'NAME': name,
            'IP_ADDRESS': self.host,
            'TCP_SOCKET': self.tcp_port
        }

        self.print_log('Sending register request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('REGISTER', payload)
        register_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        register_thread.start()

    def de_register(self, name: str):
        if name == "":
            self.print_log("Name cannot be empty")
            return
        
        self.button_toggle("disable")
        rq_num = self.get_rq_num()
        payload = {
            'RQ#': rq_num,
            'NAME': name, 
        }

        self.print_log('Sending de-register request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('DE-REGISTER', payload)
        de_register_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        de_register_thread.start()

    def publish(self, file_names: str):
        if file_names == '':
            self.print_log("File name(s) cannot be empty")
            return
        
        self.button_toggle("disable")
        files = list(file_name.strip() for file_name in file_names.split(','))
        rq_num = self.get_rq_num()
        payload = {
            'RQ#': rq_num,
            'NAME': self.client_name,
            'LIST_OF_FILES': files
        }

        self.print_log('Sending publish request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('PUBLISH', payload)
        publish_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        publish_thread.start()

    def remove(self, file_names: str):
        if file_names == '':
            self.print_log("File name(s) cannot be empty")
            return
        
        self.button_toggle("disable")
        files = list(file_name.strip() for file_name in file_names.split(','))
        rq_num = self.get_rq_num()
        payload = {
            'RQ#':  rq_num,
            'NAME': self.client_name,
            'LIST_OF_FILES': files 
        }

        self.print_log('Sending remove request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('REMOVE', payload)
        remove_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        remove_thread.start()
    
    def retrieve_all(self):
        self.button_toggle("disable")
        rq_num = self.get_rq_num()
        payload = {
            'RQ#':  rq_num,
            'NAME': self.client_name,
        }

        self.print_log('Sending retrieve all request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('RETRIEVE-ALL', payload)
        retrieve_all_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        retrieve_all_thread.start()

    def retrieve_info(self, search_name: str):
        if search_name == "":
            self.print_log("Name cannot be empty")
            return
        
        self.button_toggle("disable")
        rq_num = self.get_rq_num()
        payload = {
            'RQ#':  rq_num,
            'NAME': self.client_name,
            'SEARCH_NAME': search_name
        }

        self.print_log('Sending retrieve info request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('RETRIEVE-INFO', payload)
        retrieve_info_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        retrieve_info_thread.start()

    def search_file(self, file_name: str):
        if file_name == "":
            self.print_log("File name cannot be empty")
            return
        
        self.button_toggle("disable")
        rq_num = self.get_rq_num()
        payload = {
            'RQ#':  rq_num,
            'NAME': self.client_name,
            'FILE_NAME': file_name
        }

        self.print_log('Sending search file request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('SEARCH-FILE', payload)
        search_file_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        search_file_thread.start()

    def update_contact(self, name: str):
        if name == "":
            self.print_log("Name cannot be empty")
            return
        
        self.button_toggle("disable")
        self.client_name = name
        rq_num = self.get_rq_num()
        payload = {
            'RQ#': rq_num,
            'NAME': name,
            'IP_ADDRESS': self.host,
            'TCP_SOCKET': self.tcp_port
        }

        self.print_log('Sending update request RQ# {}...'.format(rq_num))
        request = msg_lib.create_request('UPDATE-CONTACT', payload)
        update_contact_thread = threading.Thread(target=self.send_to_udp_server, args=(rq_num, request), daemon=True)
        update_contact_thread.start()

    def download(self, host, port, file_name):
        if file_name == "" and host =="" and port == "":
            self.print_log("File name, host or port cannot be empty")
            return
        
        self.button_toggle("disable")
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
            stop_download_check = False

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
                    stop_download_check = True

                if (stop_download_check):
                    total_chunk_set = set(range(1, total_chunk_num + 1))
                    current_chunk_set = set(chunk_dict.keys())
                    if (total_chunk_set.issubset(current_chunk_set)):
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
            self.button_toggle("enable")

    def display_client_name(self):
        self.client_name_label.config(text="Client: {}".format(self.client_name))

    def insert_log(self,msg):
        self.log_text.configure(state=NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.configure(state=DISABLED)
        
    def button_toggle(self, button_name):
        if button_name == "server":
            self.register_button.config(state=NORMAL)
            self.degister_button.config(state=NORMAL)
            self.updatecontact_button.config(state=NORMAL)
        elif button_name == "disable":
            self.register_button.config(state=DISABLED)
            self.degister_button.config(state=DISABLED)
            self.publish_button.config(state=DISABLED)
            self.remove_button.config(state=DISABLED)
            self.retrieveall_button.config(state=DISABLED)
            self.retrieveinfo_button.config(state=DISABLED)
            self.searchfile_button.config(state=DISABLED)
            self.download_button.config(state=DISABLED)
            self.updatecontact_button.config(state=DISABLED)
            self.connect_button.config(state=DISABLED)
        elif button_name == "enable":
            self.register_button.config(state=NORMAL)
            self.degister_button.config(state=NORMAL)
            self.publish_button.config(state=NORMAL)
            self.remove_button.config(state=NORMAL)
            self.retrieveall_button.config(state=NORMAL)
            self.retrieveinfo_button.config(state=NORMAL)
            self.searchfile_button.config(state=NORMAL)
            self.download_button.config(state=NORMAL)
            self.updatecontact_button.config(state=NORMAL)
            self.connect_button.config(state=NORMAL)

    def gui(self):
        window = tk.Tk()
        window.geometry("1200x900")
        window.resizable(False, False)

        scroll = tk.Scrollbar(window)

        self.log_text = tk.Text(window, height=51, width=149, state=DISABLED)
        self.log_text.place(x=0, y=100)

        self.client_name_label = tk.Label(text="Client: ")
        self.client_name_label.place(x=0, y=0)

        name_label = tk.Label(text="Name").place(x=0, y=25)
        name_entry = tk.Entry(window, width=15)
        name_entry.place(x=80, y=25)
        
        file_name_label = tk.Label(text="File name(s)").place(x=190, y=25)
        file_name_entry = tk.Entry(window, width=80)
        file_name_entry.place(x=270, y=25)
        
        host_name_label = tk.Label(text="Host name").place(x=0, y=50)
        host_name_entry = tk.Entry(window, width=15)
        host_name_entry.place(x=80, y=50)
        
        port_name_label = tk.Label(text="Port number").place(x=190, y=50)
        port_name_entry = tk.Entry(window, width=15)
        port_name_entry.place(x=270, y=50)
        port_name_entry.insert(0, '9000')
             
        self.register_button = tk.Button(window, text="Register", width=10, state = DISABLED, command=lambda: self.register(name_entry.get().strip()))
        self.register_button.place(x=0, y=75)

        self.degister_button = tk.Button(window, text="Deregister", width=10, state = DISABLED, command=lambda: self.de_register(name_entry.get().strip()))
        self.degister_button.place(x=85, y=75)

        self.publish_button = tk.Button(window, text="Publish", width=10, state = DISABLED, command=lambda: self.publish(file_name_entry.get().strip()))
        self.publish_button.place(x=170, y=75)

        self.remove_button = tk.Button(window, text="Remove", width=10, state = DISABLED, command=lambda: self.remove(file_name_entry.get().strip()))
        self.remove_button.place(x=255, y=75)

        self.retrieveall_button = tk.Button(window, text="Retrieve-all", width=10, state = DISABLED, command=lambda: self.retrieve_all())
        self.retrieveall_button.place(x=340, y=75)

        self.retrieveinfo_button = tk.Button(window, text="Retrieve-info", width=10, state = DISABLED, command=lambda: self.retrieve_info(name_entry.get().strip()))
        self.retrieveinfo_button.place(x=425, y=75)

        self.searchfile_button = tk.Button(window, text="Search-file", width=10, state = DISABLED, command=lambda: self.search_file(file_name_entry.get().split(',')[0].strip()))
        self.searchfile_button.place(x=510, y=75)

        self.download_button = tk.Button(window, text="Download", width=10, state = DISABLED, command=lambda: self.download(host_name_entry.get().strip(), int(port_name_entry.get()), file_name_entry.get().strip()))
        self.download_button.place(x=595, y=75)

        self.updatecontact_button = tk.Button(window, text="Update-contact", width=15, state = DISABLED, command=lambda: self.update_contact(name_entry.get().strip()))
        self.updatecontact_button.place(x=680, y=75)

        self.connect_button = tk.Button(window, text="Connect to Server", width=15, command=lambda: self.connect_to_server(host_name_entry.get().strip(), int(port_name_entry.get())))
        self.connect_button.place(x=1080, y=75)

        self.start_ui_lock.release()

        window.mainloop()



def main():
    client = Client()

if __name__ == "__main__":
   main()
