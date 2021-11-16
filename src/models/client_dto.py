class ClientDto():
    def __init__(self, name, ip_address, udp_socket, tcp_socket) -> None:
        self.name = name
        self.ip_address = ip_address
        self.udp_socket = udp_socket
        self.tcp_socket = tcp_socket
