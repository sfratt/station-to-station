from data.store import Store, StoreException
from models.client_dto import ClientDto
from models.file_dto import FileDto


class ClientStore(Store):
    """Concrete implementation of the Repository and Unit of Work patterns for the SQLite database."""

    def __init__(self):
        super().__init__()
        self.cursor = self.connection.cursor()

    def create_tables(self) -> None:
        """Create the `clients` and `files` tables in the SQLite database."""
        try:
            clients_sql = """CREATE TABLE clients (
                            name TEXT,
                            ip_address TEXT,
                            udp_socket INTEGER,
                            tcp_socket INTEGER,
                            PRIMARY KEY (name)
                        )"""

            files_sql = """CREATE TABLE files (
                            client_name TEXT REFERENCES clients (name),
                            file_name TEXT,
                            PRIMARY KEY (client_name, file_name)
                        )"""

            self.cursor.execute(clients_sql)
            self.cursor.execute(files_sql)
        except Exception as e:
            raise StoreException('error creating tables', e.args)

    def get_all_clients(self) -> list[ClientDto]:
        try:
            self.cursor.execute("SELECT * FROM clients")
            clients = self.cursor.fetchall()
            return clients
        except Exception as e:
            raise StoreException('error retrieving clients', e.args)

    # def check_client_exists(self, client: ClientDto) -> bool:
    #     sql = "SELECT * FROM clients WHERE name = (?)"
    #     self.cursor.execute(sql, (client.name,))
    #     if (self.cursor.fetchone()):
    #         return True
    #     else:
    #         return False
        # client = self._cursor.fetchone()
        # return client

    def add_client(self, client: ClientDto) -> None:
        try:
            # if (not self.check_client_exists(client)):
            self.cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?)", (
                client.name, client.ip_address, client.udp_socket, client.tcp_socket))
        # else:
        except Exception as e:
            raise StoreException(
                f"name {client.name} already exists in the database", e.args)

    def delete_client(self, client: ClientDto) -> None:
        try:
            self.cursor.execute(
                "DELETE FROM clients WHERE name = (?)", (client.name,))
        except Exception as e:
            raise StoreException("error deleting client", e.args)

    def update_client(self, client: ClientDto) -> None:
        try:
            sql = "UPDATE clients SET name = (?), ip_address = (?), udp_socket = (?), tcp_socket = (?) WHERE name = (?)"
            self.cursor.execute(
                sql, (client.name, client.ip_address, client.udp_socket, client.tcp_socket, client.name))
        except Exception as e:
            raise StoreException("error updating client", e.args)

    def get_all_files(self) -> list[FileDto]:
        try:
            sql = "SELECT client_name, file_name FROM clients INNER JOIN files ON name = client_name"
            self.cursor.execute(sql)
            files = self.cursor.fetchall()
            return files
        except Exception as e:
            raise StoreException('error retrieving clients', e.args)

    # deletion of client requires deletion of all files as well
