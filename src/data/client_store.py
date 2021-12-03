from typing import List, Tuple

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
        except Exception as err:
            raise StoreException(err)

    def __check_client_exists(self, client_name: str) -> bool:
        """Check if a client is registered/exists or not."""
        self._cursor.execute(
            "SELECT * FROM clients WHERE name = (?)", (client_name,))
        if (self._cursor.fetchone()):
            return True
        else:
            return False

    def __check_files_exist(self, name: str, files: List[str]) -> bool:
        """Check if files have been published/exist for a particular client."""
        sql = "SELECT * FROM files WHERE client_name = (?) AND file_name IN ({0})".format(
            ', '.join('?' for _ in files))
        self._cursor.execute(sql, (name, *files))
        if (self._cursor.fetchall()):
            return True
        else:
            return False

    def __check_file_exists(self, file_name: str) -> bool:
        """Check if a file has been published/exists or not."""
        self._cursor.execute(
            "SELECT * FROM files WHERE file_name = (?)", (file_name, ))
        if (self._cursor.fetchone()):
            return True
        else:
            return False

    def register_client(self, client_dto: ClientDto) -> None:
        """
        Registers a new client's name, IP address, UDP socket, and TCP socket.
        Implements `REGISTER` and returns None for `REGISTERED` and 
        StoreException for `REGISTER-DENIED` (Specification 2.1).
        """
        try:
            if (not self.__check_client_exists(client_dto.name)):
                self._cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?)", (
                    client_dto.name, client_dto.ip_address, client_dto.udp_socket, client_dto.tcp_socket))
            else:
                raise Exception(
                    f"name {client_dto.name} already exists in the database")
        except Exception as err:
            raise StoreException(err)

    def update_client(self, client_dto: ClientDto) -> None:
        """
        Modifies an existing client's IP address, UDP socket, and/or TCP socket.
        Implements `UPDATE-CONTACT` and returns None for `UPDATE-CONFIRMED`
        and StoreException for `UPDATE-DENIED` (Specification 2.5).
        """
        try:
            if (self.__check_client_exists(client_dto.name)):
                sql = "UPDATE clients SET ip_address = (?), udp_socket = (?), tcp_socket = (?) WHERE name = (?)"
                self._cursor.execute(
                    sql, (client_dto.ip_address, client_dto.udp_socket, client_dto.tcp_socket, client_dto.name))
            else:
                raise Exception(
                    f"name {client_dto.name} does not exist in the database")
        except Exception as err:
            raise StoreException(err)

    def deregister_client(self, name: str) -> None:
        """
        Deletes an existing client's name and all associated information.
        Implements `DE-REGISTER` and returns None or StoreException
        depending if the operation succeeds or fails (Specification 2.1).
        """
        try:
            if (self.__check_client_exists(name)):
                self._cursor.execute(
                    "DELETE FROM files WHERE client_name = (?)", (name,))
                self._cursor.execute(
                    "DELETE FROM clients WHERE name = (?)", (name,))
            else:
                raise Exception(
                    f"name {name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err)

    def publish_files(self, file_dto: FileDto) -> None:
        """
        Publishes a list of files available to the client.
        Implements `PUBLISH` and returns None for `PUBLISHED` and 
        StoreException for `PUBLISH-DENIED` (Specification 2.2).
        """
        try:
            if (self.__check_client_exists(file_dto.client_name)):
                file_tuples = [(file_dto.client_name, file)
                               for file in file_dto.files]
                self._cursor.executemany(
                    "INSERT INTO files VALUES (?, ?)", file_tuples)
            else:
                raise Exception(
                    f"name {file_dto.client_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err)

    def remove_files(self, file_dto: FileDto) -> None:
        """
        Removes a file or list of files belonging to a particular client.
        Implements `REMOVE` and returns None for `REMOVED` and 
        StoreException for `REMOVE-DENIED` (Specification 2.2).
        """
        try:
            if (self.__check_client_exists(file_dto.client_name)):
                if (self.__check_files_exist(file_dto.client_name, file_dto.files)):
                    file_tuples = [(file_dto.client_name, file)
                                   for file in file_dto.files]
                    self._cursor.executemany(
                        "DELETE FROM files WHERE client_name = (?) AND file_name = (?)", file_tuples)
                else:
                    raise Exception(
                        f"trying to remove file(s) {file_dto.files} that do not exist in the database")
            else:
                raise Exception(
                    f"name {file_dto.client_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err)

    def retrieve_all(self, client_name: str) -> List:
        """
        Retrieves name, IP address, TCP socket and file list for all clients.
        Implements `RETRIEVE-ALL` and returns None for `RETRIEVE` and 
        StoreException for `RETRIEVE-ERROR` (Specification 2.3).
        """
        try:
            if (self.__check_client_exists(client_name)):
                self._cursor.execute(
                    "SELECT name, ip_address, tcp_socket FROM clients")
                clients = self._cursor.fetchall()
                all_info = []
                for client in clients:
                    self._cursor.execute(
                        "SELECT file_name FROM clients LEFT JOIN files ON name = client_name WHERE name = (?)", (client[0],))
                    files = self._cursor.fetchall()
                    files_info = [file[0]
                                  for file in files if not file[0] is None]
                    client += (files_info,)
                    all_info.append(client)
                return all_info
            else:
                raise Exception(
                    f"name {client_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err)

    def retrieve_info(self, client_name: str, search_name: str) -> Tuple:
        """
        Retrieves a single client's name, IP address, TCP socket and file list.
        Implements `RETRIEVE-INFO` and returns None for `RETRIEVE-INFO` and 
        StoreException for `RETRIEVE-ERROR` (Specification 2.3).
        """
        try:
            if (self.__check_client_exists(client_name) and self.__check_client_exists(search_name)):
                sql = "SELECT name, ip_address, tcp_socket FROM clients WHERE name = (?)"
                self._cursor.execute(sql, (search_name,))
                client_info = self._cursor.fetchone()
                self._cursor.execute(
                    "SELECT file_name FROM clients LEFT JOIN files ON name = client_name WHERE name = (?)", (search_name,))
                files = self._cursor.fetchall()
                file_info = [file[0]
                             for file in files if not file[0] is None]
                client_info += (file_info,)
                return tuple(client_info)
            else:
                raise Exception(
                    f"name {client_name} or {search_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err)

    def search_file(self, client_name: str, file_name: str) -> List:
        """
        Searches for a specific file and responds with the associated client information.
        Implements `SEARCH-FILE` and returns None for `SEARCH-FILE` and 
        StoreException for `SEARCH-ERROR` (Specification 2.3).
        """
        try:
            if (self.__check_client_exists(client_name)):
                if (self.__check_file_exists(file_name)):
                    sql = "SELECT name, ip_address, tcp_socket FROM files INNER JOIN clients ON client_name = name WHERE file_name = (?)"
                    self._cursor.execute(sql, (file_name,))
                    files = self._cursor.fetchall()
                    return files
                else:
                    raise Exception(
                        f"file name {file_name} does not exist in the database")
            else:
                raise Exception(
                    f"name {client_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err)
