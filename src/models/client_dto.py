class ClientDto():
    def __init__(self, name: str, ip_address: str = None, udp_socket: int = None, tcp_socket: int = None) -> None:
        self.name = name
        self.ip_address = ip_address
        self.udp_socket = udp_socket
        self.tcp_socket = tcp_socket
