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

    # TODO: Determine best way to check if files exist or not for remove_files method
    # def __check_file_exists(self, name: str, files: List[str]) -> bool:
    #     """Check if a file has been published/exists or not."""
    #     file_tuples = [(name, file) for file in files]
    #     self._cursor.executemany(
    #         "SELECT * FROM files WHERE client_name = (?) AND file_name = (?)", (name, file_tuples))
    #     if (self._cursor.fetchone()):
    #         return True
    #     else:
    #         return False

    def __check_file_exists(self, file_name: str) -> bool:
        """Check if a file has been published/exists or not."""
        self._cursor.execute(
            "SELECT * FROM files WHERE file_name = (?)", (file_name, ))
        if (self._cursor.fetchone()):
            return True
        else:
            return False

    def register_client(self, clientDto: ClientDto) -> None:
        """
        Registers a new client's name, IP address, UDP socket, and TCP socket.
        Implements `REGISTER` and returns None for `REGISTERED` and 
        StoreException for `REGISTER-DENIED` (Specification 2.1).
        """
        try:
            if (not self.__check_client_exists(clientDto.name)):
                self._cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?)", (
                    clientDto.name, clientDto.ip_address, clientDto.udp_socket, clientDto.tcp_socket))
            else:
                raise Exception(
                    f"name {clientDto.name} already exists in the database")
        except Exception as err:
            raise StoreException("error creating client", err.args)

    def update_client(self, clientDto: ClientDto) -> None:
        """
        Modifies an existing client's IP address, UDP socket, and/or TCP socket.
        Implements `UPDATE-CONTACT` and returns None for `UPDATE-CONFIRMED`
        and StoreException for `UPDATE-DENIED` (Specification 2.5).
        """
        try:
            if (self.__check_client_exists(clientDto.name)):
                sql = "UPDATE clients SET ip_address = (?), udp_socket = (?), tcp_socket = (?) WHERE name = (?)"
                self._cursor.execute(
                    sql, (clientDto.ip_address, clientDto.udp_socket, clientDto.tcp_socket, clientDto.name))
            else:
                raise Exception(
                    f"name {clientDto.name} does not exist in the database")
        except Exception as err:
            raise StoreException("error updating client", err.args)

    # TODO: Delete ALL client information including associated files
    def deregister_client(self, clientDto: ClientDto) -> None:
        """
        Deletes an existing client's name and all associated information.
        Implements `DE-REGISTER` and returns None or StoreException
        depending if the operation succeeds or fails (Specification 2.1).
        """
        try:
            self._cursor.execute(
                "DELETE FROM clients WHERE name = (?)", (clientDto.name,))
        except Exception as err:
            raise StoreException("error deleting client", err.args)

    def publish_files(self, fileDto: FileDto):
        """
        Publishes a list of files available to the client.
        Implements `PUBLISH` and returns None for `PUBLISHED` and 
        StoreException for `PUBLISH-DENIED` (Specification 2.2).
        """
        try:
            if (self.__check_client_exists(fileDto.client_name)):
                file_tuples = [(fileDto.client_name, file)
                               for file in fileDto.files]
                self._cursor.executemany(
                    "INSERT INTO files VALUES (?, ?)", file_tuples)
            else:
                raise Exception(
                    f"name {fileDto.client_name} does not exist in the database")
        except Exception as err:
            raise StoreException("error inserting files", err.args)

    # TODO: Delete operation does not fail if files have already been removed
    def remove_files(self, fileDto: FileDto):
        """
        Removes a file or list of files belonging to a particular client.
        Implements `REMOVE` and returns None for `REMOVED` and 
        StoreException for `REMOVE-DENIED` (Specification 2.2).
        """
        try:
            if (self.__check_client_exists(fileDto.client_name)):
                file_tuples = [(fileDto.client_name, file)
                               for file in fileDto.files]
                self._cursor.executemany(
                    "DELETE FROM files WHERE client_name = (?) AND file_name = (?)", file_tuples)
            else:
                raise Exception(
                    f"name {fileDto.client_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException("error removing files", err.args)

    # TODO: Fix formatting before returning and add docstring comment
    def retrieve_all(self) -> List[FileDto]:
        try:
            sql = "SELECT name, ip_address, tcp_socket, file_name FROM clients INNER JOIN files ON name = client_name"
            self._cursor.execute(sql)
            files = self._cursor.fetchall()
            return files
        except Exception as err:
            raise StoreException("error retrieving clients", err.args)

    def retrieve_info(self, client_name: str, search_name: str) -> Tuple:
        """
        Retrives a client's information if it exists and is registered.
        Implements `RETRIEVE-INFO` and returns None for `RETRIEVE-INFO` and 
        StoreException for `RETRIEVE-ERROR` (Specification 2.3).
        """
        try:
            if (self.__check_client_exists(client_name)):
                sql = "SELECT name, ip_address, tcp_socket FROM clients INNER JOIN files ON name = client_name WHERE name = (?)"
                self._cursor.execute(sql, (search_name,))
                client_info = self._cursor.fetchone()
                self._cursor.execute(
                    "SELECT file_name FROM files INNER JOIN clients ON client_name = name WHERE client_name = (?)", (search_name,))
                file_info = self._cursor.fetchall()
                files = [file[0] for file in file_info]
                client_info += (files,)
                return tuple(client_info)
            else:
                raise Exception(
                    f"file name {client_name} is not registered/does not exist in the database")
        except Exception as err:
            raise StoreException(err.args)

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
        except Exception as err:
            raise StoreException(err.args)
