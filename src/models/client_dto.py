class ClientDto():
    def __init__(self, name: str, ip_address: str, udp_socket: int, tcp_socket: int) -> None:
        self.name = name
        self.ip_address = ip_address
        self.udp_socket = udp_socket
        self.tcp_socket = tcp_socket
