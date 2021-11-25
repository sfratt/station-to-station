from typing import List

from models.client_dto import ClientDto
from models.file_dto import FileDto

from data.store import Store, StoreException


class ClientStore(Store):
    """
    Client store class that persists data to the SQLite database or retrieves data 
    from the SQLite database. It implements the Repository pattern to achieve loose 
    coupling between the data access layer and controllers, along with the Unit of 
    Work pattern to achieve atomic operations.
    """

    def __init__(self):
        super().__init__()
        self._cursor = self.connection.cursor()

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

            self._cursor.execute(clients_sql)
            self._cursor.execute(files_sql)
        except Exception as e:
            raise StoreException('error creating tables', e.args)

    def __check_client_exists(self, name: str) -> bool:
        """Check if a client is registered/exists or not."""
        self._cursor.execute(
            "SELECT * FROM clients WHERE name = (?)", (name,))
        if (self._cursor.fetchone()):
            return True
        else:
            return False

    def get_all_clients(self) -> List[ClientDto]:
        try:
            self._cursor.execute("SELECT * FROM clients")
            clients = self._cursor.fetchall()
            return clients
        except Exception as e:
            raise StoreException('error retrieving clients', e.args)

    def get_client(self, name: str) -> ClientDto:
        """"""
        try:
            self._cursor.execute(
                "SELECT * FROM clients WHERE name = (?)", (name,))
            client = self._cursor.fetchone()
            return client
        except Exception as e:
            raise StoreException('error retrieving clients', e.args)

    def add_client(self, client: ClientDto) -> None:
        """
        Registers a new client's name, IP address, UDP socket, and TCP socket.
        Implements `REGISTER` and returns None for `REGISTERED` and 
        StoreException for `REGISTER-DENIED` (Specification 2.1).
        """
        try:
            if (not self.__check_client_exists(client.name)):
                self._cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?)", (
                    client.name, client.ip_address, client.udp_socket, client.tcp_socket))
            else:
                raise Exception(
                    f"name {client.name} already exists in the database")
        except Exception as e:
            raise StoreException("error creating client", e.args)

    def update_client(self, client: ClientDto) -> None:
        """
        Modifies an existing client's IP address, UDP socket, and/or TCP socket.
        Implements `UPDATE-CONTACT` and returns None for `UPDATE-CONFIRMED`
        and StoreException for `UPDATE-DENIED` (Specification 2.5).
        """
        try:
            if (self.__check_client_exists(client.name)):
                sql = "UPDATE clients SET ip_address = (?), udp_socket = (?), tcp_socket = (?) WHERE name = (?)"
                self._cursor.execute(
                    sql, (client.ip_address, client.udp_socket, client.tcp_socket, client.name))
            else:
                raise Exception(
                    f"name {client.name} does not exist in the database")
        except Exception as e:
            raise StoreException("error updating client", e.args)

    def delete_client(self, client: ClientDto) -> None:
        """
        Deletes an existing client's name and all associated information.
        Implements `DE-REGISTER` and returns None or StoreException
        depending if the operation succeeds or fails (Specification 2.1).
        """
        try:
            self._cursor.execute(
                "DELETE FROM clients WHERE name = (?)", (client.name,))
        except Exception as e:
            raise StoreException("error deleting client", e.args)

    def get_all_files(self) -> List[FileDto]:
        try:
            sql = "SELECT client_name, file_name FROM clients INNER JOIN files ON name = client_name"
            self._cursor.execute(sql)
            files = self._cursor.fetchall()
            return files
        except Exception as e:
            raise StoreException("error retrieving clients", e.args)

    def add_files(self, name: str, files: List[FileDto]):
        """
        Publishes a list of files available to the client.
        Implements `PUBLISH` and returns None for `PUBLISHED` and 
        StoreException for `PUBLISH-DENIED` (Specification 2.2).
        """
        try:
            if (self.__check_client_exists(name)):
                file_tuples = [(name, file) for file in files]
                self._cursor.executemany(
                    "INSERT INTO files VALUES (?, ?)", file_tuples)
            else:
                raise Exception(f"name {name} does not exist in the database")
        except Exception as e:
            raise StoreException("error inserting files", e.args)

    # deletion of client requires deletion of all files as well
